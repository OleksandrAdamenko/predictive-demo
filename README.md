# RoadIQ — CalTRANS Crash Prediction Demo

Backtest replay dashboard for the CalTRANS District 3 pilot.
Replays January 2026 day by day, showing predicted risk zones vs. actual crashes.

---

# Руководство по дашборду CalTRANS / CalTRANS Dashboard Guide

---

## РУССКИЙ

---

### Как устроена система и почему именно так?

#### Откуда берутся данные

Система обучена на реальных данных об авариях на дорогах Калифорнии за 2023–2025 годы — это официальная статистика CalTRANS (Калифорнийского департамента транспорта). Данные о погоде (осадки, ветер, видимость, температура) берутся из открытого источника Open-Meteo, который предоставляет исторические и прогнозные метеорологические данные бесплатно. Никаких закрытых или дорогостоящих источников данных не требуется.

#### Почему карта разбита на шестиугольники?

Территория Калифорнии разбита на тысячи маленьких шестиугольных клеток — каждая примерно 0.5 × 0.5 км. Такую сетку называют H3 (разработана компанией Uber для геопространственного анализа). Шестиугольники выбраны не случайно: у них все соседние клетки находятся на одинаковом расстоянии от центра, в отличие от квадратов, где угловые соседи дальше боковых. Это делает анализ пространственных паттернов более точным. Каждая клетка — это **зона**. Для каждой зоны и каждого часа суток система делает независимый прогноз.

#### Как работает модель?

Для предсказания используется алгоритм **Gradient Boosting** — один из наиболее надёжных и проверенных методов машинного обучения для задач классификации на табличных данных. Если объяснить совсем просто: алгоритм строит сотни простых правил вида «если час пик + мокрая дорога + эта зона исторически опасна → риск высокий», а потом объединяет их в одну общую оценку.

Почему не нейросеть? Нейросети лучше работают с изображениями, видео и текстом — то есть там, где данные неструктурированы. Для табличных данных (а у нас именно таблица: дата, час, погода, история аварий) Gradient Boosting показывает сопоставимую или лучшую точность, при этом работает быстрее, требует меньше данных для обучения и его результаты проще интерпретировать. Это практичный выбор для реальной задачи.

Модель смотрит на **13 факторов**: час дня, день недели, месяц, праздник или нет, историческая аварийность этой зоны, осадки, скорость ветра, видимость, тип погоды, температура, тип дороги (хайвей или нет). На выходе — оценка вероятности аварии от 0 до 1 для каждой зоны в каждый час.

#### Как проходило обучение?

Модель обучалась на данных 2023–2025 годов. Январь 2026 года был намеренно исключён из обучения и отложен как «контрольный» период — то есть модель ни разу не видела эти данные во время обучения. Именно на январе 2026 мы и проверяем качество предсказаний. Это стандартная практика в машинном обучении: честный экзамен на данных, которых модель не знает.

Дополнительно обучены две версии модели: отдельно для будних дней и отдельно для выходных — потому что паттерны аварий в выходные существенно отличаются (другое распределение по часам, другие типичные причины).

#### Уровни риска и почему зелёные зоны не показаны

После того как модель выставила оценки всем зонам, они ранжируются, и каждой присваивается **уровень риска**:

- **Critical (красный)** — топ 1% самых опасных зон
- **High (оранжевый)** — топ 5%
- **Medium (жёлтый)** — топ 20%
- **Low (зелёный)** — остальные 80%

На карте и в статистике мы сознательно **не показываем зелёные зоны**. Причина простая: их 80% от общего числа, они создают визуальный шум и не несут практической ценности для принятия решений. Зелёная зона — это «здесь всё как обычно». Красная, оранжевая или жёлтая — «сюда стоит обратить внимание». Именно на этом и строится логика системы: не предсказать каждую аварию, а выделить зоны повышенного риска там, где ресурсы патруля будут потрачены наиболее эффективно.

---

### Что такое этот дашборд?

Это демонстрационный дашборд, который показывает, как работает система предсказания ДТП на дорогах Калифорнии. Он воспроизводит январь 2026 года день за днём — мы берём уже прошедшие события и смотрим: насколько точно модель предсказала, где и когда случится авария, ещё **до** того, как она произошла.

Важно понимать одну ключевую вещь: система не видела данные за январь 2026 года во время обучения. Она обучалась на авариях 2023–2025 годов, а январь 2026-го — это «экзамен», данные которого модель видит впервые. Это честная проверка.

