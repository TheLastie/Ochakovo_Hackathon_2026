using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

public partial class FactoryWindowsDesktop : MonoBehaviour {
 public FactoryComputerPuzzle puzzle;public Font font,bold,mono;public Texture2D logo;public Texture2D[] selfies;
 public string CurrentPage{get;private set;}="desktop";
 public string ActiveApp{get;private set;}="desktop";
 public bool ExplorerVisible=>explorerWindow&&explorerWindow.gameObject.activeSelf;
 public string VisibleNames=>string.Join("|",Listed().Select(e=>e.name));public string SelectedName=>Find(selected)?.name??"";public string SearchQuery=>query;public bool DetailsView=>details;public bool Maximized=>maximized;public string CalculatorResult=>calcDisplay;public int TrashCount=>entries.Count(e=>e.deleted);public int AppCount=>applications.Count(e=>e.Value);public float ExplorerX=>explorerWindow?explorerWindow.anchoredPosition.x:0;public float ExplorerY=>explorerWindow?-explorerWindow.anchoredPosition.y:0;
 public bool StartVisible=>startMenu&&startMenu.gameObject.activeSelf;
 const float SW=1148,SH=646,TB=42;
 readonly Color ink=new Color32(25,25,25,255),gray=new Color32(96,96,96,255),border=new Color32(211,211,211,255),blue=new Color32(0,120,215,255),hover=new Color32(229,243,255,255),dark=new Color32(31,31,31,255);
 readonly Dictionary<string,RectTransform> applications=new Dictionary<string,RectTransform>();
 RectTransform screen,windows,explorerWindow,fileBody,appWindow,startMenu,popup,taskbar;Text status,clock,languageLabel;InputField searchField,addressField;Texture2D wallpaper;Button explorerTask;bool maximized,details,extensions=true,hiddenFiles,descending,darkWallpaper;string selected="",clipboard="",folder="departments",query="",ribbon="Главная";int historyAt=-1;readonly List<string> history=new List<string>();
 public void Build(Transform parent){
  R(parent,"Monitor shadow",56,40,1184,708).gameObject.AddComponent<Image>().color=new Color(0,0,0,.4f);
  var bezel=Panel(parent,"Physical monitor",48,30,1184,708,new Color32(32,34,37,255));Panel(bezel,"Inner bevel",12,12,1160,658,new Color32(8,9,11,255));screen=Panel(bezel,"Windows 10 display",18,18,SW,SH,Color.black);
  wallpaper=Wallpaper();var art=R(screen,"Windows blue wallpaper",0,0,SW,SH).gameObject.AddComponent<RawImage>();art.texture=wallpaper;art.raycastTarget=false;Icon(screen,"wallpaper",720,146,224,272);
  foreach(var d in new[]{new {id="pc",name="Этот компьютер",kind="pc"},new {id="trash",name="Корзина",kind="bin"},new {id="departments",name="Рабочие папки",kind="folder"},new {id="welcome",name="Начни здесь",kind="note"}}.Select((x,i)=>new{x,i})){
   var b=B(screen,"Desktop · "+d.x.name,8,12+d.i*112,98,106,"",()=>{},new Color(0,0,0,0));Icon(b.transform,d.x.kind,25,3,48,48);var l=T(b.transform,d.x.name,1,55,96,52,15,false,Color.white);l.alignment=TextAnchor.UpperCenter;var click=b.gameObject.AddComponent<FactoryDesktopClick>();string id=d.x.id;click.open=()=>{if(id=="welcome")OpenNote("welcome");else Navigate(id);};click.select=()=>{selected=id;};click.context=pos=>DesktopContext(id,pos);
  }
  T(screen,"ЛАБОРАТОРИЯ · ПК-04",800,524,320,26,18,false,Color.white).alignment=TextAnchor.MiddleRight;T(screen,"Найди свою рабочую карточку",720,557,400,25,16,false,Color.white).alignment=TextAnchor.MiddleRight;
  windows=R(screen,"Desktop windows",0,0,SW,SH-TB);
  taskbar=Panel(screen,"Windows taskbar",0,SH-TB,SW,TB,new Color32(25,25,25,255));var start=B(taskbar,"Start",0,0,46,TB,"",ToggleStart,dark);Icon(start.transform,"windows",11,9,24,24,Color.white);
  var sb=B(taskbar,"Taskbar search",46,0,228,TB,"Поиск в Windows",()=>SearchDesktop(),new Color32(243,243,243,255),ink,15);Icon(sb.transform,"search",9,12,19,19,gray);sb.GetComponentInChildren<Text>().rectTransform.anchoredPosition=new Vector2(34,0);sb.GetComponentInChildren<Text>().rectTransform.sizeDelta=new Vector2(190,42);
  var taskview=B(taskbar,"Task view",278,0,46,TB,"",()=>ShowTasks(),dark,Color.white,24);Icon(taskview.transform,"taskview",11,9,25,25,Color.white);
  explorerTask=B(taskbar,"Explorer taskbar",328,0,48,TB,"",ToggleExplorer,dark);Icon(explorerTask.transform,"folder",12,8,27,27);
  var note=B(taskbar,"Notepad taskbar",378,0,48,TB,"",()=>OpenNote(noteId.Length>0?noteId:"welcome"),dark);Icon(note.transform,"note",12,7,27,27);
  var calc=B(taskbar,"Calculator taskbar",428,0,48,TB,"",OpenCalculator,dark);Icon(calc.transform,"calculator",13,6,25,29);
  var hidden=B(taskbar,"Hidden tray icons",SW-272,0,30,TB,"",()=>Tray("background"),dark,Color.white,18);Icon(hidden.transform,"up",9,14,13,13,Color.white);
  var net=B(taskbar,"Network tray",SW-239,0,33,TB,"",()=>Tray("network"),dark);Icon(net.transform,"network",7,11,20,20,Color.white);
  var vol=B(taskbar,"Volume tray",SW-204,0,33,TB,"",()=>Tray("volume"),dark);Icon(vol.transform,"volume",6,9,23,23,Color.white);
  languageLabel=B(taskbar,"Keyboard language",SW-168,0,44,TB,"РУС",()=>Tray("language"),dark,Color.white,13).GetComponentInChildren<Text>();
  var date=B(taskbar,"Clock and calendar",SW-123,0,85,TB,"09:41\n24.10.2026",()=>Tray("calendar"),dark,Color.white,12);clock=date.GetComponentInChildren<Text>();
  var action=B(taskbar,"Action center",SW-39,0,33,TB,"",()=>Tray("notifications"),dark);Icon(action.transform,"notification",6,10,21,21,Color.white);
  B(taskbar,"Show desktop",SW-5,0,5,TB,"",ShowDesktopOnly,new Color32(74,74,74,255));
  if(logo){var lr=R(bezel,"Company sticker",22,679,93,20);var raw=lr.gameObject.AddComponent<RawImage>();raw.texture=logo;raw.raycastTarget=false;}
  T(bezel,"ПК-04",556,681,80,22,13,false,new Color(.7f,.72f,.74f)).alignment=TextAnchor.MiddleCenter;
  T(bezel,"Двойной клик — открыть · Esc — в цех",693,681,395,24,14,false,new Color(.8f,.82f,.84f)).alignment=TextAnchor.MiddleRight;
  var power=B(bezel,"Leave workstation",1105,674,52,33,"",()=>puzzle.Close(),new Color32(32,34,37,255));Icon(power.transform,"power",17,6,20,20,new Color(.75f,.8f,.85f));Panel(bezel,"Power LED",1166,688,4,4,new Color32(80,190,230,255));
  Panel(parent,"Monitor neck",592,738,96,24,new Color32(35,37,41,255));Panel(parent,"Monitor base",503,762,274,10,new Color32(45,47,51,255));
  SeedFiles();
 }
 public void Show(){if(puzzle.Completed)OpenNote("task");else ShowDesktopOnly();}
 public void HandleKeyboard(){
  if(Input.GetKeyDown(KeyCode.Escape)){if(trayPanel){Destroy(trayPanel.gameObject);trayPanel=null;return;}if(popup){Dismiss();return;}if(StartVisible){HideStart();return;}puzzle.Close();return;}
  if((Input.GetKey(KeyCode.LeftControl)||Input.GetKey(KeyCode.RightControl))&&Input.GetKeyDown(KeyCode.S)){SaveNote();return;}
  var selectedObject=EventSystem.current?EventSystem.current.currentSelectedGameObject:null;var field=selectedObject?selectedObject.GetComponent<InputField>():null;if(field&&field.isFocused)return;
  bool ctrl=Input.GetKey(KeyCode.LeftControl)||Input.GetKey(KeyCode.RightControl),alt=Input.GetKey(KeyCode.LeftAlt)||Input.GetKey(KeyCode.RightAlt);
  if(ctrl&&Input.GetKeyDown(KeyCode.C)&&ExplorerVisible)Copy();if(ctrl&&Input.GetKeyDown(KeyCode.V)&&ExplorerVisible)Paste();if(ctrl&&Input.GetKeyDown(KeyCode.S))SaveNote();
  if(ctrl&&Input.GetKeyDown(KeyCode.F)){if(ActiveApp=="notepad")FindInNote();else{if(!ExplorerVisible)Navigate("departments");explorerWindow.SetAsLastSibling();ActiveApp="explorer";CurrentPage=folder;searchField?.ActivateInputField();}}
  if(Input.GetKeyDown(KeyCode.F2))Rename();if(Input.GetKeyDown(KeyCode.Delete)&&ExplorerVisible)Delete();if(Input.GetKeyDown(KeyCode.F5)&&ExplorerVisible)RefreshFiles();
  if((Input.GetKeyDown(KeyCode.Backspace)||alt&&Input.GetKeyDown(KeyCode.LeftArrow))&&ExplorerVisible)Back();if(alt&&Input.GetKeyDown(KeyCode.RightArrow))Forward();
  if(Input.GetKeyDown(KeyCode.Return)&&!string.IsNullOrEmpty(selected))OpenItem(selected);
  if(Input.GetKeyDown(KeyCode.Alpha1)){if(folder=="lab"&&ExplorerVisible)Navigate("methods");else Navigate("lab");}
  if(Input.GetKeyDown(KeyCode.Alpha2)){if(folder=="lab"&&ExplorerVisible)Navigate("archive");else Navigate("bottling");}
  if(Input.GetKeyDown(KeyCode.Alpha3)){if(folder=="lab"&&ExplorerVisible)Navigate("shift");else Navigate("warehouse");}
  if(Input.GetKeyDown(KeyCode.Alpha4))Navigate("service");
 }
 public void Back(){if(historyAt>0){historyAt--;Go(history[historyAt]);}else Up();}
 void Forward(){if(historyAt+1<history.Count){historyAt++;Go(history[historyAt]);}}
 void Up(){Navigate(Parent(folder));}
 public void ShowDesktopOnly(){HideStart();Dismiss();if(explorerWindow)explorerWindow.gameObject.SetActive(false);foreach(var app in applications.Values)if(app)app.gameObject.SetActive(false);ActiveApp="desktop";CurrentPage="desktop";}
 void ToggleExplorer(){if(ExplorerVisible&&ActiveApp=="explorer"){explorerWindow.gameObject.SetActive(false);ActiveApp="desktop";CurrentPage="desktop";}else{if(!explorerWindow)Navigate("departments");else{explorerWindow.gameObject.SetActive(true);explorerWindow.SetAsLastSibling();ActiveApp="explorer";CurrentPage=folder;}}}
 void ToggleMax(){maximized=!maximized;RenderExplorer();}
 void CloseExplorer(){if(explorerWindow)Destroy(explorerWindow.gameObject);explorerWindow=null;ActiveApp="desktop";CurrentPage="desktop";}
 void HideStart(){if(startMenu)startMenu.gameObject.SetActive(false);}
 void ToggleStart(){Dismiss();if(StartVisible){HideStart();return;}if(startMenu)Destroy(startMenu.gameObject);startMenu=Panel(screen,"Start menu",0,SH-TB-456,494,456,new Color32(31,31,31,255));
  T(startMenu,"Стажёр · химик-лаборант",24,21,440,30,18,false,Color.white);
  string[] labels={"Проводник","Блокнот","Калькулятор","Параметры","Этот компьютер","Корзина"},icons={"folder","note","calculator","gear","pc","bin"};Action[] acts={()=>Navigate("departments"),()=>OpenNote("welcome"),OpenCalculator,OpenSettings,()=>Navigate("pc"),()=>Navigate("trash")};
  for(int i=0;i<labels.Length;i++){var b=B(startMenu,"Start · "+labels[i],14,68+i*48,243,44,labels[i],acts[i],new Color32(31,31,31,255),Color.white,17);Icon(b.transform,icons[i],8,7,30,30,Color.white);var text=b.GetComponentInChildren<Text>();text.alignment=TextAnchor.MiddleLeft;text.rectTransform.anchoredPosition=new Vector2(51,0);text.rectTransform.sizeDelta=new Vector2(180,44);}
  T(startMenu,"Работа",276,71,190,25,15,false,Color.white);var tile=B(startMenu,"Pinned working folders",276,109,198,118,"Рабочие папки",()=>Navigate("departments"),blue,Color.white,16);Icon(tile.transform,"folder",72,12,50,50);tile.GetComponentInChildren<Text>().alignment=TextAnchor.LowerCenter;
  var memo=B(startMenu,"Pinned shift memo",276,236,198,118,"Задание.txt",()=>OpenNote("welcome"),new Color32(14,91,158,255),Color.white,16);Icon(memo.transform,"note",72,12,50,50);memo.GetComponentInChildren<Text>().alignment=TextAnchor.LowerCenter;
  var shut=B(startMenu,"Virtual computer power",16,403,456,40,"Выключить компьютер",()=>puzzle.Close(),new Color32(31,31,31,255),Color.white,16);Icon(shut.transform,"power",10,8,24,24,Color.white);
 }
 void ShowTasks(){Dialog("Представление задач","Открытые приложения",new[]{("Проводник",(Action)(()=>{Dismiss();if(ExplorerVisible){explorerWindow.SetAsLastSibling();ActiveApp="explorer";CurrentPage=folder;}else ToggleExplorer();})),("Блокнот",(Action)(()=>OpenNote("welcome"))),("Калькулятор",(Action)OpenCalculator)});}
 void SearchDesktop(){HideStart();var r=Popup("Поиск в Windows",420,230);T(r,"Найти файл или приложение",20,52,380,28,18);var input=EditField(r,"Windows search",20,94,380,34,"",s=>{});B(r,"Run search",20,151,380,38,"Найти в рабочих папках",()=>{query=input.text;string term=query.ToLowerInvariant();Dismiss();if(term.Contains("кальк")||term.Contains("calc"))OpenCalculator();else if(term.Contains("блокнот")||term.Contains("notepad"))OpenNote(noteId.Length>0?noteId:"welcome");else if(term.Contains("параметр")||term.Contains("settings"))OpenSettings();else Navigate("departments",false);},blue,Color.white);input.ActivateInputField();}
 RectTransform R(Transform p,string name,float x,float y,float w,float h){var o=new GameObject(name,typeof(RectTransform));var r=(RectTransform)o.transform;r.SetParent(p,false);r.anchorMin=r.anchorMax=new Vector2(0,1);r.pivot=new Vector2(0,1);r.anchoredPosition=new Vector2(x,-y);r.sizeDelta=new Vector2(w,h);return r;}
 RectTransform Panel(Transform p,string n,float x,float y,float w,float h,Color c,bool ray=true){var r=R(p,n,x,y,w,h);var image=r.gameObject.AddComponent<Image>();image.color=c;image.raycastTarget=ray;return r;}
 Text T(Transform p,string s,float x,float y,float w,float h,int size=16,bool heavy=false,Color? c=null){var r=R(p,s,x,y,w,h);var t=r.gameObject.AddComponent<Text>();t.font=heavy?bold:font;t.fontSize=size;t.text=s;t.color=c??ink;t.alignment=TextAnchor.UpperLeft;t.raycastTarget=false;t.horizontalOverflow=HorizontalWrapMode.Wrap;t.verticalOverflow=VerticalWrapMode.Truncate;return t;}
 Button B(Transform p,string n,float x,float y,float w,float h,string text,Action action,Color? bg=null,Color? fg=null,int size=16){var r=Panel(p,n,x,y,w,h,bg??Color.white);var b=r.gameObject.AddComponent<Button>();b.targetGraphic=r.GetComponent<Image>();var cs=b.colors;cs.normalColor=Color.white;cs.highlightedColor=bg.HasValue&&bg.Value.grayscale<.3f?new Color(1.4f,1.4f,1.4f):hover;cs.selectedColor=cs.highlightedColor;cs.pressedColor=new Color(.75f,.85f,.95f);b.colors=cs;b.onClick.AddListener(()=>action());if(text.Length>0){var t=T(r,text,4,0,w-8,h,size,false,fg);t.alignment=TextAnchor.MiddleCenter;}return b;}
 FactoryDesktopIcon Icon(Transform p,string kind,float x,float y,float w,float h,Color? tint=null){var i=R(p,kind,x,y,w,h).gameObject.AddComponent<FactoryDesktopIcon>();i.kind=kind;i.tint=tint??gray;i.raycastTarget=false;return i;}
 InputField EditField(Transform p,string n,float x,float y,float w,float h,string value,Action<string> changed,bool multi=false){var r=Panel(p,n,x,y,w,h,Color.white);var outline=r.gameObject.AddComponent<Outline>();outline.effectColor=border;outline.effectDistance=new Vector2(1,-1);var field=r.gameObject.AddComponent<InputField>();var text=T(r,"",6,multi?6:0,w-12,h-(multi?12:0),16);text.alignment=multi?TextAnchor.UpperLeft:TextAnchor.MiddleLeft;field.textComponent=text;field.lineType=multi?InputField.LineType.MultiLineNewline:InputField.LineType.SingleLine;field.text=value;field.onValueChanged.AddListener(v=>changed(v));return field;}
 void Clear(RectTransform r){foreach(Transform t in r){t.gameObject.SetActive(false);Destroy(t.gameObject);}}
 RectTransform Popup(string title,float w,float h){Dismiss();HideStart();popup=Panel(screen,title,(SW-w)/2,Mathf.Max(10,(SH-TB-h)/2),w,h,Color.white);popup.gameObject.AddComponent<Outline>().effectColor=gray;Panel(popup,"Dialog title",0,0,w,36,Color.white);T(popup,title,12,8,w-60,25,16);GlyphButton(popup,"Close dialog",w-42,0,42,34,"close",Dismiss);return popup;}
 void Dismiss(){if(popup){popup.gameObject.SetActive(false);Destroy(popup.gameObject);popup=null;}}
 Button GlyphButton(Transform p,string name,float x,float y,float w,float h,string icon,Action action){var b=B(p,name,x,y,w,h,"",action);Icon(b.transform,icon,(w-18)/2,(h-18)/2,18,18);return b;}
 void Dialog(string title,string message,(string,Action)[] actions){var r=Popup(title,510,236);T(r,message,24,64,462,82,18);float width=(462-(actions.Length-1)*10)/actions.Length;for(int i=0;i<actions.Length;i++){var a=actions[i];B(r,a.Item1,24+i*(width+10),170,width,38,a.Item1,a.Item2,new Color32(238,238,238,255));}}
 Texture2D Wallpaper(){var t=new Texture2D(768,432,TextureFormat.RGB24,false);for(int y=0;y<432;y++)for(int x=0;x<768;x++){float px=x/768f,py=y/432f;float glow=Mathf.Exp(-((px-.70f)*(px-.70f)*12+(py-.57f)*(py-.57f)*8));var c=Color.Lerp(new Color(.005f,.075f,.20f),new Color(.005f,.37f,.66f),glow*.85f+px*.12f);float left=.63f,right=.82f,top=.72f,bottom=.34f;float slant=(px-left)*.28f;bool pane=px>left&&px<right&&py>bottom-slant&&py<top+slant;bool gap=Mathf.Abs(px-.715f)<.005f||Mathf.Abs(py-.53f)<.006f;float beam=Mathf.Max(0,1-Mathf.Abs(py-.53f)/(.03f+(.72f-px)*.43f));if(px<.63f)c+=new Color(0,.06f,.09f)*beam;t.SetPixel(x,y,c);}t.Apply();return t;}
 void OnDestroy(){if(wallpaper)Destroy(wallpaper);}
}
