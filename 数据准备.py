# -*- coding: utf-8 -*-

import pymssql
import pandas as pd
from lxml import etree
import requests
import json
from function import *
import pickle
import decimal
import time
from w2v import *

def index_of_str(seq, sub_seq):
    seq = ''.join(seq)
    index=[]
    n1=len(seq)
    n2=len(sub_seq)
    for i in range(n1-n2+1):
        if seq[i:i+n2]==sub_seq:
            index.append(i)
    return index
SubCategoryCode = '0101'
sql_ZIdatabase = sql_find('ZI_DataBase', False)
sql_ZIdatabase.cursor.execute(f"select SubTitle from VW_Relation_Property where ispeijian = '1' and SubCategoryCode = '{SubCategoryCode}'")
subtitle_lyst = [str(f"'{x[0]}'") for x in sql_ZIdatabase.cursor.fetchall()]
subtitle_lyst = ','.join(subtitle_lyst)
sql_ZIdatabase.cursor.execute(f"select ProductName,参数名称,参数值 from vw_productValue where SubCategoryCode = '{SubCategoryCode}' and 参数名称 in ({subtitle_lyst}) and ProductName not like '%wrong'")
data = sql_ZIdatabase.cursor.fetchall()
data = pd.DataFrame(data,columns=[tuple[0] for tuple in sql_ZIdatabase.cursor.description])
################################################################
f = open('name_data.txt','w',encoding='utf-8')
for name in set(data['ProductName'].tolist()):
    f.write(f'{name}\n')
f.close()
###############################################################
data = data.drop(['ProductName'], axis=1)
data = data.drop_duplicates()
data.to_excel(f'{SubCategoryCode}_train_data.xlsx')
################################################################
f = open('name_data.txt','r',encoding='utf-8')
g = open('name_data_w2v.txt','w',encoding='utf-8')
for line in f:
    line = line.replace(' ','')
    line = ' '.join(list(line))
    g.write(line)
f.close()
g.close()
################################################################
f = open('name_data.txt','r',encoding='utf-8')
g = open(f'{SubCategoryCode}_vec_300.txt','w',encoding='utf-8')
w2v_train('name_data_w2v.txt', f'{SubCategoryCode}.bin')
model_w2v = load_wordVectors(f'{SubCategoryCode}.bin')
word_data = []
for line in f:
    line = line.replace(' ','')
    line = list(line)
    for word in line:
        word_data.append(word)
word_data = set(word_data)
word_data.remove('\n')
for word in word_data:
    g.write(f"{word} {' '.join([str(x) for x in model_w2v[word].tolist()])}\n")
g.close()
f.close()
################################################################
f = open('name_data.txt','r',encoding='utf-8')
g = open(f'{SubCategoryCode}_train.txt','w',encoding='utf-8')
model_w2v = load_wordVectors('0101.bin')
word_data = []     #字序列
m = 0
for line in f:
    m += 1
    line = line.replace(' ','')
    line = list(line)
    line.append(';')
    for word in line:
        if word != '\n':
            word_data.append(word)
sign_data = []     #标记序列 
for i in range(len(word_data)):
    sign_data.append('O')
table = pd.read_excel(f'{SubCategoryCode}_train_data.xlsx')
o = 0
for param_name, param_value in zip(table['参数名称'],table['参数值']):
    print(o,end = '\r')
    o += 1
    param_str_len = len(param_value)
    if param_str_len < 2:
        continue
    param_value = param_value.upper()
    sign_list = index_of_str(word_data, param_value)
    for n in sign_list:
        sign_data[n] = f'{param_name}-B'
        for j in range(param_str_len-1):
            sign_data[n+j+1] = f'{param_name}-I'
for word,sign in zip(word_data,sign_data):
    g.write(f'{word}\t{sign}\n')
f.close()
g.close()

#将生成的"子类编码_vec_300.txt"放入model作为词向量，将生成的"子类编码_train.txt"放入data作为训练集。