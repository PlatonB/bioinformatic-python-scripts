print('''
Скрипт, создающий точечные диаграммы "позиция SNP - частота SNP в популяции" по данным из Haploreg 4.x-таблиц.
Автор: Платон Быкадоров, 2017.
Лицензия: GNU General Public License version 3.
Поддержать проект: https://money.yandex.ru/to/41001832285976

Для построение графиков этой программой необходимо установить Python-модуль Matplotlib:
Fedora: sudo dnf install python3-matplotlib
Ubuntu: sudo apt install python3-matplotlib

Диаграммы строятся по всем HaploReg-таблицам, находящимся в одной папке.
Ось X: позиции SNP в текущей хромосоме.
Ось Y: частоты SNP в популяциях.
Частоты набора SNP в определённой популяции обозначаются определённым цветом точек (см. легенду к каждому графику).
Если в таблице представлены SNPs нескольких хромосом, то программа построет несколько графиков: каждый - для снипов одной хромосомы.
Если какие-то элементы полученных программой графиков съехали, смешались или срезались, сообщайте в Issues.

Получение читаемой скриптом исходной таблицы в HaploReg 4.x (http://archive.broadinstitute.org/mammals/haploreg/haploreg.php):
1. Build Query --> Обзор... --> загружаете список идентификаторов вида rs1234567890, каждый на отдельной строке.
2. Set Options --> выбираем любые опции; Output mode - HTML.
3. Копируем HTML-вывод без раздела "Query SNP enhancer summary" в Microsoft Excel 365, а оттуда сохраняем как "Текстовые файлы с разделителями табуляции".
Внимание!
Каждый текстовый либо табличный редактор сохраняет гаплореговские HTML-таблицы в plain text, переформатируя их по-своему.
Этот скрипт способен обрабатывать только таблицы, сохранённые в txt с помощью Excel 365 (желательно, с последними обновлениями).
Если требуется обработать подготовленные другим путём HaploReg-таблицы, пишите в Issues.
''')

sourcedir = input('Путь к папке с HaploReg 4.x-таблицами (не забывать экранировать): ')
targetdir = input('Путь к папке с графиками (не забывать экранировать): ')

import os
import re
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter as fsf

def create_chart(x_pos, y_afr, y_amr, y_asn, y_eur, x_label, y_label, sourcefile, cur_chr_num):
        
        #Построение диаграммы из четырёх наборов координат.
        plt.scatter(x_pos, y_afr, label = 'afr')
        plt.scatter(x_pos, y_amr, label = 'amr')
        plt.scatter(x_pos, y_asn, label = 'asn')
        plt.scatter(x_pos, y_eur, label = 'eur')

        #Главные деления (major ticks) по оси X будут обозначаться целыми числами.
        plt.gca().xaxis.set_major_formatter(fsf('%d'))

        #Устанавливаем такой размер шрифта подписей к делениям, чтобы после сохранения методом savefig() они не наползали друг на друга.
        plt.gca().tick_params(labelsize=5)

        #Сетка, соответствующая главным делениям.
        plt.grid(True)

        #Названия осей, взятые из шапки HaploReg-таблицы.
        plt.xlabel(x_label)
        plt.ylabel(y_label)

        #Формирование легенды из "лейблов", указанных в качестве аргумента функции построения диаграммы.
        #Легенда будет расположена внизу слева относительно области рисования.
        #Задаём такой шрифт, чтобы легенда не срезалась и не наползла на область рисования.
        plt.legend(loc = (-0.15, 0.0), fontsize = 5)

        #Заголовок графика будет содержать название текущего HaploReg-файла и текущий номер хромосомы.
        plt.title(os.path.basename(sourcefile) + '; Хромосома ' + str(cur_chr_num))

        #Сохранение графика в формате svg.
        targetfile = sourcefile.split('.')[0] + '_chr' + str(cur_chr_num) + '.svg'
        plt.savefig(os.path.join(targetdir, targetfile), format = 'svg')
        plt.close()

sourcefiles = os.listdir(sourcedir)

for sourcefile in sourcefiles:
        s = open(os.path.join(sourcedir, sourcefile))
        sourcelist = list(s)
        s.close()

        #Создание нового списка, в котором не будет пустых и ненужных для построения графика строк (но шапка не удаляется).
        #Формирование названий осей из прописанных Гаплорегом заголовков соответствующих столбцов.
        slist = []
        for line in sourcelist:
                row = re.split(r'\t', line)
                if line.find('(hg38)') != -1:
                        x_label = row[1]
                        slist.append(row)
                elif line.find('(r?)') != -1:
                        y_label = row[7]
                        slist.append(row)
                if re.match(r'\d+', line) != None and row[7] != '' and re.search(r'[NM]', ''.join(row[8:12])) == None:
                        row[0], row[1], row[2] = int(row[0]), int(row[1]), int(row[2])
                        slist.append(row)

        #Сортировка очищенных HaploReg-таблиц.
        #Двухстрочная шапка в сортировке не участвует и добавляется к отсортированным файлам отдельно.
        slist_sorted = sorted(slist[2:])
        slist_sorted.insert(0, slist[1])
        slist_sorted.insert(0, slist[0])

        #Накапливаем 4 списка значений частоты SNP, соответственно, в 4-х популяциях.
        #Рисуем график только, когда в списках накопились все позиции и частоты снипов данной хромосомы.
        #Завершение накопления осуществляется, если в очередной строке появился новый номер хромосомы, или когда закончилась вся таблица.
        #После рисования графика списки очищаются и заново накапливаются позициями и частотами SNPs уже новой хромосомы.
        x_pos, y_afr, y_amr, y_asn, y_eur = [], [], [], [], []
        cur_chr_num = int(slist_sorted[2][0])
        line_num = 3
        for row in slist_sorted[2:]:
                line_num += 1
                if int(row[0]) > cur_chr_num:
                        create_chart(x_pos, y_afr, y_amr, y_asn, y_eur, x_label, y_label, sourcefile, cur_chr_num)
                        cur_chr_num = int(row[0])
                        x_pos.clear()
                        y_afr.clear()
                        y_amr.clear()
                        y_asn.clear()
                        y_eur.clear()
                elif line_num == len(slist_sorted):
                        create_chart(x_pos, y_afr, y_amr, y_asn, y_eur, x_label, y_label, sourcefile, cur_chr_num)
                        break
                x_pos.append(int(row[1]))
                y_afr.append(float(row[7]))
                y_amr.append(float(row[8]))
                y_asn.append(float(row[9]))
                y_eur.append(float(row[10]))
