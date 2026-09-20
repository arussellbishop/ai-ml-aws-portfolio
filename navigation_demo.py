"""Synthetic 1-D navigation fusion exercise; no hardware or control interface.

Compare a fixed-noise Kalman update with innovation-gated updates on identical
seeded observations. This is a statistical baseline, not a trained AI model.
"""
import argparse
import hashlib
import json
import math
import random
from pathlib import Path

def observations(seed, steps=300):
    rng=random.Random(seed)
    truth=0.0
    rows=[]
    for t in range(steps):
        delta=0.1+0.02*math.sin(t/20)
        truth+=delta
        odometry=delta+0.004+rng.gauss(0,0.02)
        gnss=None if 100<=t<180 else truth+rng.gauss(0,0.3)
        radio=truth+rng.gauss(0,0.5)+(5.0 if 140<=t<200 else 0.0)
        rows.append({'t':t,'truth':truth,'odometry':odometry,'gnss':gnss,'radio':radio})
    return rows

def estimate(rows, gated=False):
    position=0.0
    variance=1.0
    estimates=[]
    rejected=0
    for row in rows:
        position+=row['odometry']
        variance+=0.02**2
        for sensor,measurement_variance in [('gnss',0.3**2),('radio',0.5**2)]:
            observation=row[sensor]
            if observation is None:
                continue
            innovation=observation-position
            innovation_variance=variance+measurement_variance
            if gated and innovation**2/innovation_variance>9.0:
                rejected+=1
                continue
            gain=variance/innovation_variance
            position+=gain*innovation
            variance=(1-gain)*variance
        estimates.append(position)
    errors=[p-r['truth'] for p,r in zip(estimates,rows)]
    return {'rmse':math.sqrt(sum(e*e for e in errors)/len(errors)),
            'max_absolute_error':max(map(abs,errors)),
            'rejected_updates':rejected,'estimates':estimates}

def evaluate(seeds=range(20)):
    runs=[]
    for seed in seeds:
        rows=observations(seed)
        plain=estimate(rows)
        gated=estimate(rows,True)
        runs.append({'seed':seed,'input_sha256':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest(),
                     'fixed_rmse':plain['rmse'],'gated_rmse':gated['rmse'],
                     'fixed_max_error':plain['max_absolute_error'],'gated_max_error':gated['max_absolute_error'],
                     'rejected_updates':gated['rejected_updates']})
    return {'scope':'Synthetic scalar position units; no real GNSS, RF interference, Tello flight or trained ML model.',
            'scenario':'300 steps; GNSS missing steps 100–179; radio +5 bias steps 140–199; odometry drift 0.004 per step.',
            'method':'Fixed Kalman baseline versus 3-sigma innovation gate; fixed parameters, seeds 0–19.',
            'mean_fixed_rmse':sum(r['fixed_rmse'] for r in runs)/len(runs),
            'mean_gated_rmse':sum(r['gated_rmse'] for r in runs)/len(runs),
            'gated_lower_rmse_runs':sum(r['gated_rmse']<r['fixed_rmse'] for r in runs),
            'limitations':['Engineered fault scenario favours rejection; not evidence of general superiority.',
                          'No calibrated 3D sensor models, covariance-consistency study, independent dataset or timing solution.',
                          'No learned selector; compare learned and robust fusion only in a future frozen evaluation.'],
            'runs':runs}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    report=json.dumps(evaluate(),indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(report)
    else:
        print(report)
