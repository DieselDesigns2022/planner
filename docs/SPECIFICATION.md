# PROJECT: Diesel Designs — Dinner & Grocery Planner

## 1. Project Overview

We are rebuilding the dinner-planning functionality on my website:

**Website:** https://dieseldesigns.co/planner/

I want a very simple, reliable, mobile-friendly website that plans 14 days of family dinners and automatically produces one combined grocery shopping list.

The existing page has features I do not want. Do not carry over unnecessary task management, water tracking, daily productivity tools, or unrelated features into the new dinner planner.

**The most important requirement: Build the entire working base in one coordinated development pass, rather than making dozens of tiny edits.**

I am using ChatGPT Work to help code the website.

### Primary Goals

1. Preload all 29 existing family dinner recipes.
2. Allow me to add, edit, and delete recipes.
3. Select any starting date and automatically plan 14 consecutive days of dinners.
4. Follow all permanent meal-planning rules.
5. Automatically build a combined shopping list for those dinners.
6. Combine repeated ingredients and quantities correctly.
7. Keep at least 60 days of dinner-planning history.
8. Make individual dinners easy to change without rebuilding the entire plan.
9. Preserve saved plans and changes when refreshing or reopening the website.
10. Make the entire experience simple, fast, and easy to use.

I do not want a complicated meal-planning platform. I want a personal tool that saves me time every two weeks.

---

## 2. Permanent Coding Rules — Mandatory

These rules apply throughout the project.

1. **ALWAYS back up files before editing them.** No exceptions. Keep backups outside publicly served directories whenever possible.

2. **NEVER guess.** Inspect the actual files, database structure, server environment, and existing code before making changes.

3. **Use as FEW terminal commands as safely possible.** Each command should accomplish as much work as safely possible. Prefer one complete, fail-safe script over repetitive one-line commands.

4. **Never assume code works because it was saved.** Test every major feature, and verify changes before declaring them complete.

5. **Keep responses SHORT, simple, and direct.** Avoid long explanations during actual coding. The project specification can be detailed; daily coding responses should not be.

6. **Always tell me what to do NEXT.** Never leave me wondering what command to run, what result to check, or what should happen next.

7. **Follow the established phase plan and checklist.** Track what has actually been completed, not what was merely attempted. Keep me updated whenever we begin or finish a step or phase.

8. Do not modify unrelated websites, databases, financial systems, or applications.

9. Do not make destructive changes without taking and verifying backups.

10. Do not commit, push, or deploy broken or untested code.

11. Do not repeat inspection steps unnecessarily. Remember what we have already verified during this session.

12. Make sensible implementation decisions without stopping for approval on every small detail. Ask questions only when a decision could risk data loss, security, or important existing functionality.

### Mandatory Coding Response Format

Every coding response must use this format:

**Project:** Diesel Designs — Dinner & Grocery Planner

**Task:** What we are currently building or fixing

**Step:** Short explanation of what the command accomplishes

**Command:** Exact copy-and-paste terminal command

**Next:** What I need to test or what output I should send back

If ChatGPT Work can perform the work directly, perform it rather than making me manually enter commands. Still give me a short summary of what was done and what needs to happen next.

---

# 3. Website Design and User Experience

## Main Design Goal

**Simple, clean, and functional.**

Do not turn this into a large dashboard or complicated recipe manager.

I should be able to open the website, generate a meal plan, view the grocery list, and leave.

### Main Page Layout

**Header**

- Title: Dinner Planner
- Starting date selector
- Main button: Generate 2 Weeks
- Small link: Manage Recipes
- Small link: History

Below the header, show the generated meal plan.

### Meal Plan Display

Display 14 consecutive calendar dates, beginning with whichever date I select.

Every day should show:

- Day of the week
- Full date
- Dinner name
- Small option to change that day's dinner

Example:

**Saturday, November 14**
Fend for Yourself

**Sunday, November 15**
Lasagna & Garlic Bread

**Monday, November 16**
Chicken & Dumplings

**Tuesday, November 17**
Enchiladas & Rice

Each day must be easy to read.

Use a clean vertical list or simple cards.

Do not create a complex calendar grid requiring horizontal scrolling.

### Grocery List Display

Below the dinner schedule, display:

**Shopping List — November 14–27**

Organize groceries into simple groups:

- Meat & Poultry
- Dairy & Eggs
- Bread, Pasta & Grains
- Canned & Packaged Foods
- Produce & Fresh Herbs
- Frozen Foods
- Sauces, Oils & Seasonings
- Other

Show the total quantity needed for each ingredient.

Provide one simple way to copy the entire grocery list, including its quantities and categories.

The grocery list should remain easy to read and print.

Optional shopping checkboxes are acceptable, but should not make the interface cluttered.

### Design Preferences

- Mobile-friendly and desktop-friendly.
- Simple text and readable font sizes.
- Comfortable spacing.
- Clean background and subtle accents.
- Minimal buttons.
- Avoid pop-ups except when necessary.
- Avoid animations, charts, dashboards, and unnecessary visual features.
- Do not require multiple screens to generate a meal plan.

**The planner must prioritize usefulness over decoration.**

---

# 4. Generating the 14-Day Dinner Plan

## Starting Date

I select any starting date.

Example: November 14, 2026.

The system generates dinner suggestions for November 14 through November 27, inclusive.

It must always create exactly 14 consecutive calendar entries.

