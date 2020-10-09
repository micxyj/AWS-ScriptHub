# 步骤4 配置ALB Ingress Controller

4. 1使用ALB Ingress Controller

参考文档 

https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html

https://aws.amazon.com/cn/blogs/opensource/kubernetes-ingress-aws-alb-ingress-controller/

> 4.2.1 创建ALB Ingress Controller所需要的IAM policy , EKS OIDC provider, service account

> 4.2.1.1 创建EKS OIDC Provider (这个操作每个集群只需要做一次）

```bash
eksctl utils associate-iam-oidc-provider --cluster=${CLUSTER_NAME} --approve --region ${AWS_DEFAULT_REGION}
[ℹ]  eksctl version 0.24.0-rc.0
[ℹ]  using region us-east-1
[ℹ]  will create IAM Open ID Connect provider for cluster "ekslab" in "us-east-1"
[✔]  created IAM Open ID Connect provider for cluster "ekslab" in "us-east-1"
```

> 4.2.1.2 下载并创建ALB入口控制器pod所需的IAM policy
```bash
curl -o iam-policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.8/docs/examples/iam-policy.json
aws iam create-policy --policy-name ALBIngressControllerIAMPolicy \
  --policy-document file://iam-policy.json --region ${AWS_DEFAULT_REGION}

# 记录返回的Plociy ARN
POLICY_NAME=$(aws iam list-policies --query 'Policies[?PolicyName==`ALBIngressControllerIAMPolicy`].Arn' --output text --region ${AWS_DEFAULT_REGION})

```

>4.2.1.3 请使用上述返回的policy ARN创建service account

```bash
eksctl create iamserviceaccount \
       --cluster=${CLUSTER_NAME} \
       --namespace=kube-system \
       --name=alb-ingress-controller \
       --attach-policy-arn=${POLICY_NAME} \
       --override-existing-serviceaccounts \
       --approve

参考输出
[ℹ]  eksctl version 0.24.0-rc.0
[ℹ]  using region us-east-1
[ℹ]  1 iamserviceaccount (kube-system/alb-ingress-controller) was included (based on the include/exclude rules)
[!]  metadata of serviceaccounts that exist in Kubernetes will be updated, as --override-existing-serviceaccounts was set
[ℹ]  1 task: { 2 sequential sub-tasks: { create IAM role for serviceaccount "kube-system/alb-ingress-controller", create serviceaccount "kube-system/alb-ingress-controller" } }
[ℹ]  building iamserviceaccount stack "eksctl-ekslab-addon-iamserviceaccount-kube-system-alb-ingress-controller"
[ℹ]  deploying stack "eksctl-ekslab-addon-iamserviceaccount-kube-system-alb-ingress-controller"
[ℹ]  created serviceaccount "kube-system/alb-ingress-controller"
```



4.3 部署 ALB Ingress Controller

 >4.3.1 创建 ALB Ingress Controller 所需要的RBAC

 ```bash
 kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.8/docs/examples/rbac-role.yaml
 
 ```

>4.2.2 部署 ALB Ingress Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.8/docs/examples/alb-ingress-controller.yaml

 ```


修改alb-ingress-controller.yaml 为以下配置
```bash
  #为alb-ingress-controller.yaml添加以下内容（添加一行集群名称即可）
  kubectl edit deployment.apps/alb-ingress-controller -n kube-system

      spec:
      containers:
      - args:
        - --ingress-class=alb
        - --cluster-name=<步骤2 创建的集群名字>

 
 #确认ALB Ingress Controller是否工作
 kubectl get pods -n kube-system
 ```

```bash
 #参考输出
-------------------------------------------------------------------------------
NAME                                      READY   STATUS    RESTARTS   AGE
alb-ingress-controller-55b5bbcb5b-bc8q9   1/1     Running   0          56s
-------------------------------------------------------------------------------
```


4.3 使用ALB Ingress，部署2048 game 

```bash

kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.8/docs/examples/2048/2048-namespace.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.8/docs/examples/2048/2048-deployment.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.8/docs/examples/2048/2048-service.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.8/docs/examples/2048/2048-ingress.yaml

#几分钟后，验证是否已使用以下命令创建入口资源
kubectl get ingress/2048-ingress -n 2048-game

#输出类似于
-------------------------------------------------------------------------------
NAME           HOSTS   ADDRESS                                                                 PORTS      AGE
2048-ingress   *       example-2048game-2048ingr-6fa0-352729433.region-code.elb.amazonaws.com   80      24h
-------------------------------------------------------------------------------
#在console上观察alb状态，等到active后，在浏览器输入dns名称，看看是否能访问

#清除资源
kubectl delete -f https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.8/docs/examples/2048/2048-ingress.yaml
kubectl delete -f https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.8/docs/examples/2048/2048-service.yaml
kubectl delete -f https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.8/docs/examples/2048/2048-deployment.yaml
kubectl delete -f https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.8/docs/examples/2048/2048-namespace.yaml
```
