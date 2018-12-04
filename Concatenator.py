print('''
Python3-скрипт, объединяющий тексты в один файл.
Автор: Платон Быкадоров (platon.work@gmail.com), 2018.
Версия: V2.0.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Простое руководство по установке среды разработки и запуску скриптов:
github.com/PlatonB/bioinformatic-python-scripts#Установка-среды-разработки

Если хэдер(-ы) одинаков(-ы) во всех исходных текстах,
то он(-и) станет(-ут) хэдером(-ами) объединённого текста.
''')

'''
Считывание определённого пользователем
количества строк в начале текста.
Их очистка от переносов и сохранение в список.
'''
retrieve_headers = lambda file_opened, num_of_headers: \
                   [file_opened.readline().split('\n')[0] for header_index in range(num_of_headers)]

def write_into_file(file_or_dataset, trg_file_opened):
        '''
        Прописывание результатов в конечный файл.
        '''
        for line in file_or_dataset:
                if line.find('\n') == -1:
                        line += '\n'
                trg_file_opened.write(line)

import sys, os

src_dir_path = input('Путь к папке с исходными файлами: ')
trg_dir_path = input('\nПуть к папке для конкатенированного файла: ')
num_of_headers = input('''\nКоличество хэдеров/шапок в начале каждого текста
(игнорирование ввода ==> все строки без
исключения пойдут в конкатенированный текст)
[0(|<enter>)|1|2|...]: ''')
if num_of_headers == '':
        num_of_headers = 0
else:
        num_of_headers = int(num_of_headers)
kill_repeats = input('''\nУдалять копии строк?
(игнорирование ввода ==> не удалять)
[yes(|y)|no(|n|<enter>)]: ''')
if kill_repeats != 'yes' and kill_repeats != 'y' and kill_repeats != 'no' \
   and kill_repeats != 'n' and kill_repeats != '':
        print(f'{kill_repeats} - недопустимая опция')
        sys.exit()
        
#Создание списка имён объединяемых файлов.
src_file_names = os.listdir(src_dir_path)

#Проверка, имеется ли в папке хотя бы минимально
#необходимое для конкатенации количество файлов.
if len(src_file_names) < 2:
        print(f'''В исходной папке {src_dir_path} менее
двух файлов. Конкатенация невозможна.''')
        sys.exit()

#В значительной части скриптов репозитория
#результаты работы размещаются в файлы,
#соответствующие каждому исходному файлу.
#В виду специфики программы-конкатенатора, все
#результаты пропишутся в один конечный файл.
#Создаём его уже после построения списка
#имён исходных файлов, иначе конечный
#файл считается вместе с исходными.
trg_file_name = os.path.basename(src_dir_path) + '_conc' + '.txt'
with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
        
        ##Если, согдасно пользовательскому вводу, в каждом исходном тексте
        ##есть, как минимум, один хэдер, то скрипт проверит, одинаковы
        ##ли хэдеры (или наборы хэдеров) среди всех исходными файлов.
        ##Если да, то, очевидно, тексты гомологичны, поэтому при объединении
        ##имеет смысл этот константный хэдер сделать общим хэдером.
        if num_of_headers > 0:
                with open(os.path.join(src_dir_path, src_file_names[0])) as fir_file_opened:
                        
                        #Формирование списка хэдеров первого текста.
                        prev_headers = retrieve_headers(fir_file_opened, num_of_headers)
                        
                for src_file_name in src_file_names[1:]:
                        with open(os.path.join(src_dir_path, src_file_name)) as src_file_opened:
                                
                                #Формирование списка хэдеров текущего текста.
                                cur_headers = retrieve_headers(src_file_opened, num_of_headers)
                                
                                #Раз хоть в одном тексте попались другие хэдеры, то
                                #попытки создания единого хэдера сворачиваются.
                                if cur_headers != prev_headers:
                                        break

                                #Если очередные хэдеры не отличаются от
                                #найденных ранее, то определение возможности
                                #размещения общего хэдера может быть продолжено.
                                else:
                                        prev_headers = cur_headers

                #Хэдеры (или наборы хэдеров) от
                #текста к тексту не меняются.
                #Значит, начинаем с них конечный файл.
                else:
                        for header in cur_headers:
                                trg_file_opened.write(header + '\n')
                                
        ##Если пользователь предпочёл уничтожать копии уже встретившихся
        ##строк, то результаты конкатенации будут накапливаться во множество.
        ##Если нет - это множество останется пустым.
        data_wo_repeats = set()
        
        ##Работа с исходными файлами.
        for src_file_name in src_file_names:
                with open(os.path.join(src_dir_path, src_file_name)) as src_file_opened:
                        
                        #Считывание вхолостую хэдеров, количество
                        #которых было определено пользователем, чтобы
                        #сместить курсор к началу основной части текста.
                        for header_index in range(num_of_headers):
                                src_file_opened.readline()
                                
                        #Если пользователь выбрал не уничтожать повторы, то
                        #строки сразу пропишутся в файл, без накопления в массиве.
                        if kill_repeats == 'no' or kill_repeats == 'n' or kill_repeats == '':
                                write_into_file(src_file_opened, trg_file_opened)
                                
                        #Если же пользователь предпочёл повторы убрать,
                        #то придётся задействовать оперативную память,
                        #сохранив строки всех текстов во множество.
                        elif kill_repeats == 'yes' or kill_repeats == 'y':
                                data_wo_repeats |= set(line for line in src_file_opened)
                                
        #Прописывание строк конкатенированного текста,
        #избавленного от повторов, в конечный файл.
        if data_wo_repeats != set():
                write_into_file(data_wo_repeats, trg_file_opened)
