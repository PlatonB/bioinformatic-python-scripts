print('''
Python3-скрипт, дополняющий ячейки заданных столбцов определённой строкой
(под строкой здесь и далее подразумевается любой введённый пользователем набор символов, добавляемый к ячейкам).
Автор: Платон Быкадоров, 2018.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Пример: добавление "приставки" chr к номеру хромосомы в BED-таблицах.
Было:
6	32768325	32768326	rs9296043
6	32430006	32430007	rs3129852
6	31475792	31475793	rs2516516

Стало:
chr6	32768325	32768326	rs9296043
chr6	32430006	32430007	rs3129852
chr6	31475792	31475793	rs2516516
''')

import os

src_dir_path = input('Путь к папке с исходными файлами: ')
trg_dir_path = input('Путь к папке для конечных файлов: ')
col_numbers = [int(col_number) for col_number in input('''Номер одного или номера нескольких дополняемых столбцов
(через пробел): ''').split()]
addition = input('Строка, которой будут дополнены ячейки указанных столбцов: ')
addition_loc = input('Расположение добавляемой строки относительно каждой ячейки [left|right]: ')
num_of_headers = int(input('''Количество не считываемых строк в начале файла
(хэдер, шапка таблицы и т.д.) [0|1|2|(...)]: '''))

src_file_names = os.listdir(src_dir_path)
for src_file_name in src_file_names:
        with open(os.path.join(src_dir_path, src_file_name)) as src_file_opened:
                with open(os.path.join(trg_dir_path, src_file_name), 'w') as trg_file_opened:

                        #Формирование списка хэдеров и добавление хэдеров в конечный файл.
                        #Курсор смещается к началу основной части таблицы.
                        headers = [src_file_opened.readline() for header_index in range(num_of_headers)]
                        for header in headers:
                                trg_file_opened.write(header)

                        #Обработка основной части таблицы.
                        #Во избежание переполнения оперативной памяти,
                        #исходный файл не будет преобразовываться в двумерный массив.
                        #Каждая строка будет приводиться в окончательный вид
                        #непосредственно после считывания из файла.
                        for line in src_file_opened:
                                row = line.split('\t')

                                #Введённая пользователем строка добавляется к ячейкам
                                #либо слева, либо справа - в зависимости от указанной
                                #им соответствующей опции.
                                for col_number in col_numbers:
                                        if addition_loc == 'left':
                                                row[col_number - 1] = addition + row[col_number - 1]
                                        elif addition_loc == 'right':
                                                row[col_number - 1] += addition
                                
                                if row[-1].find('\n') == -1:
                                        row[-1] += '\n'
                                trg_file_opened.write('\t'.join(row))
