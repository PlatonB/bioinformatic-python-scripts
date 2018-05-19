print('''
Python3-скрипт, который выводит строки той или иной таблицы,
содержащие определённый refSNPID.
Автор: Платон Быкадоров, 2018.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

В этом репозитории есть также программа,
которая ищет не один refSNPID, а целые наборы.

Остановить поиск, не закрывая окно консоли,
можно следующим образом:
IDLE Python Shell: CTRL+F6
Терминал в Linux: CTRL+Z
''')

import os
import re

rs_id = input('Идентификатор SNP [rs1234567890]: ')
base_file_path = input('Путь к таблице, в которой нужно искать: ')

if os.path.getsize(base_file_path) > 1000000000:
    print('Поиск в файле ' + os.path.basename(base_file_path) + ' может быть длительным')
with open(base_file_path) as base_op:
    for line in base_op:

        #При поиске rs1234 могут найтись rs123412, rs123400 и т.п..
        #Поэтому с помощью спецсимвола \b должен быть чётко обозначен конец идентификатора.
        if re.search(r'{}\b'.format(rs_id), line):
            print(line.split('\n')[0])
