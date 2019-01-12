print('''
Python3-скрипт, отбирающий строки
таблицы, содержащие запрашиваемые refSNPIDs.
Подходит для аннотирования наборов SNP.
Версия: V6.3.
Автор: Платон Быкадоров (platon.work@gmail.com), 2017-2019.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Простое руководство по установке среды разработки и запуску скриптов:
github.com/PlatonB/bioinformatic-python-scripts#Установка-среды-разработки

Сокращения, используемые в документации:
Таблицы с искомыми SNPs далее будут называться "таблицами исследователя".
Таблица, из которой вытаскиваем строки с искомыми SNPs — "база".

Один из столбцов исследовательских таблиц должен содержать
идентификаторы однонуклеотидных полиморфизмов (refSNPID вида rs1234567890).
Скрипт самостоятельно обнаружит столбец с refSNPID в любой таблице,
даже если в разных таблицах имеется разное положение rs-столбца.
Таблицы исследователя могут содержать
заголовок, начинающийся с "#" или "track name".

Скрипт может сократить "базу" по верхнему порогу
p-value или иной величины (допустим, q-value).

Примеры "баз" - GTEx-таблицы. Их можно найти по ссылке
https://www.gtexportal.org/home/datasets (требуется регистрация).
Скрипт протестирован на нескольких GTEx-таблицах, в частности,
Whole_Blood.egenes.annotated.txt архива GTEx_Analysis_v7_eQTL.tar.gz.

Для поиска: Genotype-Tissue Expression (GTEx) project,
eQTL, SNP, биоинформатика, программирование, python 3.
''')

def get_ram_size(src_dir):
        '''
        ОС-специфичное получение значения полного объёма оперативной памяти.
        '''
        os_name = os.name
        system_info_temp = os.path.join(src_dir, 'info_temp.txt')

        ##Создание файла, в который будет выводиться
        ##подробная информация о компьютере.
        ##Оттуда не без грязных хаков будет
        ##извлекаться значение объёма оперативной памяти.
        ##В зависимости от ОС, способы получения
        ##и считывания данных о железе будут разными.
        
        #Windows.
        if os_name == 'nt':
                print('Из-за нерешённой проблемы с кодировками, Windows пока не поддерживается')
                sys.exit()

                #В Windows вывести информацию о
                #железе позволяет утилита systeminfo.
                #Эти характеристики будут выведены во временный
                #файл, а уже оттуда можно извлечь объём RAM.
                #Если знаете способ попроще - пишите в Issues.
                os.system("systeminfo > {}".format(system_info_temp))
                with open(system_info_temp) as system_info_temp_opened:
                        
                        #Извлечение строки, содержащей значение
                        #размера оперативной памяти в мегабайтах.
                        ram_size_line = [line for line in system_info_temp_opened \
                                         if line.find('Полный объем физической памяти') != -1][0]

                        #Файл с характеристиками компьютера
                        #больше не нужен, поэтому будет удалён.
                        os.remove(system_info_temp)

                        #Получение размера оперативной памяти в байтах.
                        #Исходное значение из systeminfo-файла
                        #представлено числом, разделённым пробелами,
                        #поэтому приходится его дополнительно
                        #склеивать регулярным выражением.
                        if re.search(r'МБ', ram_size_line) != None:
                                ram_size = int(''.join(re.findall(r'\d+', ram_size_line))) * 1000000
                                return ram_size
                        else:
                                print('Ошибка. systeminfo вывел объём RAM не в МБ')
                                
        #Linux и, возможно, FreeBSD.
        elif os_name == 'posix':

                #Вывод в файл сведений об оперативной
                #памяти с помощью программы free.
                #Флаг -b позволяет выводить
                #значения сразу в байтах.
                os.system("free -b > {}".format(system_info_temp))
                with open(system_info_temp) as system_info_temp_opened:

                        #Поиск значения объёма RAM в таблице,
                        #сгенерированной программой free.
                        total_col_index = re.split(r'\s+', system_info_temp_opened.readline()).index('total')
                        ram_size = int(re.split(r'\s+', system_info_temp_opened.readline())[total_col_index])

                        #Файл с информацией об оперативной памяти
                        #больше не нужен, поэтому будет удалён.
                        os.remove(system_info_temp)
                        
                        return ram_size
        else:
                print('Скрипт не поддерживает ОС типа', os_name)

