# Необходимость использования скриптов в биоинформатике.
Делая первые шаги в изучении биоинформатики, вы можете по-началу собирать из баз данных таблицы с результатами биологических исследований и обрабатывать их популярными табличными процессорами типа Microsoft Excel и LibreOffice Calc. Но по мере усложнения задач, вам конечно же понадобятся специализированные решения. Довольно богатые наборы простых и сложных алгоритмов обработки биоинформатических текстов включены в облачные инструментарии Galaxy и UCSC, а также в управляемую командной строкой программу BedTools. Но со временем их функциональность перестанет вас устраивать. Вам потребуется максимально кастомизировать и автоматизировать формирование наборов данных для различных биоинформатических программ, а из выведенных биоинформатическими программами текстов, в свою очередь, быстро и грамотно извлекать нужную для вашего исследования информацию. Тут уже сложно будет обойтись без самописных скриптов. Но вполне может быть, что у вас нет желания изучать программирование, или, несмотря на имеющееся знание языка, реализация необходимого алгоритма кажется вам слишком долгим и муторным процессом.

# О проекте.
Проект, как вы уже поняли, посвящён созданию готовых скриптов под различные задачи обработки биоинформатических текстов.

## Глобальные цели.
- Упростить рутинные биоинформатические операции.
- Популяризовать биоинформатику.

## Предполагаемая аудитория.
- Биологи
- Генетики
- Врачи
- Биоинформатики
- Студенты/специалисты **без знания программирования**
	- если нужно просто эксплуатировать скрипты
- Студенты/специалисты со знанием программирования
	- если есть желание ещё и помогать развитию проекта

## Рекомендуемый уровень квалификации пользователя.
- Уверенное пользование компьютером
- Ясное понимание выполняемых научных задач

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
	- С человеко-понятными именами переменных

## Язык - Python 3.
Для написания кода я выбрал язык Python 3, т.к. он очень простой и включает в себя большое количество готовых функций для работы с текстовой информацией.

# Установка среды разработки.
Рекомендую для запуска скриптов официальную питоновскую среду разработки IDLE (не ниже 3-й версии!).

## Windows/ReactOS.
IDLE входит в пакет Python. Скачать Python для Windows или ReactOS:
https://www.python.org/ftp/python/3.7.0/python-3.7.0-amd64.exe
(ссылка будет периодически вручную обновляться)

## Fedora Linux.
Обзор → Показать приложения → Утилиты → Терминал. Введите команду:

`sudo dnf install python3-idle`

## Ubuntu Linux.

`sudo apt install idle3`

# Сохранение скрипта(-ов) на свой компьютер.

## Вариант I. Автоматическое сохранение всего репозитория (рекомендую)
1. `Clone or download`
2. `Download ZIP`
3. Распакуйте архив со всеми скриптами

## Вариант II. Вручную по одному скрипту
1. Создайте файл с расширением .py
2. Откройте его с помощью IDLE
3. `Ctrl+V` - вставьте скрипт из этого репозитория
4. `Ctrl+S` - сохраните

## Вариант III. Вручную по одному скрипту
1. Откройте IDLE
2. `Ctrl+N` - создайте новый файл
3. `Ctrl+V` - вставьте скрипт из этого репозитория
4. `Ctrl+S` - сохраните

**Внимание!** При ручном копировании из Github может съехать последняя строчка скрипта. После вставки в IDLE отступите то количество табуляций, которое имеется в выложенной на Github версии.

# Эксплуатация скрипта.
1. `F5` - запустите скрипт
2. Следуйте указаниям в появившейся интерактивной оболочке Python Shell

Аварийно: `Ctrl+F6` - остановка выполнения скрипта.

Примечание: в IDLE 3 на Windows (включая актуальную на 2017 г. версию 3.6), есть такой неприятный баг, что хоткеи работают только при английской раскладке.

# Диалог с пользователем.

`[опция1|опция2]` - введите одну из перечисленных опций.

`[опция1(|<enter>)|опция2]` - опция1 - опция по умолчанию. Т.е. вместо ввода этой опции можно просто нажать enter.

`[опция1(|опция2|опция3)|опция4]` - опции 1, 2 и 3 равнозначны. Т.е., какую бы из этих опций вы не ввели, результаты работы программы будут одинаковыми.

`[пример1|пример2|...]` - если в конце перечисления в квадратных скобках стоит многоточие, то это - не опции, а примеры того, что вы должны ввести.

# Качество.
1. Производится тестирование на элементарных выборках
	- позволяет легко визуально оценить правильность результатов
2. Производится тестирование на реальных данных
	- опубликованные на данный момент скрипты прошли многократную проверку в рамках моих научных и научно-коммерческих работ

Если скрипт выводит ошибку, кидайте в [Issues](https://github.com/PlatonB/bioinformatic-python-scripts/issues) полный текст (Traceback) этой ошибки и отрывки исходных файлов — попробуем разобраться вместе.

# Присоединяйтесь!
С любыми вопросами и предложениями смело обращайтесь в разделе [Issues](https://github.com/PlatonB/bioinformatic-python-scripts/issues). Приглашаю к сотрудничеству других добровольцев-программистов. Если ваши скрипты качественные и соответствуют [философии проекта](#О-проекте), то буду рад их разместить.

# Поддержка проекта.
Возможно, в дальнейшем буду создавать и дорабатывать скрипты под индивидуальные запросы заказчиков на платной основе, но сейчас проект держится исключительно на моём энтузиазме. Если вам пригодились скрипты, или просто понравилась идея проекта, вы можете выразить благодарность пожертвованием, пройдя по ссылке https://money.yandex.ru/to/41001832285976. Плюс расскажите о проекте однокурсникам или коллегам:). Заранее огромное спасибо!
