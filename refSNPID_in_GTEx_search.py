print('''
Python3-скрипт, который выводит строки таблицы GTEx, содержащие искомые refSNPID.
Автор: Платон Быкадоров, 2017.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

На вход подаются таблицы, один из столбцов которых содержит идентификаторы однонуклеотидных полиморфизмов (refSNPID вида rs1234567890).
Скрипт самостоятельно обнаружит столбец с искомыми refSNPID в каждой таблице пользователя (даже если в разных таблицах разный номер rs-столбца).
Также скрипт не растеряется, если в rs-столбце присутствуют иные данные, точки, прочерки и т.д..
rs-столбец может быть единственным столбцом исходной таблицы.
Исходные refSNPID-таблицы могут содержать заголовок, начинающийся с "#" или "track name".

GTEx-таблицы можно найти по ссылке https://www.gtexportal.org/home/datasets (требуется регистрация).
Скрипт протестирован на таблице Whole_Blood.egenes.annotated.txt архива GTEx_Analysis_v7_eQTL.tar.gz.

В исходной папке не желательно держать файлы, отличные от refSNPID-содержащих таблиц.
Папку для результатов перед выполнением работы лучше оставлять пустой.
Могу доработать скрипт таким образом, чтобы он искал снипы сразу по нескольким GTEx-таблицам (обращайтесь в Issues).

Для поиска: Genotype-Tissue Expression (GTEx) project, eQTL, SNP, биоинформатика, программирование, python 3.
''')

import os
import re
import csv

rs_dir = input('Путь к папке с refSNPID-содержащими таблицами: ')
gtex_file_path = input('Путь к GTEx-таблице (не забывайте указывать расширение .txt): ')
targetdir = input('Путь к папке для конечных файлов: ')

def rs_col_index_search(two_dim):
        '''
        Поиск индекса "столбца" любой содержащей refSNPID таблицы, представленной с помощью модуля csv в виде двумерного массива.
        Столбец с refSNPID может быть единственным столбцом подаваемого на вход двумерного массива.
        Если во второй строке refSNPID отсутствует (например, в таблицах GTEx вместо refSNPID может быть точка),
        то ищем в третьей, если нет и в третьей, движемся дальше по строкам, пока не найдём.
        Функция может применяться и для таблиц с хэдерами.
        '''
        for row_num in range(1, len(two_dim)):
                for cell in two_dim[row_num]:
                        if re.match(r'rs\d+', cell):
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
                two_dim_pure = [row for row in two_dim_unique if re.search(r'rs\d+', row[self.rs_col_index]) != None]
                two_dim_pure.sort(key = lambda row: row[self.rs_col_index])
                return two_dim_pure
        
class GTExTable(AnyTable):
        '''
        Действия, производимые с таблицей GTEx.
        '''
        def __init__(self, two_dim, rs_col_index):
                super().__init__(two_dim, rs_col_index)

        def header_save(self):
                '''
                Проверка наличия шапки GTEx-таблицы.
                При наличии шапки - её временный вынос из таблицы.
                '''
                if self.two_dim[0][0].find('gene_id') != -1:
                        two_dim_header = '\t'.join(self.two_dim[0])
                        two_dim_wo_header = self.two_dim[1:]
                else:
                        two_dim_wo_header = self.two_dim
                return two_dim_header, two_dim_wo_header

        def dict_create(self):
                '''
                Создание словаря, в котором ключи - refSNPID, а значения - соответствующие им строки GTEx-таблицы.
                На вход подаётся отсортированная по refSNPID GTEx-таблица с очищенным столбцом refSNPID, без хэдера.
                Если refSNPID уникален, то соответствующая ему строка таблицы пойдёт в двумерный массив,
                служащий значением этому refSNPID-ключу, и будет представлять собой единственный вложенный список.
                Если же встречается несколько строк подряд с одним и тем же refSNPID,
                добавляем их в качестве элементов двумерного массива, являющегося значением "общему" refSNPID-ключу.
                '''
                row_num, rs_and_ann_dict = 1, {}
                for index in range(1, len(self.two_dim)):
                        if self.two_dim[row_num][self.rs_col_index] != self.two_dim[row_num - 1][self.rs_col_index]:
                                rs_and_ann_dict[self.two_dim[row_num][self.rs_col_index]] = [self.two_dim[row_num]]
                        else:
                                rs_and_ann_dict[self.two_dim[row_num - 1][self.rs_col_index]] += [self.two_dim[row_num]]
                        row_num += 1
                return rs_and_ann_dict

