print('''
Этот Python3-скрипт преобразовывает подстроки chr№:pos или chr№:pos1-pos2
в интервальную (BED-подобную) запись (...    chr№    pos1    pos2    ...).
Автор: Платон Быкадоров (platon.work@gmail.com), 2018.
Версия: V3.0.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

ВАЖНО!
Часто в базах данных локализация SNP обозначается номером хромосомы
и лишь одной координатой, разделёнными двоеточием, например, chr14:105706543.
Многие программы, в том числе BedTools, не работают с таким форматом.
Но для решения проблемы не достаточно убрать двоеточие и удвоить координату.
Получаются нулевые координатные интервалы, не принимаемые рядом программ.
Согласно полученному в ответ на мой запрос комментарию специалиста команды Galaxy
(https://biostar.usegalaxy.org/p/13027/#13166), если координата дана только одна, то
для получения двух координат с ненулевой дельтой следует вычесть 1 из первой координаты.
Компонент скрипта, решающий проблему дельты, базируется исключительно на информации из этой дискуссии.
Если вы считаете такой подход неверным, выскажите, пожалуйста, своё мнение в Issues.

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

import os, re, sys

src_dir_path = input('Путь к папке с исходными tab-файлами: ')
trg_dir_path = input('\nПуть к папке для конечных файлов: ')
num_of_headers = input('''\nКоличество не обрабатываемых строк в начале каждой таблицы
(игнорирование ввода ==> хэдеров/шапок в таблицах нет)
[0(|<enter>)|1|2|...]: ''')
if num_of_headers == '':
        num_of_headers = 0
else:
        num_of_headers = int(num_of_headers)
        
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
                                
                                #Ни разу не видел chr:pos(-pos)-содержащие таблицы,
                                #в которых chr:pos(-pos)-столбец идёт после столбца
                                #с аналогичной r'\b\w+:\d+(?:-\d+)?\b'-конструкцией.
                                #Поэтому искомой подстрокой будет считаться
                                #первое вхождение упомянутого паттерна.
                                chr_col_pos_obj = re.search(r'\b\w+:\d+(?:-\d+)?\b', line)
                                
                                #Получение искомой подстроки и её
                                #индексов начала-конца в текущей строке.
                                #Если в подстроке лишь одна координата, то
                                #chr:pos будет преобразован в chr\tpos-1\tpos.
                                #А если в ней уже есть обе координаты, то они, оставшись
                                #сами по себе неизменными, будут разделены табуляциями.
                                #Но если в случае наличия двух координат первая координата
                                #окажется равной второй, будет возбуждена ошибка.
                                chr_col_pos_start = chr_col_pos_obj.span()[0]
                                chr_col_pos_end = chr_col_pos_obj.span()[1]
                                chr_pos_sep = re.split(r'[:-]', chr_col_pos_obj.group())
                                if len(chr_pos_sep) == 2:
                                        chrom, pos_1, pos_2 = chr_pos_sep[0], str(int(chr_pos_sep[1]) - 1), chr_pos_sep[1]
                                elif len(chr_pos_sep) == 3:
                                        chrom, pos_1, pos_2 = chr_pos_sep
                                        if pos_1 == pos_2:
                                                print('''
{} = {}
Ошибка. Геномные координаты не должны быть равны друг другу.
Частичные результаты обработки таблицы {} не будут сохранены.
Для уточнения координат свяжитесь, пожалуйста, с создателями этой таблицы.
'''.format(pos_1, pos_2, src_file_name))
                                                os.remove(os.path.join(trg_dir_path, trg_file_name))
                                                break
                                chr_pos_pos = chrom + '\t' + pos_1 + '\t' + pos_2
                                
                                #Интеграция изменённой подстроки в текущую строку.
                                #Прописывание обновлённой текущей строки в конечный файл.
                                line = line[:chr_col_pos_start] + chr_pos_pos + line[chr_col_pos_end:]
                                if line.find('\n') == -1:
                                        line += '\n'
                                trg_file_opened.write(line)
