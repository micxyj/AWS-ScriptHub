# 步骤5 部署官方的Kubernetes dashboard

5.1 下载配置文件

```bash
#2.0.0rc3
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0-rc3/aio/deploy/recommended.yaml

kubectl get pods -n kube-system
kubectl get services -n kube-system

#通过kubectl proxy 进行访问
#由于我们部署的EKS cluster是private cluster，所以我们需要通过 proxy. Kube-proxy进行访问Dashboard
kubectl proxy --port=8080 --address='0.0.0.0' --disable-filter=true &

#登录
#在cloud9里面选择tools -> preview -> preview run application

#在URL的结尾附加：/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/，然后按回车

#获取登录的token
aws eks get-token --cluster-name ${CLUSTER_NAME} --region ${AWS_DEFAULT_REGION} | jq -r '.status.token'

选择 Dashbaord 登录页面的 “Token” 单选按钮，复制上述命令的输出，粘贴，之后点击 Sign In。

#资源清理
pkill -f 'kubectl proxy --port=8080'

#删除dashboard
kubectl delete -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0-rc3/aio/deploy/recommended.yaml

```