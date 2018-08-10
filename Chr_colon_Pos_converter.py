print('''
Этот Python3-скрипт преобразовывает таблицы chr:pos в
BED-подобную структуру (...    chr№    pos - 1    pos    ...).
Автор: Платон Быкадоров (platon.work@gmail.com), 2018.
Версия: V2.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Часто в базах данных локализация SNP обозначается номером хромосомы
и лишь одной координатой, разделёнными двоеточием, например, chr14:105706543.
Многие программы, в том числе BedTools, не работают с таким форматом.
Но для решения проблемы не достаточно убрать двоеточие и удвоить координату.
Получаются нулевые координатные интервалы, не принимаемые рядом программ.
Согласно полученному в ответ на мой запрос комментарию специалиста команды Galaxy
(https://biostar.usegalaxy.org/p/13027/#13166), если стартовая
и конечная координаты геномного интервала равны друг другу, то для
получения ненулевой дельты следует вычесть 1 из первой координаты.
Компонент скрипта, решающий проблему дельты, базируется
исключительно на информации из упомянутого треда.
Если вы считаете этот подход неверным, сообщите, пожалуйста, в Issues.

Пример.
Было:
rs12894947	CHR_HSCHR14_3_CTG1:105801402	G	intergenic_variant
rs11160877	CHR_HSCHR14_3_CTG1:105802388	C	intergenic_variant
rs61994836	CHR_HSCHR14_3_CTG1:105802566	C	intergenic_variant

Стало:
rs12894947	CHR_HSCHR14_3_CTG1	105801401	105801402	G	intergenic_variant
rs11160877	CHR_HSCHR14_3_CTG1	105802387	105802388	C	intergenic_variant
rs61994836	CHR_HSCHR14_3_CTG1	105802565	105802566	C	intergenic_variant
''')

import os
import re

src_dir_path = input('Путь к папке с исходными файлами: ')
num_of_headers = int(input('''Количество не считываемых строк в начале файла
(хэдер, шапка таблицы и т.д.) [0|1|2|(...)]: '''))
trg_dir_path = input('Путь к папке для конечных файлов: ')

src_file_names = os.listdir(src_dir_path)
for src_file_name in src_file_names:
        with open(os.path.join(src_dir_path, src_file_name)) as src_file_opened:
                trg_file_name = src_file_name.split('.')[0] + '_' + 'c_p_p' + '.txt'
                with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
                        
                        #Формирование списка хэдеров и добавление хэдеров в конечный файл.
                        #Курсор смещается к началу основной части таблицы.
                        headers = [src_file_opened.readline() for header_index in range(num_of_headers)]
                        for header in headers:
                                if header.find('\n') == -1:
                                        header += '\n'
                                trg_file_opened.write(header)
                                
                        #Для экономии оперативной памяти строки будут обрабатываться
                        #без предварительного накопления в списке, а после обработки -
                        #прописываться непосредственно в конечный файл.
                        for line in src_file_opened:

                                #Ни разу не видел chr:pos-содержащие таблицы,
                                #в которых chr:pos-столбец идёт после столбца
                                #с аналогичной r'.:\d+'-конструкцией.
                                #Поэтому искомой подстрокой будет считаться
                                #первое вхождение упомянутого паттерна.
                                chr_col_pos_obj = re.search(r'.:\d+', line)

                                #Получение искомой подстроки и её
                                #индексов начала-конца в текущей строке.
                                #Преобразование chr:pos в chr\tpos-1\tpos.
                                #Интеграция изменённой подстроки в текущую строку.
                                #Прописывание текущей строки в конечный файл.
                                chr_col_pos_start = chr_col_pos_obj.span()[0]
                                chr_col_pos_end = chr_col_pos_obj.span()[1]
                                chrom, pos = re.split(r':', chr_col_pos_obj.group())
                                chr_pos_pos = chrom + '\t' + str(int(pos) - 1) + '\t' + pos
                                line = line[:chr_col_pos_start] + chr_pos_pos + line[chr_col_pos_end:]
                                if line.find('\n') == -1:
                                        line += '\n'
                                trg_file_opened.write(line)
