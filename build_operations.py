"""Generate a bounded AWS operations foundation template."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sub = lambda s: {'Fn::Sub': s}
ref = lambda s: {'Ref': s}
get = lambda s, a: {'Fn::GetAtt': [s, a]}
heartbeat = "import boto3,datetime,json,os\ns3=boto3.client('s3')\ndef handler(event,context):\n now=datetime.datetime.now(datetime.timezone.utc).isoformat()\n key='heartbeats/'+now.replace(':','-')+'.json'\n body={'schema_version':1,'generated_at':now,'status':'PASS','read_only':True,'live_trading':'DISABLED','telegram_sending':'DISABLED'}\n s3.put_object(Bucket=os.environ['EVIDENCE_BUCKET'],Key=key,Body=json.dumps(body).encode(),ContentType='application/json')\n return body\n"
template = {
  'AWSTemplateFormatVersion':'2010-09-09',
  'Description':'Portable bounded AIOS operations: versioned evidence, heartbeat, DLQ and alarm.',
  'Resources': {
    'EvidenceBucket': {'Type':'AWS::S3::Bucket','DeletionPolicy':'Retain','UpdateReplacePolicy':'Retain','Properties':{'BucketEncryption':{'ServerSideEncryptionConfiguration':[{'ServerSideEncryptionByDefault':{'SSEAlgorithm':'AES256'}}]},'VersioningConfiguration':{'Status':'Enabled'},'PublicAccessBlockConfiguration':{'BlockPublicAcls':True,'BlockPublicPolicy':True,'IgnorePublicAcls':True,'RestrictPublicBuckets':True}}},
    'FailureQueue': {'Type':'AWS::SQS::Queue','Properties':{'MessageRetentionPeriod':1209600,'VisibilityTimeout':300}},
    'FailureAlarm': {'Type':'AWS::CloudWatch::Alarm','Properties':{'AlarmDescription':'Operations failures require review.','Namespace':'AWS/SQS','MetricName':'ApproximateNumberOfMessagesVisible','Dimensions':[{'Name':'QueueName','Value':ref('FailureQueue')}],'Statistic':'Maximum','Period':300,'EvaluationPeriods':1,'Threshold':1,'ComparisonOperator':'GreaterThanOrEqualToThreshold','TreatMissingData':'notBreaching'}},
    'HeartbeatRole': {'Type':'AWS::IAM::Role','Properties':{'AssumeRolePolicyDocument':{'Version':'2012-10-17','Statement':[{'Effect':'Allow','Principal':{'Service':'lambda.amazonaws.com'},'Action':'sts:AssumeRole'}]},'Policies':[{'PolicyName':'HeartbeatWrite','PolicyDocument':{'Version':'2012-10-17','Statement':[{'Effect':'Allow','Action':['s3:PutObject'],'Resource':sub('${EvidenceBucket.Arn}/heartbeats/*')},{'Effect':'Allow','Action':['logs:CreateLogGroup','logs:CreateLogStream','logs:PutLogEvents'],'Resource':'*'}]}}]}},
    'HeartbeatFunction': {'Type':'AWS::Lambda::Function','Properties':{'Runtime':'python3.12','Handler':'index.handler','Timeout':30,'Role':get('HeartbeatRole','Arn'),'Environment':{'Variables':{'EVIDENCE_BUCKET':ref('EvidenceBucket')}},'Code':{'ZipFile':heartbeat}}},
    'HeartbeatSchedule': {'Type':'AWS::Events::Rule','Properties':{'ScheduleExpression':'rate(15 minutes)','State':'ENABLED','Targets':[{'Arn':get('HeartbeatFunction','Arn'),'Id':'heartbeat'}]}},
    'HeartbeatPermission': {'Type':'AWS::Lambda::Permission','Properties':{'FunctionName':ref('HeartbeatFunction'),'Action':'lambda:InvokeFunction','Principal':'events.amazonaws.com','SourceArn':get('HeartbeatSchedule','Arn')}},
    'OperationsLog': {'Type':'AWS::Logs::LogGroup','DeletionPolicy':'Retain','UpdateReplacePolicy':'Retain','Properties':{'LogGroupName':sub('/aws/aios/${AWS::StackName}/operations'),'RetentionInDays':30}}
  },
  'Outputs': {'EvidenceBucket':{'Value':ref('EvidenceBucket')},'FailureQueue':{'Value':ref('FailureQueue')},'HeartbeatFunction':{'Value':ref('HeartbeatFunction')},'HeartbeatSchedule':{'Value':ref('HeartbeatSchedule')}}
}
(ROOT/'infra/operations.json').write_text(json.dumps(template,indent=2)+'\n')
print('Generated infra/operations.json')
