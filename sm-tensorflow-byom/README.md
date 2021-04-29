# 在SageMaker上使用BYOM部署TensorFlow Serving
#### 本实验使用已经训练好的iris模型，展示带有inference.py和不带inference.py在SageMaker上进行模型部署的过程，并调用Classify API进行推理。实验所需环境：
- 使用cn-northwest-1区域；
- 在SageMaker中创建一台Jupyter Notebook实例，创建过程可参考官方文档：https://docs.aws.amazon.com/sagemaker/latest/dg/howitworks-create-ws.html
- 将tf-byom文件夹打包上传至SageMaker Notebook环境
#### 实验步骤如下：
- 打开Notebook命令行，cd进SageMaker/目录，解压刚刚打包上传的文件；
- 双击打开tf_byom.ipynb笔记本文件，逐步执行notebook中的步骤。
