"""Create a portable, credential-free notebook from the tested validator."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def md(text):return {'cell_type':'markdown','metadata':{},'source':text.splitlines(keepends=True)}
def code(text):return {'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':text.splitlines(keepends=True)}
sample="""sample = {'as_of': '2026-09-19', 'rows': [
    {'asset': 'DEMO', 'date': '2026-09-18', 'acquired_on': '2026-09-19', 'close': 100}
]}
result = validate(sample)
assert result['status'] == 'PASS'
print(json.dumps(result, indent=2))
"""
fail="""import copy
broken = copy.deepcopy(sample)
broken['rows'].append(copy.deepcopy(broken['rows'][0]))
broken['rows'].append({'asset': 'OTHER', 'date': '2026-09-20', 'acquired_on': '2026-09-19', 'close': -5})
result = validate(broken)
assert result['status'] == 'FAIL'
assert result['valid_rows'] == 1
assert len(result['issues']) == 2
print(json.dumps(result, indent=2))
"""
nb={'nbformat':4,'nbformat_minor':0,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'cells':[md('# Data-quality walkthrough\n\nA self-contained Python demonstration for the portfolio. Uses the standard library and synthetic data; no credentials, Drive mount, cloud account or external request is required. Code cells are executed in a clean local Python process during release checks. In Colab, upload this file and choose Runtime → Run all. This does not test the AWS S3/Lambda integration.\n'),code((root/'quality.py').read_text()),md('## A valid record\n\nDates express observation and acquisition order; they do not prove point-in-time source availability.\n'),code(sample),md('## Find duplicate, price and date errors\n'),code(fail),md('## Review notes\n\nRecord Python version, input changes, observed output and limitations. A passing validation result does not establish investment value or source accuracy. No model is trained in this demonstration.\n')]}
(root/'notebooks/data-quality-walkthrough.ipynb').write_text(json.dumps(nb,indent=2)+'\n')
print('Created standard-library execution notebook.')
