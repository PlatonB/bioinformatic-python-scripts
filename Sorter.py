print('''
Python3-скрипт, сортирующий таблицу по указанным пользователем столбцам.
Автор: Платон Быкадоров, 2018.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

В каждом из столбцов, по которым сортируется таблица,
должен быть только 1 тип данных: либо числа (в т.ч. дробные с разделителем точкой),
либо наборы символов, в которых хотя бы один символ - нечисловой (пример: rs1051112).
''')

import os

src_dir_path = input('Путь к папке с исходными файлами: ')
trg_dir_path = input('Путь к папке для конечных файлов: ')
col_numbers = input('Номер одного или номера нескольких сортируемых столбцов (через пробел): ').split()
num_of_headers = int(input('''Количество не считываемых строк в начале файла
(хэдер, шапка таблицы и т.д.) [0|1|2|(...)]: '''))

src_file_names = os.listdir(src_dir_path)
for src_file_name in src_file_names:
        with open(os.path.join(src_dir_path, src_file_name)) as src_file_opened:

                #Формирование списка хэдеров.
                #Курсор смещается к началу основной части таблицы.
                headers = [src_file_opened.readline() for header_index in range(num_of_headers)]

                #Основная часть таблицы преобразуется в двумерный массив.
                src_table = [line.split('\t') for line in src_file_opened]

        #Формирование двумерного массива, для каждого
        #элемента которого определён тип данных.
        #Это необходимо для правильной сортировки,
        #чтобы, к примеру, после 19 не шло 2.
        for row_index in range(len(src_table)):
                for cell_index in range(len(src_table[row_index])):
                        try:
                                src_table[row_index][cell_index] = int(src_table[row_index][cell_index])
                        except ValueError:
                                try:
                                        src_table[row_index][cell_index] = float(src_table[row_index][cell_index])
                                except ValueError:
                                        pass
        
        #Сортировка.
        src_table.sort(key = lambda row: [row[int(col_number) - 1] for col_number in col_numbers])
                
        trg_file_name = src_file_name.split('.')[0] + '_' + 'srtd' + '.txt'
        with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
                for header in headers:
                        trg_file_opened.write(header)
                for row in src_table:
                        if str(row[-1]).find('\n') == -1:
                                row[-1] = str(row[-1]) + '\n'
                        trg_file_opened.write('\t'.join([str(cell) for cell in row]))
