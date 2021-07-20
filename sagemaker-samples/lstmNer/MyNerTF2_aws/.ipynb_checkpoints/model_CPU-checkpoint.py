#!-*-coding:utf-8-*-
#import tensorflow as tf
#import tensorflow_addons as tf_ad
import os

os.system("pip3 install tensorflow_addons==0.9.1")
os.system("pip3 install tf2crf")




from tf2crf import CRF
#from crf21 import CRF
import tensorflow as tf
from tensorflow.keras.layers import Input,Dense,Embedding,Bidirectional,LSTM,TimeDistributed,GRU
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint
import config,data_process
import numpy as np
import argparse

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



class BiLSTMCRF(object):
    def __init__(self):
        self.n_chars=config.config["n_chars"]
        self.embedding_dim=config.config["embedding_dim"]
        self.max_len=config.config["maxlen"]
        self.n_tags=config.config["n_tags"]
        self.hidden_dim=config.config["hidden_num"]
        # self.model_path = './ModelWeights/model_' + config.lang + '/BiLSTM'
        self.model_path = args.model_dir
        self.mask=config.config["mask"]
    def create_model(self):


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

        # checkpointer = ModelCheckpoint(filepath='ModelWeights/model_zh/BiLSTM', monitor='val_accuracy', save_best_only=True, mode='max')
        
        checkpointer = ModelCheckpoint(filepath=args.model_dir, monitor='val_accuracy', save_best_only=True, mode='max')
        
        self.model.fit_generator(generator=data_process.data_generator(training=True),
                            epochs=config.config["epoch"],
                            steps_per_epoch=data_process.get_steps(training=True),
                            validation_data=data_process.data_generator(training=False),
                            validation_steps=data_process.get_steps(training=False),
                            callbacks=[checkpointer]
                            )
        self.model.save(os.path.join(args.sm_model_dir,'000000001'))

def my_load_model(file_path):
    my_object={"loss":CRF.loss,"accuracy":CRF.accuracy}
    model_loaded = tf.keras.models.load_model(file_path,custom_objects=my_object)
    return model_loaded
if __name__=="__main__":
    mymodel=BiLSTMCRF()
    mymodel.model_train()


