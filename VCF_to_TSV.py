print('''
Python3-скрипт, конвертирующий VCF-файлы (Variant Call Format) в TSV (Tab-Separated Values).
Автор: Платон Быкадоров (platon.work@gmail.com), 2018.
Версия: V1.0.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Простое руководство по установке среды разработки и запуску скриптов:
github.com/PlatonB/bioinformatic-python-scripts#Установка-среды-разработки

Работа скрипта сосредоточена на восьмом (INFO) столбце VCF.
Именно этот столбец нуждается в табификации, чтобы
информация оттуда стала парсибельнее и, возможно, нагляднее.
Скрипт также выполняет роль валидатора
правильности оформления ваших VCF-файлов.

Пример.
Исходный VCF-файл:
##fileformat=VCFv4.1
<...>
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
1	10019	rs775809821	TA	T	.	.	dbSNP_ver=dbSNP_150;TSA=deletion
1	10039	rs978760828	A	C	.	.	dbSNP_ver=dbSNP_150;TSA=SNV
1	10043	rs1008829651	T	A	.	.	dbSNP_ver=dbSNP_150;TSA=SNV

Полученный TSV-файл:
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	dbSNP_ver	TSA
1	10019	rs775809821	TA	T	.	.	dbSNP_150	deletion
1	10039	rs978760828	A	C	.	.	dbSNP_150	SNV
1	10043	rs1008829651	T	A	.	.	dbSNP_150	SNV
''')

import os, sys

src_dir_path = input('Путь к папке с исходными VCF-файлами: ')
trg_dir_path = input('\nПуть к папке для конечных файлов: ')
meta_lines_fate = input('''\nСохранять строки мета-информации в конечные файлы?
(игнорирование ввода ==> сохранять)
[yes(|y|<enter>)|no(|n)]: ''')
if meta_lines_fate != 'yes' and meta_lines_fate != 'y' and \
   meta_lines_fate != 'no' and meta_lines_fate != 'n' and meta_lines_fate != '':
        print(f'{meta_lines_fate} - недопустимая опция')
        sys.exit()

#Обязательные согласно стандарту VCF заголовки
#полей (столбцов) и их порядковые номера.
#Это множество пригодится для проверки
#правильности шапки в пользовательских таблицах.
#Далее оно будет называться референсом.
fixed_fields = set(['1_#CHROM',
                    '2_POS',
                    '3_ID',
                    '4_REF',
                    '5_ALT',
                    '6_QUAL',
                    '7_FILTER',
                    '8_INFO'])

