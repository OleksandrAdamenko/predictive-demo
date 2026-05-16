# RoadIQ — CalTRANS Crash Prediction Demo

Backtest replay dashboard for the CalTRANS District 3 pilot.
Replays January 2026 day by day, showing predicted risk zones vs. actual crashes.

---

# Руководство по дашборду CalTRANS / CalTRANS Dashboard Guide

---

## РУССКИЙ

---

### Что такое этот дашборд?

Это демонстрационный дашборд, который показывает, как работает система предсказания ДТП на дорогах Калифорнии. Он воспроизводит январь 2026 года день за днём — мы берём уже прошедшие события и смотрим: насколько точно модель предсказала, где и когда случится авария, ещё **до** того, как она произошла.

Важно понимать одну ключевую вещь: система не видела данные за январь 2026 года во время обучения. Она обучалась на авариях 2023–2025 годов, а январь 2026-го — это «экзамен», данные которого модель видит впервые. Это честная проверка.

---

### Как устроена система в целом?

Калифорния разбита на тысячи маленьких шестиугольных клеток (примерно 0.5 × 0.5 км каждая). Каждая такая клетка — это **зона**. Для каждой зоны и каждого часа суток система вычисляет: насколько вероятна авария здесь, в это время?

Для этого она смотрит на 13 факторов: час дня, день недели, месяц, праздник или нет, историческая аварийность этой зоны, осадки, скорость ветра, видимость, тип погоды, температура, тип дороги (хайвей или нет).

Получается оценка риска от 0 до 1 (например, 0.23 означает «23% вероятность аварии»). Затем все зоны ранжируются, и каждой присваивается **уровень риска (tier)**:

- **Critical (красный)** — топ 1% самых опасных зон в этот час
- **High (оранжевый)** — топ 5%
- **Medium (жёлтый)** — топ 20%
- **Low (зелёный)** — остальное (нижние 80%)

---

### Боковая панель (слева) — элементы управления

**Логотип CalTRANS** — напоминает, для кого сделана система: Калифорнийский департамент транспорта.

**Выбор даты** — выбираете любой день из января 2026 года. Система показывает, что предсказывалось и что происходило в реальности именно в этот день. Рядом с датой указан день недели (например, Saturday — суббота).

**Map view** — переключатель между двумя режимами карты:
- **Prediction** — карта показывает то, что система предсказала утром того дня. Зоны окрашены по уровню риска. Это ответ на вопрос: «Куда смотрела система?»
- **Reality check** — карта показывает, что случилось на самом деле. Зоны, где авария действительно произошла, сохраняют свой цвет. Зоны, где аварии не было, становятся серыми. Это ответ на вопрос: «Угадала ли система?»

**Show 'low' tier zones** — галочка, которая включает/выключает отображение зелёных зон (низкий риск). По умолчанию они скрыты, потому что их очень много и они «замусоривают» карту. Обычно интереснее смотреть только на зоны с высоким риском.

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

Главный элемент дашборда. На карте показаны дороги и шестиугольные зоны в виде кружков.

**Цвет кружка** — уровень риска зоны (красный = критический, оранжевый = высокий, жёлтый = средний, зелёный = низкий).

**Размер кружка** — тоже зависит от уровня риска: красные кружки крупнее, зелёные — мельче. Это позволяет сразу визуально выделить самые опасные места.

**В режиме Reality check:**
- Зоны с реальными авариями сохраняют яркий цвет и белую обводку
- Зоны без аварий становятся серыми и прозрачными

**При наведении на кружок** появляется подсказка с названием дороги и уровнем риска.

**При клике на кружок** открывается всплывающее окно с подробностями:
- Название дороги
- Номер зоны
- Уровень риска
- Числовая оценка риска (например, 0.312)
- Сколько временных слотов в этой зоне имели аварии (например, «2/8 zone-hours had crashes» означает: из 8 проверяемых часов в этой зоне в 2 из них случилась авария)

