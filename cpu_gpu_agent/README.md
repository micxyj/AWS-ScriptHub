# Get Start
#### Description
部署aws cloudwatch的cpu agent与gpu agent，并创建相关指标的警报
#### Enviroment
1. 请先安装好AWS CLI并配置好您的AK/SK或ROLE。
2. 请安装好python 3.7 版本
3. 请使用pip安装好boto3
#### Installation
- 在本地执行genetrate_iam_role.py文件（需配置aksk），该步骤确保为每个ec2实例与具有相应权限的角色绑定，需在代码中替换为您实例的标签；
```python3 genetrate_iam_role.py```
-  由于CentOS没有预装ssm agent，该步骤需要登陆每一台实例执行；
    1. 将setup_agent.sh与config.json文件上传至ec2实例；
    2. 注意将setup_agent.sh代码中的config.json文件目录替换为自己的路径；
    3. 执行脚本
    ```chmod 777 setup_agent.sh```
    ```./setup_agent.sh```

! 如需为您的CloudFront创建Resource group，并创建Alarm，请将您的Region修改为us-east-1。

- 使用createEC2Alarm.py
使用时，您需要：
    1. 将groupname = 'gpu-cloudwatch' 中的gpu-cloudwatch换成您需要配置的资源组名称。
    2. 将SNSTopic = 'arn:aws:sns:ap-south-1:323109937753:SnsMessageProcessorExampleTopic'中的arn:aws:sns:ap-south-1:323109937753:SnsMessageProcessorExampleTopic换为您需要通知的SNS Topic的arn。
    3. 您可以根据需要替换function中的告警阈值。也可以以此为模板添加您需要的监控指标告警。
    4. ```python3 createEC2Alarm.py```