#Работа с исходными файлами.
src_file_names = os.listdir(src_dir_path)
for src_file_name in src_file_names:
        if src_file_name.startswith('.~lock.') == True:
                continue
        print('Обрабатывается файл', src_file_name)
        with open(os.path.join(src_dir_path, src_file_name)) as src_file_opened:
                
                #Построение имени конечного файла.
                #Открытие конечного файла на запись.
                trg_file_name = '.'.join(src_file_name.split('.')[:-1]) + '_tab.tsv'
                with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
                        
                        #Прочтение первой строки VCF-файла.
                        #Хотя бы одна строка в начале файла
                        #должна быть строкой мета-информации.
                        #Здесь и далее, в случае выявления
                        #несоответствий стандарту VCF, уже созданный
                        #текущий конечный файл будет удалён.
                        line = src_file_opened.readline()
                        if line.startswith('##') == False:
                                print(f'''\nОшибка в файле {src_file_name}:
VCF-файл должен содержать строки мета-информации, начинающиеся с ##''')
                                os.remove(os.path.join(trg_dir_path, trg_file_name))
                                sys.exit()
                                
                        #В каждой итерации цикла while осуществляется
                        #как проверка считанной в прошлой итерации строки
                        #на наличие подстроки ##, так и прочтение новой строки.
                        #Строки, определённые как строки мета-информации,
                        #в зависимости от выбора пользователя могут быть
                        #прописаны или не прописаны в конечный файл.
                        #После строк мета-информации должна идти шапка с одним #.
                        #Считывание первой же строки без ## приведёт к выходу из цикла.
                        while line[:2] == '##':
                                if meta_lines_fate == 'yes' or meta_lines_fate == 'y' or meta_lines_fate == '':
                                        if line.find('\n') == -1:
                                                line += '\n'
                                        trg_file_opened.write(line)
                                line = src_file_opened.readline()
                                
                        #Первый этап проверки, является ли строка,
                        #идущая после строк мета-информации, шапкой.
                        #Заключается он в выявлении наличия #
                        #в качестве первого символа строки.
                        if line.startswith('#') == False:
                                print(f'''\nОшибка в файле {src_file_name}:
VCF-файл должен содержать шапку, начинающуюся с #''')
                                os.remove(os.path.join(trg_dir_path, trg_file_name))
                                sys.exit()
                                
                        #Второй, более сложный этап.
                        #Сверяем первые 8 элементов шапки с референсом.
                        #Для этого создаём множество, элементы которого
                        #построены идентичным образом с референсными:
                        #номер столбца_заголовок столбца.
                        #Сверяем количество элементов шапки
                        #пользовательского VCF и референса.
                        #Если оно не одинаково, то вычитаем из
                        #пользовательского множества референсное, выявляя
                        #тем самым неправильно озаглавленные столбцы.
                        #Сортируем и перебираем полученные неправильные элементы
                        #и выводим сообщения об ошибках, где указываем позиции
                        #ошибочных заголовков столбцов и сами заголовки.
                        header_row = line.split('\n')[0].split('\t')
                        header_check_set = set(map(lambda col_num, cell: col_num + '_' + cell, [str(i) for i in range(1, 9)][:8], header_row))
                        if header_check_set != fixed_fields:
                                for cell in sorted(list(header_check_set - fixed_fields)):
                                        print(f'''\nОшибка в файле {src_file_name}:
{cell[2:]} - неправильный заголовок столбца {cell[:1]}''')
                                os.remove(os.path.join(trg_dir_path, trg_file_name))
                                sys.exit()
                                
                        #Шапка прошла проверку, но пока не приняла
                        #свой окончательный вид, поскольку ещё не заменён
                        #на подзаголовки заголовок "INFO" 8-го столбца.
                        #Перед обновлением шапки фиксируем количество
                        #считанных на данный момент байт VCF-файла.
                        #Считываем первую строку основной части VCF, чтобы извлечь
                        #из неё подзаголовки, послужащие заменой заголовку "INFO".
                        #Пересобираем и прописываем в конечный файл шапку.
                        #Поскольку первую строку с данными надо будет ещё раз считать
                        #в рамках обработки основной части таблицы, возвращаем курсор
                        #на запомненную ранее позицию, соответствующую концу шапки.
                        after_header_pos = src_file_opened.tell()
                        info_subheaders = [cell_element.split('=')[0] for cell_element in src_file_opened.readline().split('\t')[7].split(';')]
                        header_row[7] = '\t'.join(info_subheaders)
                        trg_file_opened.write('\t'.join(header_row) + '\n')
                        src_file_opened.seek(after_header_pos)
                        
                        #Эффективная с точки зрения использования
                        #RAM работа с основной частью таблицы.
                        for line in src_file_opened:
                                data_row = line.split('\t')
                                
                                #Перебираем пары ключ=значение
                                #INFO-столбца и извлекаем значения.
                                #Меняем труднопарсибельную простыню на разделённую
                                #табуляциями строку, состоящую из значений.
                                #Ключи мы ранее задействовали в качестве
                                #подзаголовков ex-INFO-столбца.
                                try:
                                        info_vals = [cell_element.split('=')[1] for cell_element in data_row[7].split(';')]
                                except IndexError:
                                        print(f'''\nОшибка в файле {src_file_name}:
INFO-столбец VCF-файла должен состоять из пар ключ=значение''')
                                        os.remove(os.path.join(trg_dir_path, trg_file_name))
                                        sys.exit()
                                data_row[7] = '\t'.join(info_vals)
                                
                                #Прописывание обновлённых строк
                                #основной части таблицы в конечный файл.
                                if data_row[-1].find('\n') == -1:
                                        data_row[-1] += '\n'
                                trg_file_opened.write('\t'.join(data_row))