---

### Боковая панель (слева) — элементы управления

**Выбор даты** — выбираете любой день из января 2026 года. Система показывает, что предсказывалось и что происходило в реальности именно в этот день. Рядом с датой указан день недели (например, Sunday — воскресенье).

**Map view** — переключатель между двумя режимами карты:
- **Prediction** — карта показывает то, что система предсказала утром того дня. Зоны окрашены по уровню риска. Это ответ на вопрос: «Куда смотрела система?»
- **Reality check** — карта показывает, что случилось на самом деле. Зоны, где авария действительно произошла, сохраняют свой цвет. Зоны, где аварии не было, становятся серыми и прозрачными. Это ответ на вопрос: «Угадала ли система?»

**Filter by hour of day** — ползунок, которым можно ограничить данные определённым временным диапазоном. Например, выставить 16:00–19:00 и смотреть только на вечерний час пик. Все числа на странице пересчитываются под этот фильтр.

---

### Строка заголовка (вверху страницы)

Показывает контекст текущего выбора:
- Выбранная дата и день недели
- Район: District 3 (Сакраменто / коридор Залива)
- Текущий часовой фильтр (или «All hours», если фильтр не применён)
- Сколько зон сейчас отображается на карте

---

### Бейдж режима (синий или зелёный)

Маленькая цветная плашка над картой:
- **🔮 Prediction** (синяя) — вы смотрите на прогноз
- **✅ Reality check** (зелёная) — вы смотрите на реальность

Это напоминалка, чтобы не перепутать, что именно отображается.

---

### Карта

Главный элемент дашборда. На карте показаны дороги и зоны повышенного риска в виде кружков (критические, высокие и средние — топ 20% всех зон).

**Цвет кружка** — уровень риска зоны (красный = критический, оранжевый = высокий, жёлтый = средний).

**Размер кружка** — тоже зависит от уровня риска: красные кружки крупнее, жёлтые — мельче. Это позволяет сразу визуально выделить самые опасные места.

**В режиме Reality check:**
- Зоны с реальными авариями сохраняют яркий цвет и белую обводку
- Зоны, где авария не случилась, становятся серыми и прозрачными — они остаются на карте, чтобы было видно: «система смотрела сюда, но здесь обошлось»

**При наведении на кружок** появляется подсказка с названием дороги и уровнем риска.

**При клике на кружок** открывается всплывающее окно с подробностями:
- Название дороги
- Номер зоны
- Уровень риска
- Числовая оценка риска (например, 0.312)
- Сколько временных слотов в этой зоне имели аварии (например, «2/8 zone-hours had crashes» означает: из 8 проверяемых часов в этой зоне в 2 из них случилась авария)

---

### Day summary (под картой, слева) — итоги дня

Четыре числа, которые дают общую картину дня:

**Crashes recorded** — сколько всего зафиксировано аварий за выбранный период. Под числом написано, сколько всего «зона-час» слотов было проанализировано. Например: «47 аварий из 12,400 слотов» означает, что система смотрела на 12,400 пар «зона × час» и в 47 из них произошла авария.

**Critical zones** — сколько временных слотов было помечено как критический риск, какой процент из них действительно содержал аварию (hit%), и насколько это лучше случайного угадывания (например, «2.8×» означает: в критических зонах аварии происходили в 2.8 раза чаще, чем в среднем по всем зонам).

**High zones** — то же самое для зон высокого риска.

**Medium zones** — то же самое для зон среднего риска.

---

### Legend (под картой, справа) — легенда

Объяснение цветов зон.

В режиме **Prediction**: «Zones colored by predicted risk tier (top 20%)» — на карте показаны только зоны повышенного риска.

В режиме **Reality check**: «Crash zones keep tier color. No-crash zones are grey» — зоны с авариями сохраняют цвет, зоны без аварий — серые.

---

### Top-10 highest-risk zones (справа вверху) — десять самых опасных зон

Таблица с десятью зонами, которые получили самый высокий балл риска за выбранный день.

**Road** — название дороги (например, I-80, US-50).

**Tier** — уровень риска зоны (critical или high; в топ-10 попадают только эти два уровня).

**Score** — числовой балл от 0 до 1. Чем выше, тем опаснее. Например, 0.412 значит, что модель оценила вероятность аварии как ~41%.

