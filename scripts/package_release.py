"""Create allowlisted public downloads and hash the exact deployable site."""
import csv,hashlib,io,json,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site';RELEASE=ROOT/'release';DOWNLOADS=SITE/'downloads'
RELEASE.mkdir(exist_ok=True);DOWNLOADS.mkdir(exist_ok=True)
for name in ('hosting.json','data-quality.json'):
 (DOWNLOADS/name).write_bytes((ROOT/'infra'/name).read_bytes())
# Export only public summaries: never local paths, private IDs, original screenshots or reports.
rows=[dict(project_id=p['id'],project=p['name'],priority=p['priority'],status=p['status'],evidence=p['evidence'],next_action=p['next_action'],completion_gate=p['completion_gate'],review_date=p['reviewed_on'],verified_percentage='NOT_SCORED') for p in json.loads((ROOT/'data/projects.json').read_text())['projects']]
fields=['project_id','project','priority','status','evidence','next_action','completion_gate','review_date','verified_percentage']
stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
source_files=['Makefile','README.md','quality.py','build.py','build_hosting.py','build_site.py','build_hub.py','infra/hosting.json','infra/data-quality.json','scripts/deploy.py','scripts/package_release.py','scripts/check_browser.py','scripts/build_walkthrough.py']
source_files += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'data').glob('*.json'))]
source_files += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'notebooks').glob('*.ipynb'))]
source_files += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'tests').glob('test_*.py'))]
source_files += [str(p.relative_to(ROOT)) for p in sorted((SITE/'assets').glob('*')) if p.is_file()]
source_files += [str(p.relative_to(ROOT)) for p in sorted(SITE.glob('*.html'))]
secret_pattern=re.compile(rb'(?:AKIA|ASIA)[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
with zipfile.ZipFile(DOWNLOADS/'portfolio-source.zip','w',zipfile.ZIP_DEFLATED) as archive:
 for name in source_files:
  data=(ROOT/name).read_bytes()
  assert not secret_pattern.search(data),name
  assert not re.search(rb'/(?:home|Users)/[A-Za-z0-9_.-]+', data),name
  archive.writestr(name,data)
 archive.writestr('PUBLIC_PROJECT_REGISTER.csv',stream.getvalue())
files={str(p.relative_to(SITE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SITE.rglob('*')) if p.is_file()}
for name in files:
 data=(SITE/name).read_bytes()
 assert not secret_pattern.search(data),name
 if not name.endswith('.zip'):assert not re.search(rb'/(?:home|Users)/[A-Za-z0-9_.-]+', data),name
release_hash=hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest()
manifest={'files':files,'release_sha256':release_hash,'scope':'public site only; no private evidence or credentials'}
(RELEASE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(RELEASE/'portfolio-site.zip','w',zipfile.ZIP_DEFLATED) as archive:
 for name in files:archive.write(SITE/name,name)
print(json.dumps({'site_files':len(files),'site_bytes':sum((SITE/n).stat().st_size for n in files),'release_sha256':release_hash}))
