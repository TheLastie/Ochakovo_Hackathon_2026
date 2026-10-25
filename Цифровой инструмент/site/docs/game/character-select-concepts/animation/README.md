# Действия персонажей

Создано 23 октября 2026 в Google Flow, Omni 1.1 Flash. Исходные изображения — `../art/`. Четыре ролика по 6 секунд, 720×1280, 24 fps. Концептуальная анимация, а не технологическая инструкция. Имена, лица и образы вымышлены.

Проект Flow: https://flow.google.com/project/087bb27c-b19b-4255-84ad-d21fbb7f2984

| Роль | Действие | ID результата |
|---|---|---|
| chemist | Поднимает колбу, рассматривает жидкость, опускает руку | 9ed132ba-4f9e-4d4a-a5b5-c99393e017c0 |
| bottling | Поднимает бутылку, проверяет её, смотрит на планшет | bc929005-e1ab-4b8a-9358-e6061a499761 |
| machinery | Смотрит на планшет, нажимает на экран, поднимает взгляд | 21376ff2-16f6-4bee-81f3-fabf022aa8f5 |
| brewer | Поднимает образец к свету и рассматривает цвет | fbc85c77-8eba-41f8-8378-0a18efca256d |

## Промпты

Общий запрос: “Full-body 6-second animation video of the attached character, preserving exact identity, face, clothes, tools and 3D style. Locked camera, full body with margins. Natural articulated arms, hands, eyes and head, blink, feet planted. No whole-image swaying, morphing, extra fingers, new props, text or camera movement. Solid uniform chroma key green background #00FF00, no floor, shadows or green spill. Silent. Vertical 9:16, one output.”

- Chemist: “She raises the flask to eye level, gently rotates it to inspect the amber liquid, follows it with her eyes, gives a small nod, then lowers it and returns to the starting pose.”
- Bottling: “The operator carefully raises his bottle, tilts it slightly to inspect fill level and label, glances down at the tablet, nods and returns to starting pose.”
- Machinery: “The technician looks down at her handheld device, presses its controls with one finger, checks the reading, looks up and returns to starting pose.”
- Brewer: “The brewer raises his sample to inspect its amber color, gently swirls it, glances at his notes and returns to starting pose.”

## Встраивание

Исходники Flow сохранены в `source/`. `scripts/prepare-character-animations.py --ffmpeg /path/to/ffmpeg` убирает зелёный фон, начальные кадры с переходом фона и звук; сохраняет RGB над монохромной альфа-маской внутри H.264. Размер для сайта 432×1536 (видимая половина 432×768), четыре файла суммарно около 2,4 МБ. Маска восстанавливается небольшим WebGL-шейдером в `web/public/game-menu/characters/animation.js`. Такой формат не зависит от поддержки VP9 alpha в Safari. Реальный Safari ещё не проверен.

Действие воспроизводится один раз при каждом выборе, в том числе повторном нажатии на выбранную роль. Последний кадр остаётся на экране. При скрытии вкладки/игрового блока видео приостанавливается. При reduced-motion используется статичная исходная иллюстрация; сбой видео или WebGL также оставляет иллюстрацию. Видимой кнопки паузы нет по запросу пользователя. Это видеослой экрана выбора, не 3D-риг персонажа в Unity; намеренно пустая сцена Unity не изменена.

## Ограничения

Генерация даёт небольшие изменения позы и предметов относительно исходного PNG, особенно при переходе к движению. Это первый вариант осмысленных действий для просмотра на сайте. Перед финальным выпуском нужны редакционная оценка движений/инструментов и проверка профильным специалистом, а также проверка Safari/iOS на устройстве.

Проверено в Chrome: каждый из четырёх роликов доходит до последнего кадра, повторный выбор запускает действие заново, альфа-маска показывает фон интерфейса, reduced-motion оставляет PNG без видео, надпись паузы отсутствует. Проверен полный путь заставка → выбор → Unity, звук, возврат и сохранение роли, мобильная ширина 390 px и обработка ошибки Unity. JavaScript-ошибок нет. Сборка TypeScript и Django system check проходят. Результат также открыт и осмотрен в пользовательском Chrome на `http://127.0.0.1:8000/#shift`.
