print('''
Python3-скрипт пересечения набора BED-треков (списков координатных интервалов) с одним BED-треком.
Формат BED:

#Заголовок со знаком решётки в начале, либо вот такой:
track name="Заголовок" description="Заголовок по стандатрам UCSC Table Browser. Любые заголовки BED-таблиц для этого скрипта необязательны" visibility=3 url=
chr6 (или 6)	32665241	32665242	(опционально) дополнительные поля, разделённые табуляциями
chr6 (или 6)	32665244	32665245	(опционально) дополнительные поля, разделённые табуляциями
...

В исходной папке не должно быть ничего, кроме пересекаемых таблиц.
Папку для результатов перед выполнением работы желательно оставлять пустой.
Если нужно, могу переслать или выложить вариант этого скрипта, обрабатывающий исходные файлы, размещённые по папкам и/или подпапкам.
''')

sourcedir1 = input('Путь к исходной папке (не забывать экранировать): ')
ucsc_path = input('Путь к BED-треку (не забывать экранировать): ')
targetdir = input('Путь к конечной папке (не забывать экранировать): ')

import os
import re

##Прочтение UCSC-таблицы и её оптимизация для производимых далее пересечений.
def preparation_of_tables(anyfile_path):
        openfile = open(anyfile_path)
        anylist = list(openfile)
        openfile.close()

        #Поиск хэдера таблицы. Если он есть, то сохраняется как отдельный объект, и добавляется лишь к конечной таблице.
        if anylist[0].find('#') != -1 or anylist[0].find('track name=') != -1:
                sourceheader = anylist[0]
                table_start = 1
        else:
                sourceheader = 'emptyheader'
                table_start = 0

        #Очистка отделённой от хэдера таблицы от повторяющихся и пустых строк.
        anyset = set(anylist[table_start:])
        anyset.discard('\n')

        #Представление всех элементов таблицы в качестве чисел для дальнейшей правильной сортировки.
        intlist = []
        for line in anyset:
                row = re.split(r'\t', line)
                if re.search('X', row[0]) != None:
                        chrom = 23
                elif re.search('Y', row[0]) != None:
                        chrom = 24
                else:
                        chrom = int(re.search(r'\d+', row[0]).group())
                start = int(row[1])
                end = int(row[2])
                intlist.append([chrom, start, end])

        #Сортировка таблицы для возможности применения алгоритма пересечения.
        intlist.sort()
        return sourceheader, intlist

##"Ядро" алгоритма пересечения.
def intersection_core(firstlist, firstlistlen, secondlist, secondlistlen):

        ##Условно 1й список VS условно 2й список.
        ##Далее для удобства будем называть их просто "1й список" и "2й список".
        ##Условно, потому что, на самом деле, при каждом запуске функции reduce_list программа проходит то по одному, то по другому списку.
        def reduce_list(anylist1, anyrownumber1, anylist2, anyrownumber2, targetset):
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
                                        if chrom2 < chrom1:
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
                                                intersection = [str(start2), str(end2)]
                                                success = success + 1
                                        elif start1 <= start2 <= end1 and end1 <= end2:
                                                intersection = [str(start2), str(end1)]
                                                success = success + 1
                                        elif start2 <= start1 and start1 <= end2 <= end1:
                                                intersection = [str(start1), str(end2)]
                                                success = success + 1
                                        elif start2 <= start1 and end1 <= end2:
                                                intersection = [str(start1), str(end1)]
                                                success += 1

                                        #Если на этом этапе не пересеклось, то, значит, интервал из 1го списка находится правее.
                                        #Такое может произойти только без пересечений ранее.
                                        #Переключаемся на 2ой список интервалов без сдвига указателя 1го списка.
                                        else:
                                                switching_flag = False
                                                break
                                                
                                        #Раз дошли до этого блока, то, значит, было успешное пересечение.
                                        #Заменяем условные названия хромосом (23 и 24) на первоначальные X и Y.
                                        #Если на выходе получается нулевой интервал, вычитаем из 1ой координаты единицу.
                                        #Прописываем полученный интервал в конечное множество.
                                        if chrom2 == 23:
                                                chrom2 = 'X'
                                        elif chrom2 == 24:
                                                chrom2 = 'Y'
                                        if start1 == end2 or start2 == end1:
                                                intersection = [str(int(intersection[0]) - 1), intersection[1]]
                                        line = str(chrom2) + '\t' + '\t'.join(intersection) #+ '\t' + row2[3] + '\t' + row1[3]
                                        targetset.add(line)
                                        
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
        
        targetset = set()
        rownumber1 = 0
        rownumber2 = 0
        while True:

                ##Проход по одному списку.
                rownumber1, rownumber2 = reduce_list(firstlist, rownumber1, secondlist, rownumber2, targetset)

                ##Проход по другому списку.
                rownumber2, rownumber1 = reduce_list(secondlist, rownumber2, firstlist, rownumber1, targetset)

                #Один из списков полностью истощился.
                #Выход из "ядра" прораммы пересечения.
                if rownumber1 == firstlistlen or rownumber2 == secondlistlen:
                        return targetset

##Прочтение UCSC-таблицы и её оптимизация для производимых далее пересечений.
utable_sorted = preparation_of_tables(ucsc_path)[1]

#Для увеличения производительности считаем длину большого трека только 1 раз и, разумеется, вне "ядра".
utable_sorted_len = len(utable_sorted)

#Представление названий исходных файлов в виде списка и перебор элементов этого списка.
sourcefiles1 = os.listdir(sourcedir1)
for sourcefile1 in sourcefiles1:
        
        ##Прочтение BED-таблиц и их оптимизация для дальнейших пересечений.
        sf1_path = os.path.join(sourcedir1, sourcefile1)
        sf1_header, sourcetable1_sorted = preparation_of_tables(sf1_path)

        #Длина текущего BED-трека.
        sourcetable1_sorted_len = len(sourcetable1_sorted)

        ##Выполнение пересечений.
        targetset = intersection_core(utable_sorted, utable_sorted_len, sourcetable1_sorted, sourcetable1_sorted_len)

        #Если конечное множество пересечений - пустое, то не создаём конечный файл, а начинаем пересекать UCSC-трек со следующим BEDом.
        if len(targetset) == 0:
                continue

        #Полученное множество пересечений преобразуем в список и сортируем.
        targetlist = sorted(list(targetset))

        #Прописываем результаты в конечный файл.
        targetfile = '[' + sourcefile1.split('.')[0] + '_I_' + os.path.basename(ucsc_path.split('.')[0]) + ']' + '.txt'
        targetheader = '#' + '[' + sf1_header.split('\n')[0].split('#')[1] + '_I_' + os.path.basename(ucsc_path.split('.')[0]) + ']'
        with open(os.path.join(targetdir, targetfile), 'w') as t:
                t.write(targetheader + '\n')
                for line in targetlist:
                        t.write(line + '\n')
