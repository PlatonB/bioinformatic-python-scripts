print('''
Python3-скрипт, объединяющий тексты в один файл.
Автор: Платон Быкадоров (platon.work@gmail.com), 2018.
Версия: V1.0.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Простое руководство по установке среды разработки и запуску скриптов:
github.com/PlatonB/bioinformatic-python-scripts#Установка-среды-разработки
''')

def write_into_file(file_or_dataset, trg_file_opened):
        '''
        Прописывание результатов в конечный файл.
        '''
        for line in file_or_dataset:
                if line.find('\n') == -1:
                        line += '\n'
                trg_file_opened.write(line)

src_dir_path = input('Путь к папке с исходными файлами: ')
trg_dir_path = input('\nПуть к папке для конкатенированного файла: ')
num_of_headers = input('''\nКоличество хэдеров/шапок в начале каждого текста
(игнорирование ввода ==> все хэдеры/шапки
пойдут в конкатенированный текст)
[0(|<enter>)|1|2|...]: ''')
if num_of_headers == '':
        num_of_headers = 0
else:
        num_of_headers = int(num_of_headers)
if num_of_headers > 0:
        headers_fate = input('''\nСделать ли хэдер(-ы)/шапку(-и) случайного исходного текста
хэдером(-ами)/шапкой(-ами) конкатенированного текста?
(рекомендуется, если исходные файлы -
таблицы с одинаковой шапкой)
(игнорирование ввода ==> не прописывать
в конечный текст хэдер(-ы)/шапку(-и))
[yes(|y)|<enter>]: ''')
else:
        headers_fate = 'no_headers'
kill_repeats = input('''\nУдалять копии строк?
(игнорирование ввода ==> не удалять)
[yes(|y)|no(|n|<enter>)]: ''')

import os

#В значительной части скриптов репозитория
#результаты работы размещаются в файлы,
#соответствующие каждому исходному файлу.
#В виду специфики программы-конкатенатора, все
#результаты пропишутся в один конечный файл.
#Создаём его сразу.
trg_file_name = os.path.basename(src_dir_path) + '_conc' + '.txt'
with open(os.path.join(trg_dir_path, trg_file_name), 'w') as trg_file_opened:
        
        #Если пользователь предпочёл уничтожать копии уже встретившихся
        #строк, то результаты конкатенации будут накапливаться во множество.
        data_wo_repeats = set()
        
        #Работа с исходными файлами.
        src_file_names = os.listdir(src_dir_path)
        for src_file_name in src_file_names:
                with open(os.path.join(src_dir_path, src_file_name)) as src_file_opened:
                        
                        #Формирование списка хэдеров.
                        #Курсор смещается к началу основной части текста.
                        headers = [src_file_opened.readline() for header_index in range(num_of_headers)]
                        
                        #Блок кода, вызываемый, если пользователь желает
                        #сохранить хэдер одного из исходных текстов
                        #в качестве хэдера конкатенированного текста.
                        #В конечный файл сохранится хэдер того файла,
                        #название которого окажется первым в списке названий.
                        #Эта опция рассчитана на тот случай, если нужно объединить
                        #однородные таблицы, имеющие одну и ту же шапку.
                        if headers_fate == 'yes' or headers_fate == 'y':
                                for header in headers:
                                        if header.find('\n') == -1:
                                                header += '\n'
                                        trg_file_opened.write(header)
                                        
                                #После выполнения блока кода, сохраняющего хэдеры в конечный
                                #файл, эта переменная должна принять любое значение, кроме
                                #тех, которые зарезервированы под срабатывание этого блока.
                                #Смена значения нужна для предотвращения повторного
                                #вызова данного блока, чтобы не плодить кучу хэдеров.
                                headers_fate = 'predestined'
                                
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
