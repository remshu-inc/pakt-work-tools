"""
Класс для модели выставления оценки за текст
"""
import numpy as np
import pandas as pd
import tensorflow as tf
from matplotlib import pyplot as plt


class MarkModel:
    """
    Класс для модели выставления оценки за текст
    """

    def __init__(self, listlayers=None, modelpath=None):
        self.listlayers = listlayers
        self.create_model(modelpath)

    def create_model(self, modelpath):
        if self.listlayers is None:
            self.model = tf.keras.models.load_model(modelpath)
        else:
            self.model = tf.keras.Sequential()
            for i in range(len(self.listlayers)):
                if i == 0:
                    self.model.add(tf.keras.layers.Dense(self.listlayers[i], input_shape=(10,), activation=tf.nn.relu))
                else:
                    self.model.add(tf.keras.layers.Dense(self.listlayers[i], activation=tf.nn.relu))

    def load_data(self, file_csv):
        df = pd.read_csv(file_csv, sep=',')
        df['gram_norm'] = df['gram'] / df['numtoken']
        df['leks_norm'] = df['leks'] / df['numtoken']
        df['punkt_norm'] = df['punkt'] / df['numtoken']
        df['orpho_norm'] = df['orpho'] / df['numtoken']
        df['diskurs_norm'] = df['diskurs'] / df['numtoken']
        df['skips_norm'] = df['skips'] / df['numtoken']
        df['extra_norm'] = df['extra'] / df['numtoken']
        df['g1_norm'] = df['g1'] / df['numtoken']
        df['g2_norm'] = df['g2'] / df['numtoken']
        df['g3_norm'] = df['g3'] / df['numtoken']
        # df['gram_norm'] = df['gram']/df['numtoken']
        # df['gram_norm1'] = df['gram1']/df['numtoken']
        # df['gram_norm2'] = df['gram2']/df['numtoken']
        # df['gram_norm3'] = df['gram3']/df['numtoken']
        # df['gram_norm4'] = df['gram4']/df['numtoken']
        # df['gram_norm5'] = df['gram5']/df['numtoken']
        # df['gram_norm6'] = df['gram6']/df['numtoken']
        # df['gram_norm7'] = df['gram7']/df['numtoken']
        # df['gram_norm8'] = df['gram8']/df['numtoken']
        # df['gram_norm9'] = df['gram9']/df['numtoken']
        # df['gram_norm10'] = df['gram10']/df['numtoken']
        # df['gram_norm11'] = df['gram11']/df['numtoken']
        # df['gram_norm12'] = df['gram12']/df['numtoken']
        # df['gram_norm13'] = df['gram13']/df['numtoken']
        # df['gram_norm14'] = df['gram14']/df['numtoken']
        # df['leks_norm15'] = df['leks15']/df['numtoken']
        # df['leks_norm16'] = df['leks16']/df['numtoken']
        # df['leks_norm17'] = df['leks17']/df['numtoken']
        # df['leks_norm18'] = df['leks18']/df['numtoken']
        # df['diskurs_norm19'] = df['diskurs19']/df['numtoken']
        # df['diskurs_norm20'] = df['diskurs20']/df['numtoken']
        # df['diskurs_norm21'] = df['diskurs21']/df['numtoken']
        # df['diskurs_norm22'] = df['diskurs22']/df['numtoken']
        self.X = df[df['text_mark'] > 0][
            ['gram_norm', 'leks_norm', 'punkt_norm', 'orpho_norm', 'diskurs_norm', 'skips_norm', 'extra_norm',
             'g1_norm', 'g2_norm', 'g3_norm']]
        self.y = df[df['text_mark'] > 0]['text_mark']
        return 'Объем данных ' + str(self.y.shape[0])

    def fit(self, batch_size=32, num_epochs=60, learning_rate=1e-4, val=0):
        if self.X is None:
            return 0

        self.learning_rate = learning_rate
        self.epochs = num_epochs
        self.batch_size = batch_size
        # optimizer = tf.optimizers.Adam(self.learning_rate)
        self.model.compile(optimizer="Adam", loss="mse", metrics=["mse"])
        self.model.fit(self.X, self.y, validation_split=val, epochs=self.epochs, verbose=1, batch_size=self.batch_size)
        return 1

    def predict(self, data):
        df = pd.DataFrame(data,
                          columns=['gram', 'leks', 'punkt', 'orpho', 'diskurs', 'skips', 'extra', 'g1', 'g2', 'g3',
                                   'numtoken'])
        df['gram_norm'] = df['gram'] / df['numtoken']
        df['leks_norm'] = df['leks'] / df['numtoken']
        df['punkt_norm'] = df['punkt'] / df['numtoken']
        df['orpho_norm'] = df['orpho'] / df['numtoken']
        df['diskurs_norm'] = df['diskurs'] / df['numtoken']
        df['skips_norm'] = df['skips'] / df['numtoken']
        df['extra_norm'] = df['extra'] / df['numtoken']
        df['g1_norm'] = df['g1'] / df['numtoken']
        df['g2_norm'] = df['g2'] / df['numtoken']
        df['g3_norm'] = df['g3'] / df['numtoken']
        df1 = df[['gram_norm', 'leks_norm', 'punkt_norm', 'orpho_norm', 'diskurs_norm', 'skips_norm', 'extra_norm',
                  'g1_norm', 'g2_norm', 'g3_norm']]
        preds = self.model.predict(df1, verbose=0).round()
        preds = [int(x) for y in preds.tolist() for x in y]
        return preds

    def val(self, dataX, dataY):
        # dataX - список списков
        # dataY - список оценок
        preds = self.predict(dataX)
        unique, counts = np.unique(
            abs(np.array(preds, dtype=np.int32).T - np.array(dataY, dtype=np.int32).T).astype(int), return_counts=True)
        plt.bar(unique, counts)
        return ('Сумма разностей оценок равна ' + str(sum(unique)))

    def save_model(self, path):
        self.model.save(path)

    def load_model(self, path):
        self.model = tf.keras.models.load_model(path)
