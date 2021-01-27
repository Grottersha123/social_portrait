import warnings

from dostoevsky.models import FastTextSocialNetworkModel
from dostoevsky.tokenization import RegexTokenizer
from icecream import ic
import numpy as np
import re
from keras.models import load_model
import pickle

from keras.preprocessing.sequence import pad_sequences

# Высота матрицы (максимальное количество слов в твите)
# 26 негативные эмоции
# 28 позитивные эмоции
# 27 негав и позитив
SENTENCE_LENGTH = 27
# Размер словаря
NUM = 100000

warnings.filterwarnings('ignore')



def open_tokenizer(path):
    with open(path, 'rb') as handle:
        tokenizer = pickle.load(handle)
        return tokenizer


def preprocess_text(text):
    text = text.lower().replace("ё", "е")
    #     text = ' '.join([stemmer.stem(word) for word in text.split(' ') if word not in stop_words])
    text = re.sub('#[^\s]+', ' ', text)
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', ' ', text)
    text = re.sub('@[^\s]+', ' ', text)
    text = re.sub('id[^\s]+', ' ', text)
    text = re.sub('[^a-zA-Zа-яА-Я1-9]+', ' ', text)
    text = text.replace('rt', '')
    text = re.sub(' +', ' ', text)
    # text = ' '.join([i for i in text.split(' ') if i not in stop_words])
    return text.strip()

def get_sequences(tokenizer, x, SENTENCE_LENGTH):
    sequences = tokenizer.texts_to_sequences(x)
    return pad_sequences(sequences, maxlen=SENTENCE_LENGTH)


def get_predict_two(text, model, tokenizer):
    if text:
        text = preprocess_text(text)
        x = get_sequences(tokenizer, [text], 26)
        global graph
        with graph.as_default():
            return int(model.predict_classes(x)[0][0]), [round(float(1 - model.predict(x)[0][0]), 3), round(float(model.predict(x)[0][0]), 3)]


def sentiment_analysis(text):
    tokenizer = RegexTokenizer()
    model = FastTextSocialNetworkModel(tokenizer=tokenizer)
    results = model.predict(text, k=3)
    return results



def multiply_array(lst_text):
    result = {'neutral': [], 'speech': [], 'negative': [], 'skip': [], 'positive': []}
    result_2 = {'negative': 0, 'positive': 0}
    lst_text_sentiment = sentiment_analysis(lst_text)
    for index, text in enumerate(lst_text_sentiment):
        if 'negative' in text.keys() and text['negative']> 0.1:
            ic(text['negative'], lst_text[index])
            result_2['negative'] += 1
        if 'positive' in text.keys() and text['positive']> 0.1:
            result_2['positive'] += 1
        for val in text:
            result[val].append(text[val])
    result = {val: round(sum(result[val]) * 100 / len(result[val]), 2) for val in result}
    return result, result_2


def multiply_array_class(lst_text):
    result = {'neutral': [], 'speech': [], 'negative': [], 'skip': [], 'positive': []}
    for text in lst_text:
        res = sentiment_analysis(text)
        for val in res:
            result[val].append(res[val])
    result = {val: round(sum(result[val]) * 100 / len(result[val]),2) for val in result}
    return result

def get_predict_two(text, model, tokenizer):
    if text:
        # text = list(map(preprocess_text, text))
        text = preprocess_text(text)
        x = get_sequences(tokenizer, [text], 26)
        return np.argmax(model.predict(x), axis=-1), [round(float(1 - model.predict(x)[0][0]), 3), round(float(model.predict(x)[0][0]), 3)]

def multiply_array_predict_two(lst_text, model, tokenizer):
    proba_pred = []
    neg, pos = 0
    neg_class, pos_class = 0
    for t in lst_text:
        class_pred, lst_two = get_predict_two(t, model, tokenizer)
        neg += lst_two[0]
        pos += lst_two[1]
        neg_class += class_pred[0]
        pos_class += class_pred[1]
    return [int(neg / len(lst_text) * 100), int(pos / len(lst_text) * 100)], [neg_class, pos_class]
# if __name__ == '__main__':
#     multiply_array(['как все ужасно', "как все прекрасно", "вот жиза блин" , "мне надоело жить вот так вот"])