Do not assume the plan always starts on a Sunday, Monday, or Saturday.

The day-of-week rules must follow actual calendar dates.

Use the website's configured local timezone, preferably America/Detroit, and handle daylight saving time correctly.

## Generate Button

Clicking **Generate 2 Weeks** should:

1. Read my recipes.
2. Read the permanent planning rules.
3. Check recent dinner history.
4. Check the selected date range.
5. Determine required Taco Tuesdays.
6. Determine required crockpot Thursdays.
7. Determine whether each Friday is an eat-out Friday.
8. Set Saturdays to Fend for Yourself unless manually changed.
9. Fill remaining dates with varied dinners.
10. Save the completed plan.
11. Automatically build the grocery list.
12. Display both the meal plan and grocery list.

Generation should happen without requiring any other choices.

## Regeneration

If I dislike the generated menu, I should have one small **Regenerate** option.

Regeneration must follow the same rules.

It should try to provide different dinners rather than reproducing the same list.

Do not silently overwrite a previously saved menu. If a menu already exists for those dates, show the saved plan first and require an intentional replace or regenerate action.

## Manual Dinner Changes

Each date should have an easy option to select another dinner from my recipe collection.

Changing a dinner should:

- Save the new selection.
- Preserve all other dates.
- Recalculate the grocery list immediately.
- Update the current saved plan.
- Preserve the previous selection in an edit history if practical.

If a manually selected dinner violates a hard scheduling rule, prevent the change or explain why it is not allowed.

Allow approved special cases such as replacing Fend for Yourself on Saturday with an ordinary meal.

---

# 5. Permanent Meal-Planning Rules

All rules below are mandatory and must be enforced by the application logic, not merely displayed as reminders.

## Rule 1: Taco Tuesday

Every Tuesday must contain a Taco Tuesday dinner.

Qualifying recipes currently include:

- Enchiladas & Rice
- Quesadillas & Rice
- Taco Salad

Additional taco-themed recipes may be added later.

Every recipe needs a simple internal Taco Tuesday eligibility field.

The system must recognize qualifying recipes when scheduling Tuesdays.

Do not schedule ordinary non-taco dinners on Tuesdays.

## Rule 2: Crockpot Thursday

Every Thursday must contain a crockpot dinner.

Use recipes marked as crockpot eligible.

Existing crockpot recipes are numbers 23 through 29.

Crockpot meals are allowed on other days too.

Do not restrict them to Thursdays.

## Rule 3: Alternating Friday Eat-Out Schedule

The every-other-Friday eat-out rotation began:

**Friday, October 16, 2026.**

This date is the permanent anchor.

Every 14 days after October 16 is an eat-out Friday.

Calculate this based on the actual calendar, not whether the previous menu happened to include an eat-out day.

Examples:

- October 16 — Eat Out
- October 23 — Normal Dinner
- October 30 — Eat Out
- November 6 — Normal Dinner
- November 13 — Eat Out
- November 20 — Normal Dinner
- November 27 — Eat Out
- December 4 — Normal Dinner

On eat-out Fridays:

- Display "Eat Out."
- Do not assign a recipe.
- Do not add dinner groceries for that day.

On the other Fridays, schedule a regular eligible dinner.

## Rule 4: Saturday

Saturday defaults to:

**Fend for Yourself**

Do not automatically assign a full family dinner on Saturdays.

However, allow me to manually change a Saturday to a dinner if desired.

When a Saturday is assigned a dinner, its grocery ingredients must be included.

## Rule 5: Weekend-Only Recipes

The following recipes can only be scheduled on Saturdays or Sundays:

- Sloppy Joes & French Fries
- Sloppy Joes, Macaroni & Cheese & Corn
- Peanut Butter Chicken & Rice

Never automatically assign these meals Monday through Friday.

Because Saturdays are Fend for Yourself by default, these recipes will normally be assigned on Sundays unless I manually choose them for a Saturday.

Do not bypass this restriction during regeneration.

## Rule 6: Eggs and Seasonal Shopping

I have chickens that provide eggs during the warmer months.

Summer:

- Do not add eggs to my grocery list.
- Still retain eggs in recipe ingredient data.

Winter:

- Add eggs to the grocery list for meals requiring eggs.

Because exact summer and winter dates have not been defined, create one simple season setting:

- Summer — Use home eggs
- Winter — Buy eggs

It must be easy to change, and the choice should be saved.

For the initial November setup, use Winter.

Do not permanently assume that summer and winter follow an arbitrary date range.

This setting affects grocery shopping, not whether meals requiring eggs can be planned.

## Rule 7: Grocery Budget

My target grocery budget is:

**$300 per 14-day shopping period.**

The generator should favor a reasonable mix of less expensive and more expensive meals.

Do not place multiple expensive meals together unnecessarily.

Do not pretend that a grocery list costs less than $300 without real pricing information.

For the first version, use simple recipe cost categories:

- Budget
- Moderate
- Higher Cost

Allow these to be adjusted in recipe management.

Use them to balance meals.

A later version may add actual grocery pricing, but do not build a complicated price-tracking system now.

If real ingredient prices are not stored, show the $300 target without inventing an estimated cost.

## Rule 8: Dinner Repeats

The system should:

- Avoid serving the same dinner on consecutive days.
- Spread repeat dinners as far apart as reasonably possible.
- Check prior saved dinner history.
- Favor dinners that have not been served recently.
- Avoid repeating the same dinner within one 14-day plan when enough eligible alternatives exist.
- Rotate Taco Tuesday meals.
- Rotate crockpot meals.
- Avoid repeatedly selecting the same cheap or easy meals.

