# 推荐系统Demo
- 在notebook上将emr设置为backend，参考：https://aws.amazon.com/cn/blogs/machine-learning/build-amazon-sagemaker-notebooks-backed-by-spark-in-amazon-emr/
- 使用user与item交互的数据集结合SparkML训练als模型，作为召回model
- 使用xgboost根据已经处理好的用户画像，商品画像数据训练排序模型
