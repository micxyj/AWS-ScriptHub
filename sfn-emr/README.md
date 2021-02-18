# 使用Step Function调度EMR任务

## Workflow

- 创建EMR集群
- 并行提交两个EMR Step任务
- 当任务失败会进行重试
- 当重试失败后会发送SNS消息，然后终止集群
- 任务执行完成，终止集群

注：在Step Function中执行Parallel并行任务，如果不对分支进行异常处理，当一个分支执行失败，会导致其他分支无法正常执行。 
