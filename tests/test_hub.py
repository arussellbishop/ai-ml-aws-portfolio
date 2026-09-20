import ast,json,re,unittest
from pathlib import Path
from urllib.parse import unquote,urlparse
ROOT=Path(__file__).resolve().parents[1]
class HubTests(unittest.TestCase):
 def test_score_ledger(self):
  model=json.loads((ROOT/'data/projects.json').read_text())
  self.assertEqual(sum(c['max'] for c in model['criteria']),100)
  self.assertEqual(len(model['projects']),len({p['id'] for p in model['projects']}))
  for p in model['projects']:
   self.assertEqual(p['score'],sum(g['earned'] for g in p['gates']))
   self.assertEqual(sum(g['max'] for g in p['gates']),100)
   for g in p['gates']:
    self.assertGreaterEqual(g['earned'],0);self.assertLessEqual(g['earned'],g['max']);self.assertTrue(g['evidence'])
   self.assertTrue(p['purpose']);self.assertTrue(p['limitations']);self.assertTrue(p['next_action'])
 def test_private_records_excluded(self):
  model=json.loads((ROOT/'data/projects.json').read_text())
  ids={p['id'] for p in model['projects']}
  self.assertNotIn('JRB',ids);self.assertNotIn('PROJECT-413531db0fb0',ids)
  for path in (ROOT/'site').rglob('*'):
   if path.is_file() and path.suffix in {'.html','.json','.ipynb','.csv'}:
    self.assertIsNone(re.search(r'/(?:home|Users)/[A-Za-z0-9_.-]+',path.read_text()))
 def test_links_and_dossiers(self):
  for path in (ROOT/'site').glob('*.html'):
   for url in re.findall(r'(?:href|src)="([^"]+)"',path.read_text()):
    parsed=urlparse(url)
    if not parsed.scheme and parsed.path:self.assertTrue((path.parent/unquote(parsed.path)).is_file(),(path.name,url))
  model=json.loads((ROOT/'data/projects.json').read_text())
  for project in model['projects']:self.assertTrue((ROOT/'site'/('work-'+project['id'].lower()+'.html')).is_file())
 def test_notebook_privacy_and_syntax(self):
  for path in (ROOT/'notebooks').glob('*.ipynb'):
   nb=json.loads(path.read_text())
   self.assertNotIn('colab',nb['metadata'])
   for cell in nb['cells']:
    self.assertEqual(cell['metadata'],{})
    if cell['cell_type']=='code':
     self.assertEqual(cell['outputs'],[]);self.assertIsNone(cell['execution_count']);ast.parse(''.join(cell['source']))
 def test_walkthrough_executes_without_cloud(self):
  nb=json.loads((ROOT/'notebooks/data-quality-walkthrough.ipynb').read_text());scope={}
  for cell in nb['cells']:
   if cell['cell_type']=='code':exec(compile(''.join(cell['source']),'walkthrough','exec'),scope)
  self.assertEqual(scope['result']['status'],'FAIL')
  self.assertEqual(scope['result']['valid_rows'],1)
