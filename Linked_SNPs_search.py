print('''
Этот Python3-клиент Ensembl REST API ищет SNPs, обладающие
неравновесием по сцеплению с запрашиваемыми SNPs не ниже определённого
порога r2 или D', и находящиеся в пределах "окна", равного 500 кбаз.
Автор: Платон Быкадоров (platon.work@gmail.com), 2018.
Версия: V1.4.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Простое руководство по установке среды разработки и запуску скриптов:
github.com/PlatonB/bioinformatic-python-scripts#Установка-среды-разработки

Скрипт разработан для замены аналогичной функциональности
заброшенной разработчиками программы HaploReg.

Исходные файлы - таблицы, содержащие столбец с набором refSNPIDs.

Скрипт попросит вас ввести ряд параметров запроса к API.
Если требуемые скриптом уточнения вам не
понятны - пишите, пожалуйста, в Issues.
''')

def query_to_ens(url_template, refsnpid):
        '''
        Добавление текущего refSNPID в шаблон
        запроса и осуществление этого запроса.
        Проверка, не выдал ли сервер наиболее популярные,
        согласно моему опыту, ответы 503 и 429.
        Возврат списка словарей, содержащих пару refSNPIDs
        (запрашиваемый и найденный), название популяции,
        а также значения r2 и D' для данной пары.
        '''
        url = url_template.replace('refsnpid', refsnpid)
        print(url)
        r = requests.get(url)
        if r.status_code == 503:
                print('''\n503
Сервер временно не имеет возможности
обрабатывать запросы по техническим причинам.
Работа программы будет завершена.''')
                sys.exit()
        elif r.status_code == 429:
                print('''\n429
Вы попытались отправить слишком
много запросов за короткое время.
Работа программы будет завершена.''')
                sys.exit()
        decoded = r.json()
        return decoded

####################################################################################################

import os, sys, requests, re, json

src_dir_path = input('Путь к папке с исходными файлами: ')
trg_top_dir_path = input('\nПуть к папке для папок с конечными файлами: ')
num_of_headers = input('''\nКоличество не обрабатываемых строк
в начале каждой исходной таблицы
(игнорирование ввода ==> хэдеров/шапок в таблицах нет)
[0(|<enter>)|1|2|...]: ''')
if num_of_headers == '':
        num_of_headers = 0
else:
        num_of_headers = int(num_of_headers)
species = input('''\nВид
(rest.ensembl.org/info/species?content-type=application/json, см. "name")
(игнорирование ввода ==> человек)
[homo_sapiens(|<enter>)|panthera_pardus|pteropus_vampyrus|...]: ''')
if species == '':
        species = 'homo_sapiens'
pop_name = input('''\nПопуляция по 1000 Genomes
(ensembl.org/info/genome/variation/species/populations.html)
(игнорирование ввода ==> 1000GENOMES:phase_3:ALL)
[1000GENOMES:phase_3:ALL(|<enter>)|1000GENOMES:phase_3:EUR|...]: ''')
if pop_name == '':
        pop_name = '1000GENOMES:phase_3:ALL'
elif pop_name.startswith('1000GENOMES:phase_3:') == False:
        print(f'{pop_name} - недопустимая опция')
        sys.exit()
ld_measure = input('''\nМера неравновесия сцепления (LD)
[r2|d_prime]: ''')
if ld_measure != 'r2' and ld_measure != 'd_prime':
        print(f'{ld_measure} - недопустимая опция')
        sys.exit()
ld_value = float(input('\n{} >= '.format(ld_measure)))
query_snp_save = input('''\nВыводить в конечный файл запрашиваемый SNP?
(игнорирование ввода ==> не выводить)
[yes(|y)|no(|n|<enter>)]: ''')
if query_snp_save != 'yes' and query_snp_save != 'y' and query_snp_save != 'no' \
   and query_snp_save != 'n' and query_snp_save != '':
        print(f'{query_snp_save} - недопустимая опция')
        sys.exit()
trg_file_format = input('''\nФормат конечных файлов
(игнорирование ввода ==> json)
[json(|<enter>)|tsv]: ''')
if trg_file_format != 'json' and trg_file_format != 'tsv' and trg_file_format != '':
        print(f'{trg_file_format} - недопустимая опция')
        sys.exit()
if trg_file_format == '':
        trg_file_format = 'json'
        
