from tf2crf import CRF
from ast import literal_eval
from data_process import Utils
import tensorflow as tf
import pandas as pd
import numpy as np
import config

utils =Utils()

from tf2crf import CRF
def load_my_model(file_path):
    my_object={"loss":CRF.loss,"accuracy":CRF.accuracy}
    loaded_model = tf.keras.models.load_model(file_path,custom_objects=my_object)
    return loaded_model
def test_data_generator():
    global test_data_path
    data_file=test_data_path

    data=pd.read_csv(data_file,sep='^',header=None,nrows=None)
    data=data.rename(columns={0:"hotel_id",1:"hotel_name",2:"hotel_name_label"})

    data["hotel_name_pad_num"]=data["hotel_name"].apply(literal_eval).apply(utils.trans_namelist).apply(utils.name_list_pad)
    data["hotel_name_label_pad_num"]=data["hotel_name_label"].apply(literal_eval).apply(utils.name_label_pad).apply(utils.name_label_pad2num)

    for idx,row in data.iterrows():
        train_data=row["hotel_name_pad_num"]
        train_label=row["hotel_name_label_pad_num"]

        x=np.array(train_data)
        y=np.array(train_label)
        yield x, y
def get_test_data():
    global test_data_path
    data_file=test_data_path

    data=pd.read_csv(data_file,sep='^',header=None,nrows=None)
    data=data.rename(columns={0:"hotel_id",1:"hotel_name",2:"hotel_name_label"})

    data["hotel_name_pad_num"]=data["hotel_name"].apply(literal_eval).apply(utils.trans_namelist).apply(utils.name_list_pad)
    data["hotel_name_label_pad_num"]=data["hotel_name_label"].apply(literal_eval).apply(utils.name_label_pad).apply(utils.name_label_pad2num)
    x=[]
    y=[]

    for idx,row in data.iterrows():
        train_data=row["hotel_name_pad_num"]
        train_label=row["hotel_name_label_pad_num"]

        x.append(np.array(train_data))
        y.append(train_label)

    return np.array(x),np.array(y)


def get_eval_data():
    """
    构建数据管道有多种方法，这里使用生成器构建
    其实在github上那个项目，是使用ndarry构建的，一次性读入了内存
    reference：https://github.com/lyhue1991/eat_tensorflow2_in_30_days/blob/master/5-1%2C%E6%95%B0%E6%8D%AE%E7%AE%A1%E9%81%93Dataset.md
    :param filepath:  val_data path
    :return:
    """
    data=tf.data.Dataset.from_generator(generator=test_data_generator,output_types=(tf.int32,tf.int32))
    return data
def get_acc_by_me(model):
    t = 0
    f = 0
    for s, l in test_data_generator():
        # print(s.tolist())
        pre = model.predict([s.tolist()])
        # print(pre)
        # print("==============")
        # print(l)
        for num in range(len(l)):
            if (l[num] == 17):
                break

            elif l[num] == pre[0][num]:
                t += 1
            else:
                f += 1
    print(float(t) / (f + t))
    return float(t) / (f + t)
if __name__=="__main__":
    model_path = "ModelWeights/model_zh/BiLSTM"
    test_data_path=config.test_data_path
    model = load_my_model(model_path)

    #get_acc_by_me(model)

    # #print(data[0])
    # data=get_eval_data()
    # x=data.map(lambda x,y:tf.expand_dims(x,axis=0))
    # y= data.map(lambda x, y: tf.expand_dims(y, axis=0))
    # model.evaluate(x=x,y_pred=y)