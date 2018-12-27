print('''
Python3-скрипт переименования папок и файлов,
а также поиска и замены подстрок в текстах.
Автор: Платон Быкадоров (platon.work@gmail.com), 2018.
Версия: V1.0.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Простое руководство по установке среды разработки и запуску скриптов:
github.com/PlatonB/bioinformatic-python-scripts#Установка-среды-разработки

Если нужно ввести пробел или табуляцию в качестве
элемента заменяемой подстроки, то не обязательно использовать
управляющий символ: достаточно нажать соответствующую клавишу.
''')

def check_input(var):
        '''
        Проверка правильности ввода пользователем опций.
        В случае ошибки работа программы завершится.
        '''
        if var != 'in_current_folder' and var != 'deep' and var != 'no' and var != 'n':
                print(f'{var} - недопустимая опция')
                sys.exit()
                
def rename(rename_fs_objs_pattern, rename_fs_objs_repl, src_fs_obj_name, src_higher_dir_path, src_fs_obj_path):
        '''
        Для переименования файлов и папок производится
        идентичная последовательность действий: и для
        одних, и для других формируется новое название,
        потом абсолютный путь с этим новым названием, а
        затем изменение применяется уже на уровне ФС ОС.
        '''
        trg_fs_obj_name = re.sub(rename_fs_objs_pattern, rename_fs_objs_repl, src_fs_obj_name)
        trg_fs_obj_path = os.path.join(src_higher_dir_path, trg_fs_obj_name)
        os.rename(src_fs_obj_path, trg_fs_obj_path)
        
def text_processing(src_file_path, src_file_name, num_of_headers, trg_dir_path, rename_ctrl_h_pattern, rename_ctrl_h_repl):
        '''
        Создание конечного файла и сохранение
        в него отредактированного текста.
        '''
        with open(src_file_path) as src_file_opened:
                print('Производится поиск и замена в', src_file_name)
                
                #Формирование списка хэдеров.
                #Курсор смещается к началу основной части текста.
                headers = [src_file_opened.readline().split('\n')[0] for header_index in range(num_of_headers)]
                
                #Конструирование имени конечного файла, создание
                #самого файла и прописывание туда хэдеров.
                src_file_base = '.'.join(src_file_name.split('.')[:-1])
                src_file_ext = '.' + src_file_name.split('.')[-1]
                trg_file_name = src_file_base + '_edtd' + src_file_ext
                with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
                        for header in headers:
                                trg_file_opened.write(header + '\n')
                                
                        #Работа с основной частью текста.
                        for line in src_file_opened:

                                #Замена подстроки.
                                edited_line = re.sub(rename_ctrl_h_pattern, rename_ctrl_h_repl, line).split('\n')[0]
                                
                                #Прописывание обработанной строки в конечный файл.
                                trg_file_opened.write(edited_line + '\n')
                                
####################################################################################################

import os, sys, re

src_top_dir_path = input('Путь к исходной верхней папке: ')

rename_dirs = input('''\nПереименовывать папки?
[in_current_folder|deep|no(|n)]: ''')
check_input(rename_dirs)
if rename_dirs == 'in_current_folder' or rename_dirs == 'deep':
        rename_dirs_pattern = input('''\nЗаменяемая часть названий папок
(четырьмя пробелами с каждой стороны
выделен пример регулярного выражения)
[Whole_Blood|2018|    ^    |...]: ''')
        rename_dirs_repl = input('\nНа что заменять?: ')
        
rename_files = input('''\nПереименовывать файлы?
[in_current_folder|deep|no(|n)]: ''')
check_input(rename_files)
if rename_files == 'in_current_folder' or rename_files == 'deep':
        rename_files_pattern = input('''\nЗаменяемая часть названий файлов
(четырьмя пробелами с каждой стороны
выделен пример регулярного выражения)
[chr14|.bed|    (txt)|(od[tsp])    |...]: ''')
        rename_files_repl = input('\nНа что заменять?: ')
                
ctrl_h = input('''\nНайти и заменить подстроку в файлах?
[in_current_folder|deep|no(|n)]: ''')
check_input(ctrl_h)
if ctrl_h == 'in_current_folder' or ctrl_h == 'deep':
        trg_top_dir_path = input('\nПуть к верхней папке для конечных файлов: ')
        if trg_top_dir_path == src_top_dir_path or trg_top_dir_path.startswith(src_top_dir_path + os.sep) == True:
                print('''Конечная папка не должна быть той же, что
и исходная, или находиться внутри исходной''')
                sys.exit()
        num_of_headers = input('''\nКоличество не обрабатываемых строк
в начале каждого исходного текста
(игнорирование ввода ==> хэдеров/шапок в текстах нет)
[0(|<enter>)|1|2|...]: ''')
        if num_of_headers == '':
                num_of_headers = 0
        else:
                num_of_headers = int(num_of_headers)
        rename_ctrl_h_pattern = input('''\nЗаменяемая часть текстов
(четырьмя пробелами с каждой стороны
выделен пример регулярного выражения)
[,|:|    (?<=Type=).+?(?=,)    |...]: ''')
        rename_ctrl_h_repl = input('\nНа что заменять?: ')

if 'rename_dirs_pattern' in locals() or 'rename_files_pattern' in locals():
        are_you_sure = input('''\nЧасть выбранных Вами действий
приведёт к потере оригинальных названий.
Вы уверены, что хотите запустить выполнение?
[yes(|y)|no(|n)]: ''')
        if are_you_sure != 'yes' and are_you_sure != 'y':
                print('Работа программы прервана.')
                sys.exit()
                
