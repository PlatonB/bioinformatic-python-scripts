print('''
Этот Python3-скрипт копирует в отдельные файлы необходимые пользователю столбцы.
Автор: Платон Быкадоров (platon.work@gmail.com), 2017-2018.
Версия: V2.1.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Пример.
Первые 7 столбцов таблицы аннотаций трёх SNP:
rs12896956	14:105767258-105767258	T	intron_variant	MODIFIER	IGHG3	ENSG00000211897
rs12897751	14:105767411-105767411	C	intron_variant	MODIFIER	IGHG3	ENSG00000211897
rs3020575	14:105760146-105760146	A	downstream_gene_variant	MODIFIER	IGHG3	ENSG00000211897
Оставляем только столбцы с refSNPID и Official Gene Symbol (1-й и 6-й):
rs12896956	IGHG3
rs12897751	IGHG3
rs3020575	IGHG3
''')

src_dir_path = input('Путь к папке с исходными файлами: ')
trg_dir_path = input('\nПуть к папке для конечных файлов: ')
num_of_headers = input('''\nКоличество не обрабатываемых строк в начале файла
(совет: табулированную шапку к ним не причисляйте)
(игнорирование ввода ==> производить работу для всех строк)
[0(|<enter>)|1|2|...]: ''')
if num_of_headers == '':
        num_of_headers = 0
else:
        num_of_headers = int(num_of_headers)
col_numbers = [int(col_number) for col_number in input('''\nНомер одного или номера нескольких экстрагируемых столбцов
(через пробел): ''').split()]

import os

src_file_names = os.listdir(src_dir_path)
for src_file_name in src_file_names:
        with open(os.path.join(src_dir_path, src_file_name)) as src_file_opened:
                
                #Конструируемое ниже имя конечного файла
                #будет содержать номера выделенных столбцов.
                trg_file_name = src_file_name.split('.')[0] + '_col' + \
                                '+'.join([str(col_number) for col_number in col_numbers]) + '.txt'
                
                with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
                        
                        #Формирование списка хэдеров и добавление хэдеров в конечный файл.
                        #Курсор смещается к началу основной части таблицы.
                        headers = [src_file_opened.readline() for header_index in range(num_of_headers)]
                        for header in headers:
                                if header.find('\n') == -1:
                                        header += '\n'
                                trg_file_opened.write(header)
                                
                        #Эффективная с точки зрения использования RAM
                        #работа с основной частью таблицы.
                        for line in src_file_opened:
                                src_row = line.split('\t')
                                
                                #Формирование списка, содержащего ячейки
                                #только запрашиваемых столбцов.
                                trg_row = [src_row[col_number - 1] for col_number in col_numbers]
                                
                                #Прописывание результатов в конечный файл.
                                if trg_row[-1].find('\n') == -1:
                                        trg_row[-1] += '\n'
                                trg_file_opened.write('\t'.join(trg_row))