Use at least the prior 60 days of history to guide selection.

This is a preference-based rule rather than an absolute ban on repeats. Tuesdays have only three currently qualifying options, so repeats will eventually be necessary.

The generator must always follow hard rules first, then optimize variety.

## Rule 9: Beef Stew

Beef Stew always uses:

**2.5 lbs beef stew meat.**

Never substitute ground beef.

## Rule 10: Ingredient Accuracy

Never silently replace ingredients.

Examples:

- Beef stew meat is not ground beef.
- Maple sausage is not regular ground beef.
- Boxed Hamburger Helper is required for Hamburger Helper.
- Boxed Velveeta Skillet Dinner is required for that recipe.
- Alfredo uses the pasta and sauce ingredients listed, not chicken or rice.
- Do not add ingredients not present in the recipe data without asking.

---

# 6. Recipe Management

All 29 recipes listed below must be installed during the initial build.

They must be stored as editable recipe records, not hardcoded into a static page that requires source code changes whenever I edit a recipe.

## Add Recipe

I want a very simple form.

**Recipe Title**

One text box.

**Ingredients**

One large multiline text box.

Each ingredient should go on its own line.

Example:

Ground beef — 2 lbs
Cheddar cheese
Tortillas
Taco seasoning

**Instructions**

One optional multiline text box.

Instructions may be left blank.

### Additional Recipe Details

Provide compact optional controls for:

- Taco Tuesday eligible
- Crockpot eligible
- Weekend only
- Cost category

These options can be placed under a small "Meal Rules" area so the basic recipe form remains simple.

Do not require me to provide cooking instructions.

## Editing Recipes

Selecting an existing recipe opens the same simple form with its stored information already filled in.

Allow me to update:

- Title
- Ingredients
- Quantities
- Instructions
- Meal eligibility
- Cost category

Saving should take one click.

Changes must persist.

## Deleting Recipes

Allow deletion with confirmation.

Prefer archiving or soft deletion so recipes used in old meal plans remain visible in history.

Deleting a recipe should not destroy historical menus.

## Ingredient Storage

Although I should edit ingredients using a simple multiline text box, the backend should store ingredients in a structured format.

Each ingredient should support:

- Name
- Quantity, if known
- Unit, if known
- Preparation note, if provided
- Optional or alternative status

For example:

"Ground beef — 2 lbs" must be understood as:

Ingredient: Ground beef
Quantity: 2
Unit: lbs

"Cheddar cheese" must remain a valid ingredient even though no specific quantity is given.

Do not force me to enter measurements for every ingredient.

An ingredient can have a blank quantity.

---

# 7. Complete Recipe Collection — Import All 29

The following is the authoritative initial recipe list.

**Import every recipe with the exact ingredient information provided.**

Do not silently change ingredient quantities, remove ingredients, or invent cooking instructions.

Instructions should be blank unless explicitly provided.

## Regular Dinners (1–22)

### 1. Enchiladas & Rice

- Tortillas
- Ground beef — 1 lb
- Cheddar cheese
- Enchilada sauce
- Roast beef — 1 can

Taco Tuesday: Yes

### 2. Breakfast Burritos

- Tortillas
- Ground sausage — maple flavored
- Cheddar cheese

### 3. French Toast Casserole

- Bread — 1 full loaf
- Milk
- Eggs
- Vanilla
- Cinnamon
- Nutmeg
- Bacon or sausage links

### 4. Quesadillas & Rice

- Tortillas
- Cheese
- Minute Rice
- Taco seasoning

Taco Tuesday: Yes

### 5. Shepherd's Pie

- Ground beef — 2 lbs
- Instant mashed potatoes
- Beef broth
- Worcestershire sauce
- Green beans — 1 can
- Corn — 1 can
- Cheddar cheese

### 6. Taco Salad

- Doritos — 1 family-size bag
- Cheddar cheese
- Ground beef — 2.5 lbs
- Taco seasoning

Taco Tuesday: Yes

### 7. Hamburger Helper

- Ground beef — 1 lb
- Hamburger Helper — 1 value-size box

### 8. Lasagna & Garlic Bread

- Lasagna noodles
- Cottage cheese
- Ricotta cheese
- Mozzarella cheese
- Parmesan cheese
- Ground beef — 4 lbs
- Spaghetti sauce — 2 cans
- Frozen garlic bread

### 9. Alfredo & Garlic Bread

- Salted butter
- Minced garlic
- All-purpose flour
- Heavy cream
- Whole milk
- Grated Parmesan & Romano cheese mix
- Salt
- Black pepper
- Penne noodles
- Frozen garlic bread

### 10. Goulash & Garlic Bread

- Ground beef — 2 lbs
- Spaghetti sauce — 1 can
- Spaghetti noodles or elbow noodles
- Frozen garlic bread

### 11. Pork Chops, Macaroni & Cheese & Corn

- Pork chops — family-size package
- Macaroni & cheese — 2 boxes
- Corn — 2 cans

### 12. Hibachi Chicken & Rice

- Minute Rice
- Chicken breasts — 2
- Garlic butter
- Sesame seed oil
- Soy sauce

### 13. Steak & Cheese Sandwiches & Soup

