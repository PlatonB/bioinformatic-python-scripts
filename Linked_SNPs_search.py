print('''
Этот Python3-клиент Ensembl REST API ищет SNPs, обладающие
неравновесием по сцеплению с запрашиваемыми SNPs не ниже определённого
порога r2 или D', и находящиеся в пределах "окна", равного 500 кбаз.
Автор: Платон Быкадоров (platon.work@gmail.com), 2018.
Версия: V1.2.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Скрипт разработан для замены аналогичной функциональности
заброшенной разработчиками программы HaploReg.

Исходные файлы - таблицы, содержащие столбец с набором refSNPIDs.

Скрипт попросит вас ввести ряд параметров запроса к API.
Если требуемые скриптом уточнения вам не
понятны - пишите, пожалуйста, в Issues.
''')

def query(url_template, refsnpid):
        '''
        Добавление текущего refSNPID в шаблон
        запроса, осуществление этого запроса.
        Возврат списка словарей, содержащих пару refSNPIDs
        (запрашиваемый и найденный), название популяции,
        а также значения r2 и D' для данной пары.
        '''
        url = url_template.replace('refsnpid', refsnpid)
        print('Обрабатывается запрос', url)
        r = requests.get(url)
        if not r.ok:
                r.raise_for_status()
                sys.exit()
        decoded = r.json()
        return decoded

####################################################################################################

import os, sys, requests, re, json

src_dir_path = input('Путь к папке с исходными файлами: ')
trg_top_dir_path = input('\nПуть к папке для папок с конечными файлами: ')
num_of_headers = input('''\nКоличество не обрабатываемых строк в начале файла
(игнорирование ввода ==> хэдеров/шапок в таблице нет)
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
pop_name = input('''\nПопуляция из 1000 Genomes
(ensembl.org/info/genome/variation/species/populations.html)
[1000GENOMES:phase_3:EUR|1000GENOMES:phase_3:ALL|...]: ''')
ld_measure = input('''\nМера неравновесия сцепления (LD)
[r2|d_prime]: ''')
ld_value = float(input('\n{} >= '.format(ld_measure)))
query_snp_save = input('''\nВыводить в конечный файл запрашиваемый SNP?
(игнорирование ввода ==> не выводить)
[yes(|y)|<enter>]: ''')
trg_file_format = input('''\nФормат конечных файлов
(игнорирование ввода ==> json)
[json(|<enter>)|tsv]: ''')
if trg_file_format == '':
        trg_file_format = 'json'

#Первичный шаблон запроса к API и его заполнение
#общими для всех запрашиваемых SNPs данными.
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
                        linked_snps_n_specs = query(fil_url_templ, rs_id)
                        
                        #Если полученный список - пустой, то соответствующий
                        #ему конечный файл создаваться не будет.
                        if linked_snps_n_specs == []:
                                continue

                        #Опциональное дополнение списка словарей элементом,
                        #содержащим пару запрашиваемый-запрашиваемый SNP.
                        if query_snp_save == 'yes' or query_snp_save == 'y':
                                query_snp_n_specs = {'variation1': rs_id,
                                                     'population_name': pop_name,
                                                     'variation2': rs_id,
                                                     'r2': '1.000000',
                                                     'd_prime': '1.000000'}
                                linked_snps_n_specs.insert(0, query_snp_n_specs)
                                
                        #Создание конечного файла того
                        #формата, который выбрал пользователь.
                        with open(trg_file_path, 'w') as trg_file_opened:
                                if trg_file_format == 'json':
                                        
                                        #Полученный список словарей пропишется
                                        #в JSON-файл с формированием отступов.
                                        json.dump(linked_snps_n_specs, trg_file_opened, indent=4)

                                elif trg_file_format == 'tsv':
                                        
                                        #От словаря к словарю энсембловского списка набор ключей идентичен.
                                        #Поэтому хэдер TSV-таблицы можно сконструировать из ключей любого словаря.
                                        #Осуществляем это по первому словарю и прописываем результат в конечный файл.
                                        trg_file_opened.write('\t'.join(linked_snps_n_specs[0].keys()) + '\n')

                                        #Строки основной части таблицы будут получаться из значений каждого словаря.
                                        for dic in linked_snps_n_specs:
                                                trg_file_opened.write('\t'.join(dic.values()) + '\n')