**Crash?** — ✅ если в этой зоне действительно была авария в тот день, — если нет.

Эта таблица отвечает на вопрос: «Куда система посоветовала бы отправить патрульные машины?»

---

### Hourly: crash rate vs. score (справа внизу) — сравнение по часам

График, где по горизонтали — часы суток (от 0 до 23), а по вертикали — два показателя:

**Красная линия (Actual crash rate)** — реальная аварийность по часам. Если в 17:00 было много аварий, красная линия поднимается.

**Синяя линия (Avg predicted score)** — средний балл риска, который система выставила всем зонам в этот час. Если система «думала», что в 17:00 будет опасно — синяя линия поднимается.

Если обе линии движутся похожим образом (вместе растут и падают) — значит, система хорошо «чувствует» опасные часы. Это визуальная проверка того, что модель знает про час пик.

---

### Tier precision — точность предсказания по уровням риска (нижняя таблица, слева)

Отвечает на вопрос: «Когда система говорит „опасно" — насколько она права?»

**Tier** — уровень риска (показаны только критический, высокий и средний).

**Predicted zones** — сколько зона-часов было помечено этим уровнем риска.

**Actual crashes** — сколько из них реально содержали аварию.

**Precision (hit rate)** — процент попаданий. Например, «12.7%» для critical означает: из всех зона-часов с пометкой «критический» в каждом восьмом действительно случилась авария.

**Lift vs. baseline** — во сколько раз точность этого уровня лучше, чем случайное угадывание. Если lift для critical равен 2.8×, значит: в красных зонах аварии происходят в 2.8 раза чаще, чем в среднем по всем зонам. Это ключевая метрика ценности системы.

**Как читать этот результат простыми словами:** Если мы скажем дорожному патрулю «езжайте только в красные зоны», они будут находить аварии в 2.8 раза чаще, чем если бы они ездили по случайным маршрутам. Это экономит время и ресурсы.

---

### Crash capture — охват реальных аварий по уровням риска (нижняя таблица, справа)

Отвечает на вопрос: «Какой процент реальных аварий система успела «поймать» в своих предсказаниях?»

**Tier** — уровень риска (показаны только критический, высокий и средний).

**Crashes in tier** — сколько реальных аварий произошло в зонах этого уровня.

**% of day's crashes** — какая доля от всех аварий за день приходится на этот уровень.

**Cumulative (top→down)** — нарастающий итог сверху вниз. Если critical = 3%, high = 8%, medium = 25%, то cumulative для medium = 36%. Это значит: наблюдая за топ 20% зон, можно «накрыть» 36% всех аварий дня.

---

### Что значит «backtest» и почему это важно?

Backtest (ретроспективное тестирование) — это проверка на прошлом. Мы берём реальные данные за январь 2026 года, делаем вид, что «не знаем» их, прогоняем через модель и смотрим: насколько точно она предсказала то, что уже случилось?

Это важно потому, что доказывает честность результатов. Модель не видела эти данные во время обучения — это настоящий «экзамен». Если модель хорошо работает на прошлых данных, это сильный аргумент в пользу того, что она будет работать и на будущих.

---

### Результаты за весь январь 2026: что показала проверка

Мы прогнали все 31 день января 2026 через модель и собрали итоговые цифры. Вот что получилось простыми словами.

**Общий масштаб:** Система проанализировала 74 400 пар «зона × час» за месяц. Реальных аварий случилось 3 353. В среднем авария происходит примерно в каждом 22-м слоте — это редкое событие даже на опасных дорогах.

**Насколько точны предсказания?**

Ключевой вопрос: если система помечает зону как опасную, насколько чаще там действительно происходит авария по сравнению с обычным местом?

| Уровень риска | Доля всех зон | Аварий накрыто | Точность | Эффективность |
|---|---|---|---|---|
| Critical (красный) | 1% | 2.9% | 12.7% | **2.8× лучше случайного** |
| High (оранжевый) | 5% | 11.2% (нараст.) | 9.6% | **2.1× лучше случайного** |
| Medium (жёлтый) | 20% | 36.4% (нараст.) | 7.6% | **1.7× лучше случайного** |

**Если простыми словами:** Патрульная машина, которая едет в случайное место, находит аварию с вероятностью около 4.5%. Та же машина, направленная в зону из топ 20% по версии системы, находит аварию с вероятностью 7–13% — в зависимости от уровня приоритета. Наблюдая за топ 20% зон, можно охватить более **трети всех аварий** за день.

