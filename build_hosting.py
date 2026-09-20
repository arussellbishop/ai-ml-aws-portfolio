"""Generate the independent HTTPS portfolio host; no resources created."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
ref=lambda name:{'Ref':name}
get=lambda name,attr:{'Fn::GetAtt':[name,attr]}
sub=lambda value:{'Fn::Sub':value}
resources={
 'SiteBucket':{'Type':'AWS::S3::Bucket','DeletionPolicy':'Retain','UpdateReplacePolicy':'Retain','Properties':{
  'PublicAccessBlockConfiguration':dict.fromkeys(['BlockPublicAcls','IgnorePublicAcls','BlockPublicPolicy','RestrictPublicBuckets'],True),
  'OwnershipControls':{'Rules':[{'ObjectOwnership':'BucketOwnerEnforced'}]},
  'VersioningConfiguration':{'Status':'Enabled'},
  'BucketEncryption':{'ServerSideEncryptionConfiguration':[{'ServerSideEncryptionByDefault':{'SSEAlgorithm':'AES256'}}]},
  'Tags':[{'Key':'Project','Value':'RussellBishopPortfolio'}]}},
 'OriginAccess':{'Type':'AWS::CloudFront::OriginAccessControl','Properties':{'OriginAccessControlConfig':{'Name':sub('${AWS::StackName}-oac'),'OriginAccessControlOriginType':'s3','SigningBehavior':'always','SigningProtocol':'sigv4'}}},
 'Cache':{'Type':'AWS::CloudFront::CachePolicy','Properties':{'CachePolicyConfig':{'Name':sub('${AWS::StackName}-cache'),'MinTTL':0,'DefaultTTL':300,'MaxTTL':86400,'ParametersInCacheKeyAndForwardedToOrigin':{'CookiesConfig':{'CookieBehavior':'none'},'HeadersConfig':{'HeaderBehavior':'none'},'QueryStringsConfig':{'QueryStringBehavior':'none'},'EnableAcceptEncodingGzip':True,'EnableAcceptEncodingBrotli':True}}}},
 'Headers':{'Type':'AWS::CloudFront::ResponseHeadersPolicy','Properties':{'ResponseHeadersPolicyConfig':{'Name':sub('${AWS::StackName}-headers'),'SecurityHeadersConfig':{
  'ContentSecurityPolicy':{'ContentSecurityPolicy':"default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",'Override':True},
  'ContentTypeOptions':{'Override':True},'FrameOptions':{'FrameOption':'DENY','Override':True},'ReferrerPolicy':{'ReferrerPolicy':'strict-origin-when-cross-origin','Override':True},'StrictTransportSecurity':{'AccessControlMaxAgeSec':31536000,'Override':True}}}}},
 'Distribution':{'Type':'AWS::CloudFront::Distribution','Properties':{'DistributionConfig':{
  'Enabled':True,'Comment':'Russell Bishop AI engineering portfolio','DefaultRootObject':'index.html','HttpVersion':'http2','IPV6Enabled':True,'PriceClass':'PriceClass_100',
  'Origins':[{'Id':'private-site','DomainName':get('SiteBucket','RegionalDomainName'),'OriginAccessControlId':ref('OriginAccess'),'S3OriginConfig':{'OriginAccessIdentity':''}}],
  'DefaultCacheBehavior':{'TargetOriginId':'private-site','ViewerProtocolPolicy':'redirect-to-https','AllowedMethods':['GET','HEAD'],'CachedMethods':['GET','HEAD'],'Compress':True,'CachePolicyId':ref('Cache'),'ResponseHeadersPolicyId':ref('Headers')},
  'ViewerCertificate':{'CloudFrontDefaultCertificate':True},
  'CustomErrorResponses':[{'ErrorCode':code,'ResponseCode':404,'ResponsePagePath':'/404.html','ErrorCachingMinTTL':10} for code in (403,404)]}}},
 'BucketPolicy':{'Type':'AWS::S3::BucketPolicy','Properties':{'Bucket':ref('SiteBucket'),'PolicyDocument':{'Version':'2012-10-17','Statement':[
  {'Sid':'CloudFrontRead','Effect':'Allow','Principal':{'Service':'cloudfront.amazonaws.com'},'Action':'s3:GetObject','Resource':sub('${SiteBucket.Arn}/*'),'Condition':{'StringEquals':{'AWS:SourceArn':sub('arn:${AWS::Partition}:cloudfront::${AWS::AccountId}:distribution/${Distribution}')}}},
  {'Sid':'RequireTLS','Effect':'Deny','Principal':'*','Action':'s3:*','Resource':[get('SiteBucket','Arn'),sub('${SiteBucket.Arn}/*')],'Condition':{'Bool':{'aws:SecureTransport':'false'}}}]}}}
}
template={'AWSTemplateFormatVersion':'2010-09-09','Description':'Private S3 origin and HTTPS CloudFront portfolio. Usage may incur charges.','Resources':resources,'Outputs':{'SiteBucket':{'Value':ref('SiteBucket')},'DistributionId':{'Value':ref('Distribution')},'SiteURL':{'Value':sub('https://${Distribution.DomainName}')}}}
(root/'infra/hosting.json').write_text(json.dumps(template,indent=2)+'\n')
print('Generated HTTPS hosting template; no cloud changes.')