- Steak-ums — frozen steak
- Hawaiian rolls — 24 ct
- Garlic butter
- Chicken noodle soup — 1 family-size can
- Tomato soup — 1 can
- Milk — for soup

### 14. Chicken Breasts, Mashed Potatoes, Corn & Peas

- Chicken breasts — 6
- Instant mashed potatoes
- Corn — 2 cans
- Peas — 1 can

### 15. Sloppy Joes & French Fries

- Ground beef — 4 lbs
- Hamburger buns — 1 pack
- Brown sugar
- BBQ sauce
- Ketchup
- Worcestershire sauce
- Frozen French fries — 1 bag

Weekend Only: Yes

### 16. Peanut Butter Chicken & Rice

- Minute Rice
- Chicken breasts
- Peanut butter
- Brown sugar
- Soy sauce
- Sesame seed oil

Weekend Only: Yes

### 17. Waffles, Eggs & Bacon or Sausage Links

- Waffle mix
- Oil
- Butter
- Milk
- Eggs
- Bacon or sausage links

### 18. French Toast, Eggs & Bacon or Sausage Links

- Texas toast bread — 1 loaf
- Milk
- Cinnamon
- Nutmeg
- Vanilla
- Eggs
- Bacon or sausage links

### 19. Sloppy Joes, Macaroni & Cheese & Corn

- Ground beef — 4 lbs
- Ketchup
- BBQ sauce
- Brown sugar
- Worcestershire sauce
- Garlic powder
- Onion powder
- Hamburger buns
- Boxed macaroni & cheese
- Milk — for macaroni & cheese
- Butter — for macaroni & cheese
- Canned corn

Weekend Only: Yes

### 20. Velveeta Skillet Dinner

- Velveeta Skillet Dinner — boxed
- Chicken breasts — 2

### 21. Chili

- Ground beef — 5 lbs
- Dark red kidney beans — 4 cans
- Light red kidney beans — 4 cans
- Tomato sauce — 2 large cans
- Chili powder
- Onion powder
- Garlic powder
- Minced garlic
- Ritz crackers
- Cheddar cheese
- Refrigerated cinnamon rolls — 1 can
- Sour cream — Halloween only

Important: Sour cream must only be included when Chili is scheduled for Halloween, October 31. It must not appear on ordinary chili shopping lists.

### 22. Meatloaf, Mashed Potatoes & Corn

- Ground beef — 2 lbs
- Italian bread crumbs
- French onion dip mix
- BBQ sauce
- Eggs
- Instant mashed potatoes
- Corn — 1 can

## Crockpot Dinners (23–29)

All seven recipes in this section must be marked as crockpot eligible.

They are available for Thursday scheduling and may also be used on other days.

### 23. Beef Stew

- Beef stew meat — 2.5 lbs
- Potatoes — 4 cups, cubed
- Green beans — 2 cans, drained
- Beef broth — 2 cups
- Minced garlic — 2 tbsp
- Onion powder — 1 tbsp
- Fresh thyme — 4 tbsp
- Fresh oregano — 2 tbsp

### 24. Pot Roast

- Chuck roast — 3–4 lbs
- Oil — for searing
- Salt
- Black pepper
- Garlic powder
- Onion powder
- Paprika
- Dried thyme
- Dried parsley
- Baby carrots
- Jumbo baking potatoes
- Minced garlic
- Beef broth
- Worcestershire sauce

### 25. Kalua Pork & Baked Potatoes

- Pork butt
- Liquid smoke
- Hawaiian sea salt
- Jumbo baking potatoes
- Hawaiian rolls

### 26. Chicken & Noodles Over Mashed Potatoes

- Chicken breasts — 2.5 lbs
- Cream of chicken soup — 2 cans
- Chicken broth — 4 cups
- Minced garlic — 2 tbsp
- Onion powder — 1 tbsp
- Black pepper — ½ tsp
- Fresh parsley — ½ cup
- Fresh thyme — 3 tbsp
- Frozen egg noodles — 1 bag
- Instant mashed potatoes

### 27. Shredded BBQ Chicken Sandwiches & Fries or Tater Tots

- Chicken breasts — 2.5 lbs
- Smooth BBQ sauce — 2 cups
- Chicken broth — ½ cup
- Minced garlic — 2 tbsp
- Onion powder — 1 tbsp
- Liquid smoke — 1 tbsp
- Fresh chives — ½ cup
- Fresh oregano — 2 tbsp
- Hawaiian rolls — 24 ct
- Frozen French fries or tater tots — 1 bag

### 28. Garlic Chicken & Chive Biscuit Base

- Chicken breasts — 2.5 lbs
- Cream of chicken soup — 2 cans
- Corn — 1 can, drained
- Chicken broth — ½ cup
- Minced garlic — 2 tbsp
- Fresh chives — ½ cup
- Fresh thyme — 2 tbsp
- Refrigerated biscuits — 2 cans

### 29. Chicken & Dumplings

- Chicken breasts — 2.5 lbs
- Cream of chicken soup — 2 cans
- Chicken broth — 2 cups
- Minced garlic — 2 tbsp
- Onion powder — 1 tbsp
- Fresh rosemary — 4 tbsp
- Fresh thyme — 2 tbsp
- Refrigerated biscuits — 2 cans

---

# 8. Shopping List Generator

The shopping list must be automatically calculated from the 14 selected dinners.

Do not maintain a second, manually entered shopping list for each recipe.

The recipe ingredients are the source of truth.

