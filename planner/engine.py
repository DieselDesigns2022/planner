"""Calendar-only dates avoid DST drift; hard rules precede ranked variety."""
from datetime import date, timedelta
import random

ANCHOR = date(2026,10,16)

def day(value):
    if not isinstance(value,str) or len(value)!=10:
        raise ValueError('Use a calendar date in YYYY-MM-DD format.')
    try: return date.fromisoformat(value)
    except ValueError: raise ValueError('Use a valid calendar date in YYYY-MM-DD format.')

def dates(start):
    first=day(start)
    try: return [(first+timedelta(days=i)).isoformat() for i in range(14)]
    except OverflowError: raise ValueError('That date range is outside the supported calendar.')

def eat_out(value):
    d=day(value)
    return d.weekday()==4 and (d-ANCHOR).days % 14 == 0

def allowed(recipe, value):
    weekday=day(value).weekday()
    return (not eat_out(value) and (not recipe['weekend'] or weekday>=5)
            and (weekday!=1 or recipe['taco']) and (weekday!=3 or recipe['crockpot']))

def validate(meal, recipes):
    d=day(meal['date'])
    if meal.get('recipe_id'):
        r=recipes.get(meal['recipe_id'])
        if not r or r.get('archived') or not allowed(r,meal['date']):
            raise ValueError('Dinner violates a calendar rule or is archived. Tuesdays need taco meals, Thursdays need crockpot meals, weekend-only meals require a weekend, and eat-out Fridays are fixed.')
    elif meal.get('special') != ('Eat Out' if eat_out(meal['date']) else 'Fend for Yourself' if d.weekday()==5 else None):
        raise ValueError('This date needs an eligible dinner.')

def generate(start, recipes, history, existing=None, seed=None):
    rng=random.Random(seed)
    existing=existing or {}
    active={r['id']:r for r in recipes if not r.get('archived')}
    result={}
    calendar=dates(start)
    # Reserve restricted dates before ordinary dates so ordinary dinners do not
    # consume all the taco/crockpot variety. Preserve saved overlapping dates.
    for value in calendar:
        if value in existing:
            result[value]=existing[value].copy()
        elif eat_out(value) or day(value).weekday()==5:
            result[value]=dict(date=value,recipe_id=None,special='Eat Out' if eat_out(value) else 'Fend for Yourself',manual=False)
    pending=[v for v in calendar if v not in result]
    pending.sort(key=lambda v:(day(v).weekday() not in (1,3),v))
    for value in pending:
        eligible=[r for r in active.values() if allowed(r,value)]
        if not eligible: raise ValueError(f'No eligible recipe for {value}. Add or restore a '+('Taco Tuesday' if day(value).weekday()==1 else 'crockpot' if day(value).weekday()==3 else 'dinner')+' recipe.')
        d=day(value)
        nearby=[m for m in history+list(result.values()) if m.get('recipe_id') and m['date']!=value and abs((day(m['date'])-d).days)<=60]
        def score(r):
            same=[abs((day(m['date'])-d).days) for m in nearby if m['recipe_id']==r['id']]
            used=sum(m.get('recipe_id')==r['id'] for m in result.values())
            consecutive=any(n==1 for n in same)
            recent=sum((61-n)/8 for n in same)
            higher_neighbor=any(abs((day(m['date'])-d).days)<=2 and active.get(m['recipe_id'],{}).get('cost')=='higher' for m in nearby)
            cost=(10 if higher_neighbor else 3) if r['cost']=='higher' else 0
            return 1000*consecutive+100*used+recent+cost+rng.random()*5
        chosen=min(eligible,key=score)
        result[value]=dict(date=value,recipe_id=chosen['id'],special=None,manual=False)
    for value in calendar:
        # Existing archived recipes remain valid saved dinners; do not rewrite them.
        if value not in existing: validate(result[value],active)
    return [result[v] for v in calendar]
