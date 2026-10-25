# Ochakovo Factory World

Unity **6000.3.22f1**, Built-in Render Pipeline, WebGL.

Основная сцена — `Assets/Scenes/Brewhouse.unity`: сохранённая производственная локация с прогулкой, персонажами, компьютерной головоломкой и проверкой pH для химика-лаборанта. Откройте сцену и нажмите Play.

Инструкции по запуску сайта и сборке — [README проекта](../README.md). Подробности игры — [docs/game/README.md](../docs/game/README.md).

Библиотека модулей — `Assets/FactoryKit/Prefabs/`, наборы Kenney CC0 — `Assets/ThirdParty/Kenney/`. Просмотровые сцены `Assets/FactoryKit/Scenes/AssetGallery.unity`, `AssemblyExample.unity` и ProductShowcase не заменяют основную сцену сайта. Исходники Blender и лицензии — в `../art/`; каталог — [docs/game/asset-library/README.md](../docs/game/asset-library/README.md).

Обычная сборка использует сохранённую сцену. Команды генератора Create Production Panorama / CreateAndBuild пересоздают композицию: не используйте их после ручных изменений без намерения заменить сцену.