## Automatic Grocery Calculation

Example:

Dinner A:
Ground beef — 2 lbs

Dinner B:
Ground beef — 4 lbs

Dinner C:
Ground beef — 1 lb

Shopping list:

**Ground beef — 7 lbs**

Do not show ground beef as three separate grocery entries.

## Quantity Rules

Combine equivalent ingredients when their units are compatible.

Examples:

- 2 lbs + 4 lbs = 6 lbs
- 2 cans + 1 can = 3 cans
- 1 cup + ½ cup = 1½ cups
- 2 tbsp + 1 tbsp = 3 tbsp

Support common fractions and measurement conversions where reliable.

Do not combine incompatible measurements without accurate conversion information.

Examples:

- A family-size package is not automatically equivalent to a measured number of pounds.
- A large can is not automatically equivalent to a regular can.
- An ingredient with no quantity should not be assigned an invented amount.

For ingredients without quantities, list them once and indicate that the amount is not specified.

For incompatible or unclear quantities, preserve enough detail for me to shop correctly rather than producing a misleading total.

## Ingredient Name Matching

Normalize common equivalent descriptions.

Examples:

- Corn — 1 can
- Canned corn — 2 cans

These can become:

Corn — 3 cans

Likewise:

- Chicken breasts — 2
- Chicken breasts — 6

These can become:

Chicken breasts — 8

However, weight-based chicken quantities must not be converted into breast counts without a defined conversion.

Do not combine unlike products.

For example, different types of cheese, different types of beans, and different meat cuts must remain distinguishable.

## Alternatives

Some recipes have ingredients such as:

- Bacon or sausage links
- Fries or tater tots
- Spaghetti noodles or elbow noodles

Do not add both alternatives to the grocery list.

Preserve the choice as a single item until a selection is made.

A simple default or one-click selection is acceptable.

If no alternative is selected, display it as "Bacon OR sausage links" rather than treating both as required.

## Grocery List Updates

If a meal changes, the shopping list must update automatically.

If I change a recipe ingredient, the system should update the current grocery list using the latest recipe data, while preserving historical records appropriately.

If I regenerate a menu, create a fresh shopping list for that menu.

## Manual Shopping List Adjustments

I should be able to:

- Add an extra item.
- Remove an item I already have at home.
- Edit a quantity if needed.

Keep these options simple.

Manual changes must persist when the page refreshes.

When a dinner changes, recalculate recipe-based groceries while preserving unrelated manual additions and stored exclusions.

Use stable identifiers rather than relying only on visible ingredient names.

## Shopping List Output

Include a **Copy Shopping List** button.

Copied output should be plain text that I can paste into Notes, Messages, or another app.

Make the page print-friendly using the browser's normal print feature.

A PDF generator, grocery retailer integration, barcode scanner, inventory system, or price comparison system is not needed.

---

# 9. Dinner History — Minimum 60 Days

The planner must remember previous dinners.

At minimum, retain the most recent 60 days of scheduled meals.

Prefer keeping history indefinitely because meal schedules take little storage.

## History View

Provide one small History option.

It should let me:

- See previous dates and dinners.
- Look back at least 60 days.
- Find which dinner was planned on a specific date.
- View previous saved two-week menus.
- Reopen old menus without changing them.

A simple date-based list is enough.

Do not build complicated reports, charts, or analytics dashboards.

## History and Generation

When generating a new plan:

- Check dinners already scheduled within the previous 60 days.
- Avoid recently used dinners where possible.
- Favor less recently used recipes.
- Respect already saved future schedules.
- Do not create conflicting dinner assignments for overlapping date ranges.

The same date should have one current dinner assignment, not several conflicting active plans.

Keep historical changes or previous versions separately if needed.

## Historical Recipe Accuracy

If a recipe is edited today, an old saved meal should still be understandable.

Store sufficient recipe information or a recipe snapshot to preserve historical meaning.

Do not delete history when recipes are archived or removed.

---

# 10. Database and Persistence

Inspect the existing technology before deciding how to implement storage.

Do not assume the site uses PHP, MySQL, SQLite, WordPress, or any other specific system.

Use the current website environment where practical.

Do not introduce an unnecessary framework or extra service.

## Required Data

The application needs persistent storage for:

**Recipes**
- Stable recipe ID
- Title
- Ingredient data
- Optional instructions
- Taco Tuesday eligibility
- Crockpot eligibility
- Weekend-only restriction
- Cost category
- Active/archived status
- Created and updated timestamps

**Ingredients**
- Structured ingredient information
- Quantity and unit when provided
- Display text
- Optional ingredient notes
- Alternative choices
- Conditional ingredients where needed

**Dinner Plans**
- Dates
- Selected dinner
- Manual changes
- Generated versus manually assigned status
- Saved meal versions or snapshots
- Created and updated timestamps

**Shopping Lists**
- Associated date range
- Generated grocery items
- Manual additions
- Manual exclusions
- Quantity adjustments
- Shopping checkbox state, if provided

**Settings**
- Current egg-shopping season
- Grocery budget target of $300
- Eat-out Friday anchor date
- Other permanent configuration values

## Storage Requirements

- All data must survive refreshes, restarts, and new browser sessions.
- Do not rely solely on browser localStorage for critical records.
- Use server-side persistent storage unless inspection shows a better existing solution.
- Use database transactions where appropriate.
- Prevent duplicate recipe imports.
- Ensure schema migrations are repeatable and safe.
- Preserve historical data.
- Protect write operations.
- Reuse existing authentication where appropriate.

