print('''
Python3-скрипт, выводящий первые n строк большого текстового файла.
Автор: Платон Быкадоров (platon.work@gmail.com), 2018.
Версия: V2.2.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Простое руководство по установке среды разработки и запуску скриптов:
github.com/PlatonB/bioinformatic-python-scripts#Установка-среды-разработки

Файлы, размеры которых исчисляются гигабайтами, практически
невозможно предпросмотреть на обычном десктопе.
Этот скрипт позволяет определить по первым строкам,
из каких столбцов состоит огромная таблица.
Ознакомление с общим видом таблицы сделает возможным
создавать специализированные программы для её обработки.

Не выводите не экран слишком много строк (тысячи), т.к.
консоль, в которой вы запускаете скрипт, может зависнуть.
''')

import sys, os

src_file_path = input('Путь к исходному файлу: ')
str_quan = int(input('\nКоличество выводимых или перенаправляемых строк: '))
redirection = input('''\nПеренаправить результат в отдельный файл?
(игнорирование ввода ==> вывести результат на экран)
[redirect|<enter>]: ''')
if redirection != 'redirect' and redirection != '':
        print(f'{redirection} - недопустимая опция')
        sys.exit()
with open(src_file_path) as src_file_opened:
        if redirection == 'redirect':
                trg_dir_path = input('\nПуть к папке для конечного файла: ')
                '.'.join(os.path.basename(src_file_path).split('.')[:-1])
                trg_file_name = '.'.join(os.path.basename(src_file_path).split('.')[:-1]) + '_fir_' + str(str_quan) + '.txt'
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
