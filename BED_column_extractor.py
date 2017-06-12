print('''
Этот Python3-скрипт копирует в отдельный (-ые) файл (-ы) необходимые пользователю столбцы одной или нескольких BED-таблиц.
Автор: Платон Быкадоров, 2017.
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

sourcedir = input('Путь к папке с исходными файлами (не забывать экранировать): ')
columnlist = [int(number) for number in input('Номер одного столбца или номера нескольких столбцов через пробел: ').split()]
targetdir = input('Путь к папке с конечными файлами (не забывать экранировать): ')

import os
import csv

sourcefiles = os.listdir(sourcedir)

for sourcefile in sourcefiles:
        s = open(os.path.join(sourcedir, sourcefile))
        sourcetable = list(csv.reader(s, delimiter = '\t'))
        s.close()

        bed = []
        for row in sourcetable:
                if row[0].find('#') != -1 or row[0].find('track name=') != -1:
                        header = row[0]
                        continue
                bedrow = []
                for number in columnlist:
                        bedrow.append(row[number - 1])
                bed.append('\t'.join(bedrow))

        targetfile = sourcefile.split('.')[0] + '_' + 'col' + '_'.join([str(number) for number in columnlist]) + '.txt'
        t = open(os.path.join(targetdir, targetfile), 'w')
        if header != None:
                t.write(header + '\n')
        for line in bed:
                t.write(line + '\n')
        t.close()
