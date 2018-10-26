print('''
Python3-скрипт пересечения набора BED-треков с единственным BED-треком.
Автор: Платон Быкадоров (platon.work@gmail.com), 2016-2018.
Версия: V4.1.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Простое руководство по установке среды разработки и запуску скриптов:
github.com/PlatonB/bioinformatic-python-scripts#Установка-среды-разработки

Формат BED:
#(опционально) Заголовок со знаком решётки в начале, либо тоже опциональный заголовок такого вида:
track name="Заголовок" description="Заголовок по стандатрам UCSC Table Browser" visibility=3 url=
chr6 (или 6)	32665241	32665242	(опционально) доп. поля, разделённые табуляциями
chr6 (или 6)	32665244	32665245	(опционально) доп. поля, разделённые табуляциями
...

Скрипт создан в качестве замены функционала пересечения гигантского монстра BEDTools.
До безобразия прост в использовании, написан на заточенном под такие задачи Питоне,
не страдает утечками памяти и запускается почти на любой ОС, не требуя установки.

Пример исходных треков и результатов их пересечения - в конце программы.

Для поиска: пересечение интервалов, биоинформатика, программирование, intersection of intervals in Python.
''')

def table_preparation(src_file_opened):
        '''
        Сначала функция определяет, является ли первая строка трека хэдером.
        Далее основная часть трека преобразуется в двумерный массив.
        Для правильности выполнения таких дальнейших действий, как
        сортировка массива и сопоставление расположения интервалов, значениям
        столбцов с геномными координатами даётся числовой тип данных.
        Для унификации поведения скрипта и инструментария BEDTools,
        нулевые интервалы исходных треков будут расширены путём
        вычитания 1 из первой координаты и прибавления 1 ко второй.
        Сортировка по всем столбцам с учётом типа данных.
        '''
        first_line = src_file_opened.readline()
        if first_line.find('#') != -1 or first_line.find('track name=') != -1:
                header = first_line
        else:
                src_file_opened.seek(0)
                header = None
        two_dim = []
        for line in src_file_opened:
                if re.match(r'\d+', line) != None:
                        line = 'chr' + line
                row = line.split('\t')
                row[1], row[2] = int(row[1]), int(row[2])
                if row[1] == row[2]:
                        row[1] -= 1
                        row[2] += 1
                two_dim.append(row)
        two_dim.sort()
        return header, two_dim