**Легенда на карте** (левый нижний угол карты) — объяснение цветов. В режиме Reality check добавляется серый кружок «No crash».

---

### Day summary (под картой, слева) — итоги дня

Четыре числа, которые дают общую картину дня:

**Crashes recorded** — сколько всего зафиксировано аварий за выбранный период. Под числом написано, сколько всего «зона-час» слотов было проанализировано. Например: «47 аварий из 12,400 слотов» означает, что система смотрела на 12,400 пар «зона × час» и в 47 из них произошла авария.

**Critical zones** — сколько временных слотов было помечено как критический риск, и какой процент из них действительно содержал аварию (hit%), и насколько это лучше случайного угадывания (например, «2.5×» означает: в критических зонах аварии происходили в 2.5 раза чаще, чем в среднем по всем зонам).

**High zones** — то же самое для зон высокого риска.

**Medium zones** — то же самое для зон среднего риска.

---

### Legend (под картой, справа) — легенда

Объяснение цветов зон. Дублирует легенду на карте, но находится рядом с элементами управления, чтобы было удобнее.

В режиме **Prediction**: «Zones colored by predicted risk tier» (зоны окрашены по предсказанному уровню риска).

В режиме **Reality check**: «Crash zones keep tier color. No-crash zones are grey» (зоны с авариями сохраняют цвет. Зоны без аварий — серые).

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

Столбцы:

**Tier** — уровень риска.

**Predicted zones** — сколько зона-часов было помечено этим уровнем риска.

**Actual crashes** — сколько из них реально содержали аварию.

**Precision (hit rate)** — процент попаданий. Например, «11.2%» для critical означает: из всех зона-часов с пометкой «критический» в каждом 9-м действительно случилась авария.

**Lift vs. baseline** — во сколько раз точность этого уровня лучше, чем случайное угадывание. Baseline — это средняя аварийность по всем зонам (обычно ~0.3–0.4%). Если lift для critical равен 2.5×, значит: в красных зонах аварии происходят в 2.5 раза чаще, чем в среднем по всем зонам. Это ключевая метрика ценности модели.

**Как читать этот результат простыми словами:** Если мы скажем дорожному патрулю «езжайте только в красные зоны», они будут находить аварии в 2.5 раза чаще, чем если бы они ездили по случайным маршрутам. Это экономит время и ресурсы.

---

### Crash capture — охват реальных аварий по уровням риска (нижняя таблица, справа)

Отвечает на вопрос: «Какой процент реальных аварий система успела «поймать» в своих предсказаниях?»

Столбцы:

**Tier** — уровень риска.

**Crashes in tier** — сколько реальных аварий произошло в зонах этого уровня.

**% of day's crashes** — какая доля от всех аварий за день приходится на этот уровень.

**Cumulative (top→down)** — нарастающий итог сверху вниз. Например, если critical = 15% и high = 30%, то cumulative для high = 45%. Это значит: если смотреть только на красные и оранжевые зоны, можно «накрыть» 45% всех аварий за день.

**Как читать этот результат простыми словами:** Если дорожный патруль будет проверять только критические и высокие зоны (топ 5% всех зон), они смогут оказаться рядом с ~40–50% всех реальных аварий. Остальные 50–60% произошли в зонах, которые система оценила как «средний» или «низкий» риск — их тоже можно мониторить, но с меньшим приоритетом.

---

### Что значит «backtest» и почему это важно?

Backtest (ретроспективное тестирование) — это проверка на прошлом. Мы берём реальные данные за январь 2026 года, делаем вид, что «не знаем» их, прогоняем через модель и смотрим: насколько точно она предсказала то, что уже случилось?

Это важно потому, что доказывает честность результатов. Модель не видела эти данные во время обучения — это настоящий «экзамен». Если модель хорошо работает на прошлых данных, это сильный аргумент в пользу того, что она будет работать и на будущих.

