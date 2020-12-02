# audio2srt操作文档


### 1. 执行audio2srt.py程序


运行脚本：
python3 audio2srt.py <s3桶名> <视频所在路径> <开头截掉的时间min> <视频尾部截掉的时间min> &

如：
python3 audio2srt.py reinventvideotesting 2/ 10 9 &

**注意：**
1、如果存在嵌套路径，须写入所有前缀，并且路径必须以‘/’结尾
![](/Users/xiaoyj/Desktop/AWS-ScriptHub/mediaconvert-audio2srt/images/iamge1.png)
如图所示，若想对目录2下的666子目录中的视频执行操作，运行命令如下：
python3 audio2srt.py reinventvideotesting 2/666/ 10 9 &

2、s3中的文件名及路径不应有中文字符，因为transcribe服务不支持输入中文路径名称

3、截取时间参数必须为整数，单位是分钟，这两个参数必须小于视频总长


### 2. 输出结果示例

执行完脚本后，结果全部在reinvent_clip路径当中（剪切后的视频与srt文件），如下图所示：
![](/Users/xiaoyj/Desktop/AWS-ScriptHub/mediaconvert-audio2srt/images/iamge2.png)

点击进入路径中，其中结果文件的路径名称会和原视频所在路径名称一一对应（包括子目录中的文件）

![](/Users/xiaoyj/Desktop/AWS-ScriptHub/mediaconvert-audio2srt/images/iamge3.png)

![](/Users/xiaoyj/Desktop/AWS-ScriptHub/mediaconvert-audio2srt/images/iamge4.png)

### 3. 提示

为了避免任务执行时间过长造成会话中断的情况，程序会在后台运行，会把任务执行情况打印到名为类似于名为job-logging-2020-11-27-10:36:57.352974.log文件当中（每次任务都会产生一个新文件，按时间排序），可使用两种方式查看日志文件：

* 在命令行输入cat job-logging-2020-11-27-10:36:57.352974.log，会把已经写入的任务状态一次性打印出来
* 在命令行输入tail -f job-logging-2020-11-27-10:36:57.352974.log，会持续监控打印任务状态（使用ctrl + c退出监控）

当日志文件最后一行输出是“Audio to srt task complete”，代表audio2srt任务执行完成（若有文件失败，所有失败的文件会被打印在日志末尾），如下图所示：
![](/Users/xiaoyj/Desktop/AWS-ScriptHub/mediaconvert-audio2srt/images/iamge5.png)


