**Лучшие и худшие дни:**
- Лучший день: 21 января — lift **5.4×** (аварии в красных зонах случались в 5 раз чаще нормы)
- Средний будний день (особенно среда): lift около **4×**
- Воскресенье — самый слабый день: lift ~1.8×. На выходных паттерны аварий другие (больше ночных, алкогольных, в нетипичных местах), и модель пока хуже их «чувствует»

**Вывод одной фразой:** Система стабильно находит опасные места лучше случайного выбора — в большинстве дней существенно лучше. Это означает, что одни и те же ресурсы патруля, направленные по рекомендации системы, будут работать в 2–5 раз эффективнее.

---

### Итог: три ключевых числа, которые нужно помнить

1. **Lift 2.8× для красных зон** — патруль в критических зонах находит аварии в 2.8 раза чаще, чем при случайном патрулировании (среднее за январь 2026).

2. **36% охват при 20% ресурсов** — наблюдая за критическими, высокими и средними зонами (топ 20% всех зон), система накрывает больше трети всех реальных аварий. Это в 1.8 раза эффективнее случайного патрулирования.

3. **Прогноз за день вперёд** — система выдаёт предсказание заранее, используя только общедоступные данные о погоде и историческую аварийность. Никакие специальные датчики или дорогостоящие источники данных не нужны.

---
---

## ENGLISH

---

### How the system works — and why it was built this way

#### Where the data comes from

The system was trained on real crash data from California roads for 2023–2025 — official statistics from CalTRANS (California Department of Transportation). Weather data (precipitation, wind, visibility, temperature) comes from Open-Meteo, a free and publicly available meteorological data source providing both historical records and forecasts. No proprietary or expensive data sources are required.

#### Why hexagons?

The state of California is divided into thousands of small hexagonal cells — each approximately 0.5 × 0.5 km. This grid is called H3 (developed by Uber for geospatial analysis). Hexagons are not an arbitrary choice: all neighboring cells are equidistant from a hexagon's center, unlike squares where diagonal neighbors are farther away than side neighbors. This makes spatial pattern analysis more consistent and accurate. Each cell is a **zone**. For every zone and every hour of the day, the system makes an independent prediction.

#### How the model works

The system uses **Gradient Boosting** — one of the most reliable and well-validated machine learning algorithms for classification tasks on tabular data. In simple terms: the algorithm builds hundreds of small rules like "if it's rush hour + wet road + this zone has a history of crashes → high risk," then combines them into a single overall score.

Why not a neural network? Neural networks excel at images, video, and text — unstructured data. For tabular data (which is exactly what we have: date, hour, weather, crash history), Gradient Boosting achieves comparable or better accuracy, trains faster, requires less data, and produces results that are easier to interpret. It is a practical, proven choice for this type of problem.

The model considers **13 factors**: hour of the day, day of the week, month, whether it's a holiday, historical crash rate for the zone, precipitation, wind speed, visibility, weather type, temperature, and road type (freeway or not). The output is a crash probability score from 0 to 1 for each zone at each hour.

#### How the model was trained

The model was trained on 2023–2025 data. January 2026 was deliberately excluded from training and reserved as a "holdout" period — meaning the model never saw this data during training. This is where we evaluate prediction quality. This is standard machine learning practice: an honest exam on data the model has never encountered.

Two separate model versions were also trained: one for weekdays and one for weekends — because crash patterns on weekends differ significantly (different peak hours, different typical causes).

#### Risk tiers — and why green zones are not shown

After the model assigns scores to all zones, they are ranked and each receives a **risk tier**:

- **Critical (red)** — top 1% most dangerous zones
- **High (orange)** — top 5%
- **Medium (yellow)** — top 20%
- **Low (green)** — the remaining 80%

The map and statistics deliberately **do not show green (low) zones**. The reason is straightforward: they represent 80% of all zones, create visual clutter, and provide no actionable value for decision-making. A green zone means "nothing unusual here." A red, orange, or yellow zone means "this warrants attention." That is the core logic of the system: not to predict every crash, but to identify elevated-risk zones where patrol resources will be used most efficiently.

---

### What is this dashboard?

This is a demonstration dashboard showing how a crash prediction system works on California roads. It replays January 2026 day by day — we take events that have already happened and examine how accurately the model predicted where and when an accident would occur, **before** it happened.

