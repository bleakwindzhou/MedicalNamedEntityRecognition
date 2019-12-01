# -*- coding:utf-8 -*-
import numpy as np
from gensim.models import word2vec
import multiprocessing
import torch.nn.functional as F
import os


def w2v_train(segment_dir = './data/segment/oil.txt', word2vec_path = './models/w2v/oil.model'):
    sentences = word2vec.PathLineSentences(segment_dir)
    model2 = train_wordVectors(sentences, embedding_size=300, window=5, min_count=1)
    save_wordVectors(model2, word2vec_path)


def load_wordVectors(word2vec_path):
    w2vModel = word2vec.Word2Vec.load(word2vec_path)
    return w2vModel

def train_wordVectors(sentences, embedding_size = 300, window = 5, min_count = 5):
    w2vModel = word2vec.Word2Vec(sentences, size=embedding_size, window=window, min_count=min_count,workers=multiprocessing.cpu_count(),iter=10,hs=1)
    return w2vModel

def save_wordVectors(w2vModel,word2vec_path):
    w2vModel.save(word2vec_path)

#w2v_train('name_data_w2v.txt', '0101.bin')
#model_w2v = load_wordVectors('0101.bin')
#print(len(model_w2v['']))
