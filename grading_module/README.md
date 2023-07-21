# Модуль построения оценок

В Модуле построения оценок реализованы два класса:
* класс GrossModel предназначен для работы с моделью определения грубости ошибки (находится в модуле "grading_module.gross_model").
* класс MarkModel предназначен для работы с моделью для формирования оценки
текста (находится в модуле "grading_module.mark_model");

и восемь функций (находятся в модуле "grading_module.common").

## Создание Python пакета
Библиотека (модуль построения оценок) содержит setup.py скрипт для создания python пакета.
Команда создания пакета:
```shell
python setup.py bdist_wheel --universal
```
После выполнения команды создается каталог dist с пакетом grading_module-...-any.whl, который можно использовать для установки библиотеки.



## Описание класса GrossModel

*Class GrossModel(modeltype = \'CosMeasure\', score = 0)*
Параметры:
* *modeltype* -- тип модели; по умолчанию -- значение «CosMeasure»; принимает одно из следующих значений:
  *  CosMeasure -- загружается модель symanto/sn-xlm-roberta-base-snli-mnli-anli-xnli;
  *  CrossEncoder -- загружается модель dbmdz/convbert-base-german-europeana-cased;
  *  CrossEncoder2 -- загружается модель ml6team/cross-encoder-mmarco-german-distilbert-base;
  *  BERTModel -- загружается модель severinsimmler/literary-german-bert;
  *  distilBERTModel -- загружается модель distilbert-base-german-cased;
* *score* -- границы для грубости ошибки; используется только с типами моделей \'CosMeasure\', \'CrossEncoder\', \'CrossEncoder2\'; принимает значение 0 (используются встроенные границы) или список из трех убывающих значений, соответствующих уровням грубости 1, 2, 3; по умолчанию -- значение 0.

### Поля класса GrossModel:
* *BERTmodel* = \'severinsimmler/literary-german-bert\' -- название BERT модели искусственной нейронной сети;
* *Cosmodel* = \'symanto/sn-xlm-roberta-base-snli-mnli-anli-xnli\' -- название модели искусственной нейронной сети с использованием косинусной меры;
* *Crossmodel* = \'dbmdz/convbert-base-german-europeana-cased\' -- название модели искусственной нейронной сети на основе кросс-энкодера;
* *Crossmodel2* = \'ml6team/cross-encoder-mmarco-german-distilbert-base\' -- название модели искусственной нейронной сети на основе кросс-энкодера;
* *device* -- устройство;
* *distilBERTmodel* = \'distilbert-base-german-cased\' -- название BERT модели искусственной нейронной сети;
* *learning\_rate* -- скорость обучения;
* *modeltype* -- тип модели;
* *model\_bert* -- загруженная модель BERT;
* *model\_cos* -- загруженная модель искусственной нейронной сети с использованием косинусной меры;
* *model\_cross* -- загруженная модель искусственной нейронной сети на основе кросс-энкодера;
* *model\_save\_path* -- название папки для сохранения модели;
* *num\_epochs* -- количество эпох для обучения;
* *train\_batch\_size* -- размер пакета;
* *train\_dataloader* -- данные для обучения;
* *test\_dataloader* -- данные для тестирования;
* *test\_shape* -- количество данных для тестирования;
* *text\_grade* -- список формулировок уровней грубости ошибки на немецком языке;
* *text\_grade\_rus* -- список формулировок уровней грубости ошибки на русском языке;
* *warmup\_steps* -- количество начальных шагов при обучении.

### Методы класса GrossModel:
* *get\_grade*( x, score) -- получить значение уровня грубости ошибки; параметры: x -- значение из диапазона \[0, 1\], рассчитанное по модели, score -- границы для уровней грубости ошибки;
* *create\_model*(device=\'cuda:0\', score=0) -- создать новую модель на основе одной из сторонних предобученных моделей Cosmodel или Crossmodel, или Crossmodel2, или distilBERTmodel, или BERTmodel; параметры: device -- устройство, score -- границы для уровней грубости ошибки;
* *load\_data*(file, testpart=0.1, train\_batch\_size=16) -- загрузить данные из файла; параметры: *file* -- имя csv файла, содержащего данные для обучения и тестирования, в файле должны быть три столбца с именами «sent» - для предложения с ошибкой, «sentcorrect» -- для предложения без ошибки, «level» -- для уровня грубости ошибки;  *testpart* -- размер тестовой выборки относительно всех данных, принимает значение от 0 до 1; *train\_batch\_size* -- размер пакета;
* *fit*(num\_epochs = 2, learning\_rate = 2e-4) -- обучить модель на обучающих данных; параметры: *num\_epochs* -- количество эпох обучения, значение по умолчанию 2, *learning\_rate* -- скорость обучения, значение по умолчанию 0,0002;
* *predict*(data) -- получить степень грубости ошибки по модели; параметры: *data* -- список из двух равновеликих списков: список предложений с ошибкой, список предложений без ошибок;
* *get\_accuracy*(data) -- получить значение метрики accuracy; параметры: *data* -- список из трех равновеликих списков: предложения с ошибкой, предложения без ошибок, уровни грубости;
* *get\_accuracy\_m*(data) -- получить значение метрики accuracy и матрицу ошибок; параметры: *data* -- список из трех равновеликих списков: предложения с ошибкой, предложения без ошибок, уровни грубости;
* *save\_model*(pathname=\'grossmodel\') -- сохранить обученную модель в папке; параметры: *pathname* -- путь к файлам модели, значение по умолчанию "grossmodel";
* *load\_model*(pathname=\'grossmodel\') -- загрузить ранее обученную модель; параметры: *pathname* -- путь к файлам модели, значение по умолчанию "grossmodel".

## Описание класса MarkModel

*Class MarkModel(listlayers=None, norm='numtoken', modelpath=None)*
Параметры :
* *listlayers* -- список количества нейронов в каждом слое. Первый слой должен содержать 10 нейронов или 32 нейрона для типов моделей "numtoken" и "numsent"; 13 нейронов или 35 нейронов для типа модели "all". Последний слой должен содержать 1 нейрон для получения оценки;
* *norm* -- тип модели; значение по умолчанию "numtoken". Принимает одно из следующих значений: "numtoken" -- нормировка количества ошибок на количество токенов в тексте, "numsent" -- нормировка количества ошибок на количество предложений в тексте, "all" -- без нормировки количества ошибок, количество предложений, токенов и символов включаются в модель в качестве самостоятельных входных данных;
* *modelpath* -- папка, где находятся файлы готовой модели.

### Поля класса MarkModel:
* *batch\_size* -- размер пакета;
* *epochs* -- количество эпох для обучения;
* *learning\_rate* -- скорость обучения;
* *listlayers* -- структура слоев -- количество нейронов в каждом слое;
* *model* -- модель;
* *norm* -- тип модели;
* *X* -- данные для обучения -- описания текстов;
* *y* -- данные для обучения -- оценки текстов.

### Методы класса MarkModel:
* *create\_model*(modelpath) -- создать новую модель для обучения; параметры: *modelpath* -- папка, где находятся файлы готовой модели;
* *load\_data*(file\_csv) -- загрузить данные для обучения; параметры: *file\_csv* -- имя csv файла, содержащего данные для обучения и тестирования, в файле должны быть следующие столбцы:
  * для модели с 10 входными нейронами: «gram», «leks», «punkt», «orpho», «diskurs», «skips», «extra», «g1», «g2», «g3», «numtoken» или «numsent»; 
  * для модели с 32 входными нейронами: «gram», «leks», «punkt», «orpho», «diskurs», «skips», «extra», «g1», «g2», «g3», «gram1», «gram2», «gram3», «gram4», «gram5», «gram6», «gram7», «gram8», «gram9», «gram10», «gram11», «gram12», «gram13», «gram14», «leks15», «leks16», «leks17», «leks18», «diskurs19», «diskurs20», «diskurs21», «diskurs22», «numtoken» или «numsent»; 
  * для модели с 13 входными нейронами: «gram», «leks», «punkt», «orpho», «diskurs», «skips», «extra», «g1», «g2», «g3», «numsent», «numtoken», «numchar»; 
  * для модели с 35 входными нейронами: «gram», «leks», «punkt», «orpho», «diskurs», «skips», «extra», «g1», «g2», «g3», «gram1», «gram2», «gram3», «gram4», «gram5», «gram6», «gram7», «gram8», «gram9», «gram10», «gram11», «gram12», «gram13», «gram14», «leks15», «leks16», «leks17», «leks18», «diskurs19», «diskurs20», «diskurs21», «diskurs22», «numsent», «numtoken», «numchar»;
* *fit*(batch\_size=32, num\_epochs=60, learning\_rate=1e-4, val=0) -- обучить модель; параметры: *batch\_size* -- размер пакета, значение по умолчанию 32, *num\_epochs* -- количество эпох для обучения, значение по умолчанию 60, *learning\_rate* -- скорость обучения, значение по умолчанию 0,0001, *val* -- доля выборки для валидации, значение по умолчанию 0;
* *predict*(data) -- получить оценку за текст; параметры: *data* -- список описаний текстов, каждый текст представлен списком в формате: 
  * для модели с 10 входными нейронами: «gram», «leks», «punkt», «orpho», «diskurs», «skips», «extra», «g1»,  «g2», «g3», «numtoken» или «numsent»; 
  * для модели с 32 входными нейронами: «gram», «leks», «punkt», «orpho», «diskurs», «skips», «extra», «g1», «g2», «g3», «gram1», «gram2», «gram3», «gram4», «gram5», «gram6», «gram7», «gram8», «gram9», «gram10», «gram11», «gram12», «gram13», «gram14», «leks15», «leks16», «leks17», «leks18», «diskurs19», «diskurs20», «diskurs21», «diskurs22», «numtoken» или «numsent»; 
  * для модели с 13 входными нейронами: «gram», «leks», «punkt», «orpho», «diskurs», «skips», «extra», «g1», «g2», «g3», «numsent», «numtoken», «numchar»; 
  * для модели с 35 входными нейронами: «gram», «leks», «punkt», «orpho», «diskurs», «skips», «extra», «g1», «g2», «g3», «gram1», «gram2», «gram3», «gram4», «gram5», «gram6», «gram7», «gram8», «gram9», «gram10», «gram11», «gram12», «gram13», «gram14», «leks15», «leks16», «leks17», «leks18», «diskurs19», «diskurs20», «diskurs21», «diskurs22», «numsent», «numtoken», «numchar»;
* *val*(dataX, dataY) -- получить значение метрики - Сумма разностей оценок; параметры: *dataX* - список списков в формате:
  * для модели с 10 входными нейронами: «gram», «leks», «punkt», «orpho», «diskurs», «skips», «extra», «g1», «g2», «g3», «numtoken» или «numsent»; 
  * для модели с 32 входными нейронами: «gram», «leks», «punkt», «orpho», «diskurs», «skips», «extra», «g1», «g2», «g3», «gram1», «gram2», «gram3», «gram4», «gram5», «gram6», «gram7», «gram8», «gram9», «gram10», «gram11», «gram12», «gram13», «gram14», «leks15», «leks16», «leks17», «leks18», «diskurs19», «diskurs20», «diskurs21», «diskurs22», «numtoken» или «numsent»; 
  * для модели с 13 входными нейронами: «gram», «leks», «punkt», «orpho», «diskurs», «skips», «extra», «g1», «g2», «g3», «numsent», «numtoken», «numchar»; 
  * для модели с 35 входными нейронами: «gram», «leks», «punkt», «orpho», «diskurs», «skips», «extra», «g1», «g2», «g3», «gram1», «gram2», «gram3», «gram4», «gram5», «gram6», «gram7», «gram8», «gram9», «gram10», «gram11», «gram12», «gram13», «gram14», «leks15», «leks16», «leks17», «leks18», «diskurs19», «diskurs20», «diskurs21», «diskurs22», «numsent», «numtoken», «numchar»;
*dataY* - список оценок; метод формирует столбчатую диаграмму для количества текстов с различиями в оценках на 1 балл, 2 балла -- 12 баллов;
* *save\_model*(path) -- сохранить модель; параметры: *path* -- путь и название папки, в которую будут сохранены файлы;
* *load\_model*(path) -- загрузить готовую модель из файла; параметры: *path* -- путь и название папки, в которой хранятся файлы модели.

## Функции модуля

Модуль построения оценок включает следующие функции:

**GetDataForGrossModel**(user, password, host, database) -- функция
формирования на основе базы данных корпуса массива исходных данных для
обучения искусственной нейронной сети для определения грубости ошибки.
Параметры: *user* -- имя пользователя базы данных, *password* -- пароль
пользователя базы данных, *host* -- адрес базы данных, *database* -- имя
базы данных. Возвращает список кортежей в формате «предложение с
ошибкой», «предложение без ошибки», «уровень грубости ошибки».

**GrossModelDataTo\_scv**(file, user, password, host, database) -- функция
формирования на основе базы данных корпуса массива исходных данных для
обучения искусственной нейронной сети для определения грубости ошибки.
Параметры: *user* -- имя пользователя базы данных, *password* -- пароль
пользователя базы данных, *host* -- адрес базы данных, *database* -- имя
базы данных. Возвращает csv-файл со структурой «sent» -- предложение с
ошибкой, «sentcorrect» -- предложение без ошибки, «level» -- уровень
грубости ошибки.

**GetDataForMarkModel**(user, password, host, database) -- функция
формирования на основе базы данных корпуса массива исходных данных для
обучения искусственной нейронной сети для формирования оценки текста.
Параметры: *user* -- имя пользователя базы данных, *password* -- пароль
пользователя базы данных, *host* -- адрес базы данных, *database* -- имя
базы данных. Возвращает объект класса *pandas.DataFrame* в формате:
* «idT» -- идентификатор текста, 
* «text\_mark» -- оценка текста, 
* «gram» -- количество грамматических ошибок в тексте, 
* «leks» -- количество лексических ошибок в тексте, 
* «punkt» -- количество пунктуационных ошибок в тексте, 
* «orpho» -- количество орфографических ошибок в тексте, 
* «diskurs» -- количество дискурсивных ошибок в тексте, 
* «skips» -- количество ошибок, связанных с пропусками слов в тексте, 
* «extra» -- количество ошибок, связанных с присутствием лишних слов в тексте, 
* «gram1» -- количество ошибок в разделе «Грамматика», 
* «gram2» -- количество ошибок в разделе «Существительное», 
* «gram3» -- количество ошибок в разделе «Артикль», 
* «gram4» -- количество ошибок в разделе «Числительное», 
* «gram5» -- количество ошибок в разделе «Местоимение», 
* «gram6» -- количество ошибок в разделе «Глагол», 
* «gram7» -- количество ошибок в разделе «Причастие»,
* «gram8» -- количество ошибок в разделе «Предлоги», 
* «gram9» -- количество ошибок в разделе «Союзы», 
* «gram10» -- количество ошибок в разделе «Прилагательное», 
* «gram11» -- количество ошибок в разделе «Наречия»,
* «gram12» -- количество ошибок в разделе «Порядок слов», 
* «gram13» -- количество ошибок в разделе «Сравнительные конструкции», 
* «gram14» -- количество ошибок в разделе «Инфинитивные конструкции», 
* «leks15» -- количество ошибок в разделе «Лексика», 
* «leks16» -- количество ошибок в разделе «Выбор лексемы», 
* «leks17» -- количество ошибок в разделе «Устойчивые обороты», 
* «leks18» -- количество ошибок в разделе «Словообразование», 
* «diskurs19» -- количество ошибок в разделе «Дискурс», 
* «diskurs20» -- количество ошибок в разделе «Логика», 
* «diskurs21» -- количество ошибок в разделе «Референтные связи внутри текста»,
* «diskurs22» -- количество ошибок в разделе «Стиль», 
* «g1» -- количество ошибок с уровнем грубости 1, 
* «g2» -- количество ошибок с уровнем грубости 2, 
* «g3» -- количество ошибок с уровнем грубости 3,
* «numsent» -- количество предложений в тексте, 
* «numtoken» -- количество слов в тексте, 
* «numchar» -- количество символов в тексте.

**MarkModelDataTo\_scv**(file, user, password, host, database) -- функция формирования массива исходных данных на основе базы данных корпуса для обучения искусственной нейронной сети для формирования оценки текста. Параметры: *file* -- имя файла, в который будут записаны данные, *user* -- имя пользователя базы данных, *password* -- пароль пользователя базы данных, *host* -- адрес базы данных, *database* -- имя базы данных.

**GetGrossError**(textError, textCorrect) -- функция для определения грубости ошибки. Параметры: *textError* -- предложение с ошибкой, *textCorrect* -- предложение с исправленной ошибкой. Возвращает кортеж, включающий уровень грубости ошибки, текстовые формулировки грубости ошибки на немецком и русском языках, значение, возвращенное нейронной сетью, если в качестве модели были использованы сеть с косинусной мерой или кросс-энкодер. Если в качестве модели были использованы сети BERT, то кортеж содержит три значения, выданные сетью, соответствующие величине соответствия каждому уровню грубости ошибки.

**GetTextMark**(Val) -- функция для формирования оценки текста. Параметры: *Val* --список списков со статистикой ошибок в тексте в формате \[\[\<список статистики ошибок для первого текста\>\],...\]. <Список статистики ошибок для текста> в формате:
«gram», «leks», «punkt», «orpho», «diskurs», «skips», «extra», «g1», «g2», «g3», «numtoken». Возвращает список оценок.

**getGrossModel**(pathname) -- функция для выгрузки предобученной модели для определения грубости ошибки в заданную папку. Параметры: *pathname* -- имя папки, в котурую будет сохранена модель.

**getMarkModel**(pathname) -- функция для выгрузки предобученной модели для определения оценки текста в заданную папку. Параметры: *pathname* -- имя папки, в котурую будет сохранена модель.

# Сценарии работы с библиотекой

Перед первым запуском необходимо установить все необходимые библиотеки для _Python_:
```
pip install -r requirements.txt
```

Для работы с библиотекой могут потребоваться файлы с данными для обучения [dataset/sent_data.csv](sent_data.csv) и
[text_data.csv](dataset/text_data.csv), которые находятся в папке [dataset](dataset).

## 1. Работа с моделью определения грубости ошибки

### Обучение новой модели на имеющемся наборе обучающих данных, сохранение модели

Алгоритм:
* Разместить в рабочей папке файл с данными для обучения "sent_data.csv".
* Импортировать класс GrossModel из модуля grading_module.gross_model.
* Создать объект класса GrossModel для выбранного типа модели.
* Вызвать метод для загрузки данных для обучения.
* Вызвать метод для обучения модели.
* Вызвать метод для сохранения модели с параметром, описывающим путь и название папки, в которую модель будет сохранена.

#### Сценарий 1.1 -- Обучение и сохранение модели с использованием косинусной меры
Исходные данные для обучения находятся в файле "sent_data.csv". 
```
import pandas as pd
from grading_module.gross_model import GrossModel
# файл с данными для обучения
fileName = 'sent_data.csv'
# создание модели
myModel = GrossModel(modeltype = 'CosMeasure', score=[0.97, 0.9, 0.8])
# загрузка данных, доля данных для тестирования равна 0 (все данные используются для обучения)
myModel.load_data(file=fileName, testpart=0)
# обучение модели на 10 эпохах 
myModel.fit(num_epochs = 10, learning_rate = 2e-5)
# получение значения метрики accuracy
df = pd.read_csv(fileName, sep = ';')
print(myModel.get_accuracy([df['sent'].to_list(), df['sentcorrect'].to_list(), df['level'].to_list()]))
# получение значения метрики accuracy и матрицы ошибок
m, acc = myModel.get_accuracy_m([df['sent'].to_list(), df['sentcorrect'].to_list(), df['level'].to_list()])
# печать матрицы ошибок
print(m)
# сохранение моделии в папке "model_Cos"
myModel.save_model(pathname = 'model_Cos')
```

#### Сценарий 1.2 -- Обучение и сохранение модели с использованием кросс-энкодера

```
import pandas as pd
from grading_module.gross_model import GrossModel
# файл с данными для обучения
fileName = 'sent_data.csv'
# создание модели
myModel = GrossModel(modeltype = 'CrossEncoder2', score=[0.97, 0.9, 0.83])
# Или: myModel = GrossModel(modelType = 'CrossEncoder', score=[0.97, 0.9, 0.83])
# загрузка данных, доля данных для тестирования равна 0
myModel.load_data(file=fileName, testpart=0)
# обучение модели на 10 эпохах
myModel.fit(num_epochs = 10, learning_rate = 2e-5)
# получение значения метрики accuracy
df = pd.read_csv(fileName, sep = ';')
print(myModel.get_accuracy([df['sent'].to_list(), df['sentcorrect'].to_list(), df['level'].to_list()]))
# получение значения метрики accuracy и матрицы ошибок
m, acc = myModel.get_accuracy_m([df['sent'].to_list(), df['sentcorrect'].to_list(), df['level'].to_list()])
# печать матрицы ошибок
print(m)
# сохранение модели в папке "model_Cross"
myModel.save_model(pathname ='model_Cross')
```

#### Сценарий 1.3 -- Обучение и сохранение модели с использованием BERT

```
import pandas as pd
from grading_module.gross_model import GrossModel
# файл с данными для обучения
fileName = 'sent_data.csv'
# создание модели
myModel = GrossModel(modeltype = 'BERTModel')
# Или: myModel = GrossModel(modelType = 'distilBERTModel')
# загрузка данных
myModel.load_data(file=fileName)
# обучение модели на 10 эпохах 
myModel.fit(num_epochs = 10, learning_rate = 2e-5)
# получение значения метрики accuracy
df = pd.read_csv(fileName, sep = ';')
print(myModel.get_accuracy([df['sent'].to_list(), df['sentcorrect'].to_list(), df['level'].to_list()]))
# получение значения метрики accuracy и матрицы ошибок
m, acc = myModel.get_accuracy_m([df['sent'].to_list(), df['sentcorrect'].to_list(), df['level'].to_list()])
# печать матрицы ошибок
print(m)
# сохранение модели в папке "model_Bert"
myModel.save_model(pathname ='model_Bert')
```

#### Сценарий 1.4 -- Обучение модели с использованием кросс-энкодера и вывод графика значений метрики accuracy для обучающей и тестовой выборок
Исходные данные из файла "sent_data.csv" разделяются на две части.  Первые записи в файле записываются в обучающую выборку, 10% записей в конце файла записываются в тестовую выборку. В процессе обучения сети для каждой эпохи фиксируются значения метрик качества обучения (accuracy). Измеряется время, затраченное на выполнение обучения. 

```
from grading_module.gross_model import GrossModel
import time
import matplotlib.pyplot as plt
import pandas as pd
# файл с данными для обучения
fileName = 'sent_data.csv'
df = pd.read_csv(fileName, sep = ';')
myModel = GrossModel(modeltype = 'CrossEncoder2', score=[0.98, 0.93, 0.87])
myModel.load_data(file=fileName, testpart=0.1)
# Количество данных для тестирования
num = myModel.test_shape
# массивы данных обучающей выборки
train_sent = df[:-num]['sent'].to_list() # предложения с ошибкой
train_correct = df[:-num]['sentcorrect'].to_list() # предложения без ошибки
train_level = df[:-num]['level'].to_list() # уровень грубости ошибки
# массивы данных тестовой выборки
test_sent = df[-num:]['sent'].to_list()
test_correct = df[-num:]['sentcorrect'].to_list()
test_level = df[-num:]['level'].to_list()
start_time = time.time() ## точка отсчета времени
m_test = [] ## метрики обучения на обучающей выборке для каждой эпохи
m_train = [] ## метрики обучения на тестовой выборке для каждой эпохи
# расчет метрик до обучения
matrix_train, acc_train = myModel.get_accuracy_m([train_sent,train_correct,train_level])
matrix_test, acc_test = myModel.get_accuracy_m([test_sent,test_correct,test_level])
print('Эпоха 0')
print('Accuracy на обучающей выборке: ' + str(round(acc_train,4)) + '; Accuracy на тестовой выборке: ' + str(round(acc_test,4)))
print(matrix_test)
m_train.append(acc_train)
m_test.append(acc_test)
# Цикл обучения
epochs = 2  # количество эпох
for i in  range(epochs):
    print('Эпоха ' + str(i+1))
    myModel.fit(num_epochs = 1, learning_rate = 2e-5)
    # расчет метрик после обучения на одной эпохе
    matrix_train, acc_train = myModel.get_accuracy_m([train_sent,train_correct,train_level])
    matrix_test, acc_test = myModel.get_accuracy_m([test_sent,test_correct,test_level])
    print('Accuracy на обучающей выборке: ' + str(round(acc_train,4)) + '; Accuracy на тестовой выборке: ' + str(round(acc_test,4)))
    print(matrix_test)
    m_train.append(acc_train)
    m_test.append(acc_test)
# время окончания обучения
end_time = time.time() - start_time
print('--------------------------------------------')
print('Время обучения: ' + str(int(end_time) // 60) + ' минут ' + str(int(end_time) % 60) + ' секунд')
print('Точность обучения: ' + str(round(max(m_train),4)))
# вывод графика обучения
t_epoch = range(epochs+1)
plt.plot(t_epoch, m_train, t_epoch, m_test)
plt.legend(['train', 'test'])
plt.show()
```
### Использование своей обученной модели для получения грубости ошибки

Алгоритм:
* Обучить свою модель и сохранить ее в папке по одному из сценариев 1.1--1.3.
* Папку с обученной моделью разместить в рабочей папке.
* Импортировать класс GrossModel из модуля grading_module.gross_model.
* Создать объект класса GrossModel, имеющую тип, совпадающий с типом обученной модели.
* Вызвать метод загрузки модели с параметром, описывающим путь и название папки, где расположена сохраненная модель.
* Вызвать метод для предсказания по модели.

#### Сценарий 1.5 -- Получение уровней грубости ошибок по своей обученной модели
Пусть, была обучена модель типа CosMeasure. Модель была сохранена в папке "model_Cos" (Сценарий 1.1)

```
from grading_module.gross_model import GrossModel
myModel = GrossModel(modeltype = 'CosMeasure')
myModel.load_model(pathname='model_Cos')
res = myModel.predict([['Jetzt muss man sich auf Abende und die Wochenenden undkonzentrieren.'], ['Jetzt muss man sich auf Abende und die Wochenenden konzentrieren.']])
print([res[i][2:][1:4] for i in  range(len(res))])```
```
#### Сценарий 1.6 -- Получение уровней грубости ошибок по своей обученной модели
Пусть, была обучена модель типа BERTModel. Модель была сохранена в папке "model_Bert" (Сценарий 1.3)

```
from grading_module.gross_model import GrossModel
myModel = GrossModel(modeltype = 'BERTModel')
myModel.load_model(pathname='model_Bert')
res = myModel.predict([['Jetzt muss man sich auf Abende und die Wochenenden undkonzentrieren.'], ['Jetzt muss man sich auf Abende und die Wochenenden konzentrieren.']])
print([[res[i][2],res[i][4],res[i][5]] for i in  range(len(res))])
```

### Использование предобученной модели для получения грубости ошибки

Предобученная модель основана на кросс-энкодере.
Предобученная модель находится по адресу https://huggingface.co/remshu-inc/mencoder.

Алгоритм:
* Создать в рабочей папке папку с именем "model_gross".
* Импортировать функции GetGrossError и getGrossModel из модуля grading_module.common.
* Вызвать функцию getGrossModel() с параметром "model_gross".
* Вызвать функцию GetGrossError() с данными: предложение с ошибками, правильное предложение.

#### Сценарий 1.7 -- Получение уровней грубости ошибок для предобученной модели

```
from grading_module.common import GetGrossError, getGrossModel
getGrossModel('model_gross')
GetGrossError('Jetzt muss man sich auf Abende und die Wochenenden undkonzentrieren.', 'Jetzt muss man sich auf Abende und die Wochenenden konzentrieren.')
```

## Работа с моделью выставления оценки за текст

### Обучение новой модели на имеющемся наборе обучающих данных, сохранение модели

Алгоритм:
* Разместить в рабочей папке файл с данными для обучения "text_data.csv".
* Импортировать класс MarkModel из модуля grading_module.mark_model.
* Создать объект класса MarkModel с параметрами, описывающими количество нейронов в каждом слое, включая входной и выходной,  и типом модели.
* Вызвать метод для загрузки данных из csv-файла.
* Вызвать метод для обучения модели с параметром, описывающим количество эпох обучения.
* Вызвать метод для сохранения модели с параметром, описывающим путь и название папки, в которую модель будет сохранена.

#### Сценарий 2.1 -- для модели с 10 входными нейронами и нормированием на количество токенов
```
from grading_module.mark_model import MarkModel
# создание модели с 5-ю слоями: 
# входной слой содержит 10 нейронов, 
# следующий слой содержит 20 нейронов, 
# следующий - 12, 
# следующий - 5, 
# выходной слой содержит 1 нейрон
myModel = MarkModel(listlayers = [10,20,12,5,1])
# загрузка данных для обучения из файла "text_data.csv"
myModel.load_data('text_data.csv')
# обучение модели на 10 эпохах
myModel.fit(num_epochs = 10)
# получить значение метрики - Сумма разностей оценок
print(myModel.val([[1,1,0,0,0,0,0,1,1,0,512],[1,3,0,3,0,0,0,2,5,0,752]], [10,5]))
# сохранение модели в папке "model_10_numtoken"
myModel.save_model('model_10_numtoken')
```

#### Сценарий 2.2 -- для модели с 32 входными нейронами и нормированием на количество токенов
```
from grading_module.mark_model import MarkModel
myModel = MarkModel(listlayers = [32,10,5,1])
myModel.load_data('text_data.csv')
myModel.fit(num_epochs = 10)
# сохранение модели в папке "model_32_numtoken"
myModel.save_model('model_32_numtoken')
```

#### Сценарий 2.3 -- для модели с 10 входными нейронами и нормированием на количество предложений
```
from grading_module.mark_model import MarkModel
myModel = MarkModel(listlayers = [10,16,8,4,1], norm='numsent')
myModel.load_data('text_data.csv')
myModel.fit(num_epochs = 10)
myModel.save_model('model_10_numsent')
```

#### Сценарий 2.4 -- для модели с 32 входными нейронами и нормированием на количество предложений
```
from grading_module.mark_model import MarkModel
myModel = MarkModel(listlayers = [32,16,8,4,1], norm='numsent')
myModel.load_data('text_data.csv')
myModel.fit(num_epochs = 10)
myModel.save_model('model_32_numsent')
```

#### Сценарий 2.5 -- для модели с 13 входными нейронами, без нормирования
```
from grading_module.mark_model import MarkModel
myModel = MarkModel(listlayers = [13,16,8,4,1], norm='all')
myModel.load_data('text_data.csv')
myModel.fit(num_epochs = 10)
myModel.save_model('model_13_all')
```

#### Сценарий 2.6 -- для модели с 35 входными нейронами, без нормирования
```
from grading_module.mark_model import MarkModel
myModel = MarkModel(listlayers = [35,16,8,4,1], norm='all')
myModel.load_data('text_data.csv')
myModel.fit(num_epochs = 10)
myModel.save_model('model_35_all')
```

### Использование своей обученной модели для получения оценки

Алгоритм:
* Обучить свою модель и сохранить ее в папке по одному из сценариев 2.1--2.6.
* Папку с обученной моделью разместить в рабочей папке.
* Импортировать класс MarkModel из модуля grading_module.mark_model.
* Создать объект класса MarkModel с параметром, описывающим путь и название папки, где расположена сохраненная модель.
* Вызвать метод для предсказания по модели.


#### Сценарий 2.7 -- Получение оценки по своей обученной модели

Пусть, была обучена модель с 32 входными нейронами и нормированием на количество токенов. Модель была сохранена в папке "model_32_numtoken" (Сценарий 2.2)

```
from grading_module.mark_model import MarkModel
myModel = MarkModel(modelpath='model_32_numtoken')
# получить оценку для одного текста
print(myModel.predict([[1,1,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,512]]))
# получить оценку для нескольких текстов
print(myModel.predict([[1,1,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,512],[1,3,0,3,0,0,0,2,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,752]]))
```

### Использование предобученной модели для получения оценки

Предобученная модель содержит 10 входных нейронов и нормируется на количество токенов в предложении.
Предобученная модель находится по адресу https://huggingface.co/remshu-inc/mmark.

Алгоритм:
* Создать в рабочей папке папку с именем "model_mark".
* Импортировать функции GetTextMark и getMarkModel из модуля grading_module.common.
* Вызвать функцию getMarkModel () с параметром "model_mark".
* Вызвать функцию GetTextMark() с данными о тексте.


#### Сценарий 2.8 -- Получение оценки по предобученной модели
```
from grading_module.common import GetTextMark, getMarkModel
getMarkModel('model_mark')
# получить оценку для одного текста
print(GetTextMark([[1,1,0,0,0,0,0,1,1,0,512]]))
# получить оценку для нескольких текстов
print(GetTextMark([[1,1,0,0,0,0,0,1,1,0,512],[1,1,6,1,1,0,0,6,5,5, 252]]))
```