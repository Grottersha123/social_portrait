import unittest

from icecream import ic

from classificator_sentiment_analysis import multiply_array, get_predict_two, open_tokenizer, multiply_array_predict_two
from keras.models import load_model

class MyTestCase(unittest.TestCase):
    def test_something(self):
        res = multiply_array(['я люблю тебя!', 'глупый кот', 'ты идиот!!'])
        self.assertIsInstance(res, dict)

class MyTestLstm(unittest.TestCase):
    def setUp(self):
        self.path = r'..\models\1-lstms-dim200Acc0.78.hdf5'
        self.model = load_model(r'..\models\1-lstms-dim200Acc0.78.hdf5')
        self.tokenizer =open_tokenizer( r'..\models\tokenizer.pickle')
    def test_two_classificator(self):
        predictions = get_predict_two('Я радуюсь всему что происходит в этом мире', self.model, self.tokenizer)
        ic(predictions)
        predictions = get_predict_two('грустно не грустно и все грустно', self.model, self.tokenizer)
        ic(predictions)
    def test_multy_two_prediction(self):
            predictions = multiply_array_predict_two(['Я радуюсь всему что происходит в этом мире', 'Иногда я грущу и мне плохо'], self.path, self.tokenizer)
            ic(predictions)
            # predictions = get_predict_two('грустно не грустно и все грустно', self.model, self.tokenizer)
            # ic(predictions)


if __name__ == '__main__':
    unittest.main()
