#!/bin/bash
# 对每个实例执行一次
cd ~

# install pip
sudo yum install -y epel-release
sudo yum install -y python-pip
sudo pip install --upgrade pip

# instll awscli wget
sudo pip install awscli
sudo yum install -y wget

# 安装创建gpu-metrics的gpumon文件，并安装相关依赖
sudo pip install nvidia-ml-py
sudo pip install boto3
wget https://s3.amazonaws.com/aws-bigdata-blog/artifacts/GPUMonitoring/gpumon.py

# install ssm-agent（与gpu指标无关，但先装好可供以后方便统一配置instance）
sudo yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm

# install and start cpu memory agent（注意config.json要替换为自己的路径，后面的/opt路径不用改）
wget https://s3.amazonaws.com/amazoncloudwatch-agent/centos/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm
sudo mv /home/centos/cpu_gpu_agent/config.json /opt/aws/amazon-cloudwatch-agent/bin/
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json -s

# start gpumon
python gpumon.py &