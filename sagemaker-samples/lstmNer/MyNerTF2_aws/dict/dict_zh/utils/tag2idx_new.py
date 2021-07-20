from ast import literal_eval
import pickle


# with open('./word2idx.pkl','rb') as f:
#     a=pickle.load(f)
# b=1
savepath='../tag2idx_new.pkl'


file=open("../tag2idx_new.txt")

tmp_line=file.readline()
line=''
while tmp_line:
    line+=tmp_line
    tmp_line=file.readline()
tagdic=literal_eval("{"+line+"}")

#序列化保存
with open(savepath,'wb') as f:
    pickle.dump(tagdic,f)