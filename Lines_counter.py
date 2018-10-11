print('''
Python3-скрипт, считающий количество строк файлов, размещённых в дереве папок.
Автор: Платон Быкадоров (platon.work@gmail.com), 2017-2018.
Версия: V2.1.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Скрипт генерирует JSON-файл такой структуры:
{
    "in_all_files": [
        61, #Общефайловое количество всех непустых строк.
        59, #Общефайловое количество непустых строк с вычетом их повторов в пределах каждого текста.
        57  #Общефайловое количество непустых строк с вычетом их повторов.
    ],
    "in_each_file": {
        "/home/platon/_0_Диссертация/Exp/os_walk_test_1": {
            "REF_os_walk_test_stat.txt": [
                27, #Количество всех непустых строк одного текста.
                25  #Количество непустых строк одного текста с вычетом их повторов.
            ],
            ...
        },
        ...
    }
}
''')

import os
import json

src_dir_path = input('Путь к исходной верхней папке: ')
trg_dir_path = input('Путь к папке для конечного JSON-файла: ')
num_of_headers = input('''\nКоличество не учитываемых строк в начале файлов
(игнорирование ввода ==> хэдеров/шапок в файлах нет)
[0(|<enter>)|1|2|...]: ''')
if num_of_headers == '':
        num_of_headers = 0
else:
        num_of_headers = int(num_of_headers)

#Словарь верхнего уровня, в котором размещены такие структуры:
#- список со значаниями суммарного количества строк текстов,
#рассчитываемых без вычета и с вычетом одинаковых элементов;
#- словарь, в котором будут накапливаться пути к родительским папкам,
#имена расположенных в них файлов и длины соответствующих текстов.
statistics = {'in_all_files': [], 'in_each_file': {}}

#Суммарные длины текстов без ликвидации межфайловых повторений
#строк вычисляются без создания отдельного конкатенированного массива.
#Для вычета межфайловых повторений приходится накапливать множество.
#Это может привести к переполнению оперативной памяти.
#Пишите в Issues, если знаете способ решения проблемы.
all_strs_quan, all_files_uniq_strs_quan, all_uniq_strs = 0, 0, set()

#Работа со списком, содержащим кортежи, в каждом из
#которых находится строковый путь к текущей родительской папке,
#список с названиями её подпапок и список с названиями её файлов.
#Список названий папок и/или файлов остаётся пустым, если
#в родительской папке чего-либо из перечисленного нет.
for parent_dir_path, dir_names, file_names in sorted(os.walk(src_dir_path)):

        #Нас интересуют только те кортежи,
        #в которых есть имена файлов.
        if file_names != []:

                #Словарь {имя файла: [количество всех его строк, строк без повторов], ...}.
                files_n_stats = {}

                #Перебор файлов текущей родительской папки.
                for file_name in file_names:
                        with open(os.path.join(parent_dir_path, file_name)) as src_file_opened:
                                
                                #Проверка исходного файла, представляет ли он собой plain text.
                                #Формирование списка из всех строк текста, кроме пустых.
                                try:
                                        one_file_strs = [line.split('\n')[0] for line in src_file_opened if line != '\n'][num_of_headers:]
                                except UnicodeDecodeError:
                                        continue
                                
                                #Количество непустых строк одного текста.
                                one_file_strs_quan = len(one_file_strs)
                                
                                #1) Непустые строки одного текста с удалёнными
                                #повторами и 2) количество этих строк.
                                one_file_uniq_strs = set(one_file_strs)
                                one_file_uniq_strs_quan = len(one_file_uniq_strs)
                                
                                #Метрики текста привязывается к имени соответствующего файла.
                                files_n_stats[file_name] = [one_file_strs_quan, one_file_uniq_strs_quan]
                                
                                #Подсчёт общефайлового количества строк c игнорированием
                                #1) только внутрифайловых повторов, 2) всех повторов.
                                all_files_uniq_strs_quan += one_file_uniq_strs_quan
                                all_strs_quan += one_file_strs_quan
                                
                                #Накопление множества для дальнейшего
                                #рассчёта бесповторного количества всех строк.
                                all_uniq_strs |= one_file_uniq_strs
                                
                #В случае, когда файлы в папке есть, но они все -
                #не plain text, условие if file_names != [] и блок
                #try-except не помогут избежать создания пустого
                #словаря (без пар "имя файла-количество строк").
                #Эта ситуация ниже предусмотрена.
                if files_n_stats != {}:
                        
                        #Привязка словаря пофайловых показателей к родительской папке.
                        statistics['in_each_file'][parent_dir_path] = files_n_stats

#Пополнение словаря суммарных показателей.
statistics['in_all_files'].append(all_strs_quan)
statistics['in_all_files'].append(all_files_uniq_strs_quan)
statistics['in_all_files'].append(len(all_uniq_strs))

#Полученная структура прописывается в JSON-файл с правильной
#обработкой кириллицы, формированием отступов и сортировкой ключей.
trg_file_name = os.path.basename(src_dir_path) + '_stat' + '.txt'
with open(os.path.join(trg_dir_path, trg_file_name), 'w', encoding='utf-8') as trg_file_opened:
        json.dump(statistics, trg_file_opened, ensure_ascii=False, indent=4, sort_keys=True)
