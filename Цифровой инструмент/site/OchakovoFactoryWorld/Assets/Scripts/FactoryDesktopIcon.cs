using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using System;

// Small, code-native desktop glyphs. No screenshots or live operating-system access.
public class FactoryDesktopIcon : MaskableGraphic {
 public string kind="folder";public Color tint=Color.white;
 protected override void OnPopulateMesh(VertexHelper v){v.Clear();
  Action<float,float,float,float,Color> box=(x,y,w,h,c)=>Quad(v,new Vector2(x,y),new Vector2(x+w,y),new Vector2(x+w,y+h),new Vector2(x,y+h),c);
  Color blue=new Color32(32,143,205,255),gold=new Color32(255,206,83,255),gray=new Color32(83,91,99,255),paper=new Color32(244,249,252,255);
  switch(kind){
   case "beacon":Ring(v,new Vector2(.5f,.5f),.23f,.46f,tint);break;
   case "pcwhite":box(.07f,.12f,.86f,.07f,tint);box(.07f,.58f,.86f,.07f,tint);box(.07f,.12f,.07f,.53f,tint);box(.86f,.12f,.07f,.53f,tint);box(.46f,.65f,.08f,.18f,tint);box(.27f,.83f,.46f,.06f,tint);break;
   case "wallpaper":{Color c=new Color32(52,191,235,255);Quad(v,new Vector2(0,.09f),new Vector2(.43f,.05f),new Vector2(.43f,.48f),new Vector2(0,.48f),c);Quad(v,new Vector2(0,.52f),new Vector2(.43f,.52f),new Vector2(.43f,.95f),new Vector2(0,.91f),c);Quad(v,new Vector2(.47f,.045f),new Vector2(.98f,0),new Vector2(.98f,.48f),new Vector2(.47f,.48f),c);Quad(v,new Vector2(.47f,.52f),new Vector2(.98f,.52f),new Vector2(.98f,1),new Vector2(.47f,.955f),c);break;}
   case "taskview":box(.03f,.23f,.10f,.55f,tint);box(.21f,.13f,.56f,.035f,tint);box(.21f,.13f,.035f,.76f,tint);box(.21f,.86f,.56f,.035f,tint);box(.74f,.13f,.035f,.76f,tint);box(.86f,.23f,.10f,.55f,tint);break;
   case "details":for(int y=0;y<3;y++){box(.05f,.16f+y*.26f,.12f,.12f,tint);box(.27f,.18f+y*.26f,.67f,.06f,tint);}break;
   case "grid":for(int y=0;y<3;y++)for(int x=0;x<3;x++)box(.1f+x*.28f,.1f+y*.28f,.19f,.19f,tint);break;
   case "checkbox":case "checked":box(.08f,.08f,.84f,.05f,tint);box(.08f,.08f,.05f,.84f,tint);box(.08f,.87f,.84f,.05f,tint);box(.87f,.08f,.05f,.84f,tint);if(kind=="checked"){Line(v,new Vector2(.23f,.48f),new Vector2(.43f,.70f),.08f,blue);Line(v,new Vector2(.43f,.70f),new Vector2(.78f,.29f),.08f,blue);}break;
   case "backspace":Line(v,new Vector2(.28f,.2f),new Vector2(.06f,.5f),.04f,tint);Line(v,new Vector2(.06f,.5f),new Vector2(.28f,.8f),.04f,tint);box(.28f,.18f,.65f,.04f,tint);box(.28f,.78f,.65f,.04f,tint);box(.9f,.2f,.04f,.6f,tint);Line(v,new Vector2(.46f,.33f),new Vector2(.73f,.66f),.04f,tint);Line(v,new Vector2(.73f,.33f),new Vector2(.46f,.66f),.04f,tint);break;
   case "sqrt":Line(v,new Vector2(.03f,.56f),new Vector2(.23f,.8f),.05f,tint);Line(v,new Vector2(.23f,.8f),new Vector2(.44f,.18f),.05f,tint);box(.43f,.16f,.53f,.05f,tint);Line(v,new Vector2(.57f,.35f),new Vector2(.88f,.73f),.04f,tint);Line(v,new Vector2(.88f,.35f),new Vector2(.57f,.73f),.04f,tint);break;
   case "flask":Line(v,new Vector2(.37f,.1f),new Vector2(.37f,.39f),.07f,tint);Line(v,new Vector2(.63f,.1f),new Vector2(.63f,.39f),.07f,tint);Line(v,new Vector2(.37f,.39f),new Vector2(.17f,.85f),.07f,tint);Line(v,new Vector2(.63f,.39f),new Vector2(.83f,.85f),.07f,tint);box(.17f,.82f,.66f,.07f,tint);box(.29f,.64f,.42f,.13f,tint);box(.32f,.08f,.36f,.07f,tint);break;
   case "photo":box(.08f,.12f,.84f,.76f,paper);box(.14f,.18f,.72f,.54f,blue);Quad(v,new Vector2(.14f,.72f),new Vector2(.4f,.35f),new Vector2(.64f,.72f),new Vector2(.14f,.72f),new Color32(55,140,82,255));box(.68f,.25f,.09f,.09f,gold);break;
   case "folder":box(.08f,.17f,.39f,.16f,new Color32(224,162,44,255));box(.08f,.29f,.83f,.57f,new Color32(236,176,55,255));box(.13f,.28f,.68f,.18f,paper);Quad(v,new Vector2(.08f,.38f),new Vector2(.96f,.38f),new Vector2(.85f,.89f),new Vector2(.02f,.89f),gold);box(.1f,.39f,.79f,.035f,new Color32(255,227,139,255));break;
   case "pc":box(.06f,.09f,.88f,.62f,gray);box(.11f,.14f,.78f,.5f,blue);box(.14f,.17f,.34f,.43f,new Color32(63,180,226,255));box(.42f,.7f,.16f,.13f,gray);box(.23f,.83f,.54f,.06f,gray);break;
   case "bin":box(.23f,.23f,.55f,.65f,new Color32(205,234,245,255));box(.2f,.18f,.61f,.08f,blue);box(.39f,.1f,.24f,.07f,blue);box(.31f,.34f,.07f,.4f,blue);box(.47f,.34f,.07f,.4f,blue);box(.63f,.34f,.07f,.4f,blue);break;
   case "note":case "document":case "sheet":box(.18f,.07f,.64f,.85f,paper);box(.18f,.07f,.08f,.85f,kind=="sheet"?new Color32(31,117,73,255):blue);for(int i=0;i<5;i++)box(.34f,.28f+i*.1f,.35f,.025f,new Color32(124,151,168,255));box(.34f,.15f,.31f,.07f,kind=="sheet"?new Color32(31,117,73,255):blue);break;
   case "calculator":box(.17f,.04f,.67f,.92f,gray);box(.25f,.13f,.51f,.19f,new Color32(160,215,225,255));for(int y=0;y<3;y++)for(int x=0;x<3;x++)box(.25f+x*.18f,.43f+y*.16f,.12f,.1f,x==2?blue:paper);break;
   case "windows":for(int y=0;y<2;y++)for(int x=0;x<2;x++)box(.12f+x*.4f,.12f+y*.4f,.34f,.34f,tint);break;
   case "copy":box(.15f,.12f,.52f,.66f,tint);box(.35f,.34f,.49f,.59f,tint);box(.4f,.39f,.39f,.49f,Color.white);break;
   case "paste":box(.2f,.15f,.61f,.78f,tint);box(.26f,.22f,.49f,.64f,Color.white);box(.34f,.05f,.32f,.22f,tint);break;
   case "search":Ring(v,new Vector2(.42f,.39f),.26f,.045f,tint);Line(v,new Vector2(.61f,.59f),new Vector2(.91f,.91f),.06f,tint);break;
   case "left":case "right":case "up":{Vector2 a=kind=="up"?new Vector2(.5f,.2f):kind=="left"?new Vector2(.2f,.5f):new Vector2(.8f,.5f);Vector2 b=kind=="up"?new Vector2(.2f,.5f):new Vector2(.5f,.2f);Vector2 c=kind=="up"?new Vector2(.8f,.5f):new Vector2(.5f,.8f);Line(v,a,b,.055f,tint);Line(v,a,c,.055f,tint);Line(v,a,kind=="up"?new Vector2(.5f,.88f):new Vector2(1-a.x,.5f),.055f,tint);break;}
   case "close":Line(v,new Vector2(.23f,.23f),new Vector2(.77f,.77f),.045f,tint);Line(v,new Vector2(.77f,.23f),new Vector2(.23f,.77f),.045f,tint);break;
   case "minimize":box(.2f,.68f,.6f,.04f,tint);break;
   case "restore":box(.37f,.14f,.5f,.035f,tint);box(.84f,.14f,.035f,.5f,tint);box(.35f,.14f,.035f,.13f,tint);box(.71f,.61f,.16f,.035f,tint);box(.17f,.32f,.54f,.035f,tint);box(.17f,.32f,.035f,.5f,tint);box(.17f,.79f,.54f,.035f,tint);box(.68f,.32f,.035f,.5f,tint);break;
   case "maximize":box(.22f,.22f,.56f,.035f,tint);box(.22f,.22f,.035f,.56f,tint);box(.22f,.75f,.56f,.035f,tint);box(.75f,.22f,.035f,.56f,tint);break;
   case "power":Ring(v,new Vector2(.5f,.55f),.31f,.05f,tint);box(.46f,.06f,.08f,.47f,tint);break;
   case "volume":box(.1f,.4f,.2f,.26f,tint);Quad(v,new Vector2(.27f,.39f),new Vector2(.52f,.2f),new Vector2(.52f,.85f),new Vector2(.27f,.66f),tint);Line(v,new Vector2(.66f,.29f),new Vector2(.81f,.49f),.04f,tint);Line(v,new Vector2(.81f,.49f),new Vector2(.66f,.73f),.04f,tint);break;
   case "network":box(.12f,.12f,.76f,.51f,tint);box(.18f,.18f,.64f,.36f,new Color32(35,35,35,255));box(.46f,.62f,.07f,.2f,tint);box(.25f,.82f,.5f,.045f,tint);break;
   case "notification":box(.15f,.17f,.7f,.57f,tint);box(.2f,.22f,.6f,.47f,new Color32(35,35,35,255));Line(v,new Vector2(.23f,.7f),new Vector2(.23f,.9f),.045f,tint);Line(v,new Vector2(.23f,.9f),new Vector2(.45f,.7f),.045f,tint);break;
   case "gear":Ring(v,new Vector2(.5f,.5f),.27f,.14f,tint);for(int i=0;i<8;i++){float a=i*Mathf.PI/4;Line(v,new Vector2(.5f,.5f)+new Vector2(Mathf.Cos(a),Mathf.Sin(a))*.27f,new Vector2(.5f,.5f)+new Vector2(Mathf.Cos(a),Mathf.Sin(a))*.43f,.12f,tint);}break;
   case "refresh":Ring(v,new Vector2(.5f,.5f),.28f,.045f,tint);box(.7f,.1f,.08f,.28f,tint);box(.55f,.31f,.22f,.06f,tint);break;
   case "info":Ring(v,new Vector2(.5f,.5f),.35f,.04f,tint);box(.47f,.42f,.06f,.3f,tint);box(.47f,.25f,.06f,.07f,tint);break;
   default:box(.18f,.18f,.64f,.64f,tint);break;
  }
 }
 void Quad(VertexHelper v,Vector2 a,Vector2 b,Vector2 c,Vector2 d,Color color){int i=v.currentVertCount;foreach(var p in new[]{a,b,c,d})v.AddVert(new Vector3(rectTransform.rect.xMin+p.x*rectTransform.rect.width,rectTransform.rect.yMax-p.y*rectTransform.rect.height),color,Vector2.zero);v.AddTriangle(i,i+1,i+2);v.AddTriangle(i,i+2,i+3);}
 void Line(VertexHelper v,Vector2 a,Vector2 b,float width,Color c){var n=new Vector2(-(b-a).y,(b-a).x).normalized*width/2;Quad(v,a+n,b+n,b-n,a-n,c);}
 void Ring(VertexHelper v,Vector2 center,float radius,float width,Color c){for(int i=0;i<32;i++){float a=i*Mathf.PI/16,b=(i+1)*Mathf.PI/16;Quad(v,center+new Vector2(Mathf.Cos(a),Mathf.Sin(a))*(radius-width/2),center+new Vector2(Mathf.Cos(b),Mathf.Sin(b))*(radius-width/2),center+new Vector2(Mathf.Cos(b),Mathf.Sin(b))*(radius+width/2),center+new Vector2(Mathf.Cos(a),Mathf.Sin(a))*(radius+width/2),c);}}
}
public class FactoryDesktopClick : MonoBehaviour,IPointerClickHandler {
 public string itemId;public Action select,open;public Action<Vector2> context;
 public void OnPointerClick(PointerEventData e){if(e.button==PointerEventData.InputButton.Right){context?.Invoke(e.position);return;}select?.Invoke();if(e.clickCount>=2||Application.isMobilePlatform)open?.Invoke();}
}
public class FactoryDesktopDrag : MonoBehaviour,IDragHandler,IPointerDownHandler {
 public RectTransform window;public float width=1148,height=604;public bool locked;public Action focus;
 public void OnPointerDown(PointerEventData e){window.SetAsLastSibling();focus?.Invoke();}
 public void OnDrag(PointerEventData e){if(locked)return;var scale=GetComponentInParent<Canvas>().scaleFactor;var p=window.anchoredPosition+e.delta/scale;p.x=Mathf.Clamp(p.x,0,Mathf.Max(0,width-window.rect.width));p.y=Mathf.Clamp(p.y,-Mathf.Max(0,height-window.rect.height),0);window.anchoredPosition=p;}
}