##Выбор пользователя - переименовывать объекты файловой системы
##(далее - ФС) только в пределах непосредственно папки верхнего уровня.
if rename_dirs == 'in_current_folder' or rename_files == 'in_current_folder':
        
        #Сохранение в список любых объектов ФС - как
        #папок, так и файлов - находящихся на начальном
        #уровне вложенности верхней исходной папки.
        #Перебор этих объектов и получение
        #абсолютного пути к каждому из них.
        src_fs_obj_names = os.listdir(src_top_dir_path)
        for src_fs_obj_name in src_fs_obj_names:
                src_fs_obj_path = os.path.join(src_top_dir_path, src_fs_obj_name)
                
                #Определение типа объекта ФС - папка это или файл.
                #Выполнение переименования, процесс которого описан
                #в строках документации к соответствующей функции.
                if rename_dirs == 'in_current_folder' and os.path.isdir(src_fs_obj_path) == True:
                        rename(rename_dirs_pattern,
                               rename_dirs_repl,
                               src_fs_obj_name,
                               src_top_dir_path,
                               src_fs_obj_path)
                if rename_files == 'in_current_folder' and os.path.isfile(src_fs_obj_path) == True:
                        rename(rename_files_pattern,
                               rename_files_repl,
                               src_fs_obj_name,
                               src_top_dir_path,
                               src_fs_obj_path)
                        
##Выбор пользователя - переименовывать
##объекты ФС всех уровней вложенности
##относительно верхней исходной папки.
elif rename_dirs == 'deep' or rename_files == 'deep':
        
        #При проходе по объектам ФС всех уровней вложенности функцией
        #os.walk происходит автоматическое определение их типов, а также
        #формирование удобной для скриптовой обработки структуры данных.
        #Каждый элемент этой структуры - путь к одной из папок, список
        #путей к подпапкам этой папки и список файлов данной папки.
        #Чтобы не пилить сук, на котором сидишь, переименовывать следует
        #начинать с самых глубоких папок и заканчивать самыми верхними.
        #В противном случае, будут меняться пути к ещё необработанным
        #более глубоким объектам ФС и теряться возможность обращения
        #к таковым (в os.walk-структуре-то хранятся ещё старые пути!).
        #Чтобы переименовывать в последовательности от глубоких папок к
        #верхним, пути к папкам сортируются по их длине в обратном порядке.
        for src_parent_dir_path, src_dir_names, src_file_names in sorted(os.walk(src_top_dir_path),
                                                                         key=lambda level: len(level[0]),
                                                                         reverse=True):

                #В зависимости от решения пользователя, перебираем в текущей
                #папке либо папки, либо файлы, либо по очереди и то, и то.
                #Переименовываем с помощью подробно описанной выше функции.
                if rename_dirs == 'deep':
                        for src_dir_name in src_dir_names:
                                src_dir_path = os.path.join(src_parent_dir_path, src_dir_name)
                                rename(rename_dirs_pattern,
                                       rename_dirs_repl,
                                       src_dir_name,
                                       src_parent_dir_path,
                                       src_dir_path)
                if rename_files == 'deep':
                        for src_file_name in src_file_names:
                                src_file_path = os.path.join(src_parent_dir_path, src_file_name)
                                rename(rename_files_pattern,
                                       rename_files_repl,
                                       src_file_name,
                                       src_parent_dir_path,
                                       src_file_path)
                                
##Выбор пользователя - производить поиск и замену подстрок
##в файлах, находящихся в папке лишь одного - верхнего уровня.
##В результате работы переименовательной части скрипта,
##файлы могут быть уже с новыми названиями, поэтому
##формируем список содержимого директории заново.
if ctrl_h == 'in_current_folder':
        src_fs_obj_names = os.listdir(src_top_dir_path)
        for src_fs_obj_name in src_fs_obj_names:
                src_fs_obj_path = os.path.join(src_top_dir_path, src_fs_obj_name)
                if os.path.isfile(src_fs_obj_path) == True:
                        text_processing(src_fs_obj_path,
                                        src_fs_obj_name,
                                        num_of_headers,
                                        trg_top_dir_path,
                                        rename_ctrl_h_pattern,
                                        rename_ctrl_h_repl)
                        
##Выбор пользователя - производить поиск и
##замену подстрок в файлах, расположенных
##по всему дереву папок верхней папки.
##Пути к файлам к этому моменту могли быть
##уже изменены, да и сами файлы - переименованы.
##Поэтому папочно-файловый объект нужно создавать заново.
##Также важно отметить, что если файлы были ранее переименованы,
##то новые имена будут как в исходной папке, так и в конечной.
if ctrl_h == 'deep':
        for src_parent_dir_path, src_dir_names, src_file_names in os.walk(src_top_dir_path):
                
                #Для сохранения отредактированных файлов нужно
                #создать в конечной папке верхнего уровня
                #дерево папок, полностью идентичное исходному.
                #Чтобы так сделать, нужно найти часть
                #каждого пути от верхней исходной папки до
                #вложенной исходной папки (относительный путь).
                #Для самой верхней исходной папки
                #такой путь будет равным пустой строке.
                #Создаём конечные папки, расположив их в
                #конечной папке верхнего уровня в соответствии
                #с полученными относительными путями.
                src_parent_dir_rel_path = src_parent_dir_path[len(src_top_dir_path) + 1:]
                trg_dir_path = os.path.join(trg_top_dir_path, src_parent_dir_rel_path)
                if os.path.exists(trg_dir_path) == False:
                        os.mkdir(trg_dir_path)
                        
                #Перебор названий исходных файлов
                #каждого уровня, переименование файлов.
                for src_file_name in src_file_names:
                        src_file_path = os.path.join(src_parent_dir_path, src_file_name)
                        text_processing(src_file_path,
                                        src_file_name,
                                        num_of_headers,
                                        trg_dir_path,
                                        rename_ctrl_h_pattern,
                                        rename_ctrl_h_repl)
