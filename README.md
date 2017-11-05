<h4>Необходимость использования скриптов в биоинформатике.</h4>
Делая первые шаги в изучении биоинформатики, вы можете по-началу собирать из баз данных таблицы с результатами биологических исследований и обрабатывать их популярными табличными процессорами типа Microsoft Excel и LibreOffice Calc. Но по мере усложнения задач, вам конечно же понадобятся специализированные решения. Довольно богатые наборы простых и сложных алгоритмов обработки биоинформатических текстов включены в облачные инструментарии Galaxy и UCSC, а также в управляемую командной строкой программу BedTools. Но со временем их функциональность перестанет вас устраивать. Вам потребуется максимально кастомизировать и автоматизировать формирование наборов данных для различных биоинформатических прогримм, а из выведенных биоинформатическими программами текстов, в свою очередь, быстро и грамотно извлекать нужную для вашего исследования информацию. Тут уже сложно будет обойтись без самописных скриптов. Но вполне может быть, что у вас нет желания изучать программирование, или, несмотря на имеющееся знание языка, реализация необходимого алгоритма кажется вам слишком долгим и муторным процессом.

<h4>О проекте.</h4>
Проект, как вы уже поняли, посвящён созданию готовых скриптов под различные задачи обработки биоинформатических текстов. Для написания кода я выбрал язык Python 3, т.к. он очень простой и включает в себя большое количество готовых функций для работы с текстовой информацией. Скрипты могут быть полезны как биологам и медикам, не желающим изучать программирование, так и студентам и специалистам биомедицинской сферы, стремящимся познать хотя бы основы скриптовых языков. Глобальные цели проекта - упростить рутинные биоинформатические операции и популяризовать биоинформатику. Скрипты из этого репозитория невелики по объёму кода, содержат довольно простые алгоритмы, никак не связаны друг с другом и элементарно запускаются на многих операционных системах. Если возьмусь за написание более сложных программ, то буду создавать для них отдельные репозитории. Я очень забочусь об удобстве использования (юзабилити) своих программ: в большинстве случаев при запуске скрипта достаточно лишь указать директории с исходными файлами и куда сохранять получившиеся. Считаю необходимым как можно подробнее комментировать код: все участки кода должны быть сходу понятны даже совсем начинающим программистам.

<h4>Запуск скриптов.</h4>
Думаю, проще всего сделать так: установить официальную питоновскую среду разработки IDLE (не ниже 3-й версии), создать там новый файл (Ctrl+N), скопировать в этот файл нужный скрипт, сохранить его (Ctrl+S), запустить (F5) и далее следовать простейшим указаниям в появившейся интерактивной оболочке Python Shell. В случае чего, остановить выполнения скрипта можно, либо закрыв окно Python Shell, либо нажав Ctrl+F6. Примечание: в IDLE 3 на Windows (включая актуальную на 2017 г. версию 3.6), есть такой неприятный баг, что хоткеи работают только при английской раскладке.

<h4>Качество.</h4>
Внимательно тестирую все свои программы вначале на элементарных выборках (так, чтобы легко было визуально оценить правильность результатов), а потом на реальных. Но имейте в виду, что применяемые в биоинформатике программы способны принимать только определённые форматы входных текстовых данных и могут неправильно работать с небрежно отформатированными текстами. Рекомендации по подготовке исходных файлов прописываю в начале каждого скрипта.

<h4>Присоединяйтесь!</h4>
С любыми вопросами и предложениями смело обращайтесь в разделе Issues. Приглашаю к сотрудничеству других добровольцев-программистов. Если ваши скрипты качественные и соответствуют философии проекта, описанной во втором абзаце, то буду рад их разместить.

<h4>Поддержка проекта.</h4>
Возможно, в дальнейшем буду создавать и дорабатывать скрипты под индивидуальные запросы заказчиков на платной основе, но сейчас проект держится исключительно на моём энтузиазме. Если вам пригодились скрипты, или просто понравилась идея проекта, вы можете выразить благодарность пожертвованием, пройдя по ссылке https://money.yandex.ru/to/41001832285976. Плюс расскажите о проекте однокурсникам или коллегам:). Заранее огромное спасибо!
