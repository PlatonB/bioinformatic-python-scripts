print('''
Python3-скрипт пересечения набора BED-треков (списков координатных интервалов) с единственным BED-треком.
Автор: Платон Быкадоров, 2016-2017.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Формат BED:

#Заголовок со знаком решётки в начале, либо такого вида:
track name="Заголовок" description="Заголовок по стандатрам UCSC Table Browser. Любые заголовки BED-таблиц для этого скрипта необязательны" visibility=3 url=
chr6 (или 6)	32665241	32665242	(опционально) дополнительные поля, разделённые табуляциями
chr6 (или 6)	32665244	32665245	(опционально) дополнительные поля, разделённые табуляциями
...

В исходной папке не должно быть ничего, кроме пересекаемого с одиночным BED-треком набора треков, а одиночный BED-трек должен находиться в любой другой папке.
Папку для результатов перед выполнением работы желательно оставлять пустой.
Если нужно, могу переслать или выложить вариант этого скрипта, обрабатывающий исходные файлы, размещённые по папкам и/или подпапкам.

Для поиска: пересечение интервалов, биоинформатика, программирование, python.
''')

sourcedir1 = input('Путь к исходной папке с набором BED-треков (не забывать экранировать): ')
ucsc_path = input('Путь к исходному "одиночному" BED-треку (не забывать экранировать): ')
targetdir = input('Путь к конечной папке (не забывать экранировать): ')

import os
import re

##Конвертация строк из множества в список списков.
##Полученный список должен состоять из списков, содержащих номер хромосомы без приставки chr (тип данных - строка) и координаты (число).
def set_to_list(anyset):
        anylist = []
        for line in anyset:
                row = re.split(r'\t', line)
                if re.match('chr', row[0]) != None:
                        chrom = re.split('chr', row[0])[1]
                else:
                        chrom = row[0]
                start = int(row[1])
                end = int(row[2])
                anylist.append([chrom, start, end])
        return anylist

##Прочтение любого трека (как из набора BEDов, так и "одиночного"), и его оптимизация для производимых далее пересечений.
def preparation_of_tables(anyfile_path):
        openfile = open(anyfile_path)
        anylist = list(openfile)
        openfile.close()

        #Поиск хэдера таблицы. Если он есть, то сохраняется как отдельный объект, и добавляется лишь к конечной таблице.
        if anylist[0].find('#') != -1 or anylist[0].find('track name=') != -1:
                sourceheader = anylist[0]
                table_start = 1
        else:
                sourceheader = 'empty'
                table_start = 0

        #Очистка отделённой от хэдера таблицы от повторяющихся и пустых строк.
        anyset = set(anylist[table_start:])
        anyset.discard('\n')

        ##Превращение множества координат в список.
        intlist = set_to_list(anyset)

        #Сортировка таблицы для возможности применения алгоритма пересечения.
        intlist.sort()
        return sourceheader, intlist

