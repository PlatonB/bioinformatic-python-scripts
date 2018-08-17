print('''
Python3-скрипт, выводящий первые n строк большого текстового файла.
Автор: Платон Быкадоров (platon.work@gmail.com), 2018.
Версия: V2.0.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Файлы, размеры которых исчисляются гигабайтами, практически
невозможно предпросмотреть на обычном десктопе.
Этот скрипт позволяет определить по первым строкам,
из каких столбцов состоит огромная таблица.
Ознакомление с общим видом таблицы сделает возможным
создавать специализированные программы для её обработки.

Не выводите не экран слишком много строк (тысячи), т.к.
консоль, в которой вы запускаете скрипт, может зависнуть.
''')

import os

src_file_path = input('Путь к исходному файлу: ')
str_quan = int(input('Количество выводимых или перенаправляемых строк: '))
redirection = input('''Перенаправить результат в отдельный файл?
[redirect|<enter>]: ''')
with open(src_file_path) as src_file_opened:
        if redirection == 'redirect':
                trg_dir_path = input('Путь к папке для конечного файла: ')
                trg_file_name = os.path.basename(src_file_path).split('.')[0] + '_fir_' + str(str_quan) + '.txt'
                with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
                        for num in range(str_quan):
                                line = src_file_opened.readline()
                                if line.find('\n') == -1:
                                        line += '\n'
                                trg_file_opened.write(line)
        else:
                for num in range(str_quan):
                        line = src_file_opened.readline().split('\n')[0]
                        print(line)
