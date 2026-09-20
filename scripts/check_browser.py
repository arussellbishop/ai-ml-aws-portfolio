"""Real-browser interactions and responsive layout checks on the built site."""
import functools,http.server,json,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def end_headers(self):
  self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
  super().end_headers()
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'site')))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}'
errors=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000})
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('console',lambda message:errors.append(message.text) if message.type=='error' and 'favicon.ico' not in message.text else None)
 for path in sorted((ROOT/'site').glob('*.html')):
  response=page.goto(base+'/'+path.name)
  assert response.status==200,path.name
  assert page.locator('h1').count()==1,path.name
  assert not page.evaluate('document.documentElement.scrollWidth>window.innerWidth'),path.name
 page.goto(base+'/demo.html')
 page.locator('#run').click()
 result=json.loads(page.locator('#result').inner_text())
 assert result['status']=='FAIL' and result['valid_rows']==1 and len(result['issues'])==2
 page.locator('#scenario').select_option('clean');page.locator('#run').click()
 assert json.loads(page.locator('#result').inner_text())['status']=='PASS'
 page.locator('#payload').fill('{bad json');page.locator('#run').click()
 assert 'Input error:' in page.locator('#result').inner_text()
 page.goto(base+'/projects.html')
 assert page.locator('article:visible').count()==len(json.loads((ROOT/'data/projects.json').read_text())['projects'])
 page.locator('#search').fill('AIVouch')
 assert page.locator('article:visible').count()==1
 page.locator('#search').fill('');page.locator('#audience').select_option('examiner')
 assert page.locator('article:visible').count()==sum('examiner' in p['audiences'] for p in json.loads((ROOT/'data/projects.json').read_text())['projects'])
 page.locator('#category').select_option('Research & MSc')
 assert page.locator('article:visible').count()>0
 responsive_pages=('index.html','projects.html','demo.html','architecture.html','dashboard.html','review.html','execution.html','readiness.html','robotics.html','quant-research.html','automation.html','research-gaps.html','capabilities.html','cran-0091.html')
 for width in (390,768):
  page.set_viewport_size({'width':width,'height':844})
  for path in responsive_pages:
   page.goto(base+'/'+path)
   assert not page.evaluate('document.documentElement.scrollWidth>window.innerWidth'),(width,path)
 (ROOT/'release').mkdir(exist_ok=True)
 page.goto(base+'/index.html');page.screenshot(path=str(ROOT/'release/mobile.png'),full_page=True)
 page.set_viewport_size({'width':1440,'height':1000});page.screenshot(path=str(ROOT/'release/desktop.png'),full_page=True)
 page.goto(base+'/dashboard.html');page.screenshot(path=str(ROOT/'release/dashboard-review.png'),full_page=False)
 browser.close()
server.shutdown()
assert not errors,errors
report={'desktop_pages':len(list((ROOT/'site').glob('*.html'))),'mobile_tablet_layout_checks':len(responsive_pages)*2,'demo_valid_invalid_malformed':True,'catalogue_search_filter':True,'browser_errors':errors,'csp_enabled':True}
(ROOT/'release/browser-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
