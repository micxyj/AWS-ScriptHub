# EMR Flink on yarn使用手册

## Flink的两种运行方式

### 1. Standalone

一般自建Flink都会考虑该使用方法，以守护进程的方式运行在后台，web ui打开在8081端口，并且在启动Flink时需要定义好所需的资源。

### 2. Flink on yarn

目前最常用的一种方式，总结下来有两点好处：（1）相对于standalone提高集群资源利用率——启动任务的时候才消耗yarn分配的资源；（2）一套集群，可以执行MR任务，Spark任务，Flink任务等。Flink on yarn也有两种使用方式，分别是：

* 单集群模式

[Image: image.png]

* 多集群模式

[Image: image.png]
### 3. EMR Flink使用方法


在EMR上目前只有Flink on yarn的运行方式，如果要使用standalone需要自己通过emr bootstrap的方式安装flink（和自建差异不大）。

**Flink 1.10之前的版本（不包含）**

对于Flink 1.10之前的版本（不包含）可按照aws官方文档上的指导步骤进行：https://docs.aws.amazon.com/zh_cn/emr/latest/ReleaseGuide/flink-create-cluster.html

**Flink 1.10之后的版本**

1. 单集群模式

* ssh进入到emr master节点，启动flink yarn session

```
cd /usr/lib/flink/
bin/yarn-session.sh -jm 1024m -tm 1024m
```

* 在EMR界面上打开yarn资源管理界面

[Image: image.png]
[Image: image.png]
* 回到命令行提交任务，这里以wordcount为例

```
bin/flink run ./examples/batch/WordCount.jar --input s3://your_s3_file_path
```

* 提交完任务后，在yarn资源界面上点击flink web ui，可以看到已新增了一个flink任务

[Image: image.png][Image: image.png]
2. 多集群模式

* ssh进入到master节点

```
cd /usr/lib/flink/
bin/flink run -m yarn-cluster -yjm 1024 -ytm 1024 ./examples/batch/WordCount.jar \
`--output s3://xiaoyj/emr/flink_result.txt`
```

* 每个job对应一个flink集群，任务执行完成后，s3上有对应的输出

[Image: image.png][Image: image.png]
* 多集群模式下flink run命令详细用法

[Image: image.png]
### 4. flink2s3打包及运行

- mvn clean package -Pbuild-jar
- bin/flink run -m yarn-cluster -yjm 1024 -ytm 1024 -c org.myorg.quickstart.StreamingJob quickstart-0.1.jar










