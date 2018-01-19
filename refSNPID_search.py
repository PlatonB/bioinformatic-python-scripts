print('''
Python3-скрипт, который выводит строки той или иной таблицы, содержащей искомые refSNPID.
Автор: Платон Быкадоров, 2017-2018.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Сокращения, используемые в документации:
Таблицы с искомыми SNP далее будут называться "пользовательскими".
Таблица, в которой ищем SNP, далее будет называться "базой".

Один из столбцов "пользовательских" таблиц должен содержать идентификаторы однонуклеотидных полиморфизмов (refSNPID вида rs1234567890).
Скрипт самостоятельно обнаружит столбец с refSNPID в любой таблице (даже если в разных таблицах разный номер rs-столбца).
Также скрипт не растеряется, если в rs-столбце присутствуют иные данные, точки, прочерки и т.д..
rs-столбец может быть единственным столбцом "пользовательской" таблицы.
"Пользовательские" таблицы могут содержать заголовок, начинающийся с "#" или "track name".

Скрипт может сократить "базу" по верхнему порогу p-value или иной величины (допустим, q-value).

Примеры "баз" - GTEx-таблицы. Их можно найти по ссылке https://www.gtexportal.org/home/datasets (требуется регистрация).
Скрипт протестирован на нескольких GTEx-таблицах, в частности, Whole_Blood.egenes.annotated.txt архива GTEx_Analysis_v7_eQTL.tar.gz.

В исходной папке не желательно держать файлы, отличные от "пользовательских" таблиц.
Папку для результатов перед выполнением работы лучше оставлять пустой.
Могу доработать скрипт таким образом, чтобы он искал снипы сразу по нескольким "базам" (обращайтесь в Issues).

Для поиска: Genotype-Tissue Expression (GTEx) project, eQTL, SNP, биоинформатика, программирование, python 3.
''')

import os
import re
import csv

rs_dir = input('Путь к папке с "пользовательскими" таблицами: ')
base_file_path = input('Путь к "базе" (не забывайте указывать расширение .txt): ')
num_of_base_headers = int(input('Количество не считываемых строк в начале "базы" (хэдер, шапка таблицы и т.д.) [0|1|2|(...)]: '))

#Вводимый пользователем номер столбца - не индекс соответстующего элемента вложенного списка!
#Для преобразования в индекс надо будет вычесть 1.
base_pval_column = input('(Опционально) Номер столба "базы" со значениями p-value [1|2|3|(...)|<enter>]: ')
if base_pval_column == '':
        del base_pval_column
else:
        base_pval_column = int(base_pval_column)
        base_pval_threshold = float(input('Верхний порог p-value (разделитель - точка)[5.00e-19|(...)]. P-VALUE ≤ '))

targetdir = input('Путь к папке для конечных файлов: ')

def rs_col_index_search(two_dim):
        '''
        Поиск индекса "столбца" любой содержащей refSNPID таблицы, представленной с помощью модуля csv в виде двумерного массива.
        Столбец с refSNPID может быть единственным столбцом подаваемого на вход двумерного массива.
        Если во второй строке refSNPID отсутствует (например, в GTEx-базах вместо refSNPID может быть точка),
        то ищем в третьей, если нет и в третьей, движемся дальше по строкам, пока не найдём.
        Функция может применяться и для таблиц с хэдерами.
        '''
        for row_num in range(1, len(two_dim)):
                for cell in two_dim[row_num]:
                        if re.match(r'rs\d+$', cell):
                                rs_col_index = two_dim[row_num].index(cell)
                                return rs_col_index

class AnyTable():
        '''
        Действия, производимые с любым типом input-таблиц, подходящих для этой программы.
        '''
        def __init__(self, two_dim, rs_col_index):
                self.two_dim = two_dim
                self.rs_col_index = rs_col_index

        def clean_and_sort(self):
                '''
                Удаление строк таблицы, содержащих точку или какую-нибудь другую информацию вместо refSNPID.
                Если вам вдруг эти строки требуется учитывать, пишите в Issues, подумаю.
                Сортировка таблицы по столбцу с refSNPID, чтобы строки с одним и тем же refSNPID расположились друг за другом.
                '''
                two_dim_unique = [line.split('\t') for line in list(set(['\t'.join(row) for row in self.two_dim]))]
                two_dim_pure = [row for row in two_dim_unique if re.search(r'rs\d+$', row[self.rs_col_index]) != None]
                two_dim_pure.sort(key = lambda row: row[self.rs_col_index])
                return two_dim_pure

