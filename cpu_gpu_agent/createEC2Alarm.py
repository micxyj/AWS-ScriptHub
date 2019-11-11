# For using this python, you fist need to install aws cli and aws configure
# Then you need to modify groupname
# Also you can modify alarm put_metric_alarm according to your need
# If you want to create resource group for CloudFront, the region must be us-east-1

import boto3

# create cpu utilization alarm


def CPU_Utilization_Alarm(clientcw, SNSTopic, instanceid):
    clientcw.put_metric_alarm(
        AlarmName=instanceid + '_CPU_Utilization',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        ActionsEnabled=True,
        AlarmActions=[
            SNSTopic
        ],
        AlarmDescription='Alarm when server CPU exceeds 70%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instanceid
            },
        ],
    )


# create disk ReadBytes alarm
def Disk_ReadBytes_alarm(clientcw, SNSTopic, instanceid):
    clientcw.put_metric_alarm(
        AlarmName=instanceid + '_Disk_ReadBytes',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='DiskReadBytes',
        Namespace='AWS/EC2',
        Period=60,
        Statistic='Average',
        Threshold=300.0,
        ActionsEnabled=True,
        AlarmActions=[
            SNSTopic
        ],
        AlarmDescription='Alarm when disk readbytes exceeds 300',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instanceid
            },
        ],
    )

# create disk used percentage alarm


def Disk_Used_Alarm(clientcw, SNSTopic, instanceid, instancetype, ImageId):
    clientcw.put_metric_alarm(
        AlarmName=instanceid + '_Disk_Used',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='disk_used_percent',
        Namespace='CWAgent',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        ActionsEnabled=True,
        AlarmActions=[
            SNSTopic
        ],
        AlarmDescription='Alarm when disk used percentage exceeds 70%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instanceid
            },
            {
                'Name': 'path',
                'Value': '/'
            },
            {
                'Name': 'ImageId',
                'Value': ImageId
            },
            {
                'Name': 'InstanceType',
                'Value': instancetype
            },
            {
                'Name': 'device',
                'Value': 'xvda1'
            },
            {
                'Name': 'fstype',
                'Value': 'xfs'
            }
        ],
    )

# create memory used percentage alarm


def Memory_Used_Alarm(clientcw, SNSTopic, instanceid, instancetype, ImageId):
    clientcw.put_metric_alarm(
        AlarmName=instanceid + '_Memory_Used',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='mem_used_percent',
        Namespace='CWAgent',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        ActionsEnabled=True,
        AlarmActions=[
            SNSTopic
        ],
        AlarmDescription='Alarm when memory used percentage exceeds 70%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instanceid
            },
            {
                'Name': 'ImageId',
                'Value': ImageId
            },
            {
                'Name': 'InstanceType',
                'Value': instancetype
            },
        ],
    )

# create GPU utilization alarm


def GPU_Utilization_alarm(clientcw, SNSTopic, instanceid, instancetype, ImageId):
    clientcw.put_metric_alarm(
        AlarmName=instanceid + '_GPU_Utilization',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='GPU Usage',
        Namespace='DeepLearningTrain',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        ActionsEnabled=True,
        AlarmActions=[
            SNSTopic
        ],
        AlarmDescription='Alarm when gpu utilization exceeds 70%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instanceid
            },
            {
                'Name': 'ImageId',
                'Value': ImageId
            },
            {
                'Name': 'InstanceType',
                'Value': instancetype
            },
            {
                'Name': 'GPUNumber',
                'Value': '0'
            }
        ],
    )


def GPU_Memory_Alarm(clientcw, SNSTopic, instanceid, instancetype, ImageId):
    clientcw.put_metric_alarm(
        AlarmName=instanceid + '_Memory_Utilization',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='Memory Usage',
        Namespace='DeepLearningTrain',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        ActionsEnabled=True,
        AlarmActions=[
            SNSTopic
        ],
        AlarmDescription='Alarm when memory utilization exceeds 70%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instanceid
            },
            {
                'Name': 'ImageId',
                'Value': ImageId
            },
            {
                'Name': 'InstanceType',
                'Value': instancetype
            },
            {
                'Name': 'GPUNumber',
                'Value': '0'
            }
        ],
    )

# create cloudfront request alarm