If there is no authentication, implement the smallest appropriate protection for a private personal planner. Do not create a public, unauthenticated recipe-editing API.

Avoid unnecessary account creation or a complex user-management system.

---

# 11. Automatic Meal Selection Logic

Use a clear and testable meal-selection engine.

The generator should operate in the following order.

### Step 1: Build Calendar Dates

Generate all 14 dates based on the selected starting date.

### Step 2: Apply Fixed Calendar Rules

Determine:

- Taco Tuesdays
- Crockpot Thursdays
- Eat-out Fridays
- Fend for Yourself Saturdays

### Step 3: Retrieve Recipes

Load eligible active recipes and their rule flags.

### Step 4: Read Meal History

Retrieve relevant previous and already scheduled future dinners.

### Step 5: Assign Required Dinners

Choose suitable recipes for Tuesday and Thursday.

Mark fixed eat-out and Saturday entries.

### Step 6: Fill Remaining Dates

Select dinners that balance:

- Variety
- How recently they were served
- Approximate cost categories
- Recipe eligibility
- Avoidance of consecutive repeats
- Available weekend-only recipes

### Step 7: Validate the Schedule

Check every date against all permanent rules.

Do not save an invalid generated schedule.

### Step 8: Save the Menu

Store all 14 dinner assignments reliably.

### Step 9: Generate Groceries

Calculate the shopping list from the selected dinners.

### Step 10: Display Results

Show the completed dated menu and shopping list.

## Handling Conflicts

Hard calendar restrictions take priority over variety and cost preferences.

If the recipe collection becomes too limited, do not bypass a permanent restriction to produce a menu.

Instead, show a clear explanation of why the planner cannot fill a particular date.

Use a repeatable, testable selection strategy with controlled randomness for regeneration.

Avoid endless retries or selection loops.

---

# 12. Initial Data Handling and Edge Cases

Before seeding recipes, account for these details.

### Unspecified Quantities

Some ingredients have no measurement.

Keep them exactly as entered.

Do not invent measurements.

### Enchiladas & Rice

The title contains Rice, but no rice ingredient was included in the supplied ingredient list.

Preserve the supplied ingredients during import. Flag this specific recipe for later review instead of silently adding rice.

### Halloween Chili

Sour cream applies only to Chili scheduled for October 31.

Store it as a conditional ingredient, not a normal chili ingredient.

### Seasonal Eggs

Eggs remain present in recipes year-round.

Only the shopping-list inclusion changes based on the season setting.

### Alternative Ingredients

Preserve "or" ingredient options rather than purchasing both choices.

### Recipe Cost Categories

Initial categories can use clearly marked editable defaults.

Do not present these as verified grocery prices.

### Existing Website Data

Inspect current files and data before making changes.

Do not assume existing records can safely be deleted.

If the existing planner contains information unrelated to the dinner planner, preserve it in a backup and leave unrelated live systems untouched.

### One-Day Manual Overrides

Saturday manual dinner overrides should be supported without changing the permanent Saturday default.

Fixed eat-out Fridays should remain fixed unless the meal-planning rules themselves are deliberately changed.

---

# 13. Security and Reliability

The website should be simple without sacrificing safety.

Requirements:

- Protect recipe and planning changes from unauthorized access.
- Use secure database access and parameterized queries where applicable.
- Validate user input.
- Escape displayed content.
- Protect state-changing requests against CSRF when cookie-based authentication is used.
- Restrict access to backup files.
- Do not expose credentials or database settings publicly.
- Use existing HTTPS configuration.
- Handle server errors without destroying saved data.
- Avoid silent data loss.
- Ensure the interface works after refresh.

Do not add unnecessary third-party services.

---

# 14. Required Development Phases

This phase plan is mandatory.

The goal is to complete Phases 1–5 in one coordinated implementation pass wherever the actual environment safely permits.

The phases are checkpoints, not permission to turn the project into dozens of separate coding sessions.

## Phase 1 — Inspection and Backup

Checklist:

- [ ] Inspect the existing website structure.
- [ ] Identify the current language and framework.
- [ ] Identify the database and existing tables, if any.
- [ ] Inspect existing planner behavior and dependencies.
- [ ] Identify site authentication and access control.
- [ ] Determine how the current page is deployed.
- [ ] Identify any unrelated features that must remain untouched.
- [ ] Back up all files that may be modified.
- [ ] Back up the database before schema or data changes.
- [ ] Verify backups exist and are usable.
- [ ] Choose the simplest compatible implementation.

**Completion condition:** The environment is understood and backups are verified.

## Phase 2 — Data and Recipe System

Checklist:

- [ ] Create or update persistent database storage.
- [ ] Implement safe, repeatable migrations.
- [ ] Create structured ingredient support.
- [ ] Build recipe creation.
- [ ] Build recipe editing.
- [ ] Build recipe archiving/deletion.
- [ ] Support blank recipe instructions.
- [ ] Support Taco Tuesday eligibility.
- [ ] Support crockpot eligibility.
- [ ] Support weekend-only eligibility.
- [ ] Support cost categories.
- [ ] Import all 29 recipes.
- [ ] Verify all 29 recipe titles and ingredient lists.
- [ ] Prevent duplicate imports.
- [ ] Verify saved edits persist.

**Completion condition:** All 29 recipes are stored and can be managed.