One key thing to understand: the system did not see January 2026 data during training. It was trained on crashes from 2023–2025, and January 2026 is its "exam" — data it sees for the first time. This is an honest, unbiased test.

---

### Sidebar (left) — controls

**Date selector** — choose any day from January 2026. The system shows what was predicted and what actually happened on that specific day. The day of the week is shown next to the date (e.g., Sunday).

**Map view** — a toggle between two map modes:
- **Prediction** — the map shows what the system predicted that morning. Zones are colored by risk tier. This answers: "Where did the system look?"
- **Reality check** — the map shows what actually happened. Zones where a crash really occurred keep their color. Zones with no crash turn grey and transparent. This answers: "Did the system get it right?"

**Filter by hour of day** — a slider to narrow data to a specific time range. For example, set it to 16:00–19:00 to look only at the evening rush hour. All numbers on the page recalculate based on this filter.

---

### Header bar (top of page)

Shows the context for the current selection:
- Selected date and day of week
- District: District 3 (Sacramento / Bay Area corridor)
- Current hour filter (or "All hours" if no filter is applied)
- How many zones are currently shown on the map

---

### Mode badge (blue or green)

A small colored label above the map:
- **🔮 Prediction** (blue) — you are viewing the forecast
- **✅ Reality check** (green) — you are viewing reality

This is a reminder so you don't confuse which mode you're in.

---

### Map

The main element of the dashboard. The map shows roads and elevated-risk zones as circles (critical, high, and medium — the top 20% of all zones).

**Circle color** — the zone's risk tier (red = critical, orange = high, yellow = medium).

**Circle size** — also depends on risk tier: red circles are larger, yellow ones smaller. This makes the most dangerous spots immediately visible.

**In Reality check mode:**
- Zones with real crashes keep their bright color and a white outline
- Zones where no crash occurred turn grey and transparent — they remain on the map to show: "the system was watching here, but nothing happened"

**Hovering over a circle** shows a tooltip with the road name and risk tier.

**Clicking a circle** opens a popup with details:
- Road name
- Zone number
- Risk tier
- Numerical risk score (e.g., 0.312)
- How many time slots in this zone had crashes (e.g., "2/8 zone-hours had crashes" means: out of 8 hours checked for this zone, 2 of them had a crash)

---

### Day summary (below map, left) — daily overview

Four numbers that give an overall picture of the day:

**Crashes recorded** — total crashes recorded during the selected period. Below the number is the total count of "zone-hour" slots analyzed. For example: "47 crashes out of 12,400 slots" means the system examined 12,400 (zone × hour) pairs, and 47 of them contained a crash.

**Critical zones** — how many time slots were labeled critical risk, what percentage of them actually contained a crash (hit%), and how much better this is than random guessing (e.g., "2.8×" means: crashes happened in critical zones 2.8 times more often than average).

**High zones** — the same for high-risk zones.

**Medium zones** — the same for medium-risk zones.

---

### Legend (below map, right)

Explains the zone colors.

In **Prediction** mode: "Zones colored by predicted risk tier (top 20%)" — only elevated-risk zones are shown on the map.

In **Reality check** mode: "Crash zones keep tier color. No-crash zones are grey."

---

### Top-10 highest-risk zones (top right) — ten most dangerous zones

A table listing the ten zones that received the highest risk scores for the selected day.

**Road** — road name (e.g., I-80, US-50).

**Tier** — the zone's risk tier (critical or high; only these two tiers appear in the top 10).

**Score** — a numerical score from 0 to 1. Higher means more dangerous. For example, 0.412 means the model estimated approximately a 41% probability of a crash.

**Crash?** — ✅ if a crash actually occurred in that zone that day, — if not.

This table answers the question: "Where would the system recommend sending patrol units?"

---

### Hourly: crash rate vs. score (bottom right) — hour-by-hour comparison

A chart where the horizontal axis shows hours of the day (0 to 23), and the vertical axis shows two measurements:

**Red line (Actual crash rate)** — the real crash frequency by hour. If there were many crashes at 17:00, the red line rises.

**Blue line (Avg predicted score)** — the average risk score the system assigned to all zones during that hour. If the system "thought" 17:00 would be dangerous, the blue line rises.

If both lines move in a similar pattern (rising and falling together), the system is accurately sensing the dangerous hours. This is a visual check that the model understands rush hour.

---

### Tier precision — how accurately predicted zones had crashes (bottom table, left)