class RefSNPIDTable(AnyTable):
        '''
        Действия, производимые с отсортированными refSNPID-содержащими таблицами.
        '''
        def __init__(self, two_dim, rs_col_index):
                super().__init__(two_dim, rs_col_index)
                
        def rs_search(self, rs_and_ann_dict):
                '''
                Поиск строк таблицы GTEx, содержащих нужные пользователю refSNPID.
                На вход подаются отсортированные наборы refSNPID и преобразованная в словарь GTEx-таблица.
                Поскольку наборы искомых refSNPID отсортированы, можно будет несколько оптимизировать скорость поиска.
                В начале работы с очередным набором искомых refSNPID будет создаваться новый сокращающийся GTEx-словарь.
                Сокращаться словарь будет следующим образом:
                Сначала будут удалены элементы, находящиеся вне диапазона от минимального до максимального из искомых refSNPID текущего файла.
                Затем осуществится удаление элементов сокращающегося словаря, ключи которых меньше текущего искомого refSNPID.
                Результат - двумерный массив, состоящий из значений, соответствующих ключам, совпадающим с искомыми refSNPID.
                '''
                rs_and_ann_dict_red = {key: value for key, value in rs_and_ann_dict.items() if key >= self.two_dim[0][self.rs_col_index] and key <= self.two_dim[-1][self.rs_col_index]}
                out_two_dim = []
                for row in self.two_dim:
                        rs = row[self.rs_col_index]
                        if rs in rs_and_ann_dict_red:
                                out_two_dim += rs_and_ann_dict_red[rs]
                                rs_and_ann_dict_red = {key: value for key, value in rs_and_ann_dict_red.items() if key >= rs}
                return out_two_dim

##Работа с GTEx-таблицей.
with open(gtex_file_path) as gtex_op:
        gtex_two_dim = list(csv.reader(gtex_op, delimiter = '\t'))

#Поиск индекса "столбца" GTEx-таблицы.
gtex_rs_col_index = rs_col_index_search(gtex_two_dim)

#Сохранение хэдера GTEx-таблицы в переменную.
gtex_table = GTExTable(gtex_two_dim, gtex_rs_col_index)
gtex_header, gtex_two_dim_wo_header = gtex_table.header_save()

#Удаление строк GTEx-таблицы, содержащих точку вместо refSNPID, удаление дублей строк и сортировка очищенной GTEx-таблицы.
gtex_table_wo_header = AnyTable(gtex_two_dim_wo_header, gtex_rs_col_index)
gtex_two_dim_pure = gtex_table_wo_header.clean_and_sort()

#Создание словаря с refSNPID в качестве ключей, а refSNPID-содержащими строками в качестве значений.
gtex_table_pure = GTExTable(gtex_two_dim_pure, gtex_rs_col_index)
gtex_dict = gtex_table_pure.dict_create()

##Работа с refSNPID-таблицами и поиск refSNPID в таблице GTEx.
rs_files = os.listdir(rs_dir)
for rs_file in rs_files:
        print('Поиск в таблице ' + os.path.basename(gtex_file_path) + ' строк со снипами, взятыми из ' + rs_file)

        #Даже если refSNPID-содержащая таблица представлет собой единственный столбец с одними лишь refSNPID, делаем её двумерным массивом.
        with open(os.path.join(rs_dir, rs_file)) as rs_op:
                rs_two_dim = list(csv.reader(rs_op, delimiter = '\t'))

        #Поиск индекса "столбца" refSNPID-таблицы.
        rs_rs_col_index = rs_col_index_search(rs_two_dim)

        #Удаление из наборов refSNPID хэдера.
        if rs_two_dim[0][0].find('#') != -1 or rs_two_dim[0][0].find('track name') != -1:
                rs_two_dim_wo_header = rs_two_dim[1:]
        else:
                rs_two_dim_wo_header = rs_two_dim

        #Очистка и сортировка refSNPID-таблицы.
        rs_table_wo_header = AnyTable(rs_two_dim_wo_header, rs_rs_col_index)
        rs_table_pure = rs_table_wo_header.clean_and_sort()

        #Поиск строк с refSNPID, взятых из refSNPID-таблиц, в GTEx-словаре.
        #Полученный двумерный массив вновь сортируется по столбцу refSNPID, индекс которого тот же, что и в GTEx-массиве.
        #Если результатов поиска нет, ищем refSNPID из следующего файла.
        refsnpid_table = RefSNPIDTable(rs_table_pure, rs_rs_col_index)
        found_in_gtex = sorted(refsnpid_table.rs_search(gtex_dict), key = lambda row: row[gtex_rs_col_index])
        if len(found_in_gtex) == 0:
                continue

        #Сохраняем полученные таблицы в соответствующие файлы.
        targetfile = rs_file.split('.')[0] + '_I_' + os.path.basename(gtex_file_path.split('.txt')[0]) + '.txt'
        with open(os.path.join(targetdir, targetfile), 'w') as t:
                try:
                        t.write(gtex_header + '\n')
                except NameError:
                        pass
                for row in found_in_gtex:
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