class IntersectionCore():
        '''
        "Ядро" алгоритма пересечения.
        '''
        def __init__(self, two_dim_1, two_dim_2, whose_tail):
                '''
                Атрибуты - отсортированные двумерные массивы с пересекаемыми
                интервалами, их размеры, исходные значения "указателей"
                и счётчика чётности/нечётности количества проходов,
                управляемый пользователем распределитель "хвостов",
                а также массив для накопления успешных пересечений.
                Под указателями будут подразумеваться индексы тех элементов
                массивов, с которых начинается каждый новый проход.
                Значения указателей после запусков проходов увеличиваются,
                поэтому размеры ещё необработанных частей списков уменьшаются.
                Хвостами будем называть опциональные элементы каждой
                строки, идущие после первых трёх элементов.
                Результаты накапливаются не во множество, а в список,
                чтобы не убивались повторы вхождения интервала одного
                трека в накладывающиеся друг на друга интервалы другого.
                '''
                self.two_dim_1 = two_dim_1
                self.two_dim_1_row_num = 0
                self.two_dim_1_len = len(self.two_dim_1)
                self.two_dim_2 = two_dim_2
                self.two_dim_2_row_num = 0
                self.two_dim_2_len = len(self.two_dim_2)
                self.whose_tail = whose_tail
                self.pass_number = 0
                self.results = []

        def one_pass(self):
                '''
                Метод, производящий один проход.
                В рамках прохода ищутся пересечения
                одного интрервала 1-го или 2-го списка
                с интервалами 2-го или 1-го списка, соответственно.
                Деление списков на 1-й и 2-й условно, поскольку
                при каждом следующем запуске метода one_pass
                1-й и 2-й списки становятся 2-ым и 1-ым, либо наоборот.
                Чтобы наши результаты привести в соответствие с результатами пересечения
                программой BedTools, нельзя допускать получение нулевых интервалов.
                Поэтому равенство координат end_1 и start_2 будет
                считаться не успешным пересечением, а заползанием
                интервала 1-го списка влево (т.е., в меньшую сторону).
                А равенство start_1 и end_2 - заползанием интервала
                1-го списка вправо (т.е., в большую сторону).
                '''

                #Переменная, изменение значения которой на False приводит к
                #перемене местами как списков, так и сопутствующих показателей.
                switching_flag = True

                #Сюда может быть сохранён один интервал,
                #полученный в результате успешного пересечения.
                intersection = None
                
                while switching_flag:

                        #Счётчик чётности/нечётности количества проходов.
                        #Необходим для регуляции прописывания в конечные
                        #строки хвостов (дополнительных элементов, т.е.
                        #элементов, идущих после третьего столбца).
                        self.pass_number += 1
                        
                        for row_1 in self.two_dim_1[self.two_dim_1_row_num:]:
                                chrom_1 = row_1[0]
                                start_1 = row_1[1]
                                end_1 = row_1[2]

                                #Счётчик успешных пересечений.
                                #После осуществления прохода сбрасывается.
                                success = 0

                                #Количество оставшихся после предыдущих
                                #проходов элементов 2-го списка.
                                #Это значение изменяется, а, именно, уменьшается,
                                #только тогда, когда список, являющийся на
                                #данный момент 2-ым, находится в роли 1-го.
                                #Пригождается в ситуации, когда
                                #2-й список истощился (см. ниже(*)).
                                two_dim_2_rem_len = self.two_dim_2_len - self.two_dim_2_row_num
                                
                                for row_2 in self.two_dim_2[self.two_dim_2_row_num:]:
                                        chrom_2 = row_2[0]
                                        start_2 = row_2[1]
                                        end_2 = row_2[2]

                                        #chr1 больше (правее) chr2.
                                        #Это аналогично случаю, когда без успешных пересечений
                                        #интервал 1-го списка оказывается правее (см. ниже(**)).
                                        #Прозводим смену списков интервалов
                                        #без сдвига указателя 1-го списка.
                                        if chrom_1 > chrom_2:
                                                switching_flag = False
                                                break

                                        #-----[s1-----e1]---(s2-----e2)]-----
                                        #После одного или нескольких успешных пересечений
                                        #интервал 1-го списка оказался левее очередного
                                        #интервала 2-го списка в пределах одной хромосомы.
                                        #Или по ходу успешной серии пересечений chr
                                        #1-го списка стала левее chr 2-го списка.
                                        #Поскольку оказавшийся слева успешно пересекавшийся ранее
                                        #интервал 1-го списка ещё с кем-либо больше не пересечётся,
                                        #сдвигаем указатель на следующий интервал 1-го списка.
                                        #Указатель по 2-му списку здесь и во
                                        #всех остальных случаях не трогаем.
                                        #Переключаем наборы интервалов.
                                        if (end_1 <= start_2 and success > 0) or (chrom_1 < chrom_2 and success > 0):
                                                self.two_dim_1_row_num += 1
                                                switching_flag = False
                                                break

                                        #-----[s2-----e2]---(s1-----e1)]-----
                                        #Очень коварная для программиста ситуация, которая может
                                        #возникнуть, если интервалы 2-го набора накладываются друг на друга.
                                        #Успешно до этого момента пересекавшийся интервал 1-го списка
                                        #оказался правее очередного интервала 2-го списка.
                                        #Продолжаем пытаться пересекать этот интервал
                                        #со следующими интервалами 2-го списка.
                                        if start_1 >= end_2 and success > 0:
                                                continue

                                        #-----[s1-----e1]---(s2-----e2)]-----
                                        #Если ещё не пересеклось, проверяем, не левее
                                        #ли интервал 1-го списка интервала 2-го списка.
                                        #Если левее, то без переключения списков
                                        #сдвигаем указатель на следующий интервал 1-го.
                                        if end_1 <= start_2 or chrom_1 < chrom_2:
                                                self.two_dim_1_row_num += 1
                                                break
                                        
                                        ####################
                                        
                                        ##Пытаемся пересечь.
                                        ##Возможные случаи, когда chr 1-го и 2-го списка не равны друг
                                        ##другу, должны были быть обработаны ранее, поэтому на этом
                                        ##этапе сравнивать хромосомы не нужно - они точно равны.

                                        #Поиск максимума стартовых координат и минимумов конечных.
                                        #Успешное пересечение произойдёт только, если максимум
                                        #стартовых строго меньше минимума конечных.
                                        #В противном случае интервал 1-го списка находится
                                        #либо левее, либо правее интервала 2-го списка.
                                        #Но возможная ситуация, когда 1-й интервал левее 2-го,
                                        #должна была отфильтроваться в одном из предыдущих блоков.
                                        #Т.о., на стадии непосредственно пересечений либо оба интервала
                                        #имеют перекрывающуюся область более одного нуклеотида,
                                        #либо интервал из 1-го списка находится правее.
                                        max_start = max(start_1, start_2)
                                        min_end = min(end_1, end_2)

                                        #-----[s2-----e2]---(s1-----e1)]-----
                                        #(**)Если не пересеклось, то получается,
                                        #что интервал из 1-го списка оказался правее.
                                        #Этот блок кода сработает только, если
                                        #ранее не было успешных пересечений.
                                        #Меняем местами списки интервалов
                                        #без сдвига указателя 1-го.
                                        if max_start >= min_end:
                                                switching_flag = False
                                                break

                                        #-----(s1---[{s2-----e1})---e2]-----
                                        #-----[s2---({s1-----e2}]---e1)-----
                                        #-----(s1---[{s2-----e2}]---e1)-----
                                        #-----[s2---({s1-----e1})---e2]-----
                                        #Успешное пересечение.
                                        else:
                                                intersection = [chrom_1, max_start, min_end]
                                                success += 1
                                                
                                        ####################
                                                
                                        #Раз дошли до этого блока, то, значит, было успешное пересечение.
                                        #Добавляем интервал и выбранный пользователем хвост в конечный список.
                                        if self.whose_tail == 1:
                                                if self.pass_number % 2 != 0:
                                                        tail = row_1[3:]
                                                else:
                                                        tail = row_2[3:]
                                        elif self.whose_tail == 2:
                                                if self.pass_number % 2 != 0:
                                                        tail = row_2[3:]
                                                else:
                                                        tail = row_1[3:]
                                        else:
                                                tail = []
                                        self.results.append(intersection + tail)
                                        
                                        #(*)Если успешное пересечение состоялось с самым последним
                                        #интервалом второго списка, то нужно сразу переключить списки.
                                        #Сдвигаем указатель на следующий интервал 1-го списка.
                                        if success == two_dim_2_rem_len:
                                                self.two_dim_1_row_num += 1
                                                switching_flag = False
                                                break

                                #Выход из цикла работы с 1-ым и 2-ым списками
                                #для последующий их смены на 2-й и 1-й.
                                if switching_flag == False:
                                        break
                                
                        #Переключение списков.
                        #Обновлённые позиции указателей 1-го и 2-го списков сохранились
                        #в экземпляре "ядерного" класса и могут быть использованы
                        #при следующем вызове метода, осуществляющего проход.
                        #Если набор строк 1-го списка истощился, цикл
                        #"for row_1" завершится самостоятельно, т.е. без break.
                        #Находящийся вне ядра блок отследит эту ситуацию путём
                        #сопоставления позиции указателя 1-го списка с общим количеством
                        #элементов 1-го списка и произведёт выход из ядра программы
                        #(см. ниже (***)).
                        break

