print('''
Python3-скрипт, фильтрующий строки таблиц по
границам числовых значений заданных столбцов.
Автор: Платон Быкадоров (platon.work@gmail.com), 2018.
Версия: V1.0.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

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
3-5 столбцов, соответственно:
{} < 0.03
{} < 0.03
{} > 0.3

Результат:
#Location	Uploaded_variation	AFR_AF	EAS_AF	EUR_AF
14:105785012	rs10141135	0.028	0.0149	0.6243
14:105757817	rs11627978	0.0257	0.0139	0.6471
''')

import os

src_dir_path = input('Путь к папке с исходными tab-файлами: ')
trg_dir_path = input('\nПуть к папке для конечных файлов: ')
num_of_headers = int(input('''\nКоличество не считываемых строк в начале файла
(хэдер, шапка таблицы и т.д.) [0|1|2|(...)]: '''))
cont, col_numbers, rules = 'y', [], []
while cont != 'no' and cont != 'n' and cont != '':
        col_numbers.append(int(input('\nНомер столбца, по которому фильтруем: ')))
        rules.append(input('''\nВыражение, служащее правилом фильтрации
(В {} будут автоматически подставляться
значения из указанного вами столбца)
[1e-04 < {} < 1e-02|{} <= 0.05|0.3<{}|{} == 1|(...)]): '''))
        cont = input('''\nДобавить другое правило фильтрации?
(игнорирование ввода ==> не добавлять)
[yes(|y)|no(|n|<enter>)]: ''')

#Формирование списка строк, выполнение которых
#произведёт конвертацию значений из соответствующих
#ячеек заданных столбцов в числа с плавающей точкой.
float_extractors = ['float(row[' + str(col_number - 1) + '])' for col_number in col_numbers]

#Создание шаблона условий.
#Подстановка выражений, получающих
#float-значения из определённых ячеек
#считываемой строки, в шаблон условий.
filt = ' and '.join(rules).format(*float_extractors)

#Работа с исходными файлами.
src_file_names = os.listdir(src_dir_path)
for src_file_name in src_file_names:
        with open(os.path.join(src_dir_path, src_file_name)) as src_file_opened:
                print('Производится фильтрация', src_file_name)
                
                #Формирование списка хэдеров.
                #Курсор смещается к началу основной части таблицы.
                headers = [src_file_opened.readline() for header_index in range(num_of_headers)]
                
                #Создание конечного файла и прописывание в него хэдеров.
                trg_file_name = src_file_name.split('.')[0] + '_' + 'filt' + '.txt'
                with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
                        for header in headers:
                                if header.find('\n') == -1:
                                        header += '\n'
                                trg_file_opened.write(header)
                                
                        #Чтение основной части таблицы.
                        for line in src_file_opened:
                                
                                #Формирование списка из текущей строки.
                                row = line.split('\t')
                                
                                #Преобразование строки с условиями в функционирующий код.
                                #Если хотя бы в одной фильтруемой позиции текущей строки
                                #встречаются препятствующие конвертации во float символы,
                                #то эта строка точно не окажется в конечном файле.
                                try:
                                        if eval(filt):
                                                
                                                #Прописывание результатов в конечный файл.
                                                if line.find('\n') == -1:
                                                        line += '\n'
                                                trg_file_opened.write(line)
                                                
                                except ValueError:
                                        continue
