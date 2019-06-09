print('''
Python3-скрипт, выводящий первые n строк большого текстового файла.
Автор: Платон Быкадоров (platon.work@gmail.com), 2018-2019.
Версия: V3.0.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Простое руководство по установке среды разработки и запуску скриптов:
github.com/PlatonB/bioinformatic-python-scripts#Установка-среды-разработки

Файлы, размеры которых исчисляются гигабайтами, практически
невозможно предпросмотреть на обычном десктопе.
Этот скрипт позволяет определить по первым строкам,
из каких столбцов состоит огромная таблица.
Ознакомление с общим видом таблицы сделает возможным
создавать специализированные программы для её обработки.

Поддерживаются текстовые файлы в обычном и сжатом ((b)gzip) виде.

Не выводите не экран слишком много строк (тысячи), т.к.
консоль, в которой вы запускаете скрипт, может зависнуть.
''')

import sys, re, gzip, os

src_file_path = input('Путь к исходному файлу (текст или gz/bgz-архив): ')

str_quan = int(input('\nКоличество выводимых или перенаправляемых строк: '))

redirection = input('''\nПеренаправить результат в отдельный файл?
(игнорирование ввода ==> вывести результат на экран)
[redirect(|r)|<enter>]: ''')
if redirection not in ['redirect', 'r', '']:
        print(f'{redirection} - недопустимая опция')
        sys.exit()

#Открытие на чтение (b)gzip-архива.
if re.search(r'\.b?gz$', src_file_path) != None:
        src_file_opened = gzip.open(src_file_path, mode='rt')
        
#Открытие на чтение текстового файла.
else:
        src_file_opened = open(src_file_path)
        
#Выбрано перенаправление в файл.
if redirection in ['redirect', 'r']:
        trg_dir_path = input('\nПуть к папке для конечного файла: ')
        trg_file_name = '.'.join(os.path.basename(src_file_path).split('.')[:-1]) + '_fir_' + str(str_quan) + '.txt'
        with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
                for num in range(str_quan):
                        line = src_file_opened.readline()
                        if line.find('\n') == -1:
                                line += '\n'
                        trg_file_opened.write(line)
                        
#Выбран вывод на экран.
else:
        print('')
        for num in range(str_quan):
                line = src_file_opened.readline().split('\n')[0]
                print(line)
                
src_file_opened.close()
