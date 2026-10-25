using System;
using System.Globalization;
using UnityEngine;
using UnityEngine.UI;

public partial class FactoryWindowsDesktop {
 string noteId="",noteText="",savedText="",calcDisplay="0",calcOperation="";double calcValue;bool calcFresh=true;InputField noteEdit;Text calcLabel;RectTransform trayPanel;bool noteMaximized;
 RectTransform App(string title,float x,float y,float w,float h,string app){HideStart();Dismiss();if(applications.TryGetValue(app,out var previous)&&previous){previous.gameObject.SetActive(false);Destroy(previous.gameObject);}appWindow=Panel(windows,title,x,y,w,h,Color.white);appWindow.gameObject.AddComponent<Outline>().effectColor=gray;applications[app]=appWindow;var current=appWindow;ActiveApp=app;CurrentPage=app;var top=Panel(appWindow,"App title bar",0,0,w,32,Color.white);var drag=top.gameObject.AddComponent<FactoryDesktopDrag>();drag.window=appWindow;drag.focus=()=>{appWindow=current;ActiveApp=app;CurrentPage=app=="notepad"&&noteId=="task"?"task":app;};Icon(top,app=="calculator"?"calculator":app=="settings"?"gear":app=="photos"?"photo":"note",9,6,20,20);T(top,title,36,7,w-168,22,14);GlyphButton(top,"Minimize app",w-138,0,46,32,"minimize",()=>{current.gameObject.SetActive(false);ActiveApp="desktop";CurrentPage="desktop";});var maximizeButton=GlyphButton(top,"Maximize app",w-92,0,46,32,app=="notepad"&&noteMaximized?"restore":"maximize",()=>{if(app=="notepad")OpenNote(noteId,!noteMaximized);});maximizeButton.interactable=app=="notepad";GlyphButton(top,"Close app",w-46,0,46,32,"close",()=>{appWindow=current;ActiveApp=app;CloseApp();});return appWindow;}
 void CloseApp(){if(ActiveApp=="notepad"&&noteText!=savedText){Dialog("Блокнот","Сохранить изменения в файле «"+Name(noteId)+"»?",new[]{("Сохранить",(Action)(()=>{SaveNote();Dismiss();DestroyApp();})),("Не сохранять",(Action)(()=>{Dismiss();DestroyApp();})),("Отмена",(Action)Dismiss)});return;}DestroyApp();}
 void DestroyApp(){if(applications.TryGetValue(ActiveApp,out var current)&&current)Destroy(current.gameObject);applications.Remove(ActiveApp);appWindow=null;ActiveApp=ExplorerVisible?"explorer":"desktop";CurrentPage=ExplorerVisible?folder:"desktop";}
 void OpenNote(string id,bool maximize=false){var e=Find(id);if(e==null)return;if(!maximize&&!noteMaximized&&id==noteId&&Activate("notepad")){CurrentPage=id=="task"?"task":"notepad";return;}if(noteText!=savedText)SaveNote();noteMaximized=maximize;noteId=id;noteText=e.text;savedText=e.text;float w=maximize?SW:740,h=maximize?SH-TB:440;var app=App(e.name+" — Блокнот",maximize?0:256,maximize?0:85,w,h,"notepad");
  string[] menus={"Файл","Правка","Формат","Вид","Справка"};for(int i=0;i<menus.Length;i++){string m=menus[i];B(app,"Notepad · "+m,i*76,32,76,27,m,()=>NoteMenu(m),Color.white,ink,14);}
  noteEdit=EditField(app,"Notepad document",5,62,w-10,h-88,noteText,value=>noteText=value,true);noteEdit.textComponent.font=mono?mono:font;noteEdit.textComponent.fontSize=17;noteEdit.textComponent.supportRichText=false;noteEdit.textComponent.horizontalOverflow=HorizontalWrapMode.Wrap;
  Panel(app,"Notepad status",0,h-24,w,24,new Color32(240,240,240,255));T(app,"Стр 1, стл 1       |       100%       |       Windows (CRLF)       |       UTF-8",18,h-21,w-30,22,12,false,gray);
  if(id=="task"){puzzle.CompleteTask();CurrentPage="task";}
 }
 void SaveNote(){var e=Find(noteId);if(e==null)return;if(e.readOnly){Notice("Блокнот","Файл доступен только для чтения.");return;}e.text=noteText;savedText=noteText;}
 void FindInNote(){TextPrompt("Найти в документе","",s=>{int at=noteText.IndexOf(s,StringComparison.OrdinalIgnoreCase);if(at>=0){noteEdit.ActivateInputField();noteEdit.selectionAnchorPosition=at;noteEdit.selectionFocusPosition=at+s.Length;}});}
 void NoteMenu(string menu){
  if(menu=="Файл")Dialog("Файл","Действия с документом",new[]{("Создать",(Action)(()=>{string id="note"+(++serial);Add(id,"Новый документ.txt","documents","note","");OpenNote(id);})),("Сохранить",(Action)(()=>{SaveNote();Dismiss();})),("Закрыть",(Action)(()=>{Dismiss();CloseApp();}))});
  else if(menu=="Правка")Dialog("Правка","Редактирование текста",new[]{("Выделить всё",(Action)(()=>{Dismiss();noteEdit.ActivateInputField();noteEdit.selectionAnchorPosition=0;noteEdit.selectionFocusPosition=noteEdit.text.Length;})),("Найти",(Action)(()=>TextPrompt("Найти в документе","",s=>{int at=noteText.IndexOf(s,StringComparison.OrdinalIgnoreCase);if(at>=0){noteEdit.ActivateInputField();noteEdit.selectionAnchorPosition=at;noteEdit.selectionFocusPosition=at+s.Length;}})))});
  else if(menu=="Формат")Dialog("Формат","Размер текста",new[]{("Мельче",(Action)(()=>{noteEdit.textComponent.fontSize=Mathf.Max(12,noteEdit.textComponent.fontSize-1);Dismiss();})),("Крупнее",(Action)(()=>{noteEdit.textComponent.fontSize=Mathf.Min(26,noteEdit.textComponent.fontSize+1);Dismiss();}))});
  else if(menu=="Вид")Dialog("Вид","Масштаб документа",new[]{("100%",(Action)(()=>{noteEdit.textComponent.fontSize=17;Dismiss();})),("125%",(Action)(()=>{noteEdit.textComponent.fontSize=21;Dismiss();}))});
  else Notice("О программе «Блокнот»","Рабочее место лаборатории. Текстовые документы и поручения текущей смены.");
 }
 bool Activate(string app){HideStart();Dismiss();if(applications.TryGetValue(app,out var current)&&current){current.gameObject.SetActive(true);current.SetAsLastSibling();appWindow=current;ActiveApp=app;CurrentPage=app;return true;}return false;}
 void OpenCalculator(){if(Activate("calculator"))return;calcDisplay="0";calcFresh=true;calcOperation="";var app=App("Калькулятор",705,64,330,502,"calculator");Panel(app,"Calculator body",0,33,330,469,new Color32(242,242,242,255));Icon(app,"details",15,56,19,19);T(app,"Обычный",45,48,260,33,22);calcLabel=T(app,"0",15,96,300,66,39);calcLabel.alignment=TextAnchor.MiddleRight;
  string[] keys={"%","CE","C","BS","1/x","x²","sqrt","÷","7","8","9","×","4","5","6","-","1","2","3","+","±","0",",","="};for(int i=0;i<keys.Length;i++){string key=keys[i];B(app,"Calculator · "+key,5+i%4*81,178+i/4*52,77,48,(key=="BS"||key=="sqrt"?"":key),()=>Calc(key),key=="="?new Color32(136,194,235,255):char.IsDigit(key[0])?Color.white:new Color32(228,228,228,255),ink,22);if(key=="BS"||key=="sqrt")Icon(app,key=="BS"?"backspace":"sqrt",27+i%4*81,190+i/4*52,30,25);}
 }
 void Calc(string key){double n;double.TryParse(calcDisplay,NumberStyles.Any,CultureInfo.InvariantCulture,out n);
  if(key=="C"||key=="CE"){calcDisplay="0";calcOperation="";calcFresh=true;}
  else if(key=="BS"){calcDisplay=calcDisplay.Length>1?calcDisplay.Substring(0,calcDisplay.Length-1):"0";}
  else if(key=="±")calcDisplay=(-n).ToString(CultureInfo.InvariantCulture);
  else if(key=="%")calcDisplay=(n/100).ToString(CultureInfo.InvariantCulture);
  else if(key=="x²")calcDisplay=(n*n).ToString(CultureInfo.InvariantCulture);
  else if(key=="sqrt")calcDisplay=n<0?"Ошибка":Math.Sqrt(n).ToString(CultureInfo.InvariantCulture);
  else if(key=="1/x")calcDisplay=n==0?"Ошибка":(1/n).ToString(CultureInfo.InvariantCulture);
  else if(key=="+"||key=="-"||key=="×"||key=="÷"){calcValue=n;calcOperation=key;calcFresh=true;}
  else if(key=="="){double result=n;if(calcOperation=="+")result=calcValue+n;if(calcOperation=="-")result=calcValue-n;if(calcOperation=="×")result=calcValue*n;if(calcOperation=="÷")result=n==0?double.NaN:calcValue/n;calcDisplay=double.IsNaN(result)?"Ошибка":result.ToString("G10",CultureInfo.InvariantCulture);calcOperation="";calcFresh=true;}
  else{if(calcFresh){calcDisplay="0";calcFresh=false;}if(key==","){if(!calcDisplay.Contains("."))calcDisplay+=".";}else calcDisplay=calcDisplay=="0"?key:calcDisplay+key;}
  calcLabel.text=calcDisplay.Replace('.',',');
 }
 void OpenSettings(){if(Activate("settings"))return;var app=App("Параметры",268,68,700,468,"settings");T(app,"Параметры Windows",32,65,630,42,30);T(app,"Рабочее место: химик-лаборант\nКомпьютер: ПК-04",32,122,630,68,19,false,gray);
  var sound=B(app,"Settings sound",32,218,302,74,"Звук",()=>Tray("volume"),new Color32(245,245,245,255),ink,21);Icon(sound.transform,"volume",15,22,30,30,blue);
  var personalize=B(app,"Settings wallpaper",364,218,302,74,"Персонализация",()=>{darkWallpaper=!darkWallpaper;var raw=screen.GetComponentInChildren<RawImage>();raw.color=darkWallpaper?new Color(.45f,.55f,.70f):Color.white;},new Color32(245,245,245,255),ink,20);Icon(personalize.transform,"pc",12,22,30,30,blue);
  B(app,"Settings account",32,321,302,74,"Учётная запись",()=>Notice("Учётная запись","Стажёр\nХимик-лаборант\nЛаборатория качества"),new Color32(245,245,245,255),ink,20);
  B(app,"Settings information",364,321,302,74,"О компьютере",()=>Notice("О компьютере","Windows 10\nРабочая станция ПК-04\nПроизводственная сеть / лаборатория"),new Color32(245,245,245,255),ink,20);
 }
 void Tray(string kind){HideStart();if(trayPanel){Destroy(trayPanel.gameObject);trayPanel=null;}float w=kind=="calendar"?330:360,h=kind=="calendar"?388:kind=="volume"?150:238;trayPanel=Panel(screen,"System tray · "+kind,SW-w,SH-TB-h,w,h,new Color32(38,38,38,255));
  B(trayPanel,"Close tray",w-35,0,35,30,"×",()=>{Destroy(trayPanel.gameObject);trayPanel=null;},new Color32(38,38,38,255),Color.white,17);
  if(kind=="volume"){
   T(trayPanel,"Динамики",22,22,w-60,30,20,false,Color.white);T(trayPanel,"Громкость игры",22,66,w-50,26,15,false,Color.white);var baseR=Panel(trayPanel,"Volume slider",24,110,w-48,8,new Color32(115,115,115,255));var slider=baseR.gameObject.AddComponent<Slider>();var handle=Panel(baseR,"Slider handle",0,-8,12,24,blue);handle.anchorMin=handle.anchorMax=new Vector2(.5f,.5f);slider.handleRect=handle;slider.minValue=0;slider.maxValue=1;slider.value=AudioListener.volume;slider.onValueChanged.AddListener(v=>AudioListener.volume=v);
  }else if(kind=="calendar"){
   T(trayPanel,"09:41",22,22,280,48,34,false,Color.white);T(trayPanel,"24 октября 2026 г.",22,75,280,28,17,false,Color.white);T(trayPanel,"Октябрь 2026",22,118,280,26,18,false,Color.white);string[] days={"пн","вт","ср","чт","пт","сб","вс"};for(int i=0;i<7;i++)T(trayPanel,days[i],24+i*42,160,38,26,14,false,Color.white).alignment=TextAnchor.MiddleCenter;for(int d=1;d<=31;d++){int cell=d+2;int day=d;B(trayPanel,"Calendar day "+d,24+cell%7*42,191+cell/7*34,38,30,d.ToString(),()=>Notice(day+" октября","Игровой календарь: "+day+".10.2026"),d==24?blue:new Color32(38,38,38,255),Color.white,14);}
  }else if(kind=="language"){
   T(trayPanel,"Язык ввода",22,23,300,30,20,false,Color.white);B(trayPanel,"Russian keyboard",15,80,w-30,48,"РУС   Русский",()=>{languageLabel.text="РУС";Destroy(trayPanel.gameObject);trayPanel=null;},blue,Color.white);B(trayPanel,"English keyboard",15,140,w-30,48,"ENG   English",()=>{languageLabel.text="ENG";Destroy(trayPanel.gameObject);trayPanel=null;},new Color32(60,60,60,255),Color.white);
  }else{
   string title=kind=="network"?"Производственная сеть":kind=="notifications"?"Центр уведомлений":"Фоновые приложения";
   T(trayPanel,title,22,26,w-54,54,21,false,Color.white);T(trayPanel,kind=="network"?"ПК-04 · Лаборатория\nРабочие папки доступны в сети.":kind=="notifications"?(puzzle.Completed?"Поручение найдено.\nМожно вернуться в цех.":"Новая смена\nНайдите задания химика-лаборанта."):"Проводник\nБлокнот\nКалькулятор",22,94,w-44,95,17,false,Color.white);B(trayPanel,"Open shared folders",22,193,w-44,32,"Открыть рабочие папки",()=>{Destroy(trayPanel.gameObject);trayPanel=null;Navigate("departments");},blue,Color.white,15);
  }
 }
}
