"""
将bert的字典txt文件转换为字典，并存储下来。
"""
import pickle
path_vocab= '../vocab_bert_zh.txt'
# 获取 word to index 词典
def get_w2i(vocab_path = path_vocab):
    w2i = {}
    with open(vocab_path, mode='r',encoding='UTF-8') as f:
        while True:
            text = f.readline()
            if not text:
                break
            text = text.strip()
            if text and len(text) > 0:
                w2i[text] = len(w2i)
    with open('../word2idx_bertdict_zh.pkl', 'wb') as f:
        pickle.dump(w2i,f)
if __name__=="__main__":
    get_w2i(path_vocab)
   #  with open('./word2idx_bertdict.pkl',mode='rb') as f:
   #      word2idx=pickle.load(f)
   #  print([[k,v] for k,v in word2idx.items() if k=="[PAD]"])
    a=0