## Phase 3 — Meal Generator and History

Checklist:

- [ ] Implement 14-day calendar generation.
- [ ] Support any selected starting date.
- [ ] Apply Taco Tuesday.
- [ ] Apply Crockpot Thursday.
- [ ] Apply alternating Friday eat-out rotation.
- [ ] Apply Saturday default.
- [ ] Enforce weekend-only recipes.
- [ ] Support crockpot meals on other days.
- [ ] Avoid consecutive repeats.
- [ ] Check previous 60-day dinner history.
- [ ] Balance recipe variety.
- [ ] Balance cost categories.
- [ ] Save generated plans.
- [ ] Support changing individual dinners.
- [ ] Support regenerating menus safely.
- [ ] Handle overlapping saved date ranges.
- [ ] Preserve history.
- [ ] Validate every generated menu.

**Completion condition:** Meal schedules generate, follow all hard rules, and persist.

## Phase 4 — Shopping List Generator

Checklist:

- [ ] Calculate ingredients from selected dinners.
- [ ] Combine duplicate ingredients.
- [ ] Add compatible quantities correctly.
- [ ] Preserve unknown quantities.
- [ ] Support alternatives.
- [ ] Support Halloween-only sour cream.
- [ ] Support summer and winter egg rules.
- [ ] Organize grocery categories.
- [ ] Support manual grocery additions.
- [ ] Support removing already-owned ingredients.
- [ ] Support manual quantity adjustments.
- [ ] Preserve grocery edits.
- [ ] Recalculate after changing a dinner.
- [ ] Provide one-click grocery list copying.
- [ ] Provide a print-friendly layout.
- [ ] Display the $300 budget target without invented prices.

**Completion condition:** Grocery lists are accurate, easy to use, and update correctly.

## Phase 5 — Main Website Interface

Checklist:

- [ ] Build clean responsive layout.
- [ ] Add starting date selector.
- [ ] Add Generate 2 Weeks button.
- [ ] Display 14 dated dinners.
- [ ] Display the shopping list below dinners.
- [ ] Add simple individual dinner editing.
- [ ] Add one small recipe management area.
- [ ] Add one small history area.
- [ ] Add a simple egg-season setting.
- [ ] Minimize unnecessary buttons.
- [ ] Verify mobile layout.
- [ ] Verify desktop layout.
- [ ] Verify keyboard accessibility.
- [ ] Verify loading and error messages.
- [ ] Ensure all data survives refresh.

**Completion condition:** The entire website can be used through a simple, reliable interface.

## Phase 6 — Automated Testing and Final Review

Checklist:

- [ ] Run syntax and build checks.
- [ ] Test database migrations.
- [ ] Test recipe importing.
- [ ] Test recipe editing and saving.
- [ ] Test every calendar restriction.
- [ ] Test grocery quantity aggregation.
- [ ] Test seasonal eggs.
- [ ] Test conditional Halloween ingredients.
- [ ] Test alternative groceries.
- [ ] Test manual dinner replacement.
- [ ] Test regeneration.
- [ ] Test overlapping date ranges.
- [ ] Test 60-day history.
- [ ] Test persistence after refresh.
- [ ] Test access controls.
- [ ] Test desktop presentation.
- [ ] Test mobile presentation.
- [ ] Confirm unrelated website functionality is preserved.
- [ ] Resolve errors before deployment.

**Completion condition:** All required tests pass.

## Phase 7 — Deployment and Handoff

Checklist:

- [ ] Verify pre-deployment backups.
- [ ] Deploy through the existing appropriate workflow.
- [ ] Run any required database migrations safely.
- [ ] Verify deployed files and assets.
- [ ] Perform live smoke tests without destroying real data.
- [ ] Verify saved recipes and plans.
- [ ] Confirm no unrelated pages were damaged.
- [ ] Confirm the planner is ready for personal use.
- [ ] Report all actual completed checklist items.
- [ ] Report anything outstanding.
- [ ] Provide short usage instructions.
- [ ] Identify the location of backups and the rollback approach.

**Completion condition:** The website is deployed, tested, and usable.

---

# 15. Mandatory Test Cases

These tests must be implemented and run, not merely described.

## Test A — November 14, 2026

Generate November 14–27, 2026.

Expected:

- Exactly 14 consecutive days
- November 14: Fend for Yourself
- November 17: Taco Tuesday dinner
- November 19: Crockpot dinner
- November 20: Normal dinner
- November 21: Fend for Yourself
- November 24: Taco Tuesday dinner
- November 26: Crockpot dinner
- November 27: Eat Out

All other dates must receive eligible dinners.

## Test B — October 16, 2026

Verify October 16 is Eat Out.

October 23 is not.

October 30 is Eat Out.

November 13 is Eat Out.

## Test C — Weekend Only

Generate multiple schedules.

Verify no Sloppy Joes variation or Peanut Butter Chicken is scheduled Monday through Friday.

## Test D — Crockpot Eligibility

Verify every Thursday receives a crockpot recipe.

Verify crockpot meals can appear on other days.

## Test E — Quantities

Test combining:

- 2 lbs + 4 lbs ground beef = 6 lbs
- 2 cans + 1 can corn = 3 cans
- 2 cups + ½ cup broth = 2½ cups

Do not combine incompatible units.

## Test F — Eggs

When Summer is selected, eggs should be excluded from groceries.

When Winter is selected, the same egg-containing recipes should add eggs.

