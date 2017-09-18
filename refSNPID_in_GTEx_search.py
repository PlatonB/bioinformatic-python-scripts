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

GTEx-таблицы можно найти по ссылке https://www.gtexportal.org/home/datasets.
Скрипт протестирован на таблице Whole_Blood.egenes.annotated.txt архива GTEx_Analysis_v7_eQTL.tar.gz.

В исходной папке не желательно держать файлы, отличные от refSNPID-содержащих таблиц.
Папку для результатов перед выполнением работы лучше оставлять пустой.
Могу доработать скрипт таким образом, чтобы он искал снипы сразу по нескольким GTEx-таблицам (обращайтесь в Issues).

Для поиска: Genotype-Tissue Expression (GTEx) project, eQTL, SNP, биоинформатика, программирование, python 3.
''')

import os
import re
import csv

rs_dir = input('Путь к папке с refSNPID-содержащими таблицами (не забывайте экранировать): ')
gtex_file_path = input('Путь к GTEx-таблице (не забывайте экранировать и указывать расширение .txt): ')
targetdir = input('Путь к папке для конечных файлов (не забывайте экранировать): ')

#Поиск индекса "столбца" любой содержащей refSNPID таблицы, представленной с помощью модуля csv в виде двумерного массива.
#Если во второй строке refSNPID отсутствует (например, в таблицах GTEx вместо refSNPID может быть точка),
#то ищем в третьей, если нет и в третьей, движемся дальше по строкам, пока не найдём.
def rs_col_index_search(one_or_more_col_two_dim):
        for row_num in range(1, len(one_or_more_col_two_dim)):
                for cell in one_or_more_col_two_dim[row_num]:
                        if re.match(r'rs\d+', cell):
                                return one_or_more_col_two_dim[row_num].index(cell)

#Сортировка GTEx-таблицы по столбцу с refSNPID, чтобы строки с одним и тем же refSNPID расположились друг за другом.
#Создание словаря, в котором ключи - refSNPID, а значения - соответствующие строки таблицы.
#Если встречается несколько строк подряд с одним и тем же refSNPID,
#добавляем их в двумерный массив, являющийся значением этому refSNPID-ключу.
def dict_create(two_dim, rs_col_index):
        two_dim.sort(key = lambda row: row[rs_col_index])
        row_num, rs_ann_dict = 1, {}
        for index in range(1, len(two_dim)):
                if two_dim[row_num][rs_col_index] != two_dim[row_num - 1][rs_col_index]:
                        rs_ann_dict[two_dim[row_num][rs_col_index]] = [two_dim[row_num]]
                else:
                        rs_ann_dict[two_dim[row_num - 1][rs_col_index]] += [two_dim[row_num]]
                row_num += 1
        return rs_ann_dict

#Поиск строк таблицы GTEx, содержащих нужные пользователю refSNPID.
#Найденные пары ключ-значение удаляются для постепенного уменьшения словаря и, как следствие, некоторого повышения производительности поиска.
#Результат - двумерный массив, состоящий из значений, соответствующих ключам, совпадающим с искомыми refSNPID.
def rs_search(one_or_more_col_two_dim, rs_col_index, rs_ann_dict):
        out_two_dim = []
        for row in one_or_more_col_two_dim:
                rs = row[rs_col_index]
                if rs in rs_ann_dict:
                        out_two_dim += rs_ann_dict[rs]
                        del rs_ann_dict[rs]
        return out_two_dim

##Работа с GTEx-таблицей.
with open(gtex_file_path) as gtex_op:
        gtex_two_dim = list(csv.reader(gtex_op, delimiter = '\t'))

#Проверка наличия шапки GTEx-таблицы.
#При наличии шапки - её временный вынос из таблицы.
if gtex_two_dim[0][0].find('gene_id') != -1:
        gtex_header = '\t'.join(gtex_two_dim[0])
        gtex_two_dim = gtex_two_dim[1:]

#Поиск индекса "столбца" GTEx-таблицы.
gtex_rs_col_index = rs_col_index_search(gtex_two_dim)

#Удаление строк, содержащих точку вместо refSNPID.
#Если вам вдруг эти строки требуется учитывать, пишите в Issues, подумаю.
gtex_two_dim_pure = []
for row in gtex_two_dim:
        if row[gtex_rs_col_index].find('.') == -1:
                gtex_two_dim_pure.append(row)

#Создание словаря с refSNPID в качестве ключей, а refSNPID-содержащими строками в качестве значений.
gtex_dict = dict_create(gtex_two_dim_pure, gtex_rs_col_index)

##Работа с refSNPID-таблицами и поиск refSNPID в таблице GTEx.
rs_files = os.listdir(rs_dir)
for rs_file in rs_files:
        print('Поиск в таблице ' + os.path.basename(gtex_file_path) + ' строк со снипами, взятыми из ' + rs_file)
        with open(os.path.join(rs_dir, rs_file)) as rs_op:
                rs_table = list(csv.reader(rs_op, delimiter = '\t'))

        #Удаление из наборов refSNPID хэдера и одинаковых элементов.
        if rs_table[0][0].find('#') != -1 or rs_table[0][0].find('track name') != -1:
                rs_table = rs_table[1:]
        rs_table_pure = [line.split('\t') for line in list(set(['\t'.join(row) for row in rs_table]))]
        
        #Поиск индекса "столбца" refSNPID-таблицы.
        rs_rs_col_index = rs_col_index_search(rs_table_pure)

        #Поиск строк с refSNPID, взятых из refSNPID-таблиц, в GTEx-словаре.
        #Полученный двумерный массив вновь сортируется по столбцу refSNPID, индекс которого тот же, что и в GTEx-массиве.
        #Если результатов поиска нет, ищем refSNPID из следующего файла.
        found_in_gtex = sorted(rs_search(rs_table_pure, rs_rs_col_index, gtex_dict), key = lambda row: row[gtex_rs_col_index])
        if len(found_in_gtex) == 0:
                continue

        #Сохраняем полученные таблицы в соответствующие файлы.
        targetfile = rs_file.split('.')[0] + '_I_' + os.path.basename(gtex_file_path.split('.')[0]) + '.txt'
        with open(os.path.join(targetdir, targetfile), 'w') as t:
                try:
                        t.write(gtex_header + '\n')
                except NameError:
                        pass
                for row in found_in_gtex:
                        t.write('\t'.join(row) + '\n')

#####Бонус: refSNPID-содержащие таблицы для тестирования.
test = '''
#refSNPID, встречающиеся в Whole_Blood 1 раз.
rs190889721
rs184276234
rs10910055
rs11122083
rs184383837

#refSNPID, повторяющиеся в Whole_Blood несколько раз + заведомо несуществующие refSNPID.
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

#refSNPID, встречающиеся 1 раз в Whole_Blood, но идущие не с первой строки.
1	q	!@#$%^&*()
2	w	)(*&^%$#@!
3	e	rs188678711
4	r	rs2203348
5	t	rs3760905
'''
