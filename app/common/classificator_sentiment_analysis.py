#
import pickle
import re
import warnings

import numpy as np
from dostoevsky.models import FastTextSocialNetworkModel
from dostoevsky.tokenization import RegexTokenizer
from icecream import ic

#
#

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
    text = ' '.join(text).lower().replace("ё", "е")
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
    from keras.preprocessing.sequence import pad_sequences
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



def multiply_array(lst_text,post_dict):
    result = {'neutral': [], 'speech': [], 'negative': [], 'skip': [], 'positive': []}
    result_2 = {'negative': 0, 'positive': 0}
    lst_text_sentiment = sentiment_analysis(lst_text)
    for index, text in enumerate(lst_text_sentiment):
        if 'negative' in text.keys() and text['negative'] > 0.06:
            post_dict[index]['sentiment'] = -1
            # ic(text['negative'], lst_text[index])
            result_2['negative'] += 1
        if 'positive' in text.keys() and text['positive']> 0.06:
            post_dict[index]['sentiment'] = 1
            result_2['positive'] += 1
        if 'neutral' in text.keys() and not ('negative' in text.keys() and text['negative'] > 0.06 or 'positive' in text.keys() and text['positive']> 0.06):
            # ic(text['neutral'], lst_text[index])
            post_dict[index]['sentiment'] = 0
        for val in text:
            result[val].append(text[val])
    result = {val: round(sum(result[val]) * 100 / len(result[val]), 2) for val in result}
    return result, result_2, post_dict


def multiply_array_class(lst_text):
    result = {'neutral': [], 'speech': [], 'negative': [], 'skip': [], 'positive': []}
    for text in lst_text:
        res = sentiment_analysis(text)
        for val in res:
            result[val].append(res[val])
    result = {val: round(sum(result[val]) * 100 / len(result[val]), 2) for val in result}
    return result


def get_predict_two(text, model, tokenizer):
    if text:
        # text = list(map(preprocess_text, text))
        text = preprocess_text(text)
        x = get_sequences(tokenizer, [text], 26)
        return np.argmax(model.predict(x), axis=-1), [round(float(1 - model.predict(x)[0][0]), 3),
                                                      round(float(model.predict(x)[0][0]), 3)]


def multiply_array_predict_two(lst_text, path_model, tokenizer):
    from keras.models import load_model
    neg = 0
    pos = 0
    result_2 = {'negative': 0, 'positive': 0, 'neutral': 0}
    result_sentiment = []
    model = load_model(path_model)
    for t in lst_text:
        class_pred, lst_two = get_predict_two(t, model, tokenizer)
        neg += lst_two[0]
        pos += lst_two[1]
        if class_pred == 0:
            result_sentiment.append(-1)
            result_2['negative'] += 1
        if class_pred == 1:
            result_sentiment.append(1)
            result_2['positive'] += 1
        else:
            result_sentiment.append(0)
            result_2['neutral'] += 1
    return [round(neg / len(lst_text) * 100, 2), round(pos / len(lst_text) * 100, 2)], result_2
# if __name__ == '__main__':
#     multiply_array(['как все ужасно', "как все прекрасно", "вот жиза блин" , "мне надоело жить вот так вот"])