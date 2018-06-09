print('''
Python3-скрипт, фильтрующий строки таблиц Ensembl VEP по границам частот SNP в популяциях.
Автор: Платон Быкадоров, 2018.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

На вход подаётся таблица SNP, проаннотированных в Ensembl Variant Effect Predictor (VEP)
с флагом, выводящим частоты их встречаемости в различных популяциях.
При запуске скрипта вы должны указать одну или несколько
популяций и пороги частот SNP в этих популяциях.
Скрипт отсечёт SNP, выходящие хотя бы за один из указанных вами порогов.
Следовательно, в конечный файл попадут SNP только с нужным перекосом частот (bias).
''')

def pop_col_index_search(req_population):
        '''
        Определение индекса каждого столбца
        с частотами аллелей запрашиваемых популяций.
        Запрашиваемые названия популяций ищутся в
        шапке таблицы, сгенерированной Ensembl VEP.
        '''
        try:
                req_pop_col_index = first_row.index(req_population)
                return req_pop_col_index
        except ValueError:
                print('Ошибка. Скорее всего, ваш файл сгенерирован не Ensembl VEP')

import os
import re

src_dir_path = input('Путь к папке с исходными файлами: ')
trg_dir_path = input('Путь к папке для конечных файлов: ')
req_populations = input('''Отсечь SNP по частотам в следующих популяциях
[AFR_AF|AMR_AF|EAS_AF|EUR_AF|SAS_AF|AA_AF|EA_AF] (несколько - через пробел): ''').split()

#Формирование строки, представляющей собой шаблон набора условий, соответствие
#которым позволяет вывести очередную строку Ensembl-таблицы в конечный файл.
#По ходу создания этого шаблона в него сразу "вшиваются"
#вводимые пользователем границы частот для каждой популяции.
#По мере прохождения Ensembl-файла, значения частот SNP в запрашиваемых популяциях,
#извлекаемые из текущей строки, будут подставляться в этот шаблон и сравниваться
#со вшитыми в шаблон пользовательскими порогами этих частот.
#Для попадания строки в конечный файл частоты не
#должны вылезать ни за один пользовательский порог.
freq_thresholds = ' and '.join(['float(row[{}]) ' + \
                        input('Граница частоты в популяции ' + req_population + ' [<= 0.03|> 0.3|(...)]: ') \
                        for req_population in req_populations])

src_file_names = os.listdir(src_dir_path)
for src_file_name in src_file_names:
        with open(os.path.join(src_dir_path, src_file_name)) as src_file_opened:

                #Преобразование шапки Ensembl VEP-таблицы в список.
                first_row = src_file_opened.readline().split('\t')

                #Создание списка индексов запрашиваемых популяционных столбцов.
                req_pop_col_indices = list(map(pop_col_index_search, req_populations))
                
                filtered_rows = []
                for line in src_file_opened:

                        #Формирование списка из текущей строки.
                        row = re.split(r'\t', line)
                        
                        #Подстановка значений популяционных частот из считываемой
                        #строки в ранее подготовленный шаблон условий.
                        #Преобразование строки с условиями в функционирующий код.
                        #Если вместо одного или нескольких значений популяционных частот
                        #в таблице встречаются тире или иные символы, то соответствующая
                        #строка точно не окажется в конечном файле.
                        try:
                                if eval(freq_thresholds.format(*req_pop_col_indices)):
                                        filtered_rows.append(row)
                        except ValueError:
                                continue

                #Сортировка прошедших фильтрацию строк по всем столбцам.
                filtered_rows.sort()

        trg_file_name = src_file_name.split('.')[0] + '_' + 'bias' + '.txt'
        with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
                trg_file_opened.write('\t'.join(first_row))
                for row in filtered_rows:
                        trg_file_opened.write('\t'.join(row))
