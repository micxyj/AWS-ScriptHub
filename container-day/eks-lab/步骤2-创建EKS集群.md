# 步骤2: 创建EKS集群

3.1 打开Cloud9终端管理控制台， 使用eksctl 创建EKS集群(操作需要10-15分钟),该命令同时会创建一个使用t3.small的受管节点组。(这里需要check 一下eventengine默认的ec2 limit)

 ```bash
 export CLUSTER_NAME=ekslab
 eksctl create cluster \
       --name=$CLUSTER_NAME \
       --version=1.16 \
       --managed
 ```

 注意：如果报类似于以下的错：
```bash
[ℹ]  deploying stack "eksctl-ekslab-cluster"
[✖]  unexpected status "ROLLBACK_IN_PROGRESS" while waiting for CloudFormation stack "eksctl-ekslab-cluster"
[ℹ]  fetching stack events in attempt to troubleshoot the root cause of the failure
[✖]  AWS::EC2::SubnetRouteTableAssociation/RouteTableAssociationPrivateUSEAST1C: CREATE_FAILED – "Resource creation cancelled"
[✖]  AWS::EC2::Route/PublicSubnetRoute: CREATE_FAILED – "Resource creation cancelled"
[✖]  AWS::EC2::SubnetRouteTableAssociation/RouteTableAssociationPublicUSEAST1E: CREATE_FAILED – "Resource creation cancelled"
[✖]  AWS::EC2::SubnetRouteTableAssociation/RouteTableAssociationPrivateUSEAST1E: CREATE_FAILED – "Resource creation cancelled"
[✖]  AWS::EC2::NatGateway/NATGateway: CREATE_FAILED – "Resource creation cancelled"
[✖]  AWS::EC2::SubnetRouteTableAssociation/RouteTableAssociationPublicUSEAST1C: CREATE_FAILED – "Resource creation cancelled"
[✖]  AWS::EKS::Cluster/ControlPlane: CREATE_FAILED – "Cannot create cluster 'ekslab' because us-east-1e, the targeted availability zone, does not currently have sufficient capacity to support the cluster. Retry and choose from these availability zones: us-east-1a, us-east-1b, us-east-1c, us-east-1d, us-east-1f (Service: AmazonEKS; Status Code: 400; Error Code: UnsupportedAvailabilityZoneException; Request ID: f1cb4458-f727-45ad-929d-514bc9184fa7; Proxy: null)"
[!]  1 error(s) occurred and cluster hasn't been created properly, you may wish to check CloudFormation console
[ℹ]  to cleanup resources, run 'eksctl delete cluster --region=us-east-1 --name=ekslab'
[✖]  waiting for CloudFormation stack "eksctl-ekslab-cluster": ResourceNotReady: failed waiting for successful resource state
Error: failed to create cluster "ekslab"
```

则表示该可用区控制层面实例容量已达上限，请使用错误消息中建议的可用区，先删除之前失败的堆栈，再创建集群：
```bash
eksctl delete cluster --region=us-east-1 --name=ekslab
eksctl create cluster --name=$CLUSTER_NAME --version=1.16 --managed --zones=us-east-1a,us-east-1b
```

  待集群创建完成后，查看EKS集群工作节点
  ```bash
   kubectl cluster-info
   kubectl get node
  ```

3.2 (可选)部署一个测试应用
在Cloud9创建一个nginx.yaml,内容如下

```yaml
cat << EOF >> nginx.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: "service-nginx"
  annotations:
        service.beta.kubernetes.io/aws-load-balancer-type: nlb
spec:
  selector:
    app: nginx
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
EOF

```

 > 部署nginx

 ```bash
#部署
kubectl apply -f nginx.yaml
kubectl get deploy
kubectl get svc

#测试
ELB=$(kubectl get svc service-nginx -o json |  jq -r '.status.loadBalancer.ingress[].hostname')
echo $ELB
curl $ELB
  
 ```

>清除
>

```bash
kubectl delete -f nginx.yaml
```




