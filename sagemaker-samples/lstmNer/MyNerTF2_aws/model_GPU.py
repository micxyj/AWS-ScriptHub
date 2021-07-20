#!-*-coding:utf-8-*-
#import tensorflow as tf
#import tensorflow_addons as tf_ad
import os
os.system("pip3 install tensorflow_addons==0.11.2")

from crf21 import CRF
import tensorflow as tf
from tensorflow.keras.layers import Input,Dense,Embedding,Bidirectional,LSTM,TimeDistributed,GRU
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint
import config,data_process
import numpy as np
import argparse


os.environ['CUDA_VISIBLE_DEVICES'] = "0,1"
gpus = tf.config.list_physical_devices(device_type="GPU")
print(gpus)
print('='*20)
print(tf.__version__)
print('='*20)

def _parse_args():

    parser = argparse.ArgumentParser()

    # Data, model, and output directories
    # model_dir is always passed in from SageMaker. By default this is a S3 path under the default bucket.
    parser.add_argument('--model_dir', type=str)
    parser.add_argument('--sm-model-dir', type=str,
                        default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAINING'))

    return parser.parse_known_args()

args, unknown = _parse_args()

if gpus:
     gpu = gpus[0:2]  #如果有多个GPU，仅使用第0到1 GPU
     for g in gpu:
        tf.config.experimental.set_memory_growth(g, True)     # 设置GPU显存用量按需使用,注意，必须使用for循环一个个设置
     # 或者也可以设置GPU显存为固定使用量(例如：4G)
     # tf.config.experimental.set_virtual_device_configuration(gpu0,
     #    [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=4096)])
     tf.config.set_visible_devices(gpu, device_type="GPU")

class BiLSTMCRF(object):
    def __init__(self):
        self.n_chars=config.config["n_chars"]
        self.embedding_dim=config.config["embedding_dim"]
        self.max_len=config.config["maxlen"]
        self.n_tags=config.config["n_tags"]
        self.hidden_dim=config.config["hidden_num"]
        self.mask=config.config["mask"]
        if self.mask:
            # self.best_model_path = './ModelWeights/model_' + config.lang + '/BiLSTM_best_'+'mask'
            # self.last_model_path = './ModelWeights/model_' + config.lang + '/BiLSTM_last_'+'mask'
            self.best_model_path = args.model_dir + '/ModelWeights/model_' + config.lang + '/BiLSTM_best_'+'mask'
            self.last_model_path = args.model_dir + '/ModelWeights/model_' + config.lang + '/BiLSTM_last_'+'mask'
        else:
            # self.best_model_path = './ModelWeights/model_' + config.lang + '/BiLSTM_best_no_mask'
            # self.last_model_path = './ModelWeights/model_' + config.lang + '/BiLSTM_last_no_mask'
            self.best_model_path = args.model_dir + '/ModelWeights/model_' + config.lang + '/BiLSTM_best_no_mask'
            self.last_model_path = args.model_dir + '/ModelWeights/model_' + config.lang + '/BiLSTM_last_no_mask'


    def create_model(self):
        strategy = tf.distribute.MirroredStrategy(devices=["/gpu:0", "/gpu:1"])

        config.config["batchsize"]=strategy.num_replicas_in_sync*config.config["batchsize"]

        with strategy.scope():
            input=Input(shape=(self.max_len,))
            output=Embedding(input_dim=self.n_chars,output_dim=self.embedding_dim,input_length=self.max_len,mask_zero=self.mask)(input)
            output=Bidirectional(LSTM(units=self.hidden_dim,return_sequences=True))(output)
            output=TimeDistributed(Dense(self.n_tags,activation=None))(output)

            crf=CRF(dtype='float32')
            output=crf(output)
            model=Model(input,output)
            model.compile(optimizer='adam', loss=crf.loss, metrics=[crf.accuracy])
        return model

    def model_train(self):
        self.model=self.create_model()

        # checkpointer = ModelCheckpoint(filepath=self.best_model_path, monitor='val_accuracy', save_best_only=True, mode='max')
        checkpointer = ModelCheckpoint(filepath='/opt/ml/checkpoints', monitor='val_accuracy', save_best_only=True, mode='max')
        self.model.fit_generator(generator=data_process.data_generator(training=True),
                            epochs=config.config["epoch"],
                            steps_per_epoch=data_process.get_steps(training=True),
                            validation_data=data_process.data_generator(training=False),
                            validation_steps=data_process.get_steps(training=False),
                            callbacks=[checkpointer]
                            )
        # args.sm_model_dir = '/opt/ml/model'
        self.model.save(os.path.join(args.sm_model_dir,'000000001'))

def my_load_model(file_path):
    my_object={"loss":CRF.loss,"accuracy":CRF.accuracy}
    model_loaded = tf.keras.models.load_model(file_path,custom_objects=my_object)
    return model_loaded
if __name__=="__main__":
    mymodel=BiLSTMCRF()
    mymodel.model_train()


