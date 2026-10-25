"""Build an offline, searchable HTML catalog from real asset inventory and previews."""
from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/game/asset-library'
data=json.loads((DOC/'catalog.json').read_text())['assets']
product_file=DOC/'products/catalog.json'
if product_file.exists():data+=json.loads(product_file.read_text())['assets']
original_count=len(data)
for a in data:
    a['pack']='original';a['image']='thumbnails/'+a['id']+'.png'
    a['prefab']='Assets/FactoryKit/Prefabs/'+a['category']+'/'+a['id']+'.prefab'
for source,folder in [('factory','FactoryKit'),('city','CityIndustrial')]:
    source_path=ROOT/'tmp/factory-assets'/source
    target=DOC/'kenney-previews'/folder;target.mkdir(parents=True,exist_ok=True)
    models=ROOT/'OchakovoFactoryWorld/Assets/ThirdParty/Kenney'/folder/'Models'
    for f in sorted(models.glob('*.fbx')):
        image=source_path/'Previews'/(f.stem+'.png')
        if image.exists():shutil.copy2(image,target/image.name)
        elif not (target/(f.stem+'.png')).exists():raise FileNotFoundError(image)
        data.append(dict(id=f.stem,label=f.stem.replace('-',' '),category='Kenney',pack=source,image='kenney-previews/'+folder+'/'+f.stem+'.png',prefab='Assets/ThirdParty/Kenney/'+folder+'/Prefabs/'+f.stem+'.prefab'))