#Первичный шаблон запроса к API и его заполнение
#общими для всех запрашиваемых SNP данными.
emp_url_templ = 'https://rest.ensembl.org/ld/{}/refsnpid/{}?content-type=application/json;{}={}'
fil_url_templ = emp_url_templ.format(species, pop_name, ld_measure, ld_value)

#Работа с исходными файлами.
src_file_names = os.listdir(src_dir_path)
for src_file_name in src_file_names:
        with open(os.path.join(src_dir_path, src_file_name)) as src_file_opened:
                trg_dir_path = os.path.join(trg_top_dir_path, src_file_name.split('.')[0] + '_lnkd')
                
                #Результаты по каждому исходному файлу будут
                #размещены в соответствующую этому файлу подпапку.
                os.mkdir(trg_dir_path)
                
                #Считываем строки-хэдеры, чтобы сместить
                #курсор к началу основной части таблицы.
                for header_index in range(num_of_headers):
                        src_file_opened.readline()
                        
                print(f'''\n\tПолучение SNP, неравновесно сцепленных с каждым SNP из файла
\t\t{src_file_name}''')
                
                #Считывание строк основной части таблицы.
                for line in src_file_opened:
                        
                        #Попытка извлечения refSNPID из текущей строки.
                        try:
                                rs_id = re.search(r'rs\d+', line).group()
                        except AttributeError:
                                continue
                        
                        #Формирование имени конечного файла и пути к нему.
                        trg_file_name = rs_id + '_' + pop_name.split(':')[-1] + '_' \
                                        + ld_measure + '_' + str(ld_value) + '.' + trg_file_format
                        trg_file_path = os.path.join(trg_dir_path, trg_file_name)
                        
                        #Если в исходном наборе определённый SNP встретился
                        #ещё раз, то необходимо предотвратить повторный запрос.
                        if os.path.exists(trg_file_path) == True:
                                continue
                        
                        #Запрос к Ensembl REST API, получение
                        #списка словарей с выходными данными.
                        linked_snps_n_specs = query_to_ens(fil_url_templ, rs_id)
                        
                        #Если полученный список - пустой, то соответствующий
                        #ему конечный файл создаваться не будет.
                        #Если вместо списка выдаётся словарь, то этот
                        #словарь - исключительно с сообщением об ошибке.
                        #В обоих случаях переходим к следующей строке.
                        if linked_snps_n_specs == []:
                                continue
                        if type(linked_snps_n_specs).__name__ == 'dict':
                                print(rs_id, '- невалидный идентификатор')
                                continue
                        
                        #Опциональное дополнение списка словарей элементом,
                        #содержащим пару запрашиваемый-запрашиваемый SNP.
                        #Этот элемент будет добавлен в список на первую позицию.
                        if query_snp_save == 'yes' or query_snp_save == 'y':
                                query_snp_n_specs = {'variation1': rs_id,
                                                     'variation2': rs_id,
                                                     'r2': '-',
                                                     'd_prime': '-',
                                                     'population_name': pop_name}
                                linked_snps_n_specs.insert(0, query_snp_n_specs)
                                
                        #Создание конечного файла того
                        #формата, который выбрал пользователь.
                        with open(trg_file_path, 'w') as trg_file_opened:
                                if trg_file_format == 'json':
                                        
                                        #Полученный ранее список словарей пропишется
                                        #в JSON-файл с формированием отступов.
                                        json.dump(linked_snps_n_specs, trg_file_opened, indent=4)
                                        
                                elif trg_file_format == 'tsv':
                                        
                                        #Ключи в словарях, генерируемых Ensembl REST API,
                                        #одни и те же, но занимают непостоянные позиции.
                                        #Поэтому шапку конечной таблицы придётся прописывать
                                        #вручную, а не составлять из ключей одного из словарей.
                                        trg_file_opened.write('variation1\tvariation2\tr2\td_prime\tpopulation_name\n')
                                        
                                        #Строки основной части конечной таблицы будут
                                        #получаться из значений каждого словаря.
                                        #Последовательность ячеек в каждой строке
                                        #конечной таблицы при этом задаётся вручную.
                                        for dic in linked_snps_n_specs:
                                                trg_file_opened.write(dic['variation1'] + '\t' + dic['variation2'] + '\t' + \
                                                                      dic['r2'] + '\t' + dic['d_prime'] + '\t' + dic['population_name'] + '\n')
