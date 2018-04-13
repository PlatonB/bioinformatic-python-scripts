print('''
Этот Python3-скрипт копирует в отдельные файлы необходимые пользователю столбцы BED-таблиц.
Автор: Платон Быкадоров, 2017-2018.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Формат BED:

#Заголовок со знаком решётки в начале, либо такого вида:
track name="Заголовок" description="Заголовок по стандатрам UCSC Table Browser. Любые заголовки BED-таблиц для этого скрипта необязательны" visibility=3 url=
chr6 (или 6)	32665241	32665242	(опционально) дополнительные поля, разделённые табуляциями
chr6 (или 6)	32665244	32665245	(опционально) дополнительные поля, разделённые табуляциями
...

В исходной папке не должно находиться ничего, кроме BED-файлов, с которыми будет работать скрипт.
''')

source_dir = input('Путь к папке с исходными файлами: ')
columns_numbers = input('Номер одного столбца или номера нескольких столбцов через пробел: ').split()
target_dir = input('Путь к папке с конечными файлами: ')

import os
import csv

source_files = os.listdir(source_dir)
for source_file in source_files:
        with open(os.path.join(source_dir, source_file)) as sf_opened:

                #Создание двумерного массива по данным из исходной таблицы.
                two_dim = list(csv.reader(sf_opened, delimiter = '\t'))

                #Обработка хэдэра.
                if two_dim[0][0].find('#') != -1 or two_dim[0][0].find('track name=') != -1:
                        header = two_dim[0][0]
                else:
                        print('Ошибка. В файле ' + source_file + ' отсутствует или неправильно оформлен хэдер.')
                        break

                #Создание конечного двумерного массива, содержащего только запрашиваемые "столбцы".
                trun_two_dim = [[row[int(column_number) - 1] for column_number in columns_numbers] for row in two_dim[1:]]
                                
                #Формирование конечного файла.
                target_file = source_file.split('.')[0] + '_' + 'col' + '_'.join(columns_numbers) + '.txt'
                with open(os.path.join(target_dir, target_file), 'w') as tf_opened:
                        tf_opened.write(header + '\n')
                        for row in trun_two_dim:
                                tf_opened.write('\t'.join(row) + '\n')
