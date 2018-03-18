print('''
Python3-скрипт, добавляющий "приставку" chr к номеру хромосомы в BED-таблицах.
Автор: Платон Быкадоров, 2018.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Часто встречаю правильно сформированные BED-таблицы,
но в которых хромосома обозначена одним лишь числом.
Я стараюсь обеспечивать поддержку таких файлов в своих скриптах,
но многие сторонние программы, например, BEDTools,
переваривают только канонический BED.
Этот элементарный скрипт добавит недостающие приставки chr
к номерам хромосом в начале каждой строки.
''')

import os
import re

source_dir = input('Путь к папке с исходными файлами: ')
target_dir = input('Путь к папке с конечными файлами: ')

source_files = os.listdir(source_dir)
for source_file in source_files:
        with open(os.path.join(source_dir, source_file)) as sf_opened:
                with open(os.path.join(target_dir, source_file), 'w') as tf_opened:
                        for line in sf_opened:

                                #Если в начале текущей строки не содержатся расположенные друг за другом номер хромосомы,
                                #табуляция и координата, то эта строка будет прописываться в конечный файл в неизменном виде.
                                #Это необходимо для правильной обработки хэдеров таблицы.
                                if re.match(r'\d+\t\d+', line) == None:
                                        tf_opened.write(line)
                                        continue
                                else:
                                        tf_opened.write('chr' + line)
