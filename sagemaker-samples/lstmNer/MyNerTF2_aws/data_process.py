#!-*-coding:utf-8-*-
import pandas as pd
import pickle
import copy
import gc
import config
from ast import literal_eval
import numpy as np
import os


word2idx=config.get_vocab_file_content()
tag2idx=config.get_label_file_conten()



n_chars=config.config["n_chars"]        #字典大小
n_tags=config.config["n_tags"]          #实体种类个数
n_len=config.config["maxlen"]           #输入句子的最大长度
train_rate=config.config["trainrate"]   #数据集中拿来训练的数据比率
n_rows=config.config["n_rows"]          #读取csv训练集行数

# raw_data_file_path_sku=config.raw_data_file_path_sku
# complete_data_save_path=config.complete_data_save_path
train_data_path=config.train_data_path
valid_data_path=config.valid_data_path
test_data_path=config.test_data_path

class Utils(object):
    """
    just some functions applyed for Dataframe transformation
    """

    def __init__(self):
        self.maxlen = n_len
        self.cls_index = word2idx["[CLS]"]
        self.sep_index = word2idx["[SEP]"]
        self.pad_index = word2idx["[PAD]"]

    # df 工具函数
    def split_htlname(self, var):
        """
        e.g.将字符串"上海 希尔顿 大酒店"->转换成list["上海"，"希尔顿"，"大酒店"]
        :param var:
        :return:
        """
        var = var.split(" ")
        return str(var)

    # df工具函数
    def clean_sku_label(self, var):
        """
        将sku的label中的以g_开头的数据，g_去掉
        :param var:
        :return:
        """
        var = literal_eval(var)
        for idx, value in enumerate(var):
            if value.startswith('g_'):
                var[idx] = value.replace('g_', '')
        return str(var)

    # df工具函数
    def trans_namelist(self, var):
        # 将字转换为数字
        ret_list = []
        for char in var:
            if char in word2idx.keys():  # 字典里有这个字
                char_num = word2idx[char]
                ret_list.append(char_num)
            else:  # 如果字典没有这个字
                char_num = word2idx["[UNK]"]  # 就使用[UNK]字符匹配,表示未识别字符
                ret_list.append(char_num)
        return ret_list

    # df工具函数
    def name_list_pad(self, var):

        max_len_allow = self.maxlen
        if len(var) > max_len_allow:  # 先进行截断
            var = var[:max_len_allow]
        if len(var) < max_len_allow:  # 进行padding，在末位padding
            pad_num = max_len_allow - len(var)
            var = var + [self.pad_index] * pad_num
        return var

        # return pad_sequences(maxlen=n_len,sequences=[var],padding="post",value=word2idx["ENDPAD"])

    # df工具函数
    def name_list_pad_bert(self, var):
        """
        Bert的输入数据字(已转换为数字)进行处理，
        处理流程，所有的句子开始添加[CLS]和结尾添加[SEP]
        需要注意的是，于bert而言，要有句首[CLS]、句尾[SEP],与之前BiLstm+Ner不同的是，BERT通常将pading放在句首
        :param var:
        :return:
        """
        max_len_allow = self.maxlen - 2
        if len(var) > max_len_allow:  # 先进行截断
            var = var[:max_len_allow]
        var = [self.cls_index] + var + [self.sep_index]

        if len(var) < max_len_allow:  # 进行padding，在首位padding
            pad_num = max_len_allow - len(var)
            var = [self.pad_index] * pad_num + var
        return var

    # df工具函数
    def name_label_pad(self, var):
        lablen = len(var)
        ret = copy.deepcopy(var)  # 这里copy的原因是var和ret公用一个内存空间(如果直接赋值)
        padnum = self.maxlen - lablen
        if padnum > 0:  # 如果太短，则补齐(补x)
            for x in range(0, padnum):
                ret.append('X')
        elif padnum < 0:  # 如果太短，则截断(最长n_len)
            return ret[0:n_len]
        return ret

    def name_label_pad_bert(self, var):
        ret = copy.deepcopy(var)  # 这里copy的原因是var和ret公用一个内存空间(如果直接赋值)
        max_len_allow = self.maxlen - 2
        if len(var) > max_len_allow:  # 先进行截断
            var = var[:max_len_allow]
        var = ['x'] + var + ['x']  # 对于label，cls和sep也设置为x

        if len(var) < max_len_allow:  # 进行padding，在首位padding
            pad_num = max_len_allow - len(var)
            var = ['x'] * pad_num + var
        return var

    # df工具函数
    def bert_sentence_flag(self, var):
        """
        bert的输入有句子是否是同一个的标志，如0表示上句，1表示下句。
        由于我们的NER任务只有一句话，所以标志位都是0
        :return:
        """
        lenth = len(var)
        return [0] * lenth

    # df工具函数
    def idx2vector(self, idx):
        ret = [0]
        ret = ret * n_tags
        ret[idx] = 1
        return ret

    # df工具函数
    def name_label_pad2num(self, var):
        ret = []
        # tmp_vector=
        for label in var:
            idx = tag2idx[label]
            ret.append(idx) #这一步换keras自带的函数来做吧
            #ret.append(self.idx2vector(idx))
        return ret


utils = Utils()


# print([k for k,v in word2idx.items() if v==5589])
def get_steps(training=True):
    if training == True:
        data_file = config.train_data_path
    else:
        data_file = config.valid_data_path

    data = pd.read_csv(data_file, sep='^', header=None, nrows=config.config["n_rows"])
    return len(data)//config.config["batchsize"]+1

def data_generator(training=True):
    if training==True:
        data_file=config.train_data_path
    else:
        data_file=config.valid_data_path

    data=pd.read_csv(data_file,sep='^',header=None,nrows=config.config["n_rows"])
    data=data.rename(columns={0:"hotel_id",1:"hotel_name",2:"hotel_name_label"})

    data["hotel_name_pad_num"]=data["hotel_name"].apply(literal_eval).apply(utils.trans_namelist).apply(utils.name_list_pad)
    data["hotel_name_label_pad_num"]=data["hotel_name_label"].apply(literal_eval).apply(utils.name_label_pad).apply(utils.name_label_pad2num)
    while True:
        cnt=0
        x=[]
        y=[]
        for idx,row in data.iterrows():
            cnt+=1
            train_data=row["hotel_name_pad_num"]
            train_label=row["hotel_name_label_pad_num"]

            x_tmp=np.array(train_data)
            y_tmp=np.array(train_label)

            x.append(x_tmp)
            y.append(y_tmp)
            if cnt==config.config["batchsize"]:
                x = np.array(x)
                y = np.array(y)
                yield x, y
                x = []
                y = []
                cnt= 0

if __name__=="__main__":
    data_generator(training=True)






