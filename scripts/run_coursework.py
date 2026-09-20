import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
os.environ['TF_NUM_INTEROP_THREADS']='2'
os.environ['TF_NUM_INTRAOP_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
os.environ['MPLBACKEND']='Agg'
import json,hashlib,platform,contextlib,io,datetime
from pathlib import Path
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1];out=root/'release/coursework';out.mkdir(parents=True,exist_ok=True)
tf.keras.utils.set_random_seed(42)
records=[]
for name in ['sigmoid-gradients.ipynb','mnist-coursework.ipynb']:
 path=root/'notebooks'/name;nb=json.loads(path.read_text());scope={};log=io.StringIO()
 plt.show=lambda:plt.close('all')
 with contextlib.redirect_stdout(log):
  for c in nb['cells']:
   if c['cell_type']=='code':exec(compile(''.join(c['source']),name,'exec'),scope)
 record={'notebook':name,'date':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'python':platform.python_version(),'tensorflow':tf.__version__,'numpy':np.__version__,'keras':tf.keras.__version__,'seed':42,'adaptations':['CPU only','two compute threads','seed 42','noninteractive plots'],'status':'PASS'}
 if name.startswith('sigmoid'):record['gradient_mae']=float(scope['mae'])
 else:
  dataset=Path.home()/'.keras/datasets/mnist.npz'
  record['dataset_sha256']=hashlib.sha256(dataset.read_bytes()).hexdigest()
  record.update(test_loss=float(scope['test_loss']),test_accuracy=float(scope['test_accuracy']),epochs=10,dataset_training_rows=60000,training_rows=48000,validation_rows=12000,test_rows=10000)
 (out/(name+'.log')).write_text(log.getvalue());records.append(record)
 (out/'coursework-runs.json').write_text(json.dumps(records,indent=2));print(json.dumps(record),flush=True)
