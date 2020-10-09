# 步骤6 配置使用EBS CSI

6.1 创建所需要的IAM policy , EKS OIDC provider, service account

6.1.1 创建所需要的IAM policy

```bash
#下载csi driver
git clone https://github.com/kubernetes-sigs/aws-ebs-csi-driver.git

#下载policy
curl -sSL -o ebs-csi-policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-ebs-csi-driver/v0.4.0/docs/example-iam-policy.json

#创建ebs CSI 需要的IAM策略,如果报错请检查策略是否已经存在
aws iam create-policy \
    --policy-name Amazon_EBS_CSI_Driver \
    --policy-document file://ebs-csi-policy.json \
    --region ${AWS_DEFAULT_REGION}
        

#返回示例,请记录返回的Plociy ARN
POLICY_NAME=$(aws iam list-policies --query 'Policies[?PolicyName==`Amazon_EBS_CSI_Driver`].Arn' --output text --region ${AWS_DEFAULT_REGION})
```

> 6.1.2 获取EKS工作节点的IAM role

```bash
# 注意这一步如果是多个nodegroup就会有多个role
kubectl -n kube-system describe configmap aws-auth

# 单个节点组
ROLE_NAME=<Role-name-in-above-output>
aws iam attach-role-policy --policy-arn ${POLICY_NAME} \
    --role-name ${ROLE_NAME} --region ${AWS_DEFAULT_REGION}


```

> 6.1.3 部署EBS CSI 驱动到eks 集群

[官方文档 https://docs.aws.amazon.com/zh_cn/eks/latest/userguide/ebs-csi.html](https://docs.aws.amazon.com/zh_cn/eks/latest/userguide/ebs-csi.html)

```bash


kubectl apply -k aws-ebs-csi-driver/deploy/kubernetes/overlays/stable

#验证部署是否正确 
kubectl get pods -n kube-system | grep csi
#参考输出,每个节点会各自部署ebs-csi-controller和ebs-csi-node 
NAME                                      READY   STATUS              RESTARTS   AGE
ebs-csi-controller-78bc69cb98-cddl6       4/4     Running   0          4m5s
ebs-csi-controller-78bc69cb98-ng6nx       4/4     Running   0          4m5s
ebs-csi-node-l4m88                        3/3     Running   0          4m5s
ebs-csi-node-z86xc                        3/3     Running   0          4m5s
```

6.2 部署动态卷实例应用

```bash
#specs中定义了名为app的pod，pod中定义了pvc的存储需求，拿到卷后会挂载到/data路径下，并且每隔5s向/data路径下out.txt文本文件的添加数据
kubectl apply -f aws-ebs-csi-driver/examples/kubernetes/dynamic-provisioning/specs/

#查看storageclass
kubectl describe storageclass ebs-sc

#查看示例app状态
kubectl get pods --watch

kubectl get pv
PV_NAME=$(kubectl get pv -o json | jq -r '.items[0].metadata.name')
kubectl describe persistentvolumes ${PV_NAME}

#查看数据是否写成功
kubectl exec -it app --  tail -f  /data/out.txt
# Thu Mar 5 14:19:43 UTC 2020
# Thu Mar 5 14:19:48 UTC 2020

#删除示例程序
kubectl delete -f aws-ebs-csi-driver/examples/kubernetes/dynamic-provisioning/specs/
```