def rs_col_index_search(src_file_opened):
        '''
        Поиск индекса "столбца" любой содержащей refSNPID таблицы.
        Таблица подаётся в функцию в виде открытого средствами Питона файла.
        Столбец с refSNPID может быть единственным столбцом таблицы.
        Если во второй строке refSNPID отсутствует (например, в GTEx-базах
        вместо refSNPID может быть точка), то ищем в третьей, если
        нет и в третьей, движемся дальше по строкам, пока не найдём.
        После нахождения индекса refSNPID-столбца,
        курсор считывания файла сбрасывается к началу.
        Функция может применяться и для таблиц с хэдерами.
        '''
        for line in src_file_opened:
                row = line.split('\t')
                for cell in row:
                        if re.match(r'rs\d+$', cell):
                                rs_col_index = row.index(cell)
                                src_file_opened.seek(0)
                                return rs_col_index

def header_save(src_file_opened, num_of_headers):
        '''
        Сохранение хэдеров, количество которых должен
        был указать пользователь, в одномерный массив.
        Если пользователь ввёл значение количества
        хэдеров, равное 0, создастся пустой список.
        При сохранении хэдеров запомнится
        позиция курсора считываемого файла.
        Поэтому хэдеры не будут мешать
        дальнейшей работе с таблицей.
        '''
        headers = [src_file_opened.readline() for number in range(num_of_headers)]
        return headers

def table_split(src_file_opened, rs_col_index, pval_column, pval_threshold, ram_size, stop_reading):
        '''
        Дробление таблицы на фрагменты, приблизительно
        равные 1/16 объёма оперативной памяти компьютера.
        Фрагменты сортируются по refSNPID-столбцу.
        Один из аргументов функции - уже
        открытый средствами Питона файл.
        Если этот файл ранее открывался и
        считывался, то в функцию автоматически
        передастся последняя позиция курсора.
        Т.о., файл начинает считываться со строки,
        идущей после последней считанной.
        '''
        #При каждом вызове данной функции создаётся пустой
        #список, в который будет накапливаться фрагмент.
        #Также запоминается количество прочитанных
        #к моменту вызова функции байт файла.
        partial_two_dim, init_mem_usage = [], src_file_opened.tell()
        
        #Новый участок файла будет считываться до тех пор,
        #пока разница текущего прочитанного количества байт
        #и зафиксированного в начале вызова функции
        #не достигнет примерно 1/16 объёма оперативной памяти.
        while src_file_opened.tell() - init_mem_usage < ram_size // 16:
                
                #Каждая считываемая строка сразу дробится
                #по табуляциям, преобразуясь в список.
                row = src_file_opened.readline().split('\t')
                
                #Считывание файла закончилось, а определённый исходя
                #из объёма RAM предел размера фрагмента не был достигнут.
                #Если на этом месте не остановить цикл while, то к
                #фрагменту начнут присоединяться списки пустых строк.
                #Поэтому, как только встречается первый же список
                #с пустой строкой, накопленный к этому моменту
                #фрагмент сортируется и возвращается функцией.
                #При обнаружения пустого списка функция также
                #возвращает сигнал окончания дробления файла.
                #Этот сигнал реализован в виде изменения значения
                #соответствующей переменной, приводящего к выходу
                #из того цикла while, в котором однократно или
                #многократно вызывается функция дробления.
                if row == ['']:
                        partial_two_dim.sort(key = lambda row: row[rs_col_index])
                        stop_reading = 'yes'
                        return partial_two_dim, stop_reading
                
                #Если пользователь указал столбец с p-value и порог
                #p-value, то строки, в которых p-value превышает
                #заданный порог, добавляться во фрагмент не будут.
                if pval_column != None and pval_threshold != None:
                        if float(row[pval_column - 1]) > pval_threshold:
                                continue
                
                #Проверка, содержит ли текущая строка refSNPID.
                #В конечный вариант фрагмента не должны попасть
                #строки, содержащие точку или какую-нибудь
                #другую информацию вместо refSNPID.
                if re.search(r'rs\d+$', row[rs_col_index]) != None:
                        
                        #Строка, содержащая SNP-идентификатор, добавляется в список-фрагмент.
                        partial_two_dim.append(row)

        #Считываемый участок файла оказался крупнее 1/16 RAM.
        #Тогда после "естественного" выхода из while
        #функция возвратит накопленный в этом цикле фрагмент
        #файла вместе с сигналом продолжения выполнения
        #цикла, в котором вызывается функция-дробитель.
        partial_two_dim.sort(key = lambda row: row[rs_col_index])
        return partial_two_dim, stop_reading

