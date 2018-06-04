# -*- coding: utf-8 -*-

from base_answering_machine import BaseAnsweringMachine
from simple_dialog_session_factory import SimpleDialogSessionFactory

from keras.layers import Embedding
from keras.models import model_from_json
from keras.layers.merge import concatenate, add, multiply
from keras.layers import Lambda
from keras import backend as K
from keras.layers import Conv1D, GlobalMaxPooling1D, GlobalAveragePooling1D, MaxPooling1D, AveragePooling1D
from keras.models import Model
from keras.layers.core import Activation, RepeatVector, Dense, Masking
from keras.layers.wrappers import Bidirectional
from keras.layers import Input
import keras.callbacks
from keras.layers import recurrent
from keras.callbacks import ModelCheckpoint, EarlyStopping
import xgboost
from scipy.sparse import lil_matrix
import json
import os
import pickle
import gensim
import numpy as np
import logging


class WordEmbeddings(object):
    """
    Загрузка и работа с векторными моделями слов.
    """

    def __init__(self):
        self.wc2v = None
        self.wc2v_dims = None
        self.w2v = dict()
        self.w2v_dims = dict()

    def load_wc2v_model(self, wc2v_path):
        logging.info(u'Loading wordchar2vector from {}'.format(wc2v_path))
        self.wc2v = gensim.models.KeyedVectors.load_word2vec_format(wc2v_path, binary=False)
        self.wc2v_dims = len(self.wc2v.syn0[0])

    def load_w2v_model(self, w2v_path):
        logging.info(u'Loading word2vector from {}'.format(w2v_path))
        w2v = gensim.models.KeyedVectors.load_word2vec_format(w2v_path, binary=not w2v_path.endswith('.txt'))
        self.w2v[w2v_path] = w2v
        self.w2v_dims[w2v_path] = len(w2v.syn0[0])

    def get_dims(self):
        return self.wc2v_dims+self.w2v_dims

    def vectorize_words(self, w2v_path, words, X_batch, irow):
        w2v = self.w2v[w2v_path]
        w2v_dims = self.w2v_dims[w2v_path]
        for iword, word in enumerate(words):
            if word in w2v:
                X_batch[irow, iword, :w2v_dims] = w2v[word]
            if word in self.wc2v:
                X_batch[irow, iword, w2v_dims:] = self.wc2v[word]
