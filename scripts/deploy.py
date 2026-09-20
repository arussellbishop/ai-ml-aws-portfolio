"""Deploy only the packaged public site. AWS authentication must exist already."""
import argparse,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--profile',default='portfolio')
p.add_argument('--region',default='eu-north-1')
p.add_argument('--stack',default='russell-bishop-portfolio')
p.add_argument('--apply',action='store_true',help='Create/update hosting and upload the verified site')
args=p.parse_args()
aws=shutil.which('aws') or str(Path.home()/'.local/bin/aws')
env={**os.environ,'AWS_PAGER':'','AWS_EC2_METADATA_DISABLED':'true'}
def run(*parts,parse=True):
 result=subprocess.run([aws,'--profile',args.profile,'--region',args.region,*parts],capture_output=True,text=True,env=env)
 if result.returncode:raise RuntimeError(result.stderr.strip())
 return json.loads(result.stdout) if parse and result.stdout.strip() else result.stdout
manifest=json.loads((ROOT/'release/manifest.json').read_text())
site=ROOT/'site'
actual={str(f.relative_to(site)) for f in site.rglob('*') if f.is_file()}
if actual!=set(manifest['files']):raise RuntimeError('Site file list differs from the tested release. Rebuild it first.')
for name,digest in manifest['files'].items():
 if hashlib.sha256((site/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('Release file changed: '+name)
identity=run('sts','get-caller-identity')
print('AWS authentication verified. Account ID withheld from public output.')
run('cloudformation','validate-template','--template-body','file://'+str(ROOT/'infra/hosting.json'))
print('AWS hosting-template validation passed.')
if not args.apply:
 print('Preflight complete; --apply creates/updates hosting and uploads this release.')
 raise SystemExit(0)
run('cloudformation','deploy','--stack-name',args.stack,'--template-file',str(ROOT/'infra/hosting.json'),'--no-fail-on-empty-changeset','--tags','Project=RussellBishopPortfolio',parse=False)
stack=run('cloudformation','describe-stacks','--stack-name',args.stack)['Stacks'][0]
outputs={x['OutputKey']:x['OutputValue'] for x in stack['Outputs']}
# No --delete: a previously deployed release is not destructively pruned.
run('s3','sync',str(site),'s3://'+outputs['SiteBucket']+'/','--cache-control','public,max-age=300','--only-show-errors',parse=False)
invalidation=run('cloudfront','create-invalidation','--distribution-id',outputs['DistributionId'],'--paths','/*')
record={'site_url':outputs['SiteURL'],'stack':args.stack,'region':args.region,'release_sha256':manifest['release_sha256'],'deployed_at_unix':int(time.time()),'invalidation_id':invalidation['Invalidation']['Id'],'public_smoke_test':'PENDING'}
(ROOT/'release/deployment.json').write_text(json.dumps(record,indent=2)+'\n')
print('Uploaded:',outputs['SiteURL'])
print('CloudFront propagation and public smoke test remain to be checked.')
