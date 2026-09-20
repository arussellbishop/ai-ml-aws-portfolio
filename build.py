import json
from pathlib import Path
root = Path(__file__).resolve().parent
s = lambda x: {'Fn::Sub': x}
r = lambda x: {'Ref': x}
a = lambda x: {'Fn::GetAtt': [x, 'Arn']}
name = '${AWS::StackName}-${AWS::AccountId}-${AWS::Region}-in'
private = {'PublicAccessBlockConfiguration': dict.fromkeys(['BlockPublicAcls','IgnorePublicAcls','BlockPublicPolicy','RestrictPublicBuckets'], True), 'VersioningConfiguration': {'Status':'Enabled'}, 'BucketEncryption': {'ServerSideEncryptionConfiguration':[{'ServerSideEncryptionByDefault':{'SSEAlgorithm':'AES256'}}]}}
resources = {'Output': {'Type':'AWS::S3::Bucket','DeletionPolicy':'Retain','UpdateReplacePolicy':'Retain','Properties':private}, 'Logs': {'Type':'AWS::Logs::LogGroup','Properties':{'LogGroupName':s('/aws/lambda/${AWS::StackName}-quality'),'RetentionInDays':7}}}
statements = [
 {'Effect':'Allow','Action':['s3:GetObject','s3:GetObjectVersion'],'Resource':s('arn:${AWS::Partition}:s3:::'+name+'/incoming/*')},
 {'Effect':'Allow','Action':'s3:PutObject','Resource':s('${Output.Arn}/results/*')},
 {'Effect':'Allow','Action':['logs:CreateLogStream','logs:PutLogEvents'],'Resource':a('Logs')}]
resources['Role'] = {'Type':'AWS::IAM::Role','Properties':{'AssumeRolePolicyDocument':{'Version':'2012-10-17','Statement':[{'Effect':'Allow','Principal':{'Service':'lambda.amazonaws.com'},'Action':'sts:AssumeRole'}]},'Policies':[{'PolicyName':'DataQuality','PolicyDocument':{'Version':'2012-10-17','Statement':statements}}]}}
resources['Function'] = {'Type':'AWS::Lambda::Function','Properties':{'FunctionName':s('${AWS::StackName}-quality'),'Runtime':'python3.12','Handler':'index.handler','Role':a('Role'),'MemorySize':128,'Timeout':15,'Environment':{'Variables':{'INPUT_BUCKET':s(name),'OUTPUT_BUCKET':r('Output')}},'Code':{'ZipFile':(root/'quality.py').read_text()}}}
resources['InvokePermission'] = {'Type':'AWS::Lambda::Permission','Properties':{'FunctionName':r('Function'),'Action':'lambda:InvokeFunction','Principal':'s3.amazonaws.com','SourceAccount':r('AWS::AccountId'),'SourceArn':s('arn:${AWS::Partition}:s3:::'+name)}}
resources['Input'] = {'Type':'AWS::S3::Bucket','DependsOn':'InvokePermission','DeletionPolicy':'Retain','UpdateReplacePolicy':'Retain','Properties':{**private,'BucketName':s(name),'NotificationConfiguration':{'LambdaConfigurations':[{'Event':'s3:ObjectCreated:*','Function':a('Function'),'Filter':{'S3Key':{'Rules':[{'Name':'prefix','Value':'incoming/'},{'Name':'suffix','Value':'.json'}]}}}]}}}
resources['AsyncPolicy'] = {'Type':'AWS::Lambda::EventInvokeConfig','Properties':{'FunctionName':r('Function'),'Qualifier':'$LATEST','MaximumRetryAttempts':0,'MaximumEventAgeInSeconds':60}}
for bucket in ['Input','Output']:
 resources[bucket+'TLS'] = {'Type':'AWS::S3::BucketPolicy','Properties':{'Bucket':r(bucket),'PolicyDocument':{'Version':'2012-10-17','Statement':[{'Effect':'Deny','Principal':'*','Action':'s3:*','Resource':[a(bucket),s('${'+bucket+'.Arn}/*')],'Condition':{'Bool':{'aws:SecureTransport':'false'}}}]}}}
(root/'infra/data-quality.json').write_text(json.dumps({'AWSTemplateFormatVersion':'2010-09-09','Resources':resources,'Outputs':{'InputBucket':{'Value':r('Input')},'OutputBucket':{'Value':r('Output')}}},indent=2)+'\n')
print('Template generated; no deployment performed.')