class BaseTable(AnyTable):
        '''
        Действия, производимые с базой.
        '''
        def __init__(self, two_dim, rs_col_index):
                super().__init__(two_dim, rs_col_index)


        def header_save(self, num_of_base_headers):
                '''
                Отделение хэдеров, количество которых ранее указал пользователь, от самой базы.
                Хэдеры в результате будут представлять собой строки одномерного списка.
                Если пользователь ввёл значение количества хэдеров, равное 0, соответствующая переменная не создастся.
                Во время записи хэдеров в конечный файл при отсутствии этой переменной необходимо будет обработать исключение.
                '''
                if num_of_base_headers > 0:
                        headers = ['\t'.join(row) for row in self.two_dim[:num_of_base_headers]]
                two_dim_wo_header = self.two_dim[num_of_base_headers:]
                return headers, two_dim_wo_header

        def constrict_by_pval(self, two_dim_pval_column, two_dim_pval_threshold):
                '''
                Если пользователь ввёл порог p-value, то в базе останутся только строки с p-value не более заданного значения.
                Если не ввёл - нужно при вызове функции обработать исключение.
                На вход подаётся база без хэдеров.
                '''
                two_dim_constr = [row for row in self.two_dim if float(row[two_dim_pval_column - 1]) <= two_dim_pval_threshold]
                return two_dim_constr
                
        def dict_create(self):
                '''
                Создание словаря, в котором ключи - refSNPID, а значения - соответствующие им строки базы.
                На вход подаётся отсортированная по refSNPID база с очищенным столбцом refSNPID,
                без хэдера и, в случае соответствующего пользовательского выбора, с отсечением по p-value.
                Если refSNPID уникален, то соответствующая ему строка таблицы пойдёт в двумерный массив,
                служащий значением этому refSNPID-ключу, и будет представлять собой единственный вложенный список.
                Если же встречается несколько строк подряд с одним и тем же refSNPID,
                добавляем их в качестве элементов двумерного массива, являющегося значением "общему" refSNPID-ключу.
                '''
                rs_and_ann_dict = {self.two_dim[0][self.rs_col_index]: self.two_dim[0]}
                for row_num in range(1, len(self.two_dim)):
                        if self.two_dim[row_num][self.rs_col_index] != self.two_dim[row_num - 1][self.rs_col_index]:
                                rs_and_ann_dict[self.two_dim[row_num][self.rs_col_index]] = [self.two_dim[row_num]]
                        else:
                                rs_and_ann_dict[self.two_dim[row_num - 1][self.rs_col_index]] += [self.two_dim[row_num]]
                return rs_and_ann_dict

class RefSNPIDTable(AnyTable):
        '''
        Действия, производимые с отсортированными пользовательскими таблицами.
        '''
        def __init__(self, two_dim, rs_col_index):
                super().__init__(two_dim, rs_col_index)
                
        def rs_search(self, rs_and_ann_dict):
                '''
                Поиск строк базы, содержащих нужные пользователю refSNPID.
                На вход подаются отсортированные пользовательские наборы refSNPID и преобразованная в словарь база.
                Поскольку пользовательские наборы refSNPID отсортированы, можно будет несколько оптимизировать скорость поиска (но это не точно(с)).
                В начале работы с очередным набором пользовательских refSNPID будет создаваться новый сокращающийся словарь.
                Сокращаться словарь будет следующим образом:
                Сначала будут удалены элементы, находящиеся вне диапазона от минимального до максимального из искомых refSNPID текущего файла.
                Затем осуществится удаление элементов сокращающегося словаря, ключи которых меньше текущего пользовательского refSNPID.
                Результат - двумерный массив, состоящий из значений, соответствующих ключам, совпадающим с пользовательскими refSNPID.
                '''
                rs_and_ann_dict_red = {key: value for key, value in rs_and_ann_dict.items() if key >= self.two_dim[0][self.rs_col_index] and key <= self.two_dim[-1][self.rs_col_index]}
                out_two_dim = []
                for row in self.two_dim:
                        rs = row[self.rs_col_index]
                        if rs in rs_and_ann_dict_red:
                                out_two_dim += rs_and_ann_dict_red[rs]
                                rs_and_ann_dict_red = {key: value for key, value in rs_and_ann_dict_red.items() if key >= rs}
                return out_two_dim

