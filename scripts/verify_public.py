"""Verify exact release bytes, headers and browser behavior on the live URL."""
import hashlib,json,urllib.request,urllib.error
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
record=json.loads((ROOT/'release/deployment.json').read_text())
manifest=json.loads((ROOT/'release/manifest.json').read_text())
base=record['site_url']
checked=[]
for name,digest in manifest['files'].items():
 with urllib.request.urlopen(base+'/'+name,timeout=30) as response:
  assert response.status==200,(name,response.status)
  assert hashlib.sha256(response.read()).hexdigest()==digest,('Hash mismatch',name)
  for header in ('Content-Security-Policy','Strict-Transport-Security','X-Content-Type-Options','X-Frame-Options'):
   assert response.headers.get(header),(name,header)
 checked.append(name)
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
try:
 urllib.request.build_opener(NoRedirect).open(base.replace('https:','http:')+'/',timeout=30)
 raise AssertionError('HTTP did not redirect')
except urllib.error.HTTPError as error:
 assert error.code in (301,302,307,308),error.code
 assert error.headers['Location'].startswith('https://'),error.headers
try:
 urllib.request.urlopen(base+'/missing-page-verification.html',timeout=30)
 raise AssertionError('Missing page returned success')
except urllib.error.HTTPError as error:
 assert error.code==404,error.code
errors=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000})
 page.on('pageerror',lambda error:errors.append(str(error)))
 page.goto(base+'/demo.html',wait_until='networkidle')
 page.locator('#run').click()
 assert json.loads(page.locator('#result').inner_text())['status']=='FAIL'
 page.locator('#scenario').select_option('clean');page.locator('#run').click()
 assert json.loads(page.locator('#result').inner_text())['status']=='PASS'
 page.goto(base+'/projects.html',wait_until='networkidle')
 assert page.locator('article:visible').count()==len(json.loads((ROOT/'data/projects.json').read_text())['projects'])
 page.locator('#search').fill('AIVouch')
 assert page.locator('article:visible').count()==1
 page.goto(base+'/',wait_until='networkidle')
 page.screenshot(path=str(ROOT/'release/live-desktop.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':844})
 assert not page.evaluate('document.documentElement.scrollWidth>window.innerWidth')
 page.screenshot(path=str(ROOT/'release/live-mobile.png'),full_page=True)
 browser.close()
assert not errors,errors
report={'site_url':base,'verified_files':checked,'hashes_match':True,'https_redirect':True,'security_headers':True,'missing_page_404':True,'demo_and_search':True,'browser_errors':errors}
(ROOT/'release/public-verification.json').write_text(json.dumps(report,indent=2)+'\n')
record['public_smoke_test']='PASSED'
(ROOT/'release/deployment.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(report))