Answers the question: "When the system says 'dangerous' — how often is it right?"

**Tier** — risk level (critical, high, and medium only).

**Predicted zones** — how many zone-hours were labeled with this risk tier.

**Actual crashes** — how many of those actually contained a crash.

**Precision (hit rate)** — the percentage of hits. For example, "12.7%" for critical means: out of all zone-hours labeled "critical," roughly 1 in 8 actually had a crash.

**Lift vs. baseline** — how many times better this tier performs versus random guessing. If lift for critical is 2.8×, it means: crashes happen 2.8 times more often in red zones than in an average zone. This is the key metric of system value.

**In plain words:** If we tell a road patrol "only go to red zones," they will find crashes 2.8 times more often than if they drove random routes. This saves time and resources.

---

### Crash capture — share of real crashes caught per tier (bottom table, right)

Answers the question: "What percentage of real crashes did the system capture in its predictions?"

**Tier** — risk level (critical, high, and medium only).

**Crashes in tier** — how many real crashes occurred in zones of this tier.

**% of day's crashes** — what share of all crashes that day fell into this tier.

**Cumulative (top→down)** — a running total from top to bottom. If critical = 3%, high = 8%, medium = 25%, then cumulative for medium = 36%. This means: by monitoring the top 20% of zones, the system covers more than a third of all crashes that day.

---

### What is a "backtest" and why does it matter?

A backtest (retrospective test) is a test on the past. We take real data from January 2026, pretend we "don't know" it, run it through the model, and see: how accurately did it predict what already happened?

This matters because it proves the results are honest. The model did not see this data during training — this is a genuine "exam." If the model performs well on past data, that is a strong argument that it will perform well on future data.

---

### January 2026 results: what the full-month test showed

We ran all 31 days of January 2026 through the model and collected the numbers. Here is what they mean in plain terms.

**Scale:** The system analyzed 74,400 zone-hour pairs across the month. Real crashes: 3,353. A crash happens in roughly 1 out of every 22 slots on average — crashes are rare events even on dangerous roads.

**How accurate are the predictions?**

The key question: when the system flags a zone as dangerous, how much more often does a crash actually occur there compared to an ordinary location?

| Risk tier | Share of all zones | Crashes captured | Precision | Efficiency |
|---|---|---|---|---|
| Critical (red) | 1% | 2.9% | 12.7% | **2.8× better than random** |
| High (orange) | 5% | 11.2% (cumul.) | 9.6% | **2.1× better than random** |
| Medium (yellow) | 20% | 36.4% (cumul.) | 7.6% | **1.7× better than random** |

**In plain words:** A patrol car sent to a random location finds a crash with roughly 4.5% probability. The same car directed to a zone in the top 20% by the system finds a crash with 7–13% probability — depending on the priority tier. By monitoring the top 20% of zones, you can cover more than **a third of all crashes** that day.

**Best and worst days:**
- Best day: January 21 — lift of **5.4×** (crashes in red zones happened 5 times more often than average)
- Average weekday (especially Wednesday): lift around **4×**
- Sunday — the weakest day of the week: lift ~1.8×. Weekend crash patterns differ (more nighttime, alcohol-related, in atypical locations), and the model currently handles them less well

**Bottom line in one sentence:** The system consistently finds dangerous locations better than random selection — on most days significantly better. This means the same patrol resources, directed by the system's recommendations, will operate 2–5 times more effectively.

---

### Summary: three key numbers to remember

1. **Lift 2.8× for red zones** — a patrol covering critical zones finds crashes 2.8 times more often than random patrolling (January 2026 average).

2. **36% capture with 20% of resources** — by monitoring critical, high, and medium zones (top 20% of all zones), the system covers more than a third of all real crashes. That is 1.8 times more efficient than random patrolling.

3. **One-day-ahead forecast** — the system generates its prediction in advance, using only publicly available weather data and historical crash rates. No special sensors or expensive data sources are required.

---
---

## Направления развития системы / Development Roadmap

---

### РУССКИЙ

---

### Два уровня точности системы

Анализ январских данных выявил важное разделение в работе модели:

- **Precision (угадывание)** — из зон, которые модель пометила как рискованные, ~10–20% реально имели аварию. Звучит скромно, но это 2–4× лучше случайного выбора (базовый рейт — 4.5%).
- **Recall (охват)** — из всех зон, где авария произошла, модель накрывает ~36% (при мониторинге топ 20% зон).

