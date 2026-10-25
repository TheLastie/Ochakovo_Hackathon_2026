using System;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

/// <summary>First hands-on episode: approach a lab PC and find the chemist's shift folder.</summary>
[DefaultExecutionOrder(-100)]
public class FactoryComputerPuzzle : MonoBehaviour {
 public FactoryExplorer explorer;
 public Font regular,bold,systemFont,systemBold,monoFont;
 public FactoryWindowsDesktop desktop;
 public Texture2D officialLogo;public Texture2D[] mikhSelfies;
 public Vector3 computerPosition=new Vector3(-5.05f,1.7f,-3.9f),standPosition=new Vector3(-5.05f,0,-4.95f);
 public bool IsOpen{get;private set;}
 public bool Completed{get;private set;}
 public string Page=>desktop?desktop.CurrentPage:"desktop";
 public int WrongFolders{get;private set;}
 public bool Available=>explorer&&explorer.Role=="chemist";
 public bool Near=>explorer&&Vector3.Distance(new Vector3(explorer.player.position.x,0,explorer.player.position.z),standPosition)<.75f;
 public bool BlocksWorldInput=>IsOpen||Time.unscaledTime<blockUntil;
 public Vector2 ScreenPosition=>explorer.view.WorldToScreenPoint(computerPosition);
 bool approaching;float blockUntil;Canvas canvas;RectTransform marker;GameObject shade;Text markerText;FactoryDesktopIcon markerIcon,markerBadge;LineRenderer brackets,glowBrackets;Image beaconGlow;FactoryLabPreparation preparation;
 readonly Color red=new Color32(213,0,50,255),ink=new Color32(21,21,21,255),soft=new Color32(246,245,242,255),muted=new Color32(98,98,95,255),line=new Color32(220,220,215,255);
 void Start(){preparation=GetComponent<FactoryLabPreparation>();BuildCanvas();CreateHighlight();}
 void CreateHighlight(){
  var o=new GameObject("Workstation computer · interaction outline");o.transform.SetParent(transform);brackets=o.AddComponent<LineRenderer>();brackets.useWorldSpace=true;brackets.loop=true;brackets.positionCount=4;brackets.widthMultiplier=.035f;brackets.material=new Material(Shader.Find("Sprites/Default"));
  var glow=new GameObject("Computer cyan halo");glowBrackets=glow.AddComponent<LineRenderer>();glowBrackets.useWorldSpace=true;glowBrackets.loop=true;glowBrackets.positionCount=4;glowBrackets.widthMultiplier=.08f;glowBrackets.material=new Material(Shader.Find("Sprites/Default"));
  var p=computerPosition+Vector3.back*.07f;brackets.SetPositions(new[]{p+new Vector3(-.45f,-.30f,0),p+new Vector3(-.45f,.30f,0),p+new Vector3(.45f,.30f,0),p+new Vector3(.45f,-.30f,0)});var points=new Vector3[4];brackets.GetPositions(points);glowBrackets.SetPositions(points);
 }
 void Update(){
  if(!canvas)return;
  bool visible=Available&&!IsOpen&&!(preparation&&preparation.IsOpen)&&!explorer.IsPaused;
  marker.gameObject.SetActive(visible);brackets.enabled=glowBrackets.enabled=visible;
  if(visible){
   var pos=(Vector2)explorer.view.WorldToScreenPoint(computerPosition+Vector3.up*.65f);
   RectTransformUtility.ScreenPointToLocalPointInRectangle((RectTransform)canvas.transform,pos,null,out var local);marker.anchoredPosition=local;
   markerText.text=Near?"E":"";markerIcon.gameObject.SetActive(!Near);markerBadge.tint=Completed?new Color32(46,133,84,255):new Color32(213,0,50,255);markerBadge.SetVerticesDirty();
   Color c=Completed?new Color32(46,133,84,255):new Color32(213,0,50,255);brackets.startColor=brackets.endColor=c;var glowColor=(Color)c;glowColor.a=.10f+.06f*Mathf.Sin(Time.unscaledTime*2.8f);glowBrackets.startColor=glowBrackets.endColor=glowColor;beaconGlow.color=new Color(c.r,c.g,c.b,.3f);
  }
  if(!Available||explorer.HelpBlocksInput)return;
  if(IsOpen){desktop.HandleKeyboard();return;}
  if(explorer.IsPaused||preparation&&preparation.IsOpen||Time.unscaledTime<blockUntil)return;
  if(Input.GetKeyDown(KeyCode.E)&&Near)Open();
  if(approaching&&Near)Open();
  if(Input.GetKeyDown(KeyCode.W)||Input.GetKeyDown(KeyCode.A)||Input.GetKeyDown(KeyCode.S)||Input.GetKeyDown(KeyCode.D))approaching=false;
 }
 public bool ConsumePointer(Vector2 p){
  if(BlocksWorldInput)return true;
  if(!Available||preparation&&preparation.IsOpen)return false;
  var c=ScreenPosition;
  if(new Rect(c.x-48,c.y-38,96,76).Contains(p)){RequestInteraction();return true;}
  return false;
 }
 public void CancelApproach(){approaching=false;}
 void RequestInteraction(){
  if(!Available||explorer.IsPaused||preparation&&preparation.IsOpen)return;
  if(Near)Open();else{approaching=true;explorer.MoveTo(standPosition.x.ToString(System.Globalization.CultureInfo.InvariantCulture)+","+standPosition.z.ToString(System.Globalization.CultureInfo.InvariantCulture));}
 }
 public void Open(){if(!Available||!Near||explorer.IsPaused||preparation&&preparation.IsOpen)return;approaching=false;IsOpen=true;blockUntil=Time.unscaledTime+.2f;explorer.LockForComputer(true);shade.SetActive(true);desktop.Show();}
 public void Close(){IsOpen=false;shade.SetActive(false);blockUntil=Time.unscaledTime+.2f;explorer.LockForComputer(false);EventSystem.current?.SetSelectedGameObject(null);}
 RectTransform Rect(Transform parent,string name,float x,float y,float w,float h){var o=new GameObject(name,typeof(RectTransform));var r=(RectTransform)o.transform;r.SetParent(parent,false);r.anchorMin=r.anchorMax=new Vector2(0,1);r.pivot=new Vector2(0,1);r.anchoredPosition=new Vector2(x,-y);r.sizeDelta=new Vector2(w,h);return r;}
 void BuildCanvas(){
  var root=new GameObject("Computer puzzle Canvas",typeof(Canvas),typeof(CanvasScaler),typeof(GraphicRaycaster));root.transform.SetParent(transform,false);canvas=root.GetComponent<Canvas>();canvas.renderMode=RenderMode.ScreenSpaceOverlay;canvas.sortingOrder=60;var scaler=root.GetComponent<CanvasScaler>();scaler.uiScaleMode=CanvasScaler.ScaleMode.ScaleWithScreenSize;scaler.referenceResolution=new Vector2(1280,800);scaler.matchWidthOrHeight=1;
  if(!FindFirstObjectByType<EventSystem>()){var events=new GameObject("Factory UI EventSystem",typeof(EventSystem),typeof(StandaloneInputModule));events.transform.SetParent(transform,false);}
  marker=Rect(root.transform,"Computer interaction icon",0,0,48,48);marker.anchorMin=marker.anchorMax=marker.pivot=new Vector2(.5f,.5f);var image=marker.gameObject.AddComponent<Image>();image.color=Color.clear;var mb=marker.gameObject.AddComponent<Button>();mb.targetGraphic=image;mb.onClick.AddListener(RequestInteraction);
  beaconGlow=Rect(marker,"Cyan beacon glow",-16,-16,80,80).gameObject.AddComponent<Image>();beaconGlow.sprite=FactoryBeaconArt.Glow();beaconGlow.raycastTarget=false;
  markerBadge=Rect(marker,"Interaction badge",0,0,48,48).gameObject.AddComponent<FactoryDesktopIcon>();markerBadge.kind="beacon";markerBadge.tint=new Color32(213,0,50,255);markerBadge.raycastTarget=false;
  markerIcon=Rect(marker,"Computer glyph",11,10,26,26).gameObject.AddComponent<FactoryDesktopIcon>();markerIcon.kind="pcwhite";markerIcon.tint=Color.white;markerIcon.raycastTarget=false;
  markerText=Rect(marker,"Nearby E",0,0,48,48).gameObject.AddComponent<Text>();markerText.font=bold;markerText.fontSize=19;markerText.color=Color.white;markerText.alignment=TextAnchor.MiddleCenter;markerText.raycastTarget=false;
  var shadeRect=Rect(root.transform,"Computer focus",0,0,1280,800);shadeRect.anchorMin=Vector2.zero;shadeRect.anchorMax=Vector2.one;shadeRect.offsetMin=shadeRect.offsetMax=Vector2.zero;var dim=shadeRect.gameObject.AddComponent<Image>();dim.color=new Color(.025f,.03f,.04f,.78f);shade=shadeRect.gameObject;
  desktop=gameObject.AddComponent<FactoryWindowsDesktop>();desktop.puzzle=this;desktop.font=systemFont?systemFont:regular;desktop.bold=systemBold?systemBold:bold;desktop.mono=monoFont?monoFont:regular;desktop.logo=officialLogo;desktop.selfies=mikhSelfies;desktop.Build(shade.transform);shade.SetActive(false);
 }
 public void MarkWrong(){WrongFolders++;}
 public void CompleteTask(){Completed=true;}
 void OnDestroy(){if(brackets&&brackets.sharedMaterial)Destroy(brackets.sharedMaterial);if(glowBrackets&&glowBrackets.sharedMaterial)Destroy(glowBrackets.sharedMaterial);}
}