## Test G — Halloween Chili

When Chili is assigned to October 31, add sour cream.

When Chili is assigned to any other date, do not add sour cream.

## Test H — Recipe Changes

Edit one recipe.

Verify the changes save correctly.

Verify new shopping-list calculations use the edited ingredients.

Verify historical meal records remain understandable.

## Test I — Manual Dinner Changes

Replace one planned dinner.

Verify:

- Other dinners remain unchanged.
- The new dinner is saved.
- Groceries recalculate correctly.
- Manual grocery additions remain saved.
- Refreshing does not lose changes.

## Test J — Recipe Archive

Archive a recipe that appears in history.

Verify its past meal records still display correctly.

## Test K — Repeat Avoidance

Generate multiple consecutive planning periods.

Verify recently served recipes are less likely to repeat when alternatives exist.

Never sacrifice a hard scheduling rule for variety.

## Test L — Safe Regeneration

Regenerate a previously saved date range.

Verify replacement is intentional, data is preserved appropriately, and grocery items are not duplicated.

## Test M — Mobile

Test a narrow screen.

Verify dates, recipe names, grocery quantities, and essential controls remain readable and usable.

---

# 16. What NOT to Build

Do not add:

- Breakfast scheduling
- Lunch scheduling
- Water tracking
- Household task lists
- Daily productivity dashboards
- Shopping retailer integrations
- Grocery store price scraping
- Barcode scanners
- Recipe photo galleries
- Social sharing
- Nutrition tracking
- Calorie counting
- AI-generated recipes
- Complicated meal-prep workflows
- Multiple user accounts unless required by existing authentication
- Large settings dashboards
- Subscription systems
- Third-party recipe APIs
- Unnecessary notifications

The existing breakfast-themed recipes are dinners in our household. They belong in the dinner rotation.

Do not schedule breakfasts or lunches.

---

# 17. How to Execute This Build Efficiently

This is extremely important.

I want the complete foundation built together.

Avoid this workflow:

- Inspect one file.
- Stop.
- Edit one line.
- Stop.
- Add one button.
- Stop.
- Fix another button.
- Stop.
- Create a database table.
- Stop.

Instead, follow this workflow:

### Development Pass 1: Inspect, Plan, and Protect

Inspect the environment comprehensively.

Gather the necessary existing code, database structure, and deployment details.

Back up files and database.

Choose the minimal architecture.

Do not begin replacing the application before understanding the current system.

### Development Pass 2: Build the Complete Base

Implement in a coordinated change set:

- Database and migrations
- Recipe storage
- All 29 recipes
- Recipe management
- Permanent planning rules
- 14-day generation
- History
- Grocery aggregation
- Manual meal changes
- Grocery editing
- Main interface
- Security
- Automated tests

Use as few terminal commands as safely possible.

A single well-structured script or coordinated batch of changes is preferred when appropriate.

Use small, logical code files internally, even when applying them in one development pass. Do not put the entire application into one enormous unmaintainable file.

### Development Pass 3: Test and Deploy

Run all relevant automated tests.

Fix any identified problems as part of the same development session.

Verify safe database migration behavior.

Deploy only after validation.

Perform live smoke tests.

### Development Pass 4: Minor Adjustments

After the base is fully functional, we can make small changes based on real use.

Do not intentionally leave basic features unfinished for later rounds.

---

# 18. Final Acceptance Requirements

The project is not considered complete unless all of the following are true:

- All 29 recipes are present.
- Recipes can be added and edited easily.
- Recipe instructions are optional.
- Any starting date can be selected.
- The planner produces 14 dated dinner entries.
- Every hard meal rule is respected.
- Friday eat-out dates match the October 16, 2026 anchor.
- Saturdays default to Fend for Yourself.
- No weekend-only recipe is assigned on a weekday.
- Recent repeats are minimized.
- The grocery list combines duplicate items correctly.
- Grocery amounts are not invented.
- Seasonal egg shopping works.
- Halloween-only sour cream works.
- Changing a dinner updates the grocery list.
- Manual grocery adjustments persist.
- At least 60 days of meal history are available.
- Saved data survives refresh.
- The planner works well on mobile and desktop.
- Unrelated website functionality remains intact.
- The required automated tests pass.
- The live deployment is verified.
- Backups and a rollback method are available.

**The final product should allow me to plan two weeks of family dinners and prepare my grocery shopping list with minimal effort.**

---

# 19. Instructions to ChatGPT Work — Start Here

You are responsible for building this project safely and efficiently.

Begin by inspecting https://dieseldesigns.co/planner/ and its actual source environment through the available authorized connection or computer tools.

Do not assume that viewing the public website reveals its underlying files, framework, database, or deployment method.

Discover those details from the real environment.

Review the complete specification and recipe collection before writing code.

Create the smallest reliable implementation that meets every acceptance requirement.

Prioritize completing the entire base application in one coordinated development pass.

Do not interrupt the process for minor design decisions that can be reasonably resolved from this specification.

Follow my mandatory coding rules.

Track each phase using the supplied checklist.

After every major completed phase, provide a short status update using my required coding response format.

Do not claim completion without testing.

Do not stop after building the interface. The recipe database, planning engine, grocery calculations, storage, history, and tests are equally important.

**Your first task is Phase 1: inspect the real environment, create and verify backups, then build the complete implementation plan based on what actually exists. Proceed through the remaining phases as safely and efficiently as the available access allows.**