---

### Результаты за весь январь 2026: что показала проверка

Мы прогнали все 31 день января 2026 через модель и собрали итоговые цифры. Вот что получилось простыми словами.

**Общий масштаб:** Система проанализировала 74 400 пар «зона × час» за месяц. Реальных аварий случилось 3 353. Это означает, что в среднем авария происходит примерно в каждом 22-м слоте — то есть это редкое событие даже на опасных дорогах.

**Насколько точны красные зоны (Critical)?**
В среднем за месяц: из каждых 100 зона-часов, помеченных как «критический», **12–13 действительно содержали аварию**. Это в **2.8 раза лучше**, чем случайное угадывание. В лучшие дни этот показатель достигал 5× и выше — модель работала очень чётко. В худшие дни (обычно воскресенья или дни с малым числом аварий) — около 1.5×.

**Если простыми словами:** представьте, что вы наугад отправляете патрульную машину в одну из 100 зон — она найдёт аварию с вероятностью ~4.5%. Если вы отправляете её в «красную» зону по совету системы — вероятность вырастает до ~12.7%. Это почти втрое лучше «угадайки».

**Сколько аварий «накрывает» система?**

| Уровень риска | Доля всех слотов | Доля накрытых аварий |
|---|---|---|
| Critical (красный) | 1% | 2.9% |
| Critical + High (красный + оранжевый) | 5% | 11.2% |
| + Medium (+ жёлтый) | 20% | 36.4% |
| Все зоны | 100% | 100% |

Смотря на топ 5% зон — красные и оранжевые — можно «накрыть» около **11% всех аварий** за день. Это может звучать скромно, но важен контекст: эти 5% зон находят в **2.2 раза больше** аварий, чем если бы патруль ехал по случайным 5% дорог.

**Важное наблюдение:** 64% аварий происходят в «зелёных» (низкий риск) зонах. Это не ошибка системы — это отражение реальности: большинство аварий случаются неожиданно, в обычных местах. Система не претендует на то, чтобы предсказать каждую аварию. Её ценность — в том, чтобы направить ресурсы туда, где риск *повышен*.

**Лучшие и худшие дни:**
- Лучший день: 21 января — система показала lift **5.4×** (аварии в красных зонах случались в 5 раз чаще нормы)
- Средний будний день (особенно среда): lift около **4×**
- Воскресенье — самый слабый день: lift ~1.8×. Это объяснимо: на выходных паттерны аварий другие (больше ночных, алкогольных, в нетипичных местах), и модель пока хуже их «чувствует»

**Вывод одной фразой:** Система работает — она стабильно находит опасные места лучше случайного выбора, в большинстве дней существенно лучше. Потенциал для улучшения тоже есть, особенно для выходных дней.

---

### Итог: три ключевых числа, которые нужно помнить

1. **Lift 2.8×** — патруль в красных зонах находит аварии в 2.8 раза чаще, чем при случайном патрулировании (среднее за январь 2026).

2. **11% охват при 5% ресурсов** — наблюдая только за критическими и высокими зонами (топ 5% всех зон), система накрывает 11% всех аварий. Это в 2.2 раза эффективнее случайного патрулирования.

3. **Прогноз за день вперёд** — система выдаёт предсказание заранее, используя только общедоступные данные о погоде и историческую аварийность. Никакие специальные датчики или дорогостоящие источники данных не нужны.

---
---

## ENGLISH

---

### What is this dashboard?

This is a demonstration dashboard showing how a crash prediction system works on California roads. It replays January 2026 day by day — we take events that have already happened and examine how accurately the model predicted where and when an accident would occur, **before** it happened.

One key thing to understand: the system did not see January 2026 data during training. It was trained on crashes from 2023–2025, and January 2026 is its "exam" — data it sees for the first time. This is an honest, unbiased test.

---

### How does the system work overall?

