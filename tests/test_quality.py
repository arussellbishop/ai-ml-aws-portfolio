import copy
import io
import os
import unittest
from unittest.mock import Mock, patch
from quality import validate, process, MAX_BYTES

SAMPLE = {'as_of': '2026-09-19', 'rows': [
    {'asset': 'DEMO', 'date': '2026-09-18', 'acquired_on': '2026-09-19', 'close': 100}]}

class QualityTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate(SAMPLE)['status'], 'PASS')

    def test_duplicates(self):
        data = copy.deepcopy(SAMPLE)
        data['rows'] *= 2
        self.assertIn('duplicate_asset_date', validate(data)['issues'][0]['codes'])

    def test_invalid_prices(self):
        for value in [True, -1, 0, float('nan'), float('inf'), '100', None]:
            with self.subTest(value=value):
                data = copy.deepcopy(SAMPLE)
                data['rows'][0]['close'] = value
                self.assertEqual(validate(data)['status'], 'FAIL')

    def test_future_acquisition(self):
        data = copy.deepcopy(SAMPLE)
        data['rows'][0]['acquired_on'] = '2026-09-20'
        self.assertIn('invalid_temporal_order', validate(data)['issues'][0]['codes'])

    def test_limits_and_schema(self):
        for value in [None, [], {}, {'rows': []}, {'rows': [None] * 1001}]:
            with self.assertRaises(ValueError):
                validate(value)

    @patch.dict(os.environ, INPUT_BUCKET='input', OUTPUT_BUCKET='output')
    def test_versioned_event_and_repeat(self):
        import json
        client = Mock()
        client.get_object.side_effect = lambda **kwargs: {'Body': io.BytesIO(json.dumps(SAMPLE).encode())}
        event = {'Records': [{'eventSource': 'aws:s3', 'eventName': 'ObjectCreated:Put',
                 's3': {'bucket': {'name': 'input'}, 'object': {'key': 'incoming/demo.json', 'versionId': 'v1'}}}]}
        self.assertEqual(process(event, client), process(event, client))
        client.get_object.assert_called_with(Bucket='input', Key='incoming/demo.json', VersionId='v1')
        self.assertEqual(client.put_object.call_args.kwargs['Bucket'], 'output')
        event['Records'][0]['s3']['bucket']['name'] = 'other'
        with self.assertRaises(ValueError):
            process(event, client)

    @patch.dict(os.environ, INPUT_BUCKET='input', OUTPUT_BUCKET='output')
    def test_oversize_rejected(self):
        client = Mock()
        client.get_object.return_value = {'Body': io.BytesIO(b'x' * (MAX_BYTES + 1))}
        event = {'Records': [{'eventSource': 'aws:s3', 'eventName': 'ObjectCreated:Put',
                 's3': {'bucket': {'name': 'input'}, 'object': {'key': 'incoming/a.json', 'versionId': 'v1'}}}]}
        with self.assertRaises(ValueError):
            process(event, client)
        client.put_object.assert_not_called()
