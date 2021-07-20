#!-*-coding:utf-8-*-
import pickle
from ast import literal_eval
import os
import argparse


lang='zh'
site='hk'

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

# train_data_path='./data/data'+'_zh/'+'samples/example.train'
# valid_data_path='./data/data'+'_zh/'+'samples/example.dev'
# test_data_path='./data/data'+'_zh/'+'samples/example.test'
# args.train = '/opt/ml/input/data/training'

train_data_path=os.path.join(args.train, 'example.train')
valid_data_path=os.path.join(args.train, 'example.dev')
test_data_path=os.path.join(args.train, 'example.test')

label_file='./dict/dict_'+lang+'/label'+'_zh-'+site+'.txt'
vocab_file='./dict/dict_'+lang+'/vocab'+'_zh-'+site+'.txt'

def  get_vocab_file_content():
    with open(vocab_file,mode='r',encoding='UTF-8') as f:
        w2i={}
        while True:
            text=f.readline()
            if not text:
                break
            text=text.strip()
            if text and len(text)>0:
                w2i[text]=len(w2i)
    return w2i

def get_label_file_conten():
    file = open(label_file)
    tmp_line=file.readline()
    tag2idx = {}
    while tmp_line:
        tmp_line=tmp_line.replace('\n','')
        tmp=tmp_line.split('\t')
        tag2idx[tmp[1]]=int(tmp[0])
        tmp_line = file.readline()
    return tag2idx


config={
    "batchsize":32,
    "epoch":40,
    "maxlen":30,                #输入短句的最大长度
    "embedding_dim":100,             #词嵌入长度
    "hidden_num":200,           #LSTM隐藏层个数
    "trainrate":0.9,            #数据集中训练数据比例
    "n_rows":100,              #该参数为读取训练集csv行数，如果是读取全部数据，请将其设置为None
    "mask":False,
    "n_tags":len(get_label_file_conten()),       #标签个数
    "n_chars":len(get_vocab_file_content())   #字典大小(字的个数)
}
if __name__=="__main__":
    tag=get_label_file_conten()
    #word2idx=get_vocab_file_content()
