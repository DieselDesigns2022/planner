"""Lossless ingredient parsing and conservative grocery aggregation."""
import re
from fractions import Fraction

CATEGORIES = ['Meat & Poultry', 'Dairy & Eggs', 'Bread, Pasta & Grains',
              'Canned & Packaged Foods', 'Produce & Fresh Herbs', 'Frozen Foods',
              'Sauces, Oils & Seasonings', 'Other']
FRACTIONS = {'½': '1/2', '¼': '1/4', '¾': '3/4', '⅓': '1/3', '⅔': '2/3', '⅛': '1/8', '⅜': '3/8', '⅝': '5/8', '⅞': '7/8'}
UNITS = {'lb':'lbs','lbs':'lbs','pound':'lbs','pounds':'lbs','oz':'oz','ounce':'oz','ounces':'oz',
         'cup':'cups','cups':'cups','tbsp':'tbsp','tablespoon':'tbsp','tablespoons':'tbsp',
         'tsp':'tsp','teaspoon':'tsp','teaspoons':'tsp','can':'cans','cans':'cans',
         'box':'boxes','boxes':'boxes','bag':'bags','bags':'bags','pack':'packs','packs':'packs',
         'loaf':'loaves','loaves':'loaves','ct':'count'}
# Only exact, known equivalents. Never infer cheese, meat-cut or package equivalence.
ALIASES = {'canned corn':'corn', 'boxed macaroni & cheese':'macaroni & cheese'}

def canonical(name):
    key = re.sub(r'\s+', ' ', name.strip().casefold())
    return ALIASES.get(key, key)

def amount(value):
    text = value.strip()
    for glyph, fraction in FRACTIONS.items():
        text = re.sub(r'(\d)' + glyph, r'\1 ' + fraction, text)
        text = text.replace(glyph, fraction)
    return float(sum((Fraction(x) for x in text.split()), Fraction()))

def parse_line(line):
    name, sep, detail = line.strip().partition(' — ')
    if not sep:
        name, sep, detail = line.strip().partition(' – ')
    if not sep:
        name, sep, detail = line.strip().partition(' - ')
    result = dict(name=name.strip(), quantity=None, unit=None, note=detail.strip(),
                  display_text=line.strip(), optional=False, alternatives=[], condition=None)
    if not name.strip():
        raise ValueError('Each ingredient needs a name.')
    if ' or ' in name.casefold():
        result['alternatives'] = re.split(r'\s+or\s+', name, flags=re.I)
    if canonical(name) == 'sour cream' and detail.casefold() == 'halloween only':
        result['condition'] = 'halloween'
    # Ranges and qualified packages retain their exact wording, with no invented totals.
    m = re.fullmatch(r'([\d./ ½¼¾⅓⅔⅛⅜⅝⅞]+)(?:\s+([A-Za-z]+))?(?:,\s*(.*))?', detail.strip())
    if m and (not m[2] or m[2].lower() in UNITS):
        try:
            result.update(quantity=amount(m[1]), unit=UNITS.get((m[2] or '').lower(), 'count'), note=m[3] or '')
        except (ValueError, ZeroDivisionError):
            pass
    return result

def parse_text(text):
    if not isinstance(text, str) or len(text) > 30000:
        raise ValueError('Ingredients must be text under 30,000 characters.')
    return [parse_line(line) for line in text.splitlines() if line.strip()]

def category(name):
    n = canonical(name)
    if 'broth' in n: return CATEGORIES[6]
    if any(w in n for w in ['frozen', 'steak-ums']): return CATEGORIES[5]
    if any(w in n for w in ['soup','canned','beans','corn','peas','tomato sauce','hamburger helper','skillet dinner','doritos','crackers','dip mix','instant mashed','macaroni & cheese']): return CATEGORIES[3]
    if any(w in n for w in ['chicken breast','beef','pork','sausage','bacon','chuck roast']): return CATEGORIES[0]
    if any(w in n for w in ['cheese','milk','cream','butter','eggs','refrigerated']): return CATEGORIES[1]
    if any(w in n for w in ['fresh ','potato','carrot']): return CATEGORIES[4]
    if any(w in n for w in ['bread','noodle','rice','rolls','bun','tortilla','waffle','flour']): return CATEGORIES[2]
    if any(w in n for w in ['sauce','oil','salt','pepper','garlic','powder','thyme','parsley','oregano','vanilla','cinnamon','nutmeg','sugar','broth','seasoning','smoke','paprika']): return CATEGORIES[6]
    return CATEGORIES[7]

def fmt(q):
    return str(int(q)) if q == int(q) else f'{q:.4f}'.rstrip('0').rstrip('.')

def aggregate(meals, recipes, season='winter'):
    groups = {}
    for meal in meals:
        if not meal.get('recipe_id'): continue
        recipe = recipes.get(meal['recipe_id'], meal.get('snapshot', {}))
        for item in recipe.get('ingredients', []):
            name = canonical(item['name'])
            if name == 'eggs' and season == 'summer': continue
            if item.get('condition') == 'halloween' and meal['date'][5:] != '10-31': continue
            # Flavor descriptors identify a different product, not a preparation note.
            identity = name + ('|' + item['note'].casefold() if item.get('note') and any(w in item['note'].casefold() for w in ['flavored', 'flavoured']) else '')
            group = groups.setdefault(identity, dict(id=identity, name='Corn' if name == 'corn' else item['name'], category=category(name), amounts={}, unknown=False, details=set(), notes=set()))
            q, unit = item.get('quantity'), item.get('unit')
            if q is not None:
                # Exact conversions within volume and weight families only.
                family, factor = {'cups':('volume',48), 'tbsp':('volume',3), 'tsp':('volume',1), 'lbs':('weight',16), 'oz':('weight',1)}.get(unit, (unit,1))
                group['amounts'][family] = group['amounts'].get(family,0) + q * factor
            elif item.get('note'):
                group['details'].add(item['note'])
            else:
                group['unknown'] = True
            if item.get('note') and q is not None: group['notes'].add(item['note'])
    out=[]
    for g in groups.values():
        pieces=[]
        for unit,q in g.pop('amounts').items():
            if unit == 'volume': unit,q = ('cups', q/48) if q>=48 else ('tbsp',q/3) if q>=3 else ('tsp',q)
            if unit == 'weight': unit,q = ('lbs',q/16) if q>=16 else ('oz',q)
            pieces.append(fmt(q) + ('' if unit=='count' else ' '+str(unit)))
        pieces.extend(sorted(g.pop('details')))
        if g.pop('unknown'): pieces.append('additional amount not specified' if pieces else 'amount not specified')
        g['quantity'] = '; '.join(pieces)
        g['note'] = '; '.join(sorted(g.pop('notes')))
        out.append(g)
    return sorted(out,key=lambda g:(CATEGORIES.index(g['category']), g['name'].casefold()))
