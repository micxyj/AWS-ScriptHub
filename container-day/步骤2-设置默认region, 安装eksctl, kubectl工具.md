# 步骤2: 设置默认region, 安装eksctl, kubectl工具

我们将在步骤1创建的AWS Cloud9 环境里面安装eksctl,kubectl。进入Cloud9编辑器环境后，在终端中输入以下命令,进行安装。

```bash
#设置默认region
export AWS_DEFAULT_REGION=us-east-1
echo "export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}" >> ~/.bashrc

#eksctl 版本> v0.20.0
curl -L "https://github.com/weaveworks/eksctl/releases/download/latest_release/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C .
sudo mv ./eksctl /usr/local/bin

#kubectl >v1.16.0
curl -LO --silent https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
chmod 775 ./kubectl
sudo mv ./kubectl /usr/local/bin

#安装jq
 sudo yum install -y jq

```

>检查工具的版本 eksctl (版本>=0.20.0), kubectl(版本>=1.16)

```bash
eksctl version
kubectl version
```

