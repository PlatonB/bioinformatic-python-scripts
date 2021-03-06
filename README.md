# [Перейти к руководству пользователя↓](#Установка-среды-разработки)
# [Заказать доработку скриптов под свои задачи↓](#персональные-доработки-скриптов)
# Необходимость использования скриптов в биоинформатике.
Делая первые шаги в изучении биоинформатики, вы можете по-началу собирать из баз данных таблицы с результатами биологических исследований и обрабатывать их популярными табличными процессорами типа Microsoft Excel и LibreOffice Calc. Но по мере усложнения задач, вам конечно же понадобятся специализированные решения. Довольно богатые наборы простых и сложных алгоритмов обработки биоинформатических текстов включены в облачные инструментарии Galaxy и UCSC, а также в управляемую командной строкой программу BedTools. Но со временем их функциональность перестанет вас устраивать. Вам потребуется максимально кастомизировать и автоматизировать формирование наборов данных для различных биоинформатических программ, а из выведенных биоинформатическими программами текстов, в свою очередь, быстро и грамотно извлекать нужную для вашего исследования информацию. Тут уже сложно будет обойтись без самописных скриптов. Но вполне может быть, что у вас нет желания изучать программирование, или, несмотря на имеющееся знание языка, реализация необходимого алгоритма кажется вам слишком долгим и муторным процессом.

# О проекте.
Проект посвящён созданию готовых скриптов под различные задачи обработки биоинформатических текстов.

## Глобальные цели.
- Упростить рутинные биоинформатические операции.
- Популяризовать биоинформатику.

## Предполагаемая аудитория.
- Биологи
- Генетики
- Врачи
- Биоинформатики
- Студенты/специалисты **без знания программирования**
	- если необходимо и достаточно только эксплуатировать скрипты
- Студенты/специалисты со знанием программирования
	- если есть желание ещё и принимать участие в разработке.

## Рекомендуемый уровень квалификации пользователя.
- Достаточный для ясного понимания выполняемых научных задач
- Уверенное пользование компьютером.

## Характеристики скриптов.
- Универсальны
	- каждый скрипт создаётся для охвата максимума задач
- Элементарно запускаются на многих операционных системах
- **Работают без командной строки**
	- вместо неё - дружественный интерактивный диалог
- По возможности, минимальньно потребляют RAM
- (Сведения для программистов)
	- Невелики по объёму кода
	- Содержат довольно простые алгоритмы
	- Не импортируют ни друг друга, ни сторонние модули
	- С подробно прокомментированным кодом
	- С человеко-понятными именами переменных.

## Язык - Python 3.
Для написания кода я выбрал язык Python 3, т.к. он довольно простой и включает в себя большое количество готовых функций для работы с текстовой информацией.

# Установка среды разработки.
Считаю, что проще всего для запуска скриптов использовать официальную питоновскую среду разработки IDLE (не ниже версии `3.6`!).

## Windows/[ReactOS](https://www.reactos.org/).
IDLE входит в пакет Python. Скачать Python для Windows или ReactOS:

https://www.python.org/ftp/python/3.8.1/python-3.8.1-amd64.exe

(ссылка будет периодически вручную обновляться)

