"""
Получение оценки по предобученной модели
"""

from grading_module.common import GetTextMark, getMarkModel


if __name__ == "__main__":
    getMarkModel('model_mark')
    # получить оценку для одного текста
    print(GetTextMark([[1,1,0,0,0,0,0,1,1,0,512]]))
    # получить оценку для нескольких текстов
    print(GetTextMark([[1,1,0,0,0,0,0,1,1,0,512],[1,1,6,1,1,0,0,6,5,5, 252]]))
