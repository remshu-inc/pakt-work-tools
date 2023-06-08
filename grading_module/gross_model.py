"""
Класс для модели определения грубости ошибки
"""
import json
import math
import time

import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util, losses, CrossEncoder, InputExample
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm
from transformers import BertForSequenceClassification, BertTokenizer, DistilBertTokenizer, AdamW


class GrossModel:
    """
    Класс для модели определения грубости ошибки
    """

    def __init__(self, model_type='CosMeasure', score=0):
        # score = 0 - значения по умолчанию,
        # score = [1,2,3] - список из трех убывающих значений для грубости 1, 2, 3
        if model_type not in ['CosMeasure', 'CrossEncoder', 'CrossEncoder2', 'BERTModel', 'distilBERTModel']:
            raise AttributeError("Неизвестная модель")
        self.modeltype = model_type
        self.Cosmodel = 'symanto/sn-xlm-roberta-base-snli-mnli-anli-xnli'
        self.Crossmodel = 'dbmdz/convbert-base-german-europeana-cased'
        self.Crossmodel2 = 'ml6team/cross-encoder-mmarco-german-distilbert-base'
        self.distilBERTmodel = 'distilbert-base-german-cased'
        self.BERTmodel = 'severinsimmler/literary-german-bert'
        # self.BERTmodel = 'dbmdz/distilbert-base-german-europeana-cased'
        self.train_batch_size = 16
        self.num_epochs = 2
        self.model_save_path = 'grossmodel'
        self.text_grade = {1: 'Der Fehler beeinträchtigt das Verständnis nicht',
                           2: 'Der Fehler beeinträchtigt das Verständnis',
                           3: 'Der Sinn ist unverständlich oder verfälscht'}
        self.text_grade_rus = {1: 'Ошибка не влияет на понимание', 2: 'Ошибка ухудшает понимание',
                               3: 'Смысл непонятен или искажен'}
        self.create_model(score=score)
        self.train_dataloader = None
        self.test_dataloader = None

    def get_grade(self, x, score):
        # возвращает значение грубости ошибки (1, 2 или 3) по значению порога x
        if (score[1] == 0) and (score[2] == 1) and (score[3] == 2):
            return (x + 1)
        if x >= score[1]:
            return (1)
        else:
            if x >= score[2]:
                if (score[1] - x) < (x - score[2]):
                    return (1)
                else:
                    return (2)
            else:
                if x >= score[3]:
                    if (score[2] - x) < (x - score[3]):
                        return (2)
                    else:
                        return (3)
                else:
                    return (3)

    def create_model(self, device='cuda:0', score=0):
        # функция загружает стороннюю предобученную модель для последующего дообучения и пороги грубости ошибки
        self.devicename = device
        self.device = torch.device(device)
        if self.modeltype == 'CosMeasure':
            print('Загрузка модели ' + self.Cosmodel)
            self.model_cos = SentenceTransformer(self.Cosmodel)
            if (score == 0) or (score == 3):
                self.score = {1: 0.92, 2: 0.88, 3: 0.66}
            else:
                self.score = {}
                self.score[1] = score[0]
                self.score[2] = score[1]
                self.score[3] = score[2]
        if self.modeltype == 'CrossEncoder':
            print('Загрузка модели ' + self.Crossmodel)
            if score == 0:
                self.model_cross = CrossEncoder(self.Crossmodel, num_labels=1)
                self.score = {1: 0.95, 2: 0.80, 3: 0.65}
            else:
                if score == 3:
                    self.model_cross = CrossEncoder(self.Crossmodel, num_labels=3)
                    self.score = {1: 0, 2: 1, 3: 2}
                else:
                    self.model_cross = CrossEncoder(self.Crossmodel2, num_labels=1)
                    self.score = {}
                    self.score[1] = score[0]
                    self.score[2] = score[1]
                    self.score[3] = score[2]
        if self.modeltype == 'CrossEncoder2':
            print('Загрузка модели ' + self.Crossmodel2)
            if score == 0:
                self.model_cross = CrossEncoder(self.Crossmodel2, num_labels=1)
                self.score = {1: 0.95, 2: 0.80, 3: 0.65}
            else:
                if score == 3:
                    self.model_cross = CrossEncoder(self.Crossmodel2, num_labels=3)
                    self.score = {1: 0, 2: 1, 3: 2}
                else:
                    self.model_cross = CrossEncoder(self.Crossmodel2, num_labels=1)
                    self.score = {}
                    self.score[1] = score[0]
                    self.score[2] = score[1]
                    self.score[3] = score[2]

        if self.modeltype == 'BERTModel':
            print('Загрузка модели ' + self.BERTmodel)
            self.model_bert = BertForSequenceClassification.from_pretrained(self.BERTmodel, num_labels=3).to(device)
        if self.modeltype == 'distilBERTModel':
            print('Загрузка модели ' + self.distilBERTmodel)
            self.model_bert = BertForSequenceClassification.from_pretrained(self.distilBERTmodel, num_labels=3).to(
                device)
        return None

    def load_data(self, file, testpart=0.1, train_batch_size=16):
        # функция загружает данные для дообучения модели
        self.train_batch_size = train_batch_size
        df = pd.read_csv(file, sep=';', lineterminator='\n')
        numIndex = math.ceil(df.shape[0] * (1 - testpart))
        self.test_shape = df.shape[0] - numIndex
        print(
            'Объем обучающей выборки = ' + str(numIndex) + '; Объем тестовой выборки = ' + str(df.shape[0] - numIndex))
        if self.modeltype == 'CosMeasure':
            train_samples = []
            test_samples = []
            for index, row in df.iterrows():
                inp_example = InputExample(texts=[row['sent'], row['sentcorrect']], label=self.score[row['level']])
                if index < numIndex:
                    train_samples.append(inp_example)
                else:
                    test_samples.append(inp_example)
            self.train_dataloader = DataLoader(train_samples, shuffle=True, batch_size=self.train_batch_size)
            self.test_dataloader = DataLoader(test_samples, shuffle=False, batch_size=self.train_batch_size)
            self.data_val = test_samples
            return 1

        if (self.modeltype == 'CrossEncoder') or (self.modeltype == 'CrossEncoder2'):
            train_samples = []
            test_samples = []
            for index, row in df.iterrows():
                inp_example = InputExample(texts=[row['sent'], row['sentcorrect']], label=self.score[row['level']])
                if index < numIndex:
                    train_samples.append(inp_example)
                else:
                    test_samples.append(inp_example)
            self.train_dataloader = DataLoader(train_samples, shuffle=True, batch_size=self.train_batch_size)
            self.test_dataloader = DataLoader(test_samples, shuffle=False, batch_size=self.train_batch_size)
            self.data_val = test_samples
            return 1

        if self.modeltype == 'BERTModel':
            tokenizer = BertTokenizer.from_pretrained(self.BERTmodel, do_lower_case=False)
        if self.modeltype == 'distilBERTModel':
            tokenizer = DistilBertTokenizer.from_pretrained(self.distilBERTmodel, do_lower_case=False)
        if (self.modeltype == 'BERTModel') or (self.modeltype == 'distilBERTModel'):
            token_ids_train = []
            mask_ids_train = []
            seg_ids_train = []
            y_train = []
            token_ids_val = []
            mask_ids_val = []
            seg_ids_val = []
            y_val = []
            for index, row in df.iterrows():
                premise_id = tokenizer.encode(row['sent'], add_special_tokens=False)
                hypothesis_id = tokenizer.encode(row['sentcorrect'], add_special_tokens=False)
                pair_token_ids = [tokenizer.cls_token_id] + premise_id + [tokenizer.sep_token_id] + hypothesis_id + [
                    tokenizer.sep_token_id]
                premise_len = len(premise_id)
                hypothesis_len = len(hypothesis_id)
                segment_ids = torch.tensor(
                    [0] * (premise_len + 2) + [1] * (hypothesis_len + 1))  # sentence 0 and sentence 1
                attention_mask_ids = torch.tensor([1] * (premise_len + hypothesis_len + 3))  # mask padded values
                if index < numIndex:
                    token_ids_train.append(torch.tensor(pair_token_ids))
                    seg_ids_train.append(segment_ids)
                    mask_ids_train.append(attention_mask_ids)
                    y_train.append(row['level'] - 1)
                else:
                    token_ids_val.append(torch.tensor(pair_token_ids))
                    seg_ids_val.append(segment_ids)
                    mask_ids_val.append(attention_mask_ids)
                    y_val.append(row['level'] - 1)
            token_ids_train = pad_sequence(token_ids_train, batch_first=True)
            mask_ids_train = pad_sequence(mask_ids_train, batch_first=True)
            seg_ids_train = pad_sequence(seg_ids_train, batch_first=True)
            y_train = torch.tensor(y_train)
            token_ids_val = pad_sequence(token_ids_val, batch_first=True)
            mask_ids_val = pad_sequence(mask_ids_val, batch_first=True)
            seg_ids_val = pad_sequence(seg_ids_val, batch_first=True)
            y_val = torch.tensor(y_val)
            data_train = TensorDataset(token_ids_train, mask_ids_train, seg_ids_train, y_train)
            data_val = TensorDataset(token_ids_val, mask_ids_val, seg_ids_val, y_val)
            self.train_dataloader = DataLoader(data_train, shuffle=True, batch_size=self.train_batch_size)
            self.test_dataloader = DataLoader(data_val, shuffle=False, batch_size=self.train_batch_size)
            self.data_val = None
            return 1
        return 0

    def fit(self, num_epochs=2, learning_rate=2e-4, path='n'):
        # функция дообучения модели
        def multi_acc(y_pred, y):
            # функция расчета метрики accuracy
            acc = (torch.log_softmax(y_pred, dim=1).argmax(dim=1) == y).sum().float() / float(y.size(0))
            return acc

        if self.train_dataloader is None:
            return 0
        self.num_epochs = num_epochs
        self.learning_rate = learning_rate
        self.save_path = path
        self.warmup_steps = math.ceil(len(self.train_dataloader) * self.num_epochs * 0.1)

        if self.modeltype == 'CosMeasure':
            train_loss = losses.CosineSimilarityLoss(model=self.model_cos)
            # evaluator = EmbeddingSimilarityEvaluator.from_input_examples(self.data_val, name='test')
            self.model_cos.fit(train_objectives=[(self.train_dataloader, train_loss)],
                               # evaluator=evaluator,
                               epochs=self.num_epochs,
                               # evaluation_steps=70,
                               warmup_steps=self.warmup_steps,
                               output_path=self.model_save_path)
            return

        if (self.modeltype == 'CrossEncoder') or (self.modeltype == 'CrossEncoder2'):
            # evaluator = CESoftmaxAccuracyEvaluator.from_input_examples(self.data_val, name='test')
            self.model_cross.fit(train_dataloader=self.train_dataloader,
                                 # evaluator=evaluator,
                                 epochs=self.num_epochs,
                                 # evaluation_steps=len(self.train_dataloader),
                                 output_path=self.model_save_path,
                                 warmup_steps=self.warmup_steps)
            return

        if (self.modeltype == 'BERTModel') or (self.modeltype == 'distilBERTModel'):
            optimizer = AdamW(self.model_bert.parameters(), lr=self.learning_rate, correct_bias=False)
            # total_step = len(self.train_dataloader)
            for epoch in range(self.num_epochs):
                start = time.time()
                self.model_bert.train()
                total_train_loss = 0
                total_train_acc = 0
                pbar = tqdm(total=len(self.train_dataloader))
                for batch_idx, (pair_token_ids, mask_ids, seg_ids, y) in enumerate(self.train_dataloader):
                    optimizer.zero_grad()
                    pair_token_ids = pair_token_ids.to(self.device)
                    mask_ids = mask_ids.to(self.device)
                    seg_ids = seg_ids.to(self.device)
                    y = y.to(self.device)
                    loss, prediction = self.model_bert(pair_token_ids, token_type_ids=seg_ids, attention_mask=mask_ids,
                                                       labels=y).values()
                    acc = multi_acc(prediction, y)
                    loss.backward()
                    optimizer.step()
                    total_train_loss += loss.item()
                    total_train_acc += acc.item()
                    pbar.update(1)
                pbar.close()
                train_acc = total_train_acc / len(self.train_dataloader)
                train_loss = total_train_loss / len(self.train_dataloader)
                self.model_bert.eval()
                total_val_acc = 0
                total_val_loss = 0
                val_result = []
                with torch.no_grad():
                    pbar = tqdm(total=len(self.test_dataloader))
                    for batch_idx, (pair_token_ids, mask_ids, seg_ids, y) in enumerate(self.test_dataloader):
                        optimizer.zero_grad()
                        pair_token_ids = pair_token_ids.to(self.device)
                        mask_ids = mask_ids.to(self.device)
                        seg_ids = seg_ids.to(self.device)
                        y = y.to(self.device)
                        loss, prediction = self.model_bert(pair_token_ids, token_type_ids=seg_ids,
                                                           attention_mask=mask_ids, labels=y).values()
                        acc = multi_acc(prediction, y)
                        total_val_loss += loss.item()
                        total_val_acc += acc.item()
                        val_result.append([pair_token_ids, mask_ids, seg_ids, y, prediction])
                        pbar.update(1)
                    pbar.close()
                val_acc = total_val_acc / len(self.test_dataloader)
                val_loss = total_val_loss / len(self.test_dataloader)
                end = time.time()
                hours, rem = divmod(end - start, 3600)
                minutes, seconds = divmod(rem, 60)
                print(
                    f'Эпоха {epoch + 1}: train_loss: {train_loss:.4f} train_acc: {train_acc:.4f} | val_loss: {val_loss:.4f} val_acc: {val_acc:.4f}')
                print("Время {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
            return 1
        return 0

    def predict(self, data):
        # функция получения грубости ошибки по исходным данным data
        if self.modeltype == 'CosMeasure':
            # data - список из двух равновеликих списков: список предложений с ошибкой, список предложений без ошибок
            prediction = []
            # Compute embedding for both sentences
            embeddings1 = self.model_cos.encode(data[0], convert_to_tensor=False)  # data[data.columns[0]]
            embeddings2 = self.model_cos.encode(data[1], convert_to_tensor=False)
            # Compute cosine-similarities
            cosine_scores = util.cos_sim(embeddings1, embeddings2)
            for i in range(len(data[0])):
                grade = self.get_grade(cosine_scores[i][i], self.score)
                prediction.append([data[0][i], data[1][i], cosine_scores[i][i], grade, self.text_grade[grade],
                                   self.text_grade_rus[grade], cosine_scores[i][i]])
            return prediction

        if (self.modeltype == 'CrossEncoder') or (self.modeltype == 'CrossEncoder2'):
            prediction = []
            for item in range(len(data[0])):
                res = self.model_cross.predict([[data[0][item], data[1][item]]])
                grade = self.get_grade(res, self.score)
                prediction.append(
                    [data[0][item], data[1][item], grade, self.text_grade[grade], self.text_grade_rus[grade], res])
            return prediction

        if (self.modeltype == 'BERTModel') or (self.modeltype == 'distilBERTModel'):
            if self.modeltype == 'BERTModel':
                tokenizer = BertTokenizer.from_pretrained(self.BERTmodel, do_lower_case=False)
            if self.modeltype == 'distilBERTModel':
                tokenizer = DistilBertTokenizer.from_pretrained(self.distilBERTmodel, do_lower_case=False)

            token_ids_val = []
            mask_ids_val = []
            seg_ids_val = []
            y_val = []
            self.learning_rate = 2e-4
            for index in range(len(data[0])):
                premise_id = tokenizer.encode(data[0][index], add_special_tokens=False)
                hypothesis_id = tokenizer.encode(data[1][index], add_special_tokens=False)
                pair_token_ids = [tokenizer.cls_token_id] + premise_id + [tokenizer.sep_token_id] + hypothesis_id + [
                    tokenizer.sep_token_id]
                premise_len = len(premise_id)
                hypothesis_len = len(hypothesis_id)
                segment_ids = torch.tensor(
                    [0] * (premise_len + 2) + [1] * (hypothesis_len + 1))  # sentence 0 and sentence 1
                attention_mask_ids = torch.tensor([1] * (premise_len + hypothesis_len + 3))  # mask padded values
                token_ids_val.append(torch.tensor(pair_token_ids))
                seg_ids_val.append(segment_ids)
                mask_ids_val.append(attention_mask_ids)
                y_val.append(0)
            token_ids_val = pad_sequence(token_ids_val, batch_first=True)
            mask_ids_val = pad_sequence(mask_ids_val, batch_first=True)
            seg_ids_val = pad_sequence(seg_ids_val, batch_first=True)
            y_val = torch.tensor(y_val)
            data_val = TensorDataset(token_ids_val, mask_ids_val, seg_ids_val, y_val)
            dataloader = DataLoader(data_val, shuffle=False, batch_size=self.train_batch_size)
            optimizer = AdamW(self.model_bert.parameters(), lr=self.learning_rate, correct_bias=False)
            self.model_bert.eval()
            val_result = []
            with torch.no_grad():
                pbar = tqdm(total=len(dataloader))
                for batch_idx, (pair_token_ids, mask_ids, seg_ids, y) in enumerate(dataloader):
                    optimizer.zero_grad()
                    pair_token_ids = pair_token_ids.to(self.device)
                    mask_ids = mask_ids.to(self.device)
                    seg_ids = seg_ids.to(self.device)
                    y = y.to(self.device)
                    loss, prediction = self.model_bert(pair_token_ids, token_type_ids=seg_ids, attention_mask=mask_ids,
                                                       labels=y).values()
                    y_pred = torch.log_softmax(prediction, dim=1).argmax(dim=1)
                    val_result.append([pair_token_ids, mask_ids, seg_ids, y, prediction, y_pred])
                    pbar.update(1)
                pbar.close()
            prediction = []
            for i in range(len(val_result)):
                for j in range(len(val_result[i][0])):
                    prediction.append([tokenizer.decode(val_result[i][0][j]).replace(' [PAD]', '').replace('[CLS] ',
                                                                                                           '').split(
                        '[SEP]')[0],
                                       tokenizer.decode(val_result[i][0][j]).replace(' [PAD]', '').replace('[CLS] ',
                                                                                                           '').split(
                                           '[SEP]')[1],
                                       val_result[i][5][j].item() + 1,
                                       val_result[i][4][j],
                                       self.text_grade[val_result[i][5][j].item() + 1],
                                       self.text_grade_rus[val_result[i][5][j].item() + 1]])
            return prediction
        return None

    def get_accuracy(self, data):
        # функция для расчета метрики accuracy для данных data, включающих правильные выходы
        if self.modeltype == 'CosMeasure':
            # data - список из трех равновеликих списков: предложения с ошибкой, предложения без ошибок, уровни грубости
            A = self.predict(data)
            acc = 0
            for i in range(len(A)):
                # print(str(A[i][3]) + str(data[2][i]))
                if A[i][3] == data[2][i]:
                    acc += 1
            return acc / len(A)
        if (self.modeltype == 'CrossEncoder') or (self.modeltype == 'CrossEncoder2'):
            # data - список из трех равновеликих списков: предложения с ошибкой, предложения без ошибок, уровни грубости
            A = self.predict(data)
            acc = 0
            for i in range(len(A)):
                # print(str(A[i][2]) + str(data[2][i]))
                if A[i][2] == data[2][i]:
                    acc += 1
            return acc / len(A)

        if (self.modeltype == 'BERTModel') or (self.modeltype == 'distilBERTModel'):
            # data - список из трех равновеликих списков: предложения с ошибкой, предложения без ошибок, уровни грубости
            A = self.predict(data)
            acc = 0
            for i in range(len(A)):
                # print(str(A[i][2]) + str(data[2][i]))
                if A[i][2] == data[2][i]:
                    acc += 1
            return acc / len(A)

    def get_accuracy_m(self, data):
        # функция для расчета метрики accuracy для данных data, включающих правильные выходы, и вывода результата в виде матрицы ошибок Матрица ошибок (Confusion Matrix)
        if self.modeltype == 'CosMeasure':
            # data - список из трех равновеликих списков: предложения с ошибкой, предложения без ошибок, уровни грубости
            A = self.predict(data)
            acc = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            for i in range(len(A)):
                acc[A[i][3] - 1][data[2][i] - 1] += 1
            acur = (acc[0][0] + acc[1][1] + acc[2][2]) / (sum(acc[0]) + sum(acc[1]) + sum(acc[2]))
            return (acc, acur)

        if (self.modeltype == 'CrossEncoder') or (self.modeltype == 'CrossEncoder2') or (
                self.modeltype == 'BERTModel') or (self.modeltype == 'distilBERTModel'):
            # data - список из трех равновеликих списков: предложения с ошибкой, предложения без ошибок, уровни грубости
            A = self.predict(data)
            acc = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            for i in range(len(A)):
                acc[A[i][2] - 1][data[2][i] - 1] += 1
            acur = (acc[0][0] + acc[1][1] + acc[2][2]) / (sum(acc[0]) + sum(acc[1]) + sum(acc[2]))
            return (acc, acur)

    def save_model(self):
        # функция сохранения модели на диске
        modeldata = {}
        modeldata["modelType"] = self.modeltype
        modeldata["score1"] = self.score[1]
        modeldata["score2"] = self.score[2]
        modeldata["score3"] = self.score[3]
        modeldata["device"] = self.devicename

        if self.modeltype == 'CosMeasure':
            self.model_cos.save(self.model_save_path)
            with open(self.model_save_path + "/modeldata.json", "w") as file_write:
                file_write.write(json.dumps(modeldata))
            return (1)
        if (self.modeltype == 'CrossEncoder') or (self.modeltype == 'CrossEncoder2'):
            self.model_cross.save(self.model_save_path)
            with open(self.model_save_path + "/modeldata.json", "w") as file_write:
                file_write.write(json.dumps(modeldata))
            return 1
        return 0

    def load_model(self, pathname='grossmodel'):
        # функция загрузки модели с диска
        with open(pathname + "/modeldata.json", "r") as read_file:
            modeldata = json.load(read_file)

        self.modeltype = modeldata["modelType"]
        self.score[1] = modeldata["score1"]
        self.score[2] = modeldata["score2"]
        self.score[3] = modeldata["score3"]
        self.devicename = modeldata["device"]
        self.device = torch.device(self.devicename)

        if self.modeltype == 'CosMeasure':
            self.model_cos = SentenceTransformer(pathname)
            return 1
        if (self.modeltype == 'CrossEncoder') or (self.modeltype == 'CrossEncoder2'):
            self.model_cross = CrossEncoder(pathname, num_labels=1)
            return 1
        return 0