## Fedora Linux.
Обзор → Показать приложения → Утилиты → [Терминал](https://github.com/PlatonB/ngs-pipelines#преодолеваем-страх-командной-строки-linux). Введите команду:

`sudo dnf install python3-idle`

## Ubuntu Linux/[elementary OS](https://elementary.io/ru/)/KDE neon/Linux Mint.

В программе [Терминал](https://github.com/PlatonB/ngs-pipelines#преодолеваем-страх-командной-строки-linux) введите такую команду:

`sudo apt install idle-python3.6` (3.7, ...)

# Сохранение скрипта(-ов) на свой компьютер.

## Вариант I. Автоматическое сохранение всего репозитория (рекомендую)
1. `Clone or download` (зелёная кнопка наверху страницы репозитория)
2. `Download ZIP`
3. Распакуйте архив со всеми скриптами.

## Вариант II. Вручную по одному скрипту
1. Создайте файл с расширением .py
2. Откройте его с помощью IDLE
3. `Ctrl+V` - вставьте скрипт из этого репозитория
4. `Ctrl+S` - сохраните.

## Вариант III. Вручную по одному скрипту
1. Откройте IDLE (появится интерактивная оболочка)
2. `Ctrl+N` - создайте новый файл
3. `Ctrl+V` - вставьте скрипт из этого репозитория
4. `Ctrl+S` - сохраните.

**Внимание!** При ручном копировании скрипта из Github может съехать последняя строка. После вставки в IDLE отступите то количество табуляций, которое вы видите в выложенной на Github версии.

# Эксплуатация скрипта.
1. `F5` - запустите скрипт
2. Следуйте указаниям в появившейся интерактивной оболочке Python Shell.

Аварийно: `Ctrl+F6` - остановка выполнения скрипта.

Примечание: в IDLE 3 на Windows (включая актуальную на 2017 г. версию 3.6), есть такой неприятный баг, что хоткеи работают только при английской раскладке.

# Диалог с пользователем.

`[опция1|опция2]` - введите одну из перечисленных опций.

`[опция1(|<enter>)|опция2]` - опция1 - опция по умолчанию. Т.е. вместо ввода этой опции можно просто нажать enter.

`[опция1(|опция2|опция3)|опция4]` - опции 1, 2 и 3 равнозначны. Т.е., какую бы из этих опций вы не ввели, результаты работы программы будут одинаковыми.

`[пример1|пример2|...]` - если в конце перечисления в квадратных скобках стоит многоточие, то это - не опции, а примеры того, что вы должны ввести.

# Качество.
1. Произвожу тестирование на элементарных выборках
	- это позволяет легко визуально оценить правильность результатов
2. Произвожу тестирование на реальных данных
	- опубликованные на данный момент скрипты прошли многократную проверку в рамках моих научных и научно-коммерческих работ.

Если скрипт всё же выводит ошибку, кидайте в [Issues](https://github.com/PlatonB/bioinformatic-python-scripts/issues) полный текст (Traceback) этой ошибки и отрывки исходных файлов — попробуем разобраться вместе.

# Техническая поддержка.
С любыми вопросами и предложениями смело обращайтесь в разделе [Issues](https://github.com/PlatonB/bioinformatic-python-scripts/issues).

# Персональные доработки скриптов.

## Ориентировочные цены\*.
- Частичное переписывание кода опубликованного скрипта:

`от 500 до 1000 руб.`

- Полное или почти полное переписывание кода опубликованного скрипта, либо создание скрипта с нуля:

`от 1000 до 5000 руб.`

- Крупные, долгосрочные работы. Развитие скриптового конвейера, полностью автоматизирующего обработку текстов в рамках вашего научного исследования:

`от 70000 руб./месяц`.

\*Для своих коллег любые доработки произвожу бесплатно.

## Как заказать доработку?
Вы можете написать на `platon.work@gmail.com`. Пожалуйста, помните, что "без внятного ТЗ результат - ХЗ":).

# Сказать спасибо автору.
Если вам пригодились опубликованные в этом репозитории скрипты, или просто понравилась идея проекта, вы можете выразить благодарность пожертвованием, пройдя по ссылке https://money.yandex.ru/to/41001832285976. Плюс расскажите о проекте однокурсникам или коллегам:)! Также буду очень благодарен, если вы [поделитесь своим опытом использования скриптов](https://github.com/PlatonB/bioinformatic-python-scripts/issues/3).

# Другие проекты.
## [LD-tools](https://github.com/PlatonB/ld-tools).
- Формирование и визуализация матриц значений LD для пар SNP.
- Поиск SNPs в LD с запрашиваемыми.
