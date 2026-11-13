import copy
import json
import tempfile
import unittest
from pathlib import Path
from datetime import date,timedelta
from planner.engine import generate,dates,eat_out,allowed,day
from planner.ingredients import parse_line,parse_text,aggregate
from planner.store import Store

class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'planner.sqlite3'; self.store=Store(self.path)
        self.recipes={r['id']:r for r in self.store.state()['recipes']}
    def meal(self,ident,value='2026-11-16'):return dict(date=value,recipe_id=ident,snapshot=self.recipes[ident])
    def test_seed_matches_all_authoritative_lines_and_repeatable_migration(self):
        seed=json.loads(Path('planner/seed.json').read_text());self.assertEqual(len(seed),29)
        # Independent extraction from authoritative specification catches import omissions.
        import re
        text=Path('docs/SPECIFICATION.md').read_text();section=text[text.index('## Regular Dinners (1–22)'):text.index('# 8. Shopping List Generator')]
        for m in re.finditer(r'### (\d+)\. (.*?)\n(.*?)(?=\n### |\Z)',section,re.S):
            r=self.recipes[int(m[1])];self.assertEqual(r['title'],m[2]);self.assertEqual(r['ingredient_text'].splitlines(),re.findall(r'^- (.+)$',m[3],re.M));self.assertEqual(r['instructions'],'')
        Store(self.path);self.assertEqual(len(self.store.state()['recipes']),29)
        self.assertEqual(self.recipes[23]['ingredients'][0]['quantity'],2.5)
        self.assertEqual(self.recipes[23]['ingredients'][0]['name'],'Beef stew meat')
        self.assertTrue(self.recipes[1]['review'])
    def test_A_november_14(self):
        meals=generate('2026-11-14',list(self.recipes.values()),[],seed=9);self.assertEqual(len(meals),14)
        self.assertEqual([m['date'] for m in meals],dates('2026-11-14'));bydate={m['date']:m for m in meals}
        for d in ['2026-11-14','2026-11-21']:self.assertEqual(bydate[d]['special'],'Fend for Yourself')
        for d in ['2026-11-17','2026-11-24']:self.assertTrue(self.recipes[bydate[d]['recipe_id']]['taco'])
        for d in ['2026-11-19','2026-11-26']:self.assertTrue(self.recipes[bydate[d]['recipe_id']]['crockpot'])
        self.assertIsNotNone(bydate['2026-11-20']['recipe_id']);self.assertEqual(bydate['2026-11-27']['special'],'Eat Out')
    def test_B_friday_anchor(self):
        for d in ['2026-10-16','2026-10-30','2026-11-13','2026-11-27']:self.assertTrue(eat_out(d))
        for d in ['2026-10-23','2026-11-06','2026-11-20','2026-12-04']:self.assertFalse(eat_out(d))
    def test_C_D_calendar_rules_many_starts_dst_year_boundary(self):
        off_thursday=False
        for offset in range(100):
            start=(date(2026,10,1)+timedelta(days=offset)).isoformat()
            result=generate(start,list(self.recipes.values()),[],seed=offset)
            self.assertEqual([m['date'] for m in result],dates(start))
            for m in result:
                if m['recipe_id']:
                    r=self.recipes[m['recipe_id']];self.assertTrue(allowed(r,m['date']))
                    if r['weekend']:self.assertIn(day(m['date']).weekday(),[5,6])
                    if r['crockpot'] and day(m['date']).weekday()!=3:off_thursday=True
        self.assertTrue(off_thursday)
        self.assertEqual(dates('2026-12-28')[-1],'2027-01-10')
        self.assertEqual(dates('2028-02-25')[4],'2028-02-29')
    def test_E_quantity_aggregation(self):
        r={1:dict(ingredients=parse_text('Ground beef — 2 lbs\nCorn — 2 cans\nChicken broth — 2 cups\nChicken breasts — 2')),2:dict(ingredients=parse_text('Ground beef — 4 lbs\nCanned corn — 1 can\nChicken broth — ½ cup\nChicken breasts — 6'))}
        groceries={x['id']:x for x in aggregate([dict(date='2026-11-16',recipe_id=i) for i in [1,2]],r)}
        for key,value in [('ground beef','6 lbs'),('corn','3 cans'),('chicken broth','2.5 cups'),('chicken breasts','8')]:self.assertEqual(groceries[key]['quantity'],value)
        r[2]['ingredients']+=parse_text('Chicken breasts — 2.5 lbs\nCorn — 2 large cans\nChicken broth')
        groceries={x['id']:x for x in aggregate([dict(date='2026-11-16',recipe_id=i) for i in [1,2]],r)}
        self.assertEqual(groceries['chicken breasts']['quantity'],'8; 2.5 lbs')
        self.assertIn('2 large cans',groceries['corn']['quantity']);self.assertIn('additional amount not specified',groceries['chicken broth']['quantity'])
        self.assertEqual(parse_line('Broth — 2½ cups')['quantity'],2.5)
        converted=aggregate([dict(date='2026-11-16',recipe_id=1)],{1:dict(ingredients=parse_text('Broth — 1 cup\nBroth — 8 tbsp\nGround beef — 1 lb\nGround beef — 16 oz'))})
        self.assertEqual({x['id']:x['quantity'] for x in converted},{'broth':'1.5 cups','ground beef':'2 lbs'})
    def test_F_eggs_season_persists(self):
        meals=[self.meal(17)]
        self.assertIn('eggs',[x['id'] for x in aggregate(meals,self.recipes,'winter')]);self.assertNotIn('eggs',[x['id'] for x in aggregate(meals,self.recipes,'summer')])
        self.store.season('summer');self.assertEqual(Store(self.path).state()['settings']['season'],'summer');self.assertIn('Eggs',self.recipes[17]['ingredient_text'])
    def test_G_halloween_and_alternatives(self):
        self.assertIn('sour cream',[x['id'] for x in aggregate([self.meal(21,'2026-10-31')],self.recipes)])
        self.assertNotIn('sour cream',[x['id'] for x in aggregate([self.meal(21)],self.recipes)])
        alternatives=[x for x in aggregate([self.meal(17)],self.recipes) if ' or ' in x['name']]
        self.assertEqual(len(alternatives),1);self.assertEqual(alternatives[0]['name'],'Bacon or sausage links')
    def test_H_recipe_edit_current_groceries_historical_snapshot(self):
        self.store.plan('2026-11-14',seed=3);self.store.change_meal('2026-11-14','2026-11-16',7)
        recipe=copy.deepcopy(self.recipes[7]);recipe['title']='Edited Helper';recipe['ingredient_text']='Ground beef — 9 lbs\nSpecial test ingredient — 2 cans'
        self.store.save_recipe(recipe)
        state=Store(self.path).state('2026-11-14');self.assertIn('special test ingredient',[i['id'] for i in state['groceries']]);m=next(m for m in state['meals'] if m['date']=='2026-11-16');self.assertEqual(m['snapshot']['title'],'Hamburger Helper')
        self.assertTrue(any(m['snapshot'] and m['snapshot']['title']=='Hamburger Helper' for v in self.store.history()['revisions'] for m in v['data']))
    def test_I_manual_changes_and_shopping_persistence(self):
        start='2026-11-14';self.store.plan(start,seed=1);before=self.store.state(start)
        edits=dict(additions=[dict(id='manual:test',name='Apples',quantity='1 bag',category='Other')],overrides={'corn':'9 cans'},excluded=['ground beef'],checked=['corn'])
        self.store.grocery(start,edits);self.store.change_meal(start,'2026-11-14',23)
        after=Store(self.path).state(start)
        self.assertEqual(before['meals'][1:],after['meals'][1:]);self.assertEqual(after['grocery_edits'],edits)
        self.assertIn('beef stew meat',[i['id'] for i in after['groceries']]);self.assertEqual(after['meals'][0]['recipe_id'],23)
        for value,ident in [('2026-11-17',7),('2026-11-19',1),('2026-11-27',23),('2026-11-16',15)]:
            with self.assertRaises(ValueError):self.store.change_meal(start,value,ident)
    def test_J_archive_preserves_history(self):
        self.store.plan('2026-11-14',seed=2);self.store.change_meal('2026-11-14','2026-11-14',23);self.store.archive(23)
        state=Store(self.path).state('2026-11-14');self.assertTrue(next(r for r in state['recipes'] if r['id']==23)['archived']);self.assertEqual(state['meals'][0]['snapshot']['title'],'Beef Stew')
        result=generate('2026-12-01',state['recipes'],state['meals'],seed=2);self.assertNotIn(23,[m['recipe_id'] for m in result])
    def test_K_history_variety_and_retention(self):
        history=[]
        for i in range(8):
            start=(date(2026,9,1)+timedelta(days=i*14)).isoformat();self.store.plan(start,seed=i);meals=self.store.state(start)['meals']
            selected=[m['recipe_id'] for m in meals if m['recipe_id']];self.assertEqual(len(selected),len(set(selected)))
            history.extend(meals)
        self.assertEqual(len(self.store.history()['meals']),112)
        # With equivalent candidates, an unserved recipe outranks a recently served one.
        simple=[dict(id=i,taco=True,crockpot=True,weekend=False,cost='budget') for i in range(1,30)]
        recent=[dict(date='2026-11-13',recipe_id=i) for i in range(1,15)]
        chosen=generate('2026-11-14',simple,recent,seed=0)
        self.assertTrue(all(m['recipe_id'] is None or m['recipe_id']>=15 for m in chosen))
    def test_L_safe_regeneration_and_overlaps(self):
        start='2026-11-14';self.store.plan(start,seed=1);before=self.store.state(start)
        self.store.plan(start,seed=2);self.assertEqual(before['meals'],self.store.state(start)['meals'])
        self.store.plan('2026-11-20',seed=2);overlap=self.store.state('2026-11-20');self.assertEqual(before['meals'][6:],overlap['meals'][:8])
        self.store.change_meal(start,'2026-11-21',23);self.assertEqual(self.store.state('2026-11-20')['meals'][1]['recipe_id'],23)
        self.store.plan(start,replace=True,seed=8);after=self.store.state(start);self.assertNotEqual(before['meals'],after['meals']);self.assertEqual(len(after['meals']),14)
        self.assertEqual(len({i['id'] for i in after['groceries']}),len(after['groceries']))
        self.assertTrue(any(v['kind']=='before regeneration' for v in self.store.history()['revisions']))
    def test_conflict_rolls_back_and_verified_backup(self):
        for ident in [1,4,6]:self.store.archive(ident)
        with self.assertRaises(ValueError):self.store.plan('2026-11-14')
        self.assertEqual(self.store.history()['meals'],[])
        target=Path(self.tmp.name)/'backup.sqlite3';self.store.backup(target);self.assertEqual(len(Store(target).state()['recipes']),29)
    def test_invalid_inputs(self):
        for start in ['bad','2026-02-30',None,'20261114']:
            with self.assertRaises(ValueError):dates(start)
        with self.assertRaises(ValueError):self.store.season('autumn')
        with self.assertRaises(ValueError):self.store.save_recipe(dict(title='',ingredient_text='Eggs',cost='budget'))

if __name__=='__main__':unittest.main()
