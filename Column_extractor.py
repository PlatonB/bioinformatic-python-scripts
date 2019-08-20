print('''
Этот Python3-скрипт копирует в отдельные
файлы необходимые пользователю столбцы.
Автор: Платон Быкадоров (platon.work@gmail.com), 2017-2019.
Версия: V3.1.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Простое руководство по установке среды разработки и запуску скриптов:
github.com/PlatonB/bioinformatic-python-scripts#Установка-среды-разработки

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

import sys, os

src_dir_path = input('Путь к папке с исходными tab-файлами: ')

trg_dir_path = input('\nПуть к папке для конечных файлов: ')

num_of_headers = input('''\nКоличество не обрабатываемых строк
в начале каждой исходной таблицы
(совет: табулированную шапку к ним не причисляйте)
(игнорирование ввода ==> производить работу для всех строк)
[0(|<enter>)|1|2|...]: ''')
if num_of_headers == '':
        num_of_headers = 0
else:
        num_of_headers = int(num_of_headers)
        
mode = input('''\nСкопировать выбранные столбцы или
скопировать все столбцы кроме выбранных?
[include(|i)|exclude(|e)]: ''')
if mode in ['include', 'i']:
        act = 'копируемых'
elif mode in ['exclude', 'e']:
        act = 'исключаемых'
else:
        print('\nОшибка. Вы не определили действие')
        sys.exit()
        
indices = [int(col_number) - 1 for col_number in input(f'''\nНомер одного или номера
нескольких {act} столбцов
(через пробел): ''').split()]
if act == 'исключаемых':
        indices.sort()
        
print('\n')

src_file_names = os.listdir(src_dir_path)
for src_file_name in src_file_names:
        if src_file_name.startswith('.~lock.'):
                continue
        with open(os.path.join(src_dir_path, src_file_name)) as src_file_opened:
                
                print('Обрабатывается файл', src_file_name)
                
                #Создание имени конечного файла.
                src_file_base = '.'.join(src_file_name.split('.')[:-1])
                src_file_ext = '.' + src_file_name.split('.')[-1]
                trg_file_name = src_file_base + '_extr' + src_file_ext
                
                #Открытие конечного файла на запись.
                with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
                        
                        #Формирование списка
                        #хэдеров и добавление
                        #хэдеров в конечный файл.
                        #Курсор смещается к началу
                        #основной части таблицы.
                        headers = [src_file_opened.readline().split('\n')[0] \
                                   for header_index in range(num_of_headers)]
                        for header in headers:
                                trg_file_opened.write(header + '\n')
                                
                        #Эффективная с точки зрения использования
                        #RAM работа с основной частью таблицы.
                        for line in src_file_opened:
                                src_row = line.split('\n')[0].split('\t')
                                
                                if act == 'копируемых':
                                        
                                        #Формирование списка, содержащего ячейки
                                        #только запрашиваемых столбцов.
                                        trg_row = [src_row[index] for index in indices]
                                        
                                else:
                                        
                                        #Создание списка, наоборот,
                                        #без ячеек заданных столбцов.
                                        #Список индексов игнорируемых ячеек
                                        #должен быть отсортированным.
                                        #Алгоритм таков, что исходный
                                        #список будет как бы разрезаться
                                        #исключаемыми и него элементами.
                                        #Если удаляемым элементом
                                        #окажется последний, то при
                                        #попытке отмерить от него крайний
                                        #"отрезок" IndexError не возникнет.
                                        #В качестве этого отрезка
                                        #вернётся пустой список.
                                        trg_row, prev_index = [], -1
                                        for index in indices:
                                                trg_row += src_row[prev_index + 1:index]
                                                prev_index = index
                                        trg_row += src_row[prev_index + 1:]
                                        
                                #Прописывание результатов в конечный файл.
                                trg_file_opened.write('\t'.join(trg_row) + '\n')
