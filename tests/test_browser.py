"""Actual Chromium acceptance checks; temporary database, never personal data."""
import json
import tempfile
import threading
import unittest
from pathlib import Path
from planner.store import Store
from planner.server import make_server

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright=None

@unittest.skipUnless(sync_playwright,'Install Playwright to run browser acceptance checks.')
class BrowserTests(unittest.TestCase):
    def test_M_desktop_mobile_and_complete_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            server=make_server(Store(Path(tmp)/'browser.sqlite3'),'browser-test-password',port=0)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                with sync_playwright() as p:
                    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
                    context=browser.new_context(viewport={'width':1280,'height':900},permissions=['clipboard-read','clipboard-write'])
                    page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                    page.goto(f'http://127.0.0.1:{server.server_port}/');page.locator('#password').fill('browser-test-password');page.get_by_role('button',name='Unlock planner').click()
                    page.locator('#application').wait_for(state='visible')
                    page.locator('#start').fill('2026-11-14');page.locator('#start').dispatch_event('change');page.wait_for_function("() => document.querySelector('#generate').disabled === false")
                    page.locator('#generate').click();page.wait_for_function("() => document.querySelectorAll('.meal-row').length === 14")
                    page.wait_for_function("() => document.querySelector('#generate').disabled === false")
                    self.assertEqual(page.locator('.meal-row').count(),14)
                    self.assertIn('Fend for Yourself',page.locator('[data-date="2026-11-14"]').inner_text())
                    self.assertIn('Eat Out',page.locator('[data-date="2026-11-27"]').inner_text())
                    page.locator('#extra-name').fill('Browser apples');page.locator('#extra-quantity').fill('1 bag');page.get_by_role('button',name='Add item',exact=True).click();page.get_by_text('Browser apples',exact=True).wait_for()
                    page.wait_for_function("() => document.querySelector('#generate').disabled === false")
                    page.get_by_role('button',name='Change dinner for 2026-11-14').click();page.locator('#meal-2026-11-14').select_option('23');page.get_by_role('button',name='Save dinner').click()
                    page.locator('[data-date="2026-11-14"]').get_by_text('Beef Stew',exact=True).wait_for();page.get_by_text('Beef stew meat',exact=True).wait_for()
                    self.assertTrue(page.get_by_text('Browser apples',exact=True).is_visible())
                    page.reload();page.locator('[data-date="2026-11-14"]').get_by_text('Beef Stew',exact=True).wait_for();self.assertTrue(page.get_by_text('Browser apples',exact=True).is_visible())
                    page.locator('#copy').click();page.wait_for_function("() => document.querySelector('#status').textContent === 'Shopping list copied.'")
                    copied=page.evaluate('navigator.clipboard.readText()');self.assertRegex(copied,r'Beef stew meat — (2\.5|5) lbs');self.assertIn('Meat & Poultry',copied);self.assertIn('Browser apples',copied)
                    # Inline quantity adjustment and exclusions persist on refresh.
                    page.get_by_role('button',name='Edit quantity for Beef stew meat',exact=True).click();page.get_by_role('textbox',name='Quantity for Beef stew meat',exact=True).fill('3 lbs');page.get_by_role('button',name='Save amount',exact=True).click()
                    page.get_by_text('3 lbs',exact=True).wait_for();page.wait_for_function("() => document.querySelector('#generate').disabled === false")
                    page.get_by_role('button',name='Already have Beef stew meat',exact=True).click();page.locator('#excluded-details').wait_for(state='visible');page.wait_for_function("() => document.querySelector('#generate').disabled === false")
                    page.reload();page.locator('#excluded-details').wait_for(state='visible');page.locator('#excluded-details summary').click();page.get_by_role('button',name='Include again',exact=True).click();page.get_by_text('3 lbs',exact=True).wait_for()
                    # Recipe management: optional instructions, markup escaped, persistent edit, archive.
                    page.locator('#recipes-link').click();page.locator('#new-recipe').click();page.locator('#recipe-title').fill('Test <b>family dinner</b>');page.locator('#ingredient-text').fill('Test ingredient — 2 cans');page.get_by_role('button',name='Save recipe',exact=True).click();page.get_by_text('Test <b>family dinner</b>',exact=True).wait_for();self.assertEqual(page.locator('.recipe-card b').count(),0)
                    page.get_by_role('button',name='Edit Test <b>family dinner</b>',exact=True).click();page.locator('#recipe-title').fill('Edited family dinner');page.get_by_role('button',name='Save recipe',exact=True).click();page.get_by_text('Edited family dinner',exact=True).wait_for()
                    page.reload();page.locator('#recipes-link').click();page.get_by_role('button',name='Edit Edited family dinner',exact=True).click();page.locator('#archive-recipe').click();page.locator('#confirm-yes').click();page.wait_for_function("() => document.querySelector('#generate').disabled === false");self.assertEqual(page.get_by_text('Edited family dinner',exact=True).count(),0)
                    page.locator('#history-link').click();page.locator('#history-view').wait_for(state='visible');page.locator('#history-date').fill('2026-11-14');page.locator('#history-date').dispatch_event('change');self.assertIn('Beef Stew',page.locator('#history-result').inner_text());self.assertGreater(page.locator('#revisions details').count(),0)
                    page.locator('#history-view .back').click()
                    # Small screen: no horizontal scroll, controls and dates stay visible.
                    page.set_viewport_size({'width':375,'height':812})
                    self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'),375)
                    for selector in ['#generate','.meal-row','#copy','#extra-name']:
                        boxes=page.locator(selector).all()
                        for item in boxes:
                            bounds=item.bounding_box();self.assertGreaterEqual(bounds['x'],0);self.assertLessEqual(bounds['x']+bounds['width'],375)
                    artifacts=Path('/workspace/artifacts/planner');artifacts.mkdir(parents=True,exist_ok=True)
                    page.screenshot(path=str(artifacts/'mobile.png'),full_page=True)
                    page.set_viewport_size({'width':1280,'height':900});page.screenshot(path=str(artifacts/'desktop.png'),full_page=True)
                    # Escape cancels regeneration; intentional regeneration creates a new version.
                    old=page.locator('#meals').inner_text();page.locator('#regenerate').click();page.keyboard.press('Escape');self.assertEqual(old,page.locator('#meals').inner_text())
                    page.locator('#regenerate').click();page.locator('#confirm-yes').click();page.wait_for_function("() => document.querySelector('#generate').disabled === false")
                    page.get_by_text('Browser apples',exact=True).wait_for(state='detached')
                    self.assertEqual(page.locator('.meal-row').count(),14)
                    # Keyboard can reach primary controls; print stylesheet has valid application layout.
                    page.locator('#start').focus()
                    for _ in range(5):
                        page.keyboard.press('Tab')
                        if page.evaluate('document.activeElement.id')=='generate': break
                    self.assertEqual(page.evaluate('document.activeElement.id'),'generate')
                    page.emulate_media(media='print');self.assertFalse(page.locator('#generate').is_visible());self.assertTrue(page.locator('#shopping-title').is_visible())
                    self.assertEqual(errors,[])
                    browser.close()
            finally:server.shutdown();server.server_close();thread.join()

if __name__=='__main__':unittest.main()
