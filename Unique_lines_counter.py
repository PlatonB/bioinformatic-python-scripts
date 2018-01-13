print('''
Python3-скрипт, считающий общее количество уникальных строк всех файлов дерева папок.
Автор: Платон Быкадоров, 2017.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Скрипт ищет в определённой папке и её подпапках файлы с простым текстом (txt, bed и т.д.).
Выводит количество уникальных строк всех найденных текстов, вместе взятых.
Оказавшиеся в дереве папок посторонние файлы вроде xlsx-таблиц, jpg-картинок и т.д. игнорируются
(хотя, конечно, лучше их наличие не допускать).

Первыми строками ваших текстов могут быть описания, т.е., к примеру, шапки таблиц или закомментированные хэдеры.
Описывающие строки, очевидно, будут вам искажать результат, поэтому программа,
чтобы эти строки не учитывать, запросит у вас их количество.
Внимание! Если описания есть, то они должны занимать строго одинаковое количество строк во всех текстах!
''')

import os
source_dir = input('Путь к исходной верхней папке: ')
number_of_headers = int(input('Количество не подсчитываемых строк в начале каждого файла (хэдер, шапка таблицы и т.д.) [0|1|2|(...)]: '))

#Создание списка абсолютных путей к файлам исходной папки и её подпапок.
source_paths_and_files = []
for path, dirs, files in list(os.walk(source_dir)):
        if files != []:
                for file in files:
                        source_paths_and_files.append(os.path.join(path, file))

#Проверка всех исходных файлов всех подпапок, представляют ли они собой plain text.
#Накопление строк из валидных исходных файлов во множество с целью убрать повторы.
#Вывод результата.
target_set = set()
for source_file in source_paths_and_files:
        with open(os.path.join(source_dir, source_file)) as source_file_opened:
                try:
                        target_list = list(source_file_opened)[number_of_headers:]
                except UnicodeDecodeError:
                        continue
                target_set |= set(target_list)
target_set.discard('\n')
lines_quantity = len(target_set)
print('Количество строк во всех файлах папки ' + source_dir + ' и её подпапок = ' + str(lines_quantity))