def Cloudfront_Request_Alarm(clientcw, SNSTopic, distributionid):
    clientcw.put_metric_alarm(
        AlarmName=distributionid + '_cloudfront_request',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='Requests',
        Namespace='AWS/CloudFront',
        Period=60,
        Statistic='Sum',
        Threshold=70,
        ActionsEnabled=True,
        AlarmActions=[
            SNSTopic
        ],
        AlarmDescription='Alarm when request number exceed 70',
        Dimensions=[
            {
                'Name': 'DistributionId',
                'Value': distributionid
            },
            {
                'Name': 'Region',
                'Value': 'Global'
            }
        ],
    )

# create cloudfront 4xx error alarm


def Cloudfront_4xx_Alarm(clientcw, SNSTopic, distributionid):
    clientcw.put_metric_alarm(
        AlarmName=distributionid + '_4xx_error',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='4xxErrorRate',
        Namespace='AWS/CloudFront',
        Period=60,
        Statistic='Average',
        Threshold=5,
        ActionsEnabled=True,
        AlarmActions=[
            SNSTopic
        ],
        AlarmDescription='Alarm when 4xx error exceed 5',
        Dimensions=[
            {
                'Name': 'DistributionId',
                'Value': distributionid
            },
            {
                'Name': 'Region',
                'Value': 'Global'
            }
        ],
    )


# create cloudfront 5xx error alarm
def Cloudfront_5xx_Alarm(clientcw, SNSTopic, distributionid):
    clientcw.put_metric_alarm(
        AlarmName=distributionid + '_5xx_error',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='5xxErrorRate',
        Namespace='AWS/CloudFront',
        Period=60,
        Statistic='Average',
        Threshold=5,
        ActionsEnabled=True,
        AlarmActions=[
            SNSTopic
        ],
        AlarmDescription='Alarm when 5xx error exceed 5',
        Dimensions=[
            {
                'Name': 'DistributionId',
                'Value': distributionid
            },
            {
                'Name': 'Region',
                'Value': 'Global'
            }
        ],
    )


# list instance in resource groups
clientrg = boto3.client('resource-groups')

# modify groupname to your resource group name
groupname = 'cloudwatch'

# list resources in resource group
responserg = clientrg.list_group_resources(
    GroupName=groupname
)

# create alarms
clientcw = boto3.client('cloudwatch')

# get ec2 info
clientec2 = boto3.client('ec2')

# send notification
SNSTopic = 'arn:aws:sns:us-east-1:851108988172:SnsMessageProcessorExampleTopic'

for resourcerg in responserg['ResourceIdentifiers']:
    if resourcerg['ResourceType'] == 'AWS::EC2::Instance':
        instanceid = resourcerg['ResourceArn'].split('/')[1]

        # get instance type

        response_ec2 = clientec2.describe_instances(
            InstanceIds=[instanceid],
        )

        instancetype = response_ec2['Reservations'][0]['Instances'][0]['InstanceType']

        imageid = response_ec2['Reservations'][0]['Instances'][0]['ImageId']

        # create CPU utilization alarm
        CPU_Utilization_Alarm(clientcw, SNSTopic, instanceid)

        """# create disk ReadBytes alarm
        Disk_ReadBytes_alarm(clientcw, SNSTopic, instanceid)"""

        # create memory used percentage alarm
        Memory_Used_Alarm(clientcw, SNSTopic, instanceid,
                          instancetype, imageid)

        # create disk used percentage alarm
        Disk_Used_Alarm(clientcw, SNSTopic, instanceid, instancetype, imageid)

        # test whether gpu instance
        if 'p' in instancetype or 'g' in instancetype or 'f' in instancetype:

            # create GPU utilization alarm
            GPU_Utilization_alarm(clientcw, SNSTopic,
                                  instanceid, instancetype, imageid)

            # create  GPU memory alarm
            GPU_Memory_Alarm(clientcw, SNSTopic, instanceid,
                             instancetype, imageid)

    elif resourcerg['ResourceType'] == 'AWS::CloudFront::Distribution':
        distributionid = resourcerg['ResourceArn'].split('/')[1]

        # create cloudfront request alarm
        Cloudfront_Request_Alarm(clientcw, SNSTopic, distributionid)

        # create cloudfront 4xx error alarm
        Cloudfront_4xx_Alarm(clientcw, SNSTopic, distributionid)

        # create cloudfront 5xx error alarm
        Cloudfront_5xx_Alarm(clientcw, SNSTopic, distributionid)