##Работа с базой.
with open(base_file_path) as base_op:
        base_two_dim = list(csv.reader(base_op, delimiter = '\t'))

#Поиск индекса refSNPID-"столбца" базы.
base_rs_col_index = rs_col_index_search(base_two_dim)

#Сохранение хэдеров базы как списка.
base_table = BaseTable(base_two_dim, base_rs_col_index)
base_headers, base_two_dim_wo_header = base_table.header_save(num_of_base_headers)

#Отсечение по p-value (если пользователю это нужно).
base_table_wo_header = BaseTable(base_two_dim_wo_header, base_rs_col_index)
try:
        two_dim_constr = base_table_wo_header.constrict_by_pval(base_pval_column, base_pval_threshold)
except NameError:
        two_dim_constr = base_two_dim_wo_header

#Удаление строк базы, содержащих точку вместо refSNPID, удаление дублей строк и сортировка очищенной базы.
base_table_wo_header = AnyTable(two_dim_constr, base_rs_col_index)
base_two_dim_pure = base_table_wo_header.clean_and_sort()

#Создание словаря с refSNPID в качестве ключей, а refSNPID-содержащими строками в качестве значений.
base_table_pure = BaseTable(base_two_dim_pure, base_rs_col_index)
base_dict = base_table_pure.dict_create()

##Работа с пользовательскими таблицами и поиск refSNPID в базе.
rs_files = os.listdir(rs_dir)
for rs_file in rs_files:
        print('Поиск в таблице ' + os.path.basename(base_file_path) + ' строк со снипами, взятыми из ' + rs_file)

        #Даже если пользовательская таблица представлет собой единственный столбец с одними лишь refSNPID, делаем её двумерным массивом.
        with open(os.path.join(rs_dir, rs_file)) as rs_op:
                rs_two_dim = list(csv.reader(rs_op, delimiter = '\t'))

        #Поиск индекса "столбца" пользовательской таблицы.
        rs_rs_col_index = rs_col_index_search(rs_two_dim)

        #Удаление из пользовательских наборов refSNPID хэдера.
        if rs_two_dim[0][0].find('#') != -1 or rs_two_dim[0][0].find('track name') != -1:
                rs_two_dim_wo_header = rs_two_dim[1:]
        else:
                rs_two_dim_wo_header = rs_two_dim

        #Очистка и сортировка пользовательской таблицы.
        rs_table_wo_header = AnyTable(rs_two_dim_wo_header, rs_rs_col_index)
        rs_table_pure = rs_table_wo_header.clean_and_sort()

        #Поиск строк с refSNPID, взятых из пользовательских таблиц, в словаре.
        #Полученный двумерный массив вновь сортируется по столбцу refSNPID, индекс которого тот же, что и в базе.
        #Если результатов поиска нет, ищем refSNPID из следующего файла.
        refsnpid_table = RefSNPIDTable(rs_table_pure, rs_rs_col_index)
        found_in_base = sorted(refsnpid_table.rs_search(base_dict), key = lambda row: row[base_rs_col_index])
        if len(found_in_base) == 0:
                continue

        #Сохраняем полученные таблицы в соответствующие файлы.
        targetfile = rs_file.split('.')[0] + '_I_' + os.path.basename(base_file_path.split('.txt')[0]) + '.txt'
        with open(os.path.join(targetdir, targetfile), 'w') as t:
                try:
                        for line in base_headers:
                                t.write(line + '\n')
                except NameError:
                        pass
                for row in found_in_base:
                        t.write('\t'.join(row) + '\n')

#####Бонус: refSNPID-содержащие таблицы для тестирования с таблицей Whole_Blood_Analysis.perm.txt архива GTEx_Analysis_v6p_eQTL.
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