def table_to_dict(two_dim, rs_col_index):
        '''
        Создание словаря, в котором ключи - refSNPID, а значения -
        соответствующие refSNPID-содержащие строки таблицы.
        На вход подаётся отсортированная по refSNPID таблица
        с очищенным столбцом refSNPID, без хэдера и, в случае
        соответствующего пользовательского выбора, с отсечением по p-value.
        Если refSNPID уникален, то соответствующая ему строка таблицы
        пойдёт в двумерный массив, служащий значением этому refSNPID-ключу,
        и будет представлять собой единственный вложенный список.
        Если же встречается несколько строк подряд с одним и тем же
        refSNPID, добавляем их в качестве элементов двумерного
        массива, являющегося значением "общему" refSNPID-ключу.
        Чтобы алгоритм выявления одинаковых refSNPID работал
        и в самом начале формирования словаря, первая
        пара ключ-значение создаётся отдельно.
        '''
        rs_and_ann_dict = {two_dim[0][rs_col_index]: [two_dim[0]]}
        for row_num in range(1, len(two_dim)):
                if two_dim[row_num][rs_col_index] != two_dim[row_num - 1][rs_col_index]:
                        rs_and_ann_dict[two_dim[row_num][rs_col_index]] = [two_dim[row_num]]
                else:
                        rs_and_ann_dict[two_dim[row_num - 1][rs_col_index]] += [two_dim[row_num]]
        return rs_and_ann_dict

def rs_search(rem_two_dim, two_dim_rs_col_index, rs_and_ann_dict, trg_file_opened):
        '''
        Поиск строк базы, содержащих нужные пользователю refSNPID.
        На вход подаётся текущий, оставшийся после предыдущих вызовов,
        набор refSNPIDs исследователя и соответствующий
        индекс refSNPID-столбца, а также преобразованная в
        словарь база и открытый на запись конечный файл.
        Значения, соответствующие ключам, совпадающим с refSNPID
        исследователя, пойдут непосредственно в конечный файл.
        Из ненайденных в рамках текущего вызова этой функции refSNPIDs
        исследователя формируется обновлённый (сокращённый) набор refSNPIDs,
        который предполагается использовать при следующем вызове.
        '''
        trun_two_dim = []
        for row in rem_two_dim:
                try:
                        rs_id = row[two_dim_rs_col_index]
                except IndexError:
                        continue
                if rs_id in rs_and_ann_dict:
                        for ann in rs_and_ann_dict[rs_id]:
                                trg_file_opened.write('\t'.join(ann))
                else:
                        trun_two_dim.append(row)
        return trun_two_dim

####################################################################################################

import os, sys, csv, re

us_dir_path = input('Путь к папке с таблицами исследователя: ')

base_file_path = input('\nПуть к "базе": ')
base_file_name = os.path.basename(base_file_path)

trg_dir_path = input('\nПуть к папке для конечных файлов: ')

base_num_of_headers = input('''\nКоличество не обрабатываемых строк в начале "базы"
(игнорирование ввода ==> хэдеров/шапок в "базе" нет)
[0(|<enter>)|1|2|...]: ''')
if base_num_of_headers == '':
        base_num_of_headers = 0
else:
        base_num_of_headers = int(base_num_of_headers)

#Вводимый пользователем номер столбца - не
#индекс соответстующего элемента вложенного списка!
#Для преобразования в индекс надо будет вычесть 1.
base_pval_column = input('''\nНомер столбца "базы" со значениями p-value или иной величины,
по которой желаете отфильтровать строки "базы"
(игнорирование ввода ==> не фильтровать)
[no_filter(|<enter>)|1|2|3|...]: ''')
if base_pval_column == 'no_filter' or base_pval_column == '':
        base_pval_column, base_pval_threshold = None, None
else:
        base_pval_column = int(base_pval_column)
        
        base_pval_threshold = float(input('''Верхний порог фильтруемой величины
[0.05|5.5e-10|...]
значения выбранного столбца ≤ '''))

#Получение объёма оперативной памяти.
ram_size = get_ram_size(us_dir_path)