California is divided into thousands of small hexagonal cells (roughly 0.5 × 0.5 km each). Each cell is a **zone**. For every zone and every hour of the day, the system calculates: how likely is a crash here, at this time?

To do this, it looks at 13 factors: hour of the day, day of the week, month, whether it's a holiday, historical crash rate for that zone, precipitation, wind speed, visibility, weather type, temperature, and road type (freeway or not).

This produces a risk score from 0 to 1 (e.g., 0.23 means "23% probability of a crash"). All zones are then ranked, and each is assigned a **risk tier**:

- **Critical (red)** — top 1% most dangerous zones at that hour
- **High (orange)** — top 5%
- **Medium (yellow)** — top 20%
- **Low (green)** — the remaining 80%

---

### Sidebar (left) — controls

**CalTRANS logo** — a reminder of who this system is built for: the California Department of Transportation.

**Date selector** — choose any day from January 2026. The system shows what was predicted and what actually happened on that specific day. The day of the week is shown next to the date (e.g., Saturday).

**Map view** — a toggle between two map modes:
- **Prediction** — the map shows what the system predicted that morning. Zones are colored by risk tier. This answers: "Where did the system look?"
- **Reality check** — the map shows what actually happened. Zones where a crash really occurred keep their color. Zones with no crash turn grey. This answers: "Did the system get it right?"

**Show 'low' tier zones** — a checkbox that turns green (low-risk) zones on or off. By default they are hidden, because there are so many of them that they clutter the map. It's usually more useful to focus on high-risk zones only.

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

The main element of the dashboard. The map shows roads and hexagonal zones as circles.

**Circle color** — the zone's risk tier (red = critical, orange = high, yellow = medium, green = low).

**Circle size** — also depends on risk tier: red circles are larger, green ones smaller. This makes the most dangerous spots immediately visible.

**In Reality check mode:**
- Zones with real crashes keep their bright color and a white outline
- Zones with no crash turn grey and transparent

**Hovering over a circle** shows a tooltip with the road name and risk tier.

**Clicking a circle** opens a popup with details:
- Road name
- Zone number
- Risk tier
- Numerical risk score (e.g., 0.312)
- How many time slots in this zone had crashes (e.g., "2/8 zone-hours had crashes" means: out of 8 hours checked for this zone, 2 of them had a crash)

**Map legend** (bottom-left corner of the map) — explains the colors. In Reality check mode, a grey "No crash" dot is added.

---

### Day summary (below map, left) — daily overview

Four numbers that give an overall picture of the day:

**Crashes recorded** — total crashes recorded during the selected period. Below the number is the total count of "zone-hour" slots analyzed. For example: "47 crashes out of 12,400 slots" means the system examined 12,400 (zone × hour) pairs, and 47 of them contained a crash.

**Critical zones** — how many time slots were labeled critical risk, what percentage of them actually contained a crash (hit%), and how much better this is than random guessing (e.g., "2.5×" means: crashes happened in critical zones 2.5 times more often than average across all zones).

**High zones** — the same for high-risk zones.

**Medium zones** — the same for medium-risk zones.

---

### Legend (below map, right)

Explains the zone colors. Mirrors the map legend but is placed next to the controls for convenience.

In **Prediction** mode: "Zones colored by predicted risk tier."

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

Columns:

**Tier** — risk level.

**Predicted zones** — how many zone-hours were labeled with this risk tier.

**Actual crashes** — how many of those actually contained a crash.

**Precision (hit rate)** — the percentage of hits. For example, "11.2%" for critical means: out of all zone-hours labeled "critical," roughly 1 in 9 actually had a crash.

**Lift vs. baseline** — how many times better this tier performs versus random guessing. The baseline is the average crash rate across all zones (typically ~0.3–0.4%). If lift for critical is 2.5×, it means: crashes happen 2.5 times more often in red zones than in an average zone.

**In plain words:** If we tell a road patrol "only go to red zones," they will find crashes 2.5 times more often than if they drove random routes. This saves time and resources.

