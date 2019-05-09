print('''
Python3-скрипт, фильтрующий строки таблиц по
правилам, применяемым к ячейкам заданных столбцов.
Автор: Платон Быкадоров (platon.work@gmail.com), 2018-2019.
Версия: V3.1.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Простое руководство по установке среды разработки и запуску скриптов:
github.com/PlatonB/bioinformatic-python-scripts#Установка-среды-разработки

Из заданных вами постолбцовых фильтров программа сформирует
выражение, отбирающее строки таблицы в конечный файл.
Оно будет выглядеть подобным образом:
're.match("IGH[GE]", row[1]) != None and float(row[13]) == 9'

Пример.
Несколько SNP и найденные для них с помощью
Ensembl VEP script частоты в трёх популяциях:
#Location	Uploaded_variation	AFR_AF	EAS_AF	EUR_AF
6:31271529	rs7383157	0.9501	0.8294	0.8767
14:105785012	rs10141135	0.028	0.0149	0.6243
6:31380730	rs9266685	0.6884	0.9008	0.7386
14:105757817	rs11627978	0.0257	0.0139	0.6471
6:32721500	rs9275762	0.2859	0.7262	0.5954

Применяем следующие 3 фильтра для
3, 4 и 5 столбцов, соответственно:
cell < 0.03
cell < 0.03
cell > 0.3

Результат:
#Location	Uploaded_variation	AFR_AF	EAS_AF	EUR_AF
14:105785012	rs10141135	0.028	0.0149	0.6243
14:105757817	rs11627978	0.0257	0.0139	0.6471
''')

import sys, os, re

src_dir_path = input('Путь к папке с исходными tab-файлами: ')

trg_dir_path = input('\nПуть к папке для конечных файлов: ')

num_of_headers = input('''\nКоличество не обрабатываемых строк
в начале каждой исходной таблицы
(игнорирование ввода ==> хэдеров/шапок в таблицах нет)
[0(|<enter>)|1|2|...]: ''')
if num_of_headers == '':
        num_of_headers = 0
else:
        num_of_headers = int(num_of_headers)
        
cont, filters = 'y', []

while cont != 'no' and cont != 'n' and cont != '':
        col_number = int(input('\nНомер столбца, по которому фильтруем: '))
        
        data_type = input('''\nВ выбранном столбце - числа или строки?
(примеры числа: 10, -50, 0.11, 2.5e-12)
(примеры строки: A/C/G, ., rs11624464, HLA-DQB1)
[numbers(|n)|strings(|s)]: ''')
        
        if data_type == 'numbers' or data_type == 'n':
                
                #Сборка строки, представляющей собой код,
                #выполнение которого приведёт к извлечению
                #содержимого каждой ячейки заданного столбца,
                #конвертации соответствующих значений в
                #вещественные числа, и, собственно, фильтрации.
                filt = input('''\nВыражение, служащее правилом фильтрации
(На место слова cell программа будет подставлять
содержимое каждой ячейки указанного вами столбца)
[1e-04 < cell < 1e-02|cell <= 0.05|
0.3>cell|cell == 1|cell != 10|...]: ''').replace('cell',
                                                 f'float(row[{str(col_number - 1)}])')
                
        elif data_type == 'strings' or data_type == 's':
                
                #Формирование аналогичной строки, но код
                #из которой будет извлекать содержимое ячейки
                #уже без конвертации последнего во float.
                filt = input('''\nВыражение, служащее правилом фильтрации
(На место слова cell программа будет подставлять
содержимое каждой ячейки указанного вами столбца)
(Поддерживаются регулярки. Не подавляйте экранирование в паттернах!)
[cell == "IGHG3"|cell != "chr6"|
cell.startswith("IGH")|cell.find("HLA") == -1|
re.match("[ATGC](?:/[ATGC]){2}$", cell) != None|...]: ''').replace('cell',
                                                                   f'row[{str(col_number - 1)}]')
                
        else:
                print('\nОшибка. Вы не выбрали тип данных столбца')
                sys.exit()
                
        #Полученная строка-фильтр добавляется в список,
        #который может содержать фильтры по другим столбцам.
        filters.append(filt)
        
        cont = input('''\nДобавить другое правило фильтрации?
(игнорирование ввода ==> не добавлять)
[yes(|y)|no(|n|<enter>)]: ''')
        if cont != 'yes' and cont != 'y' and cont != 'no' and cont != 'n' and cont != '':
                print('''\nОшибка. Не понятно, хотите ли вы
добавить другое правило фильтрации или нет''')
                sys.exit()
                
print('\n')

#Объединение строк-фильтров в строку, которая при собственном выполнении
#извлечёт содержимое ячеек, а также отфильтрует строки, содержащие эти
#ячейки, по тем правилам, которые пользователь задал для данных ячеек.
expression = ' and '.join(filters)

#Работа с исходными файлами.
src_file_names = os.listdir(src_dir_path)
for src_file_name in src_file_names:
        if src_file_name.startswith('.~lock.'):
                continue
        with open(os.path.join(src_dir_path, src_file_name)) as src_file_opened:
                print('Производится фильтрация', src_file_name)
                
                #Формирование списка хэдеров.
                #Курсор смещается к началу
                #основной части таблицы.
                headers = [src_file_opened.readline() for header_index in range(num_of_headers)]
                
                #Создание конечного файла и прописывание в него хэдеров.
                src_file_base = '.'.join(src_file_name.split('.')[:-1])
                src_file_ext = '.' + src_file_name.split('.')[-1]
                trg_file_name = src_file_base + '_filt' + src_file_ext
                with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
                        for header in headers:
                                if header.find('\n') == -1:
                                        header += '\n'
                                trg_file_opened.write(header)
                                
                        #Чтение основной части таблицы.
                        for line in src_file_opened:
                                line = line.split('\n')[0]
                                
                                #Формирование списка из текущей строки.
                                row = line.split('\t')
                                
                                #Преобразование строки с условиями в функционирующий код.
                                #Попытка применения этого кода.
                                #Если в строке попалась не обрабатываемая
                                #по тем или иным причинам ячейка, то
                                #эта строка не попадёт в конечный файл.
                                try:
                                        if eval(expression):
                                                
                                                #Прописывание строки, соответствующей
                                                #условиям, в конечный файл.
                                                trg_file_opened.write(line + '\n')
                                                
                                except ValueError:
                                        continue