##Работа с файлами исследователя (содержащими запрашиваемые SNP).
##Предполагается, что наборы искомых SNP не настолько огромны,
##чтобы занимать больше 1/16 оперативной памяти.
##Поэтому они дробиться не будут.
##Идентификаторы SNP из каждого исследовательского
##файла будут искаться во всех фрагментах базы.
##Но если идентификатор уже найден в одном из фрагментов,
##то в следующих фрагментах он искаться не будет.
us_file_names = os.listdir(us_dir_path)
for us_file_name in us_file_names:
        print('Поиск в таблице ' + base_file_name + ' строк с SNPs, взятыми из ' + us_file_name)
        with open(os.path.join(us_dir_path, us_file_name)) as us_file_opened:
                
                #Ищем индекс refSNPID-содержащего
                #столбца исследовательского файла.
                us_rs_col_index = rs_col_index_search(us_file_opened)
                
                #Если в таблице исследователя есть хэдер-содержащая строка,
                #исключаем её попадание в следующий этап конвейера.
                us_first_line = us_file_opened.readline()
                if us_first_line.find('#') == -1 or us_first_line.find('track name') == -1:
                        us_file_opened.seek(0)
                        
                #Таблица исследователя сразу, без дробления,
                #преобразуется в двумерный массив.
                us_two_dim = list(csv.reader(us_file_opened, delimiter = '\t'))
                
                ##Работа с базой.
                with open(base_file_path) as base_file_opened:
                        trg_file_name = '.'.join(us_file_name.split('.')[:-1]) + '_I_' + base_file_name
                        with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
                                
                                #Нахождение индекса refSNPID-столбца базы.
                                base_rs_col_index = rs_col_index_search(base_file_opened)
                                
                                #"Отделение" хэдеров от базы и
                                #прописывание их в конечный файл.
                                base_headers = header_save(base_file_opened,
                                                           base_num_of_headers)
                                if base_headers != []:
                                        for line in base_headers:
                                                trg_file_opened.write(line)
                                
                                #Переменная-стоппер, служащая сигналом
                                #завершения или продолжения дробления базы.
                                base_stop_reading = 'no'
                                
                                #Найденные в текущем фрагменте "базы" SNPs не будут
                                #попадать в переформируемый массив исследовательских данных.
                                rem_us_two_dim = us_two_dim
                                
                                ##Дробление базы и поиск query-SNP-содержащих строк.
                                while base_stop_reading:
                                        
                                        #Формирование фрагмента базы.
                                        base_partial_two_dim, base_stop_reading = table_split(base_file_opened,
                                                                                              base_rs_col_index,
                                                                                              base_pval_column,
                                                                                              base_pval_threshold,
                                                                                              ram_size,
                                                                                              base_stop_reading)
                                        
                                        #Преобразование фрагмента базы в словарь.
                                        base_partial_dict = table_to_dict(base_partial_two_dim,
                                                                          base_rs_col_index)
                                        
                                        #Прописывание в файл строк базы, содержащих искомые refSNPIDs.
                                        #Переформирование исследовательского массива данных, а имеено,
                                        #получение его сокращённого на совокупность найденных SNPs варианта.
                                        rem_us_two_dim = rs_search(rem_us_two_dim,
                                                                   us_rs_col_index,
                                                                   base_partial_dict,
                                                                   trg_file_opened)
                                        
                                        #Выполнение цикла, в котором вызывается функция дробного
                                        #считывания базы, прерывается после того, как переменная-стоппер
                                        #в этой функции принимает соответствующее значение.
                                        if base_stop_reading == 'yes':
                                                break
                                        
##Бонус: refSNPID-содержащие таблицы, созданные для тестирования
##с "базой" Whole_Blood_Analysis.perm.txt архива GTEx_Analysis_v6p_eQTL.
##Эта база небольшая, поэтому на современных компьютерах она вряд ли будет разбиваться.
##Чтобы с целью тестирования искусственно разбить небольшую базу,
##в условии "while src_file_opened.tell() - init_mem_usage < ram_size // x" укажите такой x,
##чтобы неполное частное выражения ram_size // x было меньше размера базы в байтах.
##В целом, оттого, что вы выставляете разные значения x, результаты не должны меняться.
##В противном случае, немедленно составляйте баг-репорт в Issues!
'''
#refSNPID, встречающиеся в Whole_Blood_Analysis.perm 1 раз.
rs190889721
rs184276234
rs10910055
rs11122083
rs184383837

#refSNPID, повторяющиеся в Whole_Blood_Analysis.perm несколько раз + заведомо несуществующие refSNPID.
Дважды	rs1047712
Дважды	rs115477239
Трижды	rs1838150
Трижды	rs7159937
Пять_раз	rs4976210
Шесть_раз	rs67876192
Несуществующий	rs99999999999999999999
Несуществующий	rs55555555555555555555
Несуществующий	rs77777777777777777777
Несуществующий	rs22222222222222222222
Несуществующий	rs33333333333333333333

#refSNPID, встречающиеся 1 раз в Whole_Blood_Analysis.perm, но идущие не с первой строки.
1	q	!@#$%^&*()
2	w	)(*&^%$#@!
3	e	rs188678711
4	r	rs2203348
5	t	rs3760905
'''
