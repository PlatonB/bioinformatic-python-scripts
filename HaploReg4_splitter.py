print('''
Скрипт, разделяющий таблицу из Haploreg 4.x на подтаблицы и размещающий подтаблицы в отдельные файлы (1 подтаблица - в 1 файл).
Начало каждой подтаблицы - Query SNP <...>.
Автор: Платон Быкадоров, 2017.
Лицензия: GNU General Public License version 3.
Получение читаемой скриптом исходной таблицы в HaploReg 4.x (http://archive.broadinstitute.org/mammals/haploreg/haploreg.php):

1. Build Query --> Обзор... --> загружаете список идентификаторов вида rs1234567890, каждый на отдельной строке.
2. Set Options --> выбираем любые опции; Output mode - HTML.
3. Копируем HTML-вывод без раздела "Query SNP enhancer summary" в Microsoft Word, а оттуда сохраняем как txt.

Внимание!
Каждый текстовый редактор сохраняет гаплореговские HTML-таблицы в plain text, переформатируя их по-своему.
Этот скрипт способен обрабатывать только таблицы, сохранённые в txt с помощью Word.
Если требуется обработать подготовленные другим путём HaploReg-таблицы, пишите в Issues.
''')

sourcefile_path = input('Путь к исходному файлу (не забывать экранировать): ')
skip_querysnp = input('Чтобы не записывать в конечные файлы запрашиваемые SNP, введите skip: ')
targetdir_path = input('Путь к папке с конечными chr-подпапками (не забывать экранировать): ')

import os
import re

with open(sourcefile_path) as sourcefile_open:
        sourcelist = list(sourcefile_open)
        querysnp_quantity = len(re.findall('Query SNP', ''.join(sourcelist)))
        iteration_number = 0
        line_number = 0
        targetsubdir_path = None
        
        #Цикл будет выполняться до тех пор, пока количество итераций не станет равно количеству строк, содержащих словосочетание 'Query SNP'.
        while iteration_number < querysnp_quantity:
                targetlist = []

                #Поиск запрашиваемого в HaploReg снипа и заданного в настройках HaploReg значения LD threshold (r²).
                #Добавление в конечный список строки с 'QuerySNP'.
                #Увеличение счётчика количества всех строк.
                #Увеличение счётчика количества строк, содержащих 'QuerySNP'.
                querysnp = re.search(r'rs\d+', sourcelist[line_number]).group()
                r2 = re.search(r'\d\.\d', sourcelist[line_number]).group()
                targetlist.append(sourcelist[line_number])
                line_number += 1
                iteration_number += 1

                #3-я строка подтаблицы содержит номер хромосомы, актуальный для всей подтаблицы.
                #Используем номер хромосомы для построения названия создаваемой подпапки.
                #Создаём новую "хромосомную" подпапку, если она ещё не существует.
                current_chrnumber = re.match(r'\d+', sourcelist[line_number + 3]).group()
                targetsubdir_path = targetdir_path + os.sep + 'chr' + current_chrnumber
                if not os.path.exists(targetsubdir_path):
                        os.mkdir(targetsubdir_path)

                #Цикл, в котором наполняется конечный список.
                #Строка с 'Query SNP' текущей подтаблицы в этом цикле участвовать не будет,
                #т.к. при произведённой ранее работе с этой строкой уже увеличился счётчик количества всех строк.
                for line in sourcelist[line_number:]:

                        #Если пользователю не нужны в конечной таблице запращиваемые SNP и их характеристики, то переходим к следующей строке.
                        #Увеличиваем счётчик количества всех строк.
                        if skip_querysnp == 'skip':
                                if line.find(querysnp) != -1 and line.find('Query SNP') == -1:
                                        line_number += 1
                                        continue
                                
                        #Добавление строк, содержащих координаты и характеристики SNP, а также двухстрочной шапки подтаблицы, в конечный список.
                        #Увеличение счётчика количества всех строк.
                        if re.match(r'\d+', line) != None or line.find('chr\tpos') != -1 or line.find('freq\tfreq') != -1:
                                targetlist.append(line)
                                line_number += 1

                        #Если строка заполнена одними табуляциями, то не добавляем её.
                        #Только увеличиваем счётчик количества всех строк.
                        elif re.match(r'\t\t\t\t\t', line) != None:
                                line_number += 1

                        #Встретилась строка с 'QuerySNP' следующей подтаблицы.
                        #Счётчик количества всех строк увеличивать не нужно,
                        #т.к. следующая итерация начнётся с обработки как раз этой строки.
                        else:
                                break
                        
                #Запись конечного списка в файл.
                targetfile = '(' + querysnp + '_' + current_chrnumber + ')' + '.txt'
                targetheader = '#' + '(' + querysnp + '_' + 'r2' + '>=' + r2 + '_' + 'chr' + current_chrnumber + ')'
                targetfile_open = open(os.path.join(targetdir_path, targetsubdir_path, targetfile), 'w')
                targetfile_open.write(targetheader + '\n')
                for line in targetlist:
                        targetfile_open.write(line)
                targetfile_open.close()