---

### Crash capture — share of real crashes caught per tier (bottom table, right)

Answers the question: "What percentage of real crashes did the system manage to 'capture' in its predictions?"

Columns:

**Tier** — risk level.

**Crashes in tier** — how many real crashes occurred in zones of this tier.

**% of day's crashes** — what share of all crashes that day fell into this tier.

**Cumulative (top→down)** — a running total from top to bottom. For example, if critical = 15% and high = 30%, then the cumulative for high = 45%. This means: by covering only red and orange zones, you can "capture" 45% of all crashes that day.

**In plain words:** If a road patrol monitors only critical and high zones (the top 5% of all zones), they can be present for ~40–50% of all real crashes. The remaining 50–60% occurred in zones the system rated as "medium" or "low" risk — these can still be monitored, but at lower priority.

---

### What is a "backtest" and why does it matter?

A backtest (retrospective test) is a test on the past. We take real data from January 2026, pretend we "don't know" it, run it through the model, and see: how accurately did it predict what already happened?

This matters because it proves the results are honest. The model did not see this data during training — this is a genuine "exam." If the model performs well on past data, that is a strong argument that it will perform well on future data.

---

### January 2026 results: what the full-month test showed

We ran all 31 days of January 2026 through the model and collected the numbers. Here is what they mean in plain terms.

**Scale:** The system analyzed 74,400 zone-hour pairs across the month. Real crashes: 3,353. This means a crash happens in roughly 1 out of every 22 slots on average — crashes are rare events even on dangerous roads.

**How accurate are the red (Critical) zones?**
On average across the month: out of every 100 zone-hours labeled "critical," **12–13 actually contained a crash**. That is **2.8 times better** than random guessing. On the best days this reached 5× and higher. On the weakest days (typically Sundays or low-crash days) it was around 1.5×.

**In plain words:** Imagine you send a patrol car to a random zone out of 100 — it finds a crash with roughly 4.5% probability. If you send it to a red zone based on the system's recommendation — the probability rises to ~12.7%. That is nearly three times better than guessing.

**How many crashes does the system "capture"?**

| Risk tier | Share of all slots | Share of crashes captured |
|---|---|---|
| Critical (red) | 1% | 2.9% |
| Critical + High (red + orange) | 5% | 11.2% |
| + Medium (+ yellow) | 20% | 36.4% |
| All zones | 100% | 100% |

By watching the top 5% of zones — red and orange — the system captures about **11% of all crashes** that day. That may sound modest, but context matters: these 5% of zones find **2.2 times more** crashes than a random 5% of roads would.

**An important observation:** 64% of crashes occur in "green" (low-risk) zones. This is not a system failure — it reflects reality: most crashes happen unexpectedly, in ordinary places. The system does not claim to predict every crash. Its value is in directing resources toward places where risk is *elevated*.

**Best and worst days:**
- Best day: January 21 — lift of **5.4×** (crashes in red zones happened 5 times more often than average)
- Average weekday (especially Wednesday): lift around **4×**
- Sunday — the weakest day of the week: lift ~1.8×. This is expected: weekend crash patterns differ (more nighttime, alcohol-related, in atypical locations), and the model currently handles them less well

**Bottom line in one sentence:** The system works — it consistently finds dangerous locations better than random selection, and on most days it does so by a significant margin. There is clear room to improve further, particularly for weekends.

---

### Summary: three key numbers to remember

1. **Lift 2.8×** — a patrol covering red zones finds crashes 2.8 times more often than random patrolling (January 2026 average).

2. **11% capture with 5% of resources** — by watching only critical and high zones (top 5% of all zones), the system captures 11% of all crashes. That is 2.2 times more efficient than random patrolling.

3. **One-day-ahead forecast** — the system generates its prediction in advance, using only publicly available weather data and historical crash rates. No special sensors or expensive data sources are required.