####################################################################################################

import os
import re

us_dir_path = input('Путь к исходной папке с набором BED-треков: ')
ucsc_file_path = input('Путь к исходному "одиночному" BED-треку: ')
whose_tail = int(input('''BED-трек может содержать 3 основных и несколько дополнительных столбцов.
Дополнительные столбцы каких треков хотите помещать в конечные файлы?
0 - никаких (либо они отсутствуют), 1 - "одиночного" трека, 2 - из набора в указанной вами папке
[0|1|2]: '''))
trg_dir_path = input('Путь к папке для конечных файлов: ')

##Работа с "одиночным" BED-треком
##Я во время тестирования использовал в качестве "одиночных"
##файлов треки, сформированные в UCSC Table Browser, поэтому
##далее для краткости буду называть "одиночные" файлы "UCSC-файлами".
with open(ucsc_file_path) as ucsc_file_opened:

        #Получение хэдера, если таковой имеется, и
        #отсортированного двумерного массива с данными.
        ucsc_header, ucsc_two_dim = table_preparation(ucsc_file_opened)

##Работа с набором таблиц, которые должны
##будут пересекаться с UCSC-файлом.
##Далее они будут называться "пользовательскими".
us_file_names = os.listdir(us_dir_path)
for us_file_name in us_file_names:
        with open(os.path.join(us_dir_path, us_file_name)) as us_file_opened:
                print('Пересекаются треки ' + us_file_name + ' и ' + os.path.basename(ucsc_file_path))
                us_header, us_two_dim = table_preparation(us_file_opened)

        #Создание экземпляра, в котором будут накапливаться
        #промежуточные и оставаться конечные результаты работы.
        int_core = IntersectionCore(ucsc_two_dim, us_two_dim, whose_tail)

        #Цикл, запускающий проходы и производящий смену списков, будет
        #работать до тех пор, пока (***)один из списков не истощится полностью.
        #Когда истощится, осуществим выход из "ядра" программы пересечения.
        while int_core.two_dim_1_row_num != int_core.two_dim_1_len:

                #"Проход".
                int_core.one_pass()
                
                #Перед возможным запуском следующего прохода атрибуты,
                #характеризующие пересекаемые треки и степень прогресса работы,
                #принимают значения своих атрибутов-антагонистов.
                int_core.two_dim_1, int_core.two_dim_1_row_num, int_core.two_dim_1_len, \
                                    int_core.two_dim_2, int_core.two_dim_2_row_num, int_core.two_dim_2_len = \
                                    int_core.two_dim_2, int_core.two_dim_2_row_num, int_core.two_dim_2_len, \
                                    int_core.two_dim_1, int_core.two_dim_1_row_num, int_core.two_dim_1_len

        #Если окончательный список пересечений - пустой, то не создаём конечный файл,
        #а начинаем пересекать UCSC-трек со следующим пользовательским файлом.
        if len(int_core.results) == 0:
                continue

        #Сортировка.
        int_core.results.sort()

        #Прописываем результаты в конечный файл.
        trg_file_name = '[' + us_file_name.split('.')[0] + '_I_' \
                        + os.path.basename(ucsc_file_path.split('.')[0]) + ']' + '.txt'
        if ucsc_header != None and us_header != None:
                trg_header = '#[' + ucsc_header.split('\n')[0] + ' INTERSECTED WITH ' + us_header.split('\n')[0] + ']'
                if trg_header.find('\n') == -1:
                        trg_header += '\n'
        with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
                try:
                        trg_file_opened.write(trg_header)
                except NameError:
                        pass
                for row in int_core.results:
                        row[1], row[2] = str(row[1]), str(row[2])
                        if row[-1].find('\n') == -1:
                                row[-1] += '\n'
                        trg_file_opened.write('\t'.join(row))

'''
track name="test1" description="table browser query on test1" visibility=3 url=
chr1	5	11
chr2	22	30
chr2	25	28
chr2abc	15	15
chr19	1	5
chr2abc	20	32
chr2	25	27
chr2	29	40
chr1	13	20
chr1	15	20
chr2	7	20
chr19	5	6

track name="test2" description="table browser query on test2" visibility=3 url= 
chr1	1	4
chr2abc	50	99
chr2	30	32
chr1	1	12
chr2	4	7
chr2	9	23
chr2	54	64
chr2	9	22
chr1	17	21
chr2	30	39
chr2abc	1	40
chr1	14	15
chr2	32	50
chr1	17	17

#(длинный объединённый хэдер)
chr1	5	11
chr1	14	15
chr1	16	18
chr1	16	18
chr1	17	20
chr1	17	20
chr2	9	20
chr2	9	20
chr2	22	23
chr2	30	32
chr2	30	39
chr2	32	40
chr2abc	14	16
chr2abc	20	32
'''
