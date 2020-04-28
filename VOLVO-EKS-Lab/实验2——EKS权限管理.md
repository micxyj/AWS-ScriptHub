# 实验二——中国区EKS权限管理

## 前提准备

* 已部署好的EKS集群
* 创建一个S3桶
* IAM AdministratorAccess
* 确定awscli版本（至少为1.18.15）
    * 执行`aws --version`可以看到如下所示：

[Image: image.png]



## Lab 1 - 通过RBAC实现集群访问控制

### 实验步骤


**1. 将iam user map到k8s并进行测试**

* 创建新的namespace与nginx pod

```
`kubectl create ``namespace`` rbac``-``test
kubectl create deploy nginx --image=nginx -n rbac-test
`
```

* 执行`kubectl get all -n rbac-test`查看pod状态，等待pod创建完成

[Image: image.png]

* 创建一个iam用户

```
`aws iam create``-``user ``--``user``-``name rbac``-``user
aws iam create-access-key --user-name rbac-user | tee /tmp/create_output.json
`
```

[Image: image.png]
[Image: image.png]
* 记录aksk，放入`rbacuser_creds.sh`脚本当中，方便执行

```
vim rbacuser_creds.sh

`export`` AWS_SECRET_ACCESS_KEY``=``$``(``jq ``-``r ``.``AccessKey``.``SecretAccessKey`` ``/``tmp``/``create_output``.``json``)
export AWS_ACCESS_KEY_ID=$(jq -r .AccessKey.AccessKeyId /tmp/create_output.json)
`
```

* 创建k8s用户rbac-user，并将它map到之前创建的iam用户

```
vim `aws-auth.yaml`

apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapUsers: |
    - userarn: arn:aws-cn:iam::${ACCOUNT_ID}:user/rbac-user
      username: rbac-user
```

* 执行`kubectl apply -f aws-auth.yaml`
* 执行`kubectl edit -n kube-system configmap/aws-auth`可以看到

[Image: image.png]
* 执行`. rbacuser_creds.sh`（即切换aksk为iam用户rbac-user），再执行`kubectl get pods -n rbac-test`发现报错没有权限

[Image: image.png]**2. 创建role binding**

* 切换回Admin用户

```
`unset AWS_SECRET_ACCESS_KEY
unset AWS_ACCESS_KEY_ID
`
```

* 创建rbac role

```
vim `rbacuser``-``role``.``yaml

kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: rbac-test
  name: pod-reader
rules:
- apiGroups: [""] # "" indicates the core API group
  resources: ["pods"]
  verbs: ["list","get","watch"]
- apiGroups: ["extensions","apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch"]
`
```

* 创建role binding

```
vim `rbacuser``-``role``-``binding``.``yaml

kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: read-pods
  namespace: rbac-test
subjects:
- kind: User
  name: rbac-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
`
```

* 执行kubectl apply

```
`kubectl apply ``-``f rbacuser``-``role``.``yaml``
kubectl apply -f rbacuser-role-binding.yaml
`
```

**3. 重新切换回rbac-user，进行测试**

* 执行`. rbacuser_creds.sh`
* 执行`kubectl get pods -n rbac-test`，发现拥有了可以看到名为rbac-test的namespace下的pod

[Image: image.png]

* 执行`kubectl get pods -n kube-system`但由于没有看kube-system的权限，所以无权查看该namespace（kube-system）下的pod

[Image: image.png]**4. 清理资源**

```
`unset AWS_SECRET_ACCESS_KEY`
`unset AWS_ACCESS_KEY_ID`
`kubectl ``delete`` ``namespace`` rbac``-``test`
`rm rbacuser_creds``.``sh`
`rm rbacuser``-``role``.``yaml`
`rm rbacuser``-``role``-``binding``.``yaml`
`aws iam ``delete``-``access``-``key ``--``user``-``name``=``rbac``-``user ``--``access``-``key``-``id``=``$``(``jq ``-``r ``.``AccessKey``.``AccessKeyId`` ``/``tmp``/``create_output``.``json``)`
`aws iam ``delete``-``user ``--``user``-``name rbac``-``user
rm /tmp/create_output.json`
```



## Lab 2 — 通过IRSA实现pod对AWS服务的调用

### 实验步骤

**1. 为集群创建OIDC身份验证提供商与IRSA**

* 执行`eksctl utils associate-iam-oidc-provider --cluster YOUR_CLUSTER_NAME --approve`

[Image: image.png]
* 查看iam console，发现身份验证提供商已创建完成

[Image: image.png]
* 执行`eksctl create iamserviceaccount --name iam-test --namespace default --cluster YOUR_CLUSTER_NAME --attach-policy-arn arn:aws-cn:iam::aws:policy/AmazonS3ReadOnlyAccess --approve --override-existing-serviceaccounts`创建IRSA，在这里赋予其s3fullaccess权限

[Image: image.png]
* 执行`kubectl get sa`可以找到刚刚新创建的service account

[Image: image.png]

* 执行`kubectl describe sa iam-test`，可以发现其中的annotations对应iam console上的role

[Image: image.png][Image: image.png]**2. 创建用来测试的pod，并赋予其service accout**

* 创建部署pod的yaml文件，可以看到其中的serviceAccountName指向之前创建好的iam-test

```
vim `iam``-``pod``.``yaml

apiVersion: apps/v1
kind: Deployment
metadata:
    name: eks-iam-test
spec:
    replicas: 1
    selector:
        matchLabels:
            app: eks-iam-test
    template:
        metadata:
            labels:
                app: eks-iam-test
        spec:
            serviceAccountName: iam-test
            containers:
            - name: eks-iam-test
              image: sdscello/awscli:latest
              ports:
              - containerPort: 80
`
```

* 执行`kubectl apply -f iam-pod.yaml`，通过`kubectl get pods`查看pod状态，直至ready
* 执行`kubectl exec -it <Pod Name> /bin/bash`进入pod（如果报No OpenIDConnect provider的错可能需要重新登录几次，等待几分钟）
* 执行`aws s3 ls --region cn-northwest-1`可以看到s3桶被列出来

[Image: image.png]
* 执行`aws ec2 describe-instances --region cn-northwest-1`发现没有权限

[Image: image.png]**3. 清理资源**

```
`kubectl ``delete`` ``-``f iam``-``pod``.``yaml`
`eksctl ``delete`` iamserviceaccount ``--``name iam``-``test ``--``namespace`` ``default`` ``--``cluster YOUR_CLUSTER_NAME`
```











