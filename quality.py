"""Bounded financial-data quality demonstration; no trading recommendations."""
import hashlib
import json
import math
import os
from datetime import date
from urllib.parse import unquote_plus

MAX_BYTES = 262144

def validate(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get('rows'), list):
        raise ValueError('Expected an object containing rows')
    rows = payload['rows']
    if not 1 <= len(rows) <= 1000:
        raise ValueError('Expected 1–1000 rows')
    as_of = date.fromisoformat(payload['as_of'])
    seen, issues = set(), []
    for index, row in enumerate(rows):
        errors = []
        if not isinstance(row, dict):
            issues.append({'row': index, 'codes': ['invalid_row']})
            continue
        asset = row.get('asset')
        if not isinstance(asset, str) or not asset.strip() or len(asset) > 32:
            errors.append('invalid_asset')
        value = row.get('close')
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            errors.append('invalid_close')
        try:
            observed = date.fromisoformat(row['date'])
            acquired = date.fromisoformat(row['acquired_on'])
            if observed > acquired or acquired > as_of:
                errors.append('invalid_temporal_order')
            if isinstance(asset, str):
                key = (asset, observed)
                if key in seen:
                    errors.append('duplicate_asset_date')
                seen.add(key)
        except (KeyError, TypeError, ValueError):
            errors.append('invalid_date')
        if errors:
            issues.append({'row': index, 'codes': errors})
    return {'schema_version': 1, 'as_of': as_of.isoformat(), 'rows': len(rows),
            'valid_rows': len(rows) - len(issues), 'issues': issues,
            'status': 'PASS' if not issues else 'FAIL'}

def process(event, client):
    results = []
    for record in event.get('Records', []):
        source = record.get('s3', {})
        obj = source.get('object', {})
        key = unquote_plus(obj.get('key', ''))
        bucket = source.get('bucket', {}).get('name')
        if (record.get('eventSource') != 'aws:s3' or
            not record.get('eventName', '').startswith('ObjectCreated:') or
            bucket != os.environ['INPUT_BUCKET'] or
            not key.startswith('incoming/') or not key.endswith('.json')):
            raise ValueError('Unexpected event source or object')
        version = obj.get('versionId')
        if not version:
            raise ValueError('Versioned object required')
        response = client.get_object(Bucket=bucket, Key=key, VersionId=version)
        stream = response['Body']
        try:
            body = stream.read(MAX_BYTES + 1)
        finally:
            stream.close()
        if len(body) > MAX_BYTES:
            raise ValueError('Object exceeds size limit')
        result = validate(json.loads(body))
        digest = hashlib.sha256(json.dumps([bucket, key, version]).encode()).hexdigest()
        output = 'results/' + digest + '.json'
        client.put_object(Bucket=os.environ['OUTPUT_BUCKET'], Key=output,
                          Body=json.dumps(result, allow_nan=False).encode(),
                          ContentType='application/json')
        results.append(output)
    return {'outputs': results}

def handler(event, context):
    import boto3
    return process(event, boto3.client('s3'))
