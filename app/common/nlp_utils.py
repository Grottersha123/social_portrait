import re
from functools import reduce

import nltk
from nltk.tokenize import word_tokenize
from pymystem3 import Mystem

nltk.download("stopwords")
from nltk.corpus import stopwords
# TODO hash tag оставляем

mystem = Mystem()
def preprocess_text(text):
    text = 'br'.join(text).lower()
    text = text.replace('ё', 'e')
    patterns = "[0-9!$%&'()*+,./:;<=>?@[\]^_`{|}~—\"\-]+\s+"
    text = text.replace('\n', ' ').replace('\r', '')
    text = re.sub(r'https*\S+', ' ', text)
    # patterns = "[A-Za-z0-9!#$%&'()*+,./:;<=>?@[\]^_`{|}~—\"\-]+"
    text = re.sub(patterns, ' ', text)
    text = re.sub(r'\s+', ' ', text)
    word_tokens = word_tokenize(text)
    stop_words = set(stopwords.words("russian"))
    filtered_text = [word for word in word_tokens if word not in stop_words]
    return 'br'.join(filtered_text) if len(filtered_text > 2) else None

def lemmatization(text, num=100):
    text = text.split('br')
    lol = lambda lst, sz: [lst[i:i + sz] for i in range(0, len(lst), sz)]
    listmerge = lambda s: reduce(lambda d,el: d.extend(el) or d, s, [])
    txtpart = lol(text, num)
    res = []
    for txtp in txtpart:
        alltexts = ' '.join([txt + ' br ' for txt in txtp])
        print(alltexts)
        words = mystem.lemmatize(alltexts)
        print(words)
        res.append(words.split('br'))
    return listmerge(res)
if __name__ == '__main__':
    pass
