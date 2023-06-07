import time
import matplotlib.pyplot as plt
import pandas as pd

from grading_module import GrossModel

if __name__ == "__main__":
    # файл с данными для обучения
    fileName = 'data.csv'
    df = pd.read_csv(fileName, sep=';')
    # создание модели
    myModel = GrossModel(model_type='CrossEncoder2', score=[0.98, 0.93, 0.87])
    myModel.load_data(fileName)
    # Количество данных для тестирования
    num = myModel.test_shape
    train_sent = df[:-num]['sent'].to_list()
    train_correct = df[:-num]['sentcorrect'].to_list()
    train_level = df[:-num]['level'].to_list()
    test_sent = df[-num:]['sent'].to_list()
    test_correct = df[-num:]['sentcorrect'].to_list()
    test_level = df[-num:]['level'].to_list()

    ep = 40  ## Количество эпох
    lr = 2e-5  ## learning_rate

    start_time = time.time()  ## точка отсчета времени
    result = []  ## результаты обучения для каждой эпохи
    y_test = []  ## результаты на обучающей выборке для каждой эпохи
    y_train = []  ## результаты на тестовой выборке для каждой эпохи
    # расчет метрик до обучения
    r_matrix_train, r_train = myModel.get_accuracy_m(train_sent, train_correct, train_level)
    r_matrix_test, r_test = myModel.get_accuracy_m(test_sent, test_correct, test_level)
    print('Эпоха 0')
    print('Тестовая: ' + str(round(r_test, 4)) + '; Обучающая: ' + str(round(r_train, 4)))
    print(r_matrix_test)
    result.append((0, r_test, r_train))
    y_test.append(r_test)
    y_train.append(r_train)

    # Цикл обучения
    for i in range(ep):
        print('Эпоха ' + str(i + 1))
        myModel.fit(num_epochs=1, learning_rate=lr)
        # расчет метрик после обучения на одной эпохе
        r_matrix_train, r_train = myModel.get_accuracy_m(train_sent, train_correct, train_level)
        r_matrix_test, r_test = myModel.get_accuracy_m(test_sent, test_correct, test_level)
        print('Тестовая: ' + str(round(r_test, 4)) + '; Обучающая: ' + str(round(r_train, 4)))
        print(r_matrix_test)
        result.append((0, r_test, r_train))
        y_test.append(r_test)
        y_train.append(r_train)

    end_time = time.time() - start_time
    print('--------------------------------------------')
    print('Время: ' + str(int(end_time) // 60) + ' минут ' + str(int(end_time) % 60) + ' секунд')

    print('Точность обучения: ' + str(round(max(y_train), 4)))

    # вывод графика обучения
    t_epoch = range(ep + 1)
    plt.plot(t_epoch, y_test, t_epoch, y_train)
    plt.legend(['test', 'train'])
    plt.show()
