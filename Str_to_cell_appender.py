print('''
Python3-скрипт, дополняющий ячейки заданных столбцов определённой строкой
(под строкой здесь и далее подразумевается любой введённый
пользователем набор символов, добавляемый к ячейкам).
Автор: Платон Быкадоров (platon.work@gmail.com), 2018.
Версия: V1.2.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Простое руководство по установке среды разработки и запуску скриптов:
github.com/PlatonB/bioinformatic-python-scripts#Установка-среды-разработки

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

import sys, os

src_dir_path = input('Путь к папке с исходными файлами: ')
trg_dir_path = input('\nПуть к папке для конечных файлов: ')
num_of_headers = input('''\nКоличество не обрабатываемых строк
в начале каждой исходной таблицы
(игнорирование ввода ==> хэдеров/шапок в таблицах нет)
[0(|<enter>)|1|2|...]: ''')
if num_of_headers == '':
        num_of_headers = 0
else:
        num_of_headers = int(num_of_headers)
col_numbers = [int(col_number) for col_number in input('''\nНомер одного или номера нескольких дополняемых столбцов
(через пробел): ''').split()]
addition = input('\nСтрока, которой будут дополнены ячейки указанных столбцов: ')
addition_loc = input('''\nРасположение добавляемой строки относительно каждой ячейки
[left|right]: ''')
if addition_loc != 'left' and addition_loc != 'right':
        print('''\nОшибка. Некорректно указано, с какой стороны добавлять строку''')
        sys.exit()

#Перебор исходных файлов и создание конечных.
src_file_names = os.listdir(src_dir_path)
for src_file_name in src_file_names:
        with open(os.path.join(src_dir_path, src_file_name)) as src_file_opened:
                src_file_base = '.'.join(src_file_name.split('.')[:-1])
                src_file_ext = '.' + src_file_name.split('.')[-1]
                trg_file_name = src_file_base + '_extnd' + src_file_ext
                with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
                        
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
                                row = line.split('\n')[0].split('\t')
                                
                                #Введённая пользователем строка добавляется к
                                #ячейкам либо слева, либо справа - в зависимости
                                #от указанной им соответствующей опции.
                                for col_number in col_numbers:
                                        if addition_loc == 'left':
                                                row[col_number - 1] = addition + row[col_number - 1]
                                        elif addition_loc == 'right':
                                                row[col_number - 1] += addition
                                                
                                #Прописываем строку в конечный файл.
                                trg_file_opened.write('\t'.join(row) + '\n')
