print('''
Python3-скрипт, фильтрующий строки таблиц Ensembl VEP по границам частот SNP в популяциях.
Автор: Платон Быкадоров (platon.work@gmail.com), 2018.
Версия: V1.2.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

На вход подаются таблицы SNP, проаннотированных в
Ensembl Variant Effect Predictor (VEP) с флагом --af_1kg, выводящим
частоты их встречаемости в различных популяциях, и с флагом --tab.
В таблицах обязательно наличие шапки, т.е. при
их генерации нельзя использовать --no_headers.
Пример команды, осуществляющей аннотацию - после кода.
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
                print('''
Ошибка. Ваш файл сгенерирован не Ensembl VEP,
либо при аннотации указаны не те флаги.
Необходимо использовать флаги --af_1kg и --tab.
Нельзя применять флаг --no_headers
''')

import os
import re

src_dir_path = input('Путь к папке с исходными tab-файлами: ')
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

trg_dir_path = input('Путь к папке для конечных файлов: ')
src_file_names = os.listdir(src_dir_path)
for src_file_name in src_file_names:
        with open(os.path.join(src_dir_path, src_file_name)) as src_file_opened:

                #Игнорирование хэдеров, начинающихся с ##.
                #Преобразование шапки Ensembl VEP-таблицы в список.
                first_row = ['##']
                while first_row[0].startswith('##') == True:
                        first_row = src_file_opened.readline().split('\n')[0].split('\t')
                        
                #Создание списка индексов запрашиваемых популяционных столбцов.
                req_pop_col_indices = list(map(pop_col_index_search, req_populations))

                #Ensembl VEP Script при определённом построении
                #команды генерит одинаковые строки.
                #Чтобы убрать повторы, накапливаем результаты во множество.
                filt_rows = set()
                
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
                                        filt_rows.add('\t'.join(row))
                        except ValueError:
                                continue
                        
        #Сортировка прошедших фильтрацию строк по всем столбцам.
        filt_rows_srtd = sorted(list(filt_rows))

        #Прописывание результатов в конечные файлы.
        trg_file_name = src_file_name.split('.')[0] + '_' + 'bias' + '.txt'
        with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
                if first_row[-1].find('\n') == -1:
                        first_row[-1] += '\n'
                trg_file_opened.write('\t'.join(first_row))
                for line in filt_rows_srtd:
                        if line.find('\n') == -1:
                                line += '\n'
                        trg_file_opened.write(line)

'''
Пример команды, формирующей минималистичные таблицы, поддерживаемые биас-скриптом:
./vep --cache --fork 8 --no_stats --tab --species homo_sapiens --af_1kg --fields "Location,Uploaded_variation,AFR_AF,EAS_AF,EUR_AF" -i input.txt -o output.txt
'''