template='''<!doctype html>
<html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Библиотека производства — Очаково</title>
<style>
@font-face{font-family:Proxima;src:url(../../../brand/assets/fonts/ProximaNova-Regular.woff2)}
@font-face{font-family:Proxima;src:url(../../../brand/assets/fonts/ProximaNova-Bold.woff2);font-weight:700}
@font-face{font-family:Stratos;src:url(../../../brand/assets/fonts/Stratos-ExtraBold.woff2);font-weight:800}
*{box-sizing:border-box}body{margin:0;background:#fff;color:#151515;font:18px/1.45 Proxima,Arial,sans-serif}
main{max-width:1440px;margin:auto;padding:40px}header{border-top:6px solid #D50032;padding-top:22px}
.eyebrow{color:#D50032;font-weight:700;letter-spacing:.1em;text-transform:uppercase;font-size:14px}
h1,h2{font-family:Stratos,Proxima,sans-serif;line-height:1.03;font-weight:800;letter-spacing:-.03em}
h1{font-size:clamp(44px,6vw,88px);max-width:1000px;margin:16px 0 24px}h2{font-size:40px;margin:64px 0 20px}
p{max-width:850px}.lead{font-size:24px}.meta{color:#62625F}.hero{width:100%;display:block;background:#f6f5f2}
a{color:inherit;text-decoration-color:#D50032;text-underline-offset:4px}a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #032AB2;outline-offset:3px}
.links{display:flex;gap:24px;flex-wrap:wrap;margin:24px 0}.stats{display:flex;gap:40px;padding:28px 0;border-bottom:1px solid #dcdcd7}.stats b{font-family:Stratos;font-size:40px;display:block}
.controls{position:sticky;top:0;background:#fff;z-index:2;padding:16px 0;border-bottom:1px solid #dcdcd7}.packs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
button,select,input{font:inherit;min-height:44px;border:1px solid #dcdcd7;background:white;color:#151515;padding:9px 14px;border-radius:0}button{cursor:pointer}button[aria-pressed=true]{background:#D50032;border-color:#D50032;color:#fff}
.search{display:flex;gap:12px}.search input{flex:1;min-width:0}.search select{max-width:46%}
.count{margin:18px 0}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px}
article{border:1px solid #dcdcd7;min-width:0}article img{width:100%;height:210px;object-fit:contain;background:#F6F5F2;display:block}article .info{padding:18px}h3{margin:0 0 8px;font-size:22px;line-height:1.12}code{font-size:12px;word-break:break-all}.details{font-size:15px;color:#62625F;margin:8px 0}.copy{width:100%;margin-top:12px;font-size:15px}
.references,.surfaces{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.references img{width:100%;aspect-ratio:1.6;object-fit:cover}.references p{margin:10px 0}.surface{background:#f6f5f2;padding:18px}.surface img{width:100%;aspect-ratio:1;object-fit:cover}.surface h3{margin:12px 0 8px}.surface a{font-size:15px}
.note{padding:24px;background:#F6F5F2;border-left:4px solid #D50032}.unity{width:100%;background:#f6f5f2;display:block}
footer{margin-top:64px;padding:24px 0;border-top:1px solid #dcdcd7;color:#62625F;font-size:16px}
@media(max-width:1000px){.grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:720px){main{padding:20px}.grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.references,.surfaces{grid-template-columns:repeat(2,minmax(0,1fr))}.stats{gap:24px;flex-wrap:wrap}article img{height:160px}.lead{font-size:20px}h2{font-size:32px}.packs button{font-size:15px}.info{padding:12px!important}}
@media(max-width:420px){.references,.surfaces{grid-template-columns:1fr}.search{flex-direction:column}.search select{max-width:100%}}
</style>
<main><header><div class="eyebrow">Очаково · Unity · 24 октября 2026</div>
<h1>Из чего соберём производство</h1>
<p class="lead">Модульная библиотека для варочного цеха, лаборатории, линии розлива и склада. С отдельными элементами солодовни и винодельни.</p>
<div class="links"><a href="#catalog">Смотреть модели ↓</a><a href="#materials">Материалы и фактуры</a><a href="README.md">Как работать в Unity</a><a href="unity-validation.json">Проверка импорта</a></div>
</header><img class="hero" src="factory-kit-preview.png" alt="Пример цеха, собранный из моделей библиотеки и отрендеренный в Blender">
<div class="stats"><div><b>__ORIGINAL_COUNT__</b>собственных моделей</div><div><b>180</b>моделей Kenney · CC0</div><div><b>6</b>наборов PBR-текстур</div><div><b>__PREFAB_COUNT__</b>готовых prefab</div></div>
<p class="meta">Выше — рендер Blender. Это пример сочетания модулей; планировка конкретного филиала будет собираться отдельно. Подлинный логотип компании добавлен отдельной вывеской.</p>
<h2 id="products">Продукция «Очаково»</h2><p>Квас «Очаковский» в ПЭТ 0,5 л и безалкогольный «Мохито Освежающий» в банке 0,45 л. Собственные объёмные модели с настоящей графикой упаковки, отдельными материалами и двумя уровнями детализации.</p><img class="unity" src="products/products-preview.png" alt="Трёхмерные модели кваса Очаковский и Мохито Освежающий — рендер Blender"><p><a href="products/README.md">Модели, источники и работа в Unity</a> · <a href="products/unity-products-preview.png">Кадр из Unity</a></p>
<h2 id="catalog">Модели для сборки</h2>
<div class="controls"><div class="packs" role="group" aria-label="Набор моделей"><button data-pack="original" aria-pressed="true">Наш набор · __ORIGINAL_COUNT__</button><button data-pack="factory" aria-pressed="false">Kenney Factory · 143</button><button data-pack="city" aria-pressed="false">Промтерритория · 37</button></div><div class="search"><input id="search" type="search" aria-label="Поиск модели" placeholder="Название, категория или ID модели"><select id="category" aria-label="Категория"></select></div></div>
<p class="count" role="status" aria-live="polite"></p><div class="grid" id="models"></div>
<h2 id="materials">Материал ощущается по-разному</h2>
<p>Бесшовные карты цвета, нормалей и шероховатости. В Unity металличность и гладкость упакованы в одну RGBA-карту для Standard shader. Фактура остаётся спокойной: чистая нержавейка, окрашенный металл, промышленная плитка, дерево, картон и резина.</p>
<div class="surfaces" id="surfaces"></div>
<p class="note">Собственные модели имеют текстурные материалы и UV-развёртку. У готовых наборов Kenney сохранены авторские цветовые палитры; добавлен отдельный UV-канал с мелким рельефом покрытия. Новые квас и «Мохито» используют настоящие изображения упаковки. Однотонные PET_Bottle_Prototype и Can_Prototype остаются отдельными заготовками.</p>
<h2>Так это выглядит в Unity</h2><img class="unity" src="unity-assembly-preview.png" alt="Настоящий кадр из тестовой сцены Unity с текстурированными материалами и официальной вывеской">
<p>Откройте <code>Assets/FactoryKit/Scenes/AssemblyExample.unity</code> для просмотра примера или <code>Assets/FactoryKit/Scenes/AssetGallery.unity</code> для всей собственной библиотеки. Основная сцена <code>Brewhouse</code> остаётся пустой.</p>
<h2>Шесть площадок — разные локации</h2><p>Официальные фотографии помогают различать здания и окружение. Библиотека даёт общие модули; узнаваемые детали каждой площадки будем собирать по её материалам.</p>
<div class="references">__BRANCHES__</div><p><a href="references/sources.json">Источники фотографий и кадров из видео</a> · <a href="https://ochakovo.ru/kompaniya/">Официальная страница компании</a></p>
<footer>Геометрия и PBR-фактуры собственного набора созданы в Blender/Python. Kenney: CC0, исходные License.txt сохранены. Фотографии и логотип принадлежат компании. В библиотеке нет игровых заданий, анимаций персонажей и подтверждённой реконструкции помещений. Подробности и ограничения — в README.</footer>
</main><script>
const assets=__DATA__;
const categories={Products:'Продукция Очаково',Architecture:'Здание и конструкции',Process:'Оборудование',Pipes:'Трубы и арматура',Bottling:'Линия розлива',Laboratory:'Лаборатория',Logistics:'Склад и быт',Props:'Реквизит',Agriculture:'Солодовня и винодельня'};
let pack='original';const search=document.querySelector('#search'),category=document.querySelector('#category'),models=document.querySelector('#models');
const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function options(){category.innerHTML='<option value="">Все категории</option>'+Object.entries(categories).map(([k,v])=>`<option value="${k}">${v}</option>`).join('');category.hidden=pack!=='original';}
function render(){const q=search.value.toLocaleLowerCase('ru');const list=assets.filter(a=>a.pack===pack&&(!category.value||a.category===category.value)&&[a.label,a.id,categories[a.category]||''].join(' ').toLocaleLowerCase('ru').includes(q));document.querySelector('.count').textContent=`Найдено моделей: ${list.length}`;models.innerHTML=list.map(a=>`<article><img loading="lazy" src="${a.image}" alt="${escape(a.label)}"><div class="info"><h3>${escape(a.label)}</h3><code>${escape(a.id)}</code><div class="details">${a.size?a.size.map(n=>Number(n.toFixed(2))).join(' × ')+' м · '+a.triangles.toLocaleString('ru')+' треуг.': 'Готовый prefab · CC0'}</div><button class="copy" data-path="${a.prefab}">Скопировать путь Unity</button></div></article>`).join('')||'<p>Нет моделей по этому запросу.</p>';}
document.querySelectorAll('[data-pack]').forEach(b=>b.onclick=()=>{pack=b.dataset.pack;document.querySelectorAll('[data-pack]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));options();render()});search.oninput=render;category.onchange=render;
models.addEventListener('click',async e=>{const b=e.target.closest('[data-path]');if(!b)return;try{await navigator.clipboard.writeText(b.dataset.path);b.textContent='Путь скопирован'}catch{b.textContent=b.dataset.path}});
const base='../../../OchakovoFactoryWorld/Assets/FactoryKit/Textures/Surfaces/';
document.querySelector('#surfaces').innerHTML=[['BrushedSteel','Шлифованная нержавейка'],['FactoryTile','Промышленная плитка'],['PaintedMetal','Окрашенный металл'],['WoodGrain','Дерево поддонов'],['KraftCardboard','Волокна картона'],['Rubber','Резина']].map(([id,label])=>`<div class="surface"><img loading="lazy" src="materials/${id}.png" alt="Рендер материала Blender: ${label}"><h3>${label}</h3><a href="${base+id}_Albedo.png">Цвет</a> · <a href="${base+id}_Normal.png">Нормали</a> · <a href="${base+id}_Roughness.png">Шероховатость</a></div>`).join('');options();render();
</script></html>'''
sources=json.loads((DOC/'references/sources.json').read_text())[:6]
branches=''.join('<div><img loading="lazy" src="references/'+r['file']+'" alt="'+r['title']+'"><p>'+r['title']+'</p></div>' for r in sources)
(DOC/'index.html').write_text(template.replace('__DATA__',json.dumps(data,ensure_ascii=False)).replace('__BRANCHES__',branches).replace('__ORIGINAL_COUNT__',str(original_count)).replace('__PREFAB_COUNT__',str(original_count+181)))
print('CATALOG_BUILT',len(data),'models')
