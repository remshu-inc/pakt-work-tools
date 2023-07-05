"""
Класс для модели выставления оценки за текст
"""
import numpy as np
import json
import pandas as pd
import tensorflow as tf
from matplotlib import pyplot as plt


class MarkModel:
    """
    Класс для модели выставления оценки за текст
    """

    def __init__(self, listlayers=None, norm='numtoken', modelpath=None):
        # norm принимает значения: 'numtoken', 'numsent', 'all'
        self.listlayers = listlayers
        self.norm = norm
        self.create_model(modelpath)

    def create_model(self, modelpath):
        if self.listlayers is None:
            self.model = tf.keras.models.load_model(modelpath)
        else:
            if self.norm in ['numtoken', 'numsent'] and (self.listlayers[0] != 10 and self.listlayers[0] != 32):
                print('Модель не создана')
            if self.norm == 'all' and (self.listlayers[0] != 13 and self.listlayers[0] != 35):
                print('Модель не создана')
            self.model = tf.keras.Sequential()
            for i in range(1,len(self.listlayers)):
                if i == 1:
                    self.model.add(tf.keras.layers.Dense(self.listlayers[i], input_shape=(self.listlayers[0],), activation=tf.nn.relu))
                else:
                    self.model.add(tf.keras.layers.Dense(self.listlayers[i], activation=tf.nn.relu))

    def load_data(self, file_csv):
        df = pd.read_csv(file_csv, sep=',')
        if self.norm == 'numtoken':
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
            if self.listlayers[0] == 32:
                df['gram_norm1'] = df['gram1']/df['numtoken']
                df['gram_norm2'] = df['gram2']/df['numtoken']
                df['gram_norm3'] = df['gram3']/df['numtoken']
                df['gram_norm4'] = df['gram4']/df['numtoken']
                df['gram_norm5'] = df['gram5']/df['numtoken']
                df['gram_norm6'] = df['gram6']/df['numtoken']
                df['gram_norm7'] = df['gram7']/df['numtoken']
                df['gram_norm8'] = df['gram8']/df['numtoken']
                df['gram_norm9'] = df['gram9']/df['numtoken']
                df['gram_norm10'] = df['gram10']/df['numtoken']
                df['gram_norm11'] = df['gram11']/df['numtoken']
                df['gram_norm12'] = df['gram12']/df['numtoken']
                df['gram_norm13'] = df['gram13']/df['numtoken']
                df['gram_norm14'] = df['gram14']/df['numtoken']
                df['leks_norm15'] = df['leks15']/df['numtoken']
                df['leks_norm16'] = df['leks16']/df['numtoken']
                df['leks_norm17'] = df['leks17']/df['numtoken']
                df['leks_norm18'] = df['leks18']/df['numtoken']
                df['diskurs_norm19'] = df['diskurs19']/df['numtoken']
                df['diskurs_norm20'] = df['diskurs20']/df['numtoken']
                df['diskurs_norm21'] = df['diskurs21']/df['numtoken']
                df['diskurs_norm22'] = df['diskurs22']/df['numtoken']
        if self.norm == 'numsent':
            df['gram_norm'] = df['gram'] / df['numsent']
            df['leks_norm'] = df['leks'] / df['numsent']
            df['punkt_norm'] = df['punkt'] / df['numsent']
            df['orpho_norm'] = df['orpho'] / df['numsent']
            df['diskurs_norm'] = df['diskurs'] / df['numsent']
            df['skips_norm'] = df['skips'] / df['numsent']
            df['extra_norm'] = df['extra'] / df['numsent']
            df['g1_norm'] = df['g1'] / df['numsent']
            df['g2_norm'] = df['g2'] / df['numsent']
            df['g3_norm'] = df['g3'] / df['numsent']
            if self.listlayers[0] == 32:
                df['gram_norm1'] = df['gram1']/df['numsent']
                df['gram_norm2'] = df['gram2']/df['numsent']
                df['gram_norm3'] = df['gram3']/df['numsent']
                df['gram_norm4'] = df['gram4']/df['numsent']
                df['gram_norm5'] = df['gram5']/df['numsent']
                df['gram_norm6'] = df['gram6']/df['numsent']
                df['gram_norm7'] = df['gram7']/df['numsent']
                df['gram_norm8'] = df['gram8']/df['numsent']
                df['gram_norm9'] = df['gram9']/df['numsent']
                df['gram_norm10'] = df['gram10']/df['numsent']
                df['gram_norm11'] = df['gram11']/df['numsent']
                df['gram_norm12'] = df['gram12']/df['numsent']
                df['gram_norm13'] = df['gram13']/df['numsent']
                df['gram_norm14'] = df['gram14']/df['numsent']
                df['leks_norm15'] = df['leks15']/df['numsent']
                df['leks_norm16'] = df['leks16']/df['numsent']
                df['leks_norm17'] = df['leks17']/df['numsent']
                df['leks_norm18'] = df['leks18']/df['numsent']
                df['diskurs_norm19'] = df['diskurs19']/df['numsent']
                df['diskurs_norm20'] = df['diskurs20']/df['numsent']
                df['diskurs_norm21'] = df['diskurs21']/df['numsent']
                df['diskurs_norm22'] = df['diskurs22']/df['numsent']

        if self.listlayers[0] == 10:
            self.X = df[df['text_mark'] > 0][
                ['gram_norm', 'leks_norm', 'punkt_norm', 'orpho_norm', 'diskurs_norm', 'skips_norm', 'extra_norm',
                 'g1_norm', 'g2_norm', 'g3_norm']]
        if self.listlayers[0] == 13:
            self.X = df[df['text_mark'] > 0][
                ['gram', 'leks', 'punkt', 'orpho', 'diskurs', 'skips', 'extra', 'g1', 'g2', 'g3', 'numsent', 'numtoken' ,'numchar']]
        if self.listlayers[0] == 32:
            self.X = df[df['text_mark'] > 0][
                ['gram_norm', 'leks_norm', 'punkt_norm', 'orpho_norm', 'diskurs_norm', 'skips_norm', 'extra_norm',
                 'g1_norm', 'g2_norm', 'g3_norm', 'gram_norm1', 'gram_norm2', 'gram_norm3', 'gram_norm4', 'gram_norm5',
                 'gram_norm6', 'gram_norm7', 'gram_norm8', 'gram_norm9', 'gram_norm10', 'gram_norm11', 'gram_norm12', 'gram_norm13',
                 'gram_norm14', 'leks_norm15', 'leks_norm16', 'leks_norm17', 'leks_norm18', 'diskurs_norm19', 'diskurs_norm20',
                 'diskurs_norm21', 'diskurs_norm22']]
        if self.listlayers[0] == 35:
            self.X = df[df['text_mark'] > 0][
                ['gram', 'leks', 'punkt', 'orpho', 'diskurs', 'skips', 'extra',
                 'g1', 'g2', 'g3', 'gram1', 'gram2', 'gram3', 'gram4', 'gram5',
                 'gram6', 'gram7', 'gram8', 'gram9', 'gram10', 'gram11', 'gram12', 'gram13',
                 'gram14', 'leks15', 'leks16', 'leks17', 'leks18', 'diskurs19', 'diskurs20',
                 'diskurs21', 'diskurs22', 'numsent', 'numtoken' ,'numchar']]
        self.y = df[df['text_mark'] > 0]['text_mark']
        print('Объем данных ' + str(self.y.shape[0]))

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
        valInput = len(data[0])
        if valInput == 11:
            df = pd.DataFrame(data,
                          columns=['gram', 'leks', 'punkt', 'orpho', 'diskurs', 'skips', 'extra', 'g1', 'g2', 'g3', 'num'])
            df['gram_norm'] = df['gram'] / df['num']
            df['leks_norm'] = df['leks'] / df['num']
            df['punkt_norm'] = df['punkt'] / df['num']
            df['orpho_norm'] = df['orpho'] / df['num']
            df['diskurs_norm'] = df['diskurs'] / df['num']
            df['skips_norm'] = df['skips'] / df['num']
            df['extra_norm'] = df['extra'] / df['num']
            df['g1_norm'] = df['g1'] / df['num']
            df['g2_norm'] = df['g2'] / df['num']
            df['g3_norm'] = df['g3'] / df['num']
            df1 = df[['gram_norm', 'leks_norm', 'punkt_norm', 'orpho_norm', 'diskurs_norm', 'skips_norm', 'extra_norm',
                  'g1_norm', 'g2_norm', 'g3_norm']]

        if valInput == 13:
            df1 = pd.DataFrame(data,
                          columns=['gram', 'leks', 'punkt', 'orpho', 'diskurs', 'skips', 'extra', 'g1', 'g2', 'g3', 'numsent', 'numtoken' ,'numchar'])

        if valInput == 33:
            df = pd.DataFrame(data,
                          columns=['gram', 'leks', 'punkt', 'orpho', 'diskurs', 'skips', 'extra', 'g1', 'g2', 'g3',
                                   'gram1', 'gram2', 'gram3', 'gram4', 'gram5', 'gram6', 'gram7', 'gram8', 'gram9',
                                   'gram10', 'gram11', 'gram12', 'gram13', 'gram14', 'leks15', 'leks16', 'leks17',
                                   'leks18', 'diskurs19', 'diskurs20', 'diskurs21', 'diskurs22','num'])
            df['gram_norm'] = df['gram'] / df['num']
            df['leks_norm'] = df['leks'] / df['num']
            df['punkt_norm'] = df['punkt'] / df['num']
            df['orpho_norm'] = df['orpho'] / df['num']
            df['diskurs_norm'] = df['diskurs'] / df['num']
            df['skips_norm'] = df['skips'] / df['num']
            df['extra_norm'] = df['extra'] / df['num']
            df['g1_norm'] = df['g1'] / df['num']
            df['g2_norm'] = df['g2'] / df['num']
            df['g3_norm'] = df['g3'] / df['num']
            df['gram_norm1'] = df['gram1']/df['num']
            df['gram_norm2'] = df['gram2']/df['num']
            df['gram_norm3'] = df['gram3']/df['num']
            df['gram_norm4'] = df['gram4']/df['num']
            df['gram_norm5'] = df['gram5']/df['num']
            df['gram_norm6'] = df['gram6']/df['num']
            df['gram_norm7'] = df['gram7']/df['num']
            df['gram_norm8'] = df['gram8']/df['num']
            df['gram_norm9'] = df['gram9']/df['num']
            df['gram_norm10'] = df['gram10']/df['num']
            df['gram_norm11'] = df['gram11']/df['num']
            df['gram_norm12'] = df['gram12']/df['num']
            df['gram_norm13'] = df['gram13']/df['num']
            df['gram_norm14'] = df['gram14']/df['num']
            df['leks_norm15'] = df['leks15']/df['num']
            df['leks_norm16'] = df['leks16']/df['num']
            df['leks_norm17'] = df['leks17']/df['num']
            df['leks_norm18'] = df['leks18']/df['num']
            df['diskurs_norm19'] = df['diskurs19']/df['num']
            df['diskurs_norm20'] = df['diskurs20']/df['num']
            df['diskurs_norm21'] = df['diskurs21']/df['num']
            df['diskurs_norm22'] = df['diskurs22']/df['num']
            df1 = df[['gram_norm', 'leks_norm', 'punkt_norm', 'orpho_norm', 'diskurs_norm', 'skips_norm', 'extra_norm',
                  'g1_norm', 'g2_norm', 'g3_norm','gram_norm1', 'gram_norm2', 'gram_norm3', 'gram_norm4', 'gram_norm5',
                 'gram_norm6', 'gram_norm7', 'gram_norm8', 'gram_norm9', 'gram_norm10', 'gram_norm11', 'gram_norm12', 'gram_norm13',
                 'gram_norm14', 'leks_norm15', 'leks_norm16', 'leks_norm17', 'leks_norm18', 'diskurs_norm19', 'diskurs_norm20',
                 'diskurs_norm21', 'diskurs_norm22']]

        if valInput == 35:
            df1 = pd.DataFrame(data,
                          columns=['gram', 'leks', 'punkt', 'orpho', 'diskurs', 'skips', 'extra', 'g1', 'g2', 'g3',
                                   'gram1', 'gram2', 'gram3', 'gram4', 'gram5', 'gram6', 'gram7', 'gram8', 'gram9',
                                   'gram10', 'gram11', 'gram12', 'gram13', 'gram14', 'leks15', 'leks16', 'leks17',
                                   'leks18', 'diskurs19', 'diskurs20', 'diskurs21', 'diskurs22', 'numsent', 'numtoken' ,'numchar'])

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
        modeldata = {}
        modeldata["input"] = self.listlayers[0]
        modeldata["norm"] = self.norm
        with open(path + "/modeldata.json", "w") as file_write:
            file_write.write(json.dumps(modeldata))


    def load_model(self, path):
        self.model = tf.keras.models.load_model(path)
        with open(pathname + "/modeldata.json", "r") as read_file:
            modeldata = json.load(read_file)
        self.norm = modeldata["norm"]
        print('количество входных нейронов - ' + modeldata["input"])

