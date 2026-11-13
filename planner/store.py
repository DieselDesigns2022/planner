"""Transactional SQLite persistence, snapshots, and append-only meal revisions."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from .ingredients import parse_text, aggregate
from .engine import dates, validate, generate

def now(): return datetime.now(timezone.utc).isoformat()
def dump(value): return json.dumps(value,ensure_ascii=False)

class Store:
    def __init__(self,path):
        self.path=str(path)
        Path(path).parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS migrations(version INTEGER PRIMARY KEY);
                CREATE TABLE IF NOT EXISTS recipes(id INTEGER PRIMARY KEY, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS meals(date TEXT PRIMARY KEY, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS plans(start TEXT PRIMARY KEY, created TEXT NOT NULL, updated TEXT NOT NULL, groceries TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS revisions(id INTEGER PRIMARY KEY, start TEXT NOT NULL, kind TEXT NOT NULL, created TEXT NOT NULL, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            ''')
            if not db.execute('SELECT 1 FROM migrations WHERE version=1').fetchone():
                for recipe in json.loads(Path(__file__).with_name('seed.json').read_text()):
                    recipe.update(ingredients=parse_text(recipe['ingredient_text']),archived=False,created=now(),updated=now())
                    db.execute('INSERT INTO recipes(id,data) VALUES(?,?)',(recipe['id'],dump(recipe)))
                for key,value in [('season','winter'),('budget',300),('timezone','America/Detroit'),('eat_out_anchor','2026-10-16')]:
                    db.execute('INSERT INTO settings VALUES(?,?)',(key,dump(value)))
                db.execute('INSERT INTO migrations VALUES(1)')
    def connect(self):
        db=sqlite3.connect(self.path,timeout=15)
        db.row_factory=sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA journal_mode=WAL')
        return db
    def recipes(self,db): return {r['id']:json.loads(r['data']) for r in db.execute('SELECT * FROM recipes')}
    def meals(self,db): return [json.loads(r[0]) for r in db.execute('SELECT data FROM meals ORDER BY date')]
    def settings(self,db): return {r[0]:json.loads(r[1]) for r in db.execute('SELECT * FROM settings')}
    def revision(self,db,start,kind):
        calendar=dates(start)
        meals=[m for m in self.meals(db) if m['date'] in calendar]
        db.execute('INSERT INTO revisions(start,kind,created,data) VALUES(?,?,?,?)',(start,kind,now(),dump(meals)))
    def save_meal(self,db,meal,recipes):
        meal=meal.copy()
        meal['snapshot']=recipes.get(meal.get('recipe_id'))
        meal['updated']=now()
        db.execute('INSERT INTO meals VALUES(?,?) ON CONFLICT(date) DO UPDATE SET data=excluded.data',(meal['date'],dump(meal)))
    def state(self,start=None):
        with self.connect() as db:
            recipes=self.recipes(db); settings=self.settings(db)
            plans=[dict(r) for r in db.execute('SELECT start,created,updated FROM plans ORDER BY start DESC')]
            if start: dates(start)
            elif plans: start=plans[0]['start']
            meals=[m for m in self.meals(db) if start and m['date'] in dates(start)]
            row=db.execute('SELECT groceries FROM plans WHERE start=?',(start,)).fetchone() if start else None
            edits=json.loads(row[0]) if row else {'additions':[],'overrides':{},'excluded':[],'checked':[]}
            groceries=aggregate(meals,recipes,settings['season'])
            for item in groceries:
                item['excluded']=item['id'] in edits['excluded']
                item['checked']=item['id'] in edits['checked']
                if item['id'] in edits['overrides']: item['quantity']=edits['overrides'][item['id']]
            groceries.extend(edits['additions'])
            return dict(recipes=list(recipes.values()),settings=settings,plans=plans,start=start,meals=meals,groceries=groceries,grocery_edits=edits,saved=bool(row))
    def save_recipe(self,data):
        title=data.get('title','').strip()
        if not title or len(title)>200: raise ValueError('Recipe title must be 1–200 characters.')
        ingredients=parse_text(data.get('ingredient_text',''))
        if not ingredients: raise ValueError('Add at least one ingredient.')
        if data.get('cost') not in ['budget','moderate','higher']: raise ValueError('Select a valid cost category.')
        instructions=data.get('instructions','')
        if not isinstance(instructions,str) or len(instructions)>30000: raise ValueError('Instructions are too long.')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            recipes=self.recipes(db); ident=data.get('id')
            if ident is not None and ident not in recipes: raise ValueError('Recipe not found.')
            ident=ident if ident is not None else max(recipes.keys(),default=0)+1
            old=recipes.get(ident,{})
            recipe=dict(id=ident,title=title,ingredient_text=data['ingredient_text'],ingredients=ingredients,instructions=instructions,
                        taco=bool(data.get('taco')),crockpot=bool(data.get('crockpot')),weekend=bool(data.get('weekend')),
                        cost=data['cost'],archived=old.get('archived',False),created=old.get('created',now()),updated=now(),review=old.get('review',''))
            db.execute('INSERT INTO recipes VALUES(?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data',(ident,dump(recipe)))
            return recipe
    def archive(self,ident):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            recipe=self.recipes(db).get(ident)
            if not recipe: raise ValueError('Recipe not found.')
            recipe.update(archived=True,updated=now())
            db.execute('UPDATE recipes SET data=? WHERE id=?',(dump(recipe),ident))
    def plan(self,start,replace=False,seed=None):
        calendar=dates(start)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT 1 FROM plans WHERE start=?',(start,)).fetchone() and not replace: return
            recipes=self.recipes(db); history=self.meals(db)
            existing={m['date']:m for m in history if m['date'] in calendar}
            if replace:
                # Snapshot every affected saved menu before intentional shared-date replacement.
                for row in db.execute('SELECT start FROM plans').fetchall():
                    if set(dates(row[0])) & set(calendar): self.revision(db,row[0],'before regeneration')
            result=generate(start,list(recipes.values()),history,{} if replace else existing,seed)
            for meal in result:
                if not replace and meal['date'] in existing: continue
                self.save_meal(db,meal,recipes)
            edits=dump({'additions':[],'overrides':{},'excluded':[],'checked':[]})
            db.execute('INSERT INTO plans VALUES(?,?,?,?) ON CONFLICT(start) DO UPDATE SET updated=excluded.updated,groceries=excluded.groceries',(start,now(),now(),edits))
            db.execute('UPDATE plans SET updated=? WHERE start<=? AND date(start,"+13 days")>=?',(now(),calendar[-1],start))
            self.revision(db,start,'generated' if not replace else 'regenerated')
    def change_meal(self,start,value,recipe_id=None,special=None):
        if value not in dates(start): raise ValueError('Date is outside this menu.')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if not db.execute('SELECT 1 FROM plans WHERE start=?',(start,)).fetchone(): raise ValueError('Generate or open a saved menu first.')
            recipes=self.recipes(db)
            meal=dict(date=value,recipe_id=recipe_id,special=special,manual=True)
            validate(meal,recipes)
            affected=[r[0] for r in db.execute('SELECT start FROM plans') if value in dates(r[0])]
            for menu in affected: self.revision(db,menu,'before dinner change')
            self.save_meal(db,meal,recipes)
            for menu in affected:
                db.execute('UPDATE plans SET updated=? WHERE start=?',(now(),menu))
                self.revision(db,menu,'dinner changed')
    def grocery(self,start,edits):
        dates(start)
        if not isinstance(edits,dict) or set(edits)!={'additions','overrides','excluded','checked'}: raise ValueError('Invalid grocery edits.')
        if any(not isinstance(edits[k],list) for k in ['additions','excluded','checked']) or not isinstance(edits['overrides'],dict): raise ValueError('Invalid grocery edit format.')
        if len(dump(edits))>50000: raise ValueError('Shopping list is too large.')
        for item in edits['additions']:
            if not isinstance(item,dict) or not isinstance(item.get('name'),str) or not item['name'].strip() or not isinstance(item.get('quantity'),str) or not str(item.get('id','')).startswith('manual:'):
                raise ValueError('Invalid extra grocery item.')
            item['category']='Other'
        if any(not isinstance(v,str) for v in list(edits['overrides'].values())+edits['checked']+edits['excluded']): raise ValueError('Invalid grocery edit value.')
        with self.connect() as db:
            if not db.execute('UPDATE plans SET groceries=?,updated=? WHERE start=?',(dump(edits),now(),start)).rowcount: raise ValueError('Menu not found.')
    def season(self,season):
        if season not in ['summer','winter']: raise ValueError('Choose Summer or Winter.')
        with self.connect() as db: db.execute('UPDATE settings SET value=? WHERE key="season"',(dump(season),))
    def history(self):
        with self.connect() as db:
            return dict(meals=self.meals(db),revisions=[dict(r,data=json.loads(r['data'])) for r in db.execute('SELECT * FROM revisions ORDER BY id DESC')])
    def backup(self,target):
        # sqlite backup API includes committed WAL contents, unlike copying a live db file.
        with self.connect() as source, sqlite3.connect(target) as dest: source.backup(dest)
        with sqlite3.connect(target) as db:
            if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok': raise RuntimeError('Backup verification failed.')
