"""
Получение уровней грубости ошибок для предобученной модели
"""

from grading_module.common import GetGrossError, getGrossModel

if __name__ == "__main__":
    getGrossModel('model_gross')
    result = GetGrossError('Jetzt muss man sich auf Abende und die Wochenenden undkonzentrieren.',
                  'Jetzt muss man sich auf Abende und die Wochenenden konzentrieren.')
    print(result)