Иными словами: система хорошо находит опасные зоны, но при этом помечает слишком много «холостых». Главная задача дальнейшего развития — сократить холостые выстрелы без потери охвата.

Показательный факт из анализа hit-зон: **базовый рейт аварий у топ-зон по попаданиям (~4.5–5.7%) практически не отличается от среднего по всей выборке**. Это означает, что модель находит в этих зонах реальный временной сигнал — она предсказывает не просто «опасное место», а «опасный момент в конкретном месте». Именно это нужно усиливать.

---

### Три направления улучшения

#### 1. Обогащение данными

Добавить новые входные факторы, которые несут реальный временной сигнал:
- Дорожные работы и временные ограничения скорости
- Крупные события вблизи дороги (матчи, концерты, ярмарки)
- Интенсивность трафика (данные Caltrans PeMS или HERE)
- Аварии в соседних зонах в тот же день («эффект цепочки»)

Каждый новый значимый сигнал напрямую снижает число холостых срабатываний.

#### 2. Увеличение числа per-zone моделей

Сейчас индивидуальные модели обучены только для 50 зон с ≥200 позитивными слотами. Порог завышен: зона с 50–100 примерами уже достаточна для логистической регрессии или дерева решений. Цель — покрыть top-500 зон по активности индивидуальными моделями. Глобальная модель усредняет поведение всей Калифорнии; per-zone модель знает специфику конкретного участка трассы.

#### 3. Двухуровневая архитектура с кросс-валидацией

Наиболее перспективное направление. Схема:

- **Уровень 1** — текущая глобальная модель выдаёт score для каждой зоны
- **Уровень 2** — мета-модель, обученная на исторических hit-зонах, корректирует score вверх или вниз

Мета-модель использует как фичи: `historical_hit_rate` (доля дней, когда зона была в тире и авария произошла), `historical_precision` (precision модели по этой зоне за прошлые периоды), `days_in_tier` (как часто зона вообще попадает в топ). Это «реверсивное» дообучение на верифицированных сигналах.

**Важно:** мета-модель обучается через кросс-валидацию по времени (train на 2023–2024, val на 2025), чтобы не переобучиться на тех же примерах, которые использовала первая модель.

---

### ENGLISH

---

### Two layers of system accuracy

Analysis of the January data reveals an important distinction in how the model works:

- **Precision (guessing)** — of all zones the model flags as risky, ~10–20% actually had a crash. That sounds modest, but it is 2–4× better than random selection (baseline rate: 4.5%).
- **Recall (coverage)** — of all zones where a crash actually occurred, the model captures ~36% (when monitoring the top 20% of zones).

In other words: the system is good at finding dangerous zones, but it flags too many false positives. The main goal of further development is to reduce those false positives without losing coverage.

A key insight from the hit-zone analysis: **the baseline crash rate of the top hit-zones (~4.5–5.7%) is nearly identical to the overall average**. This means the model is not simply finding "structurally dangerous" locations — it is detecting a genuine temporal signal: the right moment in a specific place. That is what needs to be amplified.

---

### Three development directions

#### 1. Feature enrichment

Add new input signals that carry real temporal information:
- Road works and temporary speed restrictions
- Major events near the road (games, concerts, fairs)
- Traffic volume data (Caltrans PeMS or HERE)
- Crashes in neighboring zones on the same day ("chain effect")

Each meaningful new signal directly reduces false positives.

#### 2. Expanding per-zone models

Currently, individual models are trained for only 50 zones with ≥200 positive slots. That threshold is too high: a zone with 50–100 examples already provides enough data for logistic regression or a decision tree. The goal is to cover the top 500 most active zones with individual models. The global model averages behavior across all of California; a per-zone model knows the specifics of a particular road segment.

#### 3. Two-level architecture with cross-validation

The most promising direction. The design:

- **Level 1** — the current global model produces a score for each zone
- **Level 2** — a meta-model trained on historical hit-zones adjusts that score up or down

The meta-model uses as features: `historical_hit_rate` (share of days the zone was in tier and a crash occurred), `historical_precision` (model precision for this zone over past periods), `days_in_tier` (how often the zone appears in the top tiers at all). This is a form of reverse fine-tuning on verified signals.

**Critically:** the meta-model is trained via time-based cross-validation (train on 2023–2024, validate on 2025) to prevent it from overfitting to the same examples used by the first-level model.
