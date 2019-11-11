import boto3
import time


# define service and role name
client_iam = boto3.client('iam')
client_ec2 = boto3.client('ec2')
role_name = 'monitor-role'


if __name__ == '__main__':

    # create iam role
    with open('Trust-Policy.json', 'r') as f_obj:
        policy = f_obj.read()
    client_iam.create_role(RoleName=role_name,
                           AssumeRolePolicyDocument=policy)
    with open('policy-file.json', 'r') as f_obj:
        policy = f_obj.read()
    client_iam.put_role_policy(
        RoleName=role_name, PolicyName='Permissions-Policy-For-Ec2', PolicyDocument=policy)
    res = client_iam.create_instance_profile(InstanceProfileName='Monitoring')
    instance_profile_arn = res.get('InstanceProfile').get('Arn')
    client_iam.add_role_to_instance_profile(
        RoleName=role_name, InstanceProfileName='Monitoring')

    # waiting policy attach to role
    print("Waiting policy attach to role")
    time.sleep(10)
    print("Done")

    # attach role to every instance（dev和gpu表示标签的key和value，需更换为自己的标签和值）
    res = client_ec2.describe_instances(
        Filters=[{'Name': 'tag:dev', 'Values': ['gpu']}])
    instance_lst = []
    for i in res.get('Reservations'):
        for j in i["Instances"]:
            instance_lst.append(j["InstanceId"])
    for i in instance_lst:
        client_ec2.associate_iam_instance_profile(
            IamInstanceProfile={'Name': 'Monitoring', 'Arn': instance_profile_arn}, InstanceId=i)