##"Ядро" алгоритма пересечения.
def intersection_core(firstlist, firstlistlen, secondlist, secondlistlen):

        ##Условно 1й список VS условно 2й список.
        ##Далее для удобства будем называть их просто "1й список" и "2й список".
        ##Условно, т.к., на самом деле, при одном запуске функции reduce_list программа проходит по одному списку, при следующем - по другому.
        ##Они чередуются. Неважно, какой из списков в реальности окажется первым.
        def reduce_list(anylist1, anyrownumber1, anylist2, anyrownumber2, tset):
                switching_flag = True
                intersection = None
                while switching_flag:
                        for row1 in anylist1[anyrownumber1:]:
                                chrom1 = row1[0]
                                start1 = row1[1]
                                end1 = row1[2]

                                success = 0
                                anylist2_current_len = len(anylist2[anyrownumber2:])
                                for row2 in anylist2[anyrownumber2:]:
                                        chrom2 = row2[0]
                                        start2 = row2[1]
                                        end2 = row2[2]

                                        #chr1 больше (правее) chr2.
                                        #Это аналогично случаю, когда без успешных пересечений интервал 1го списка оказывается правее (см. ниже).
                                        #Переключаемся на 2ой список интервалов без сдвига указателя 1го списка.
                                        if chrom1 > chrom2:
                                                switching_flag = False
                                                break
                                        
                                        #После одного или нескольких успешных пересечений интервал из 2го списка оказался правее.
                                        #Или по ходу успешной серии пересечений chr2 мог оказаться правее chr1.
                                        #Сдвигаем указатель на следующий интервал 1го списка.
                                        #Указатель по 2му списку не трогаем.
                                        #Переключаемся на 2ой список интервалов.
                                        if (end1 < start2 and success > 0) or (chrom1 < chrom2 and success > 0):
                                                anyrownumber1 += 1
                                                switching_flag = False
                                                break
                                                
                                        #Если ещё не пересеклось, проверяем, не левее ли интервал 1го списка интервала 2го списка.
                                        #Если левее, то, с учётом необходимости дальнейшего переключения на 2й список, сдвигаем указатель на следующий интервал 1го списка.
                                        if end1 < start2 or chrom1 < chrom2:
                                                anyrownumber1 += 1
                                                break

                                        #Пытаемся пересечь:
                                        if start1 <= start2 <= end1 and start1 <= end2 <= end1:
                                                intersection = [chrom1, str(start2), str(end2)]
                                                success = success + 1
                                        elif start1 <= start2 <= end1 and end1 <= end2:
                                                intersection = [chrom1, str(start2), str(end1)]
                                                success = success + 1
                                        elif start2 <= start1 and start1 <= end2 <= end1:
                                                intersection = [chrom1, str(start1), str(end2)]
                                                success = success + 1
                                        elif start2 <= start1 and end1 <= end2:
                                                intersection = [chrom1, str(start1), str(end1)]
                                                success += 1

                                        #Если на этом этапе не пересеклось, то, значит, интервал из 1го списка находится правее.
                                        #Такое может произойти только без пересечений ранее.
                                        #Переключаемся на 2ой список интервалов без сдвига указателя 1го списка.
                                        else:
                                                switching_flag = False
                                                break
                                                
                                        #Раз дошли до этого блока, то, значит, было успешное пересечение.
                                        #Чтобы результаты унифицировать с результатами пересечения программой BedTools, удаляем полученные нулевые интервалы.
                                        #Добавляем интервал в конечное множество.
                                        if int(intersection[1]) != int(intersection[2]):
                                                tset.add('\t'.join(intersection))
                                        
                                        #Если успешное пересечение было с последним интервалом второго списка, то нужно "вручную" переключиться на второй список.
                                        #Сдвигаем указатель на следующий интервал 1го списка.
                                        if success == anylist2_current_len:
                                                anyrownumber1 += 1
                                                switching_flag = False
                                                break

                                #Выход из цикла работы с 1ым списком для последующего переключения на 2й.
                                if switching_flag == False:
                                        break
                                
                        #Переключение на 2й список или на блок выхода из "ядра":
                        return anyrownumber1, anyrownumber2
        
        tset = set()
        rownumber1 = 0
        rownumber2 = 0
        while True:

                ##Проход по одному списку.
                rownumber1, rownumber2 = reduce_list(firstlist, rownumber1, secondlist, rownumber2, tset)

                ##Проход по другому списку.
                rownumber2, rownumber1 = reduce_list(secondlist, rownumber2, firstlist, rownumber1, tset)

                #Один из списков полностью истощился.
                #Осуществляем выход из "ядра" прораммы пересечения.
                #На выходе - отсортированный список из списков координат или пустой список.
                #Конечный список сортируется так, чтобы после 19 не шло 2 и т.д..
                #При сортировке учитываются X и Y-хромосомы, митохондриальная ДНК,
                #а также хромосомы с неудобоваримыми обозначения типа chr6_GL000250v2_alt или chr22_KI270928v1_alt
                if rownumber1 == firstlistlen or rownumber2 == secondlistlen:
                        tlist = sorted(set_to_list(tset))
                        targetlist = []
                        tlist_numbers = []
                        tlist_letters = []
                        for row in tlist:
                                if re.search(r'\d+', row[0][0]) != None:
                                        tlist_numbers.append(row)
                                elif re.search(r'[XYMU]', row[0][0]) != None:
                                        tlist_letters.append(row)
                        tlist_numbers.sort(key = lambda currentrow: [int(re.search(r'\d+', currentrow[0]).group()), re.split(r'\d+', currentrow[0])[1], currentrow[1], currentrow[2]])
                        for row in tlist_numbers:
                                targetlist.append(row)
                        for row in tlist_letters:
                                targetlist.append(row)
                        return targetlist

##Прочтение "одиночной" таблицы и её оптимизация для производимых затем пересечений.
utable_sorted = preparation_of_tables(ucsc_path)[1]

#Для увеличения производительности считаем длину большого трека только 1 раз и, разумеется, вне "ядра".
utable_sorted_len = len(utable_sorted)

#Представление названий исходных файлов в виде списка и перебор элементов этого списка.
sourcefiles1 = os.listdir(sourcedir1)
for sourcefile1 in sourcefiles1:
        print('Пересекаются файлы ' + sourcefile1 + ' и ' + os.path.basename(ucsc_path))
        
        ##Прочтение BED-таблиц и их оптимизация для дальнейших пересечений.
        sf1_path = os.path.join(sourcedir1, sourcefile1)
        sf1_header, sourcetable1_sorted = preparation_of_tables(sf1_path)

        #Длина текущего BED-трека.
        sourcetable1_sorted_len = len(sourcetable1_sorted)

        ##Выполнение пересечений.
        targetlist = intersection_core(utable_sorted, utable_sorted_len, sourcetable1_sorted, sourcetable1_sorted_len)

        #Если конечный список пересечений - пустой, то не создаём конечный файл, а начинаем пересекать "одиночный" трек со следующим BEDом.
        if len(targetlist) == 0:
                continue

        #Прописываем результаты в конечный файл.
        targetfile = '[' + sourcefile1.split('.')[0] + '_I_' + os.path.basename(ucsc_path.split('.')[0]) + ']' + '.txt'
        if '#' in sf1_header:
                targetheader = '#' + '[' + sf1_header.split('\n')[0].split('#')[1] + '_I_' + os.path.basename(ucsc_path.split('.')[0]) + ']'
        elif 'track name=' in sf1_header:
                targetheader = '#' + '[' + sf1_header.split('\n')[0].split('"')[1] + '_I_' + os.path.basename(ucsc_path.split('.')[0]) + ']'
        elif sf1_header == 'empty':
                targetheader = '#' + '[' + sourcefile1 + '_I_' + os.path.basename(ucsc_path.split('.')[0]) + ']'
        with open(os.path.join(targetdir, targetfile), 'w') as t:
                t.write(targetheader + '\n')
                for line in targetlist:
                        t.write(line[0] + '\t' + str(line[1]) + '\t' + str(line[2]) + '\n')

#----------#
#Чтобы правильно сравнивать номера хромосом вида chr6_GL000250v2_alt,
#нужно условно раздробить их на, собственно, номер хромосомы (число) и хвост (строка), идущий после этого номера:
#chromhandler = lambda chrom: [int(re.search(r'\d+', chrom).group()), re.split(r'\d+', chrom)[1]]
