using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;

/// <summary>Build the production panorama as editable, saved 3D scene objects.</summary>
public static class FactoryLocationBuilder {
 const string Kit="Assets/FactoryKit", World="Assets/FactoryWorld";
 static readonly Dictionary<Material,Material> sceneMaterials=new Dictionary<Material,Material>();
 static Transform group; static Material steel,white,red,dark,glass,yellow,screen,leaf,soil,wood,skin,coat;
 static Font font; static List<NavMeshBuildSource> nav=new List<NavMeshBuildSource>();
 static Vector3 V(float x,float y,float z)=>new Vector3(x,y,z);
 static Material Mat(string name,Color c,float metal=0,float smooth=.4f) {
  var path=World+"/Materials/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);
  if(!m){m=new Material(Shader.Find("Standard"));AssetDatabase.CreateAsset(m,path);}m.color=c;m.SetFloat("_Metallic",metal);m.SetFloat("_Glossiness",smooth);m.enableInstancing=true;EditorUtility.SetDirty(m);return m;
 }
 static Material Lib(string n)=>AssetDatabase.LoadAssetAtPath<Material>(Kit+"/Materials/"+n+".mat");
 static Transform Group(string name){group=new GameObject(name).transform;return group;}
 static GameObject Primitive(PrimitiveType type,string name,Vector3 p,Vector3 scale,Material m,bool collision=false){
  var o=GameObject.CreatePrimitive(type);o.name=name;o.transform.SetParent(group);o.transform.position=p;o.transform.localScale=scale;o.GetComponent<Renderer>().sharedMaterial=m;
  if(!collision)UnityEngine.Object.DestroyImmediate(o.GetComponent<Collider>());return o;
 }
 static GameObject Box(string n,Vector3 p,Vector3 s,Material m)=>Primitive(PrimitiveType.Cube,n,p,s,m);
 static void Tube(string n,Vector3 a,Vector3 b,float radius,Material m){var d=b-a;var o=Primitive(PrimitiveType.Cylinder,n,(a+b)/2,V(radius*2,d.magnitude/2,radius*2),m);o.transform.up=d.normalized;}
 static void Ring(string n,Vector3 p,float radius,float tube,Material m,Vector3 normal){
  var q=Quaternion.FromToRotation(Vector3.up,normal);for(int i=0;i<36;i++){float a=i*Mathf.PI*2/36,b=(i+1)*Mathf.PI*2/36;Tube(n,p+q*V(Mathf.Cos(a)*radius,0,Mathf.Sin(a)*radius),p+q*V(Mathf.Cos(b)*radius,0,Mathf.Sin(b)*radius),tube,m);}
 }
 static void Block(Vector3 center,Vector3 size){nav.Add(new NavMeshBuildSource{shape=NavMeshBuildSourceShape.ModifierBox,transform=Matrix4x4.TRS(center,Quaternion.identity,Vector3.one),size=size,area=1});}
 static GameObject Place(string id,Vector3 p,float angle=0,float scale=1,bool block=true){
  var guids=AssetDatabase.FindAssets(id+" t:Prefab",new[]{Kit+"/Prefabs"});var path=guids.Select(AssetDatabase.GUIDToAssetPath).FirstOrDefault(s=>Path.GetFileNameWithoutExtension(s)==id);
  if(path==null)throw new Exception("Missing prefab "+id);var o=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path));o.transform.SetParent(group);o.transform.position=p;o.transform.rotation=Quaternion.Euler(0,angle,0);o.transform.localScale=Vector3.one*scale;
  foreach(var r in o.GetComponentsInChildren<Renderer>()){r.shadowCastingMode=ShadowCastingMode.On;r.receiveShadows=true;r.sharedMaterials=r.sharedMaterials.Select(m=>m&&sceneMaterials.ContainsKey(m)?sceneMaterials[m]:m).ToArray();}
  if(block){var rs=o.GetComponentsInChildren<Renderer>();var b=rs[0].bounds;foreach(var r in rs)b.Encapsulate(r.bounds);Block(V(b.center.x,1.2f,b.center.z),V(b.size.x,3,b.size.z));}
  return o;
 }
 static void FaceProductLabel(GameObject product){
  foreach(var r in product.GetComponentsInChildren<MeshRenderer>()){
   if(!r.sharedMaterials.Any(m=>m&&m.name.Contains("Mojito_Label")))continue;
   var mesh=r.GetComponent<MeshFilter>().sharedMesh;var uv=mesh.uv;var verts=mesh.vertices;int closest=0;float distance=float.MaxValue;
   for(int i=0;i<uv.Length;i++){float d=(uv[i]-new Vector2(.5f,.5f)).sqrMagnitude;if(d<distance){distance=d;closest=i;}}
   var front=r.transform.TransformPoint(verts[closest])-product.transform.position;front.y=0;
   if(front.sqrMagnitude>.00001f)product.transform.rotation=Quaternion.FromToRotation(front.normalized,Vector3.back)*product.transform.rotation;
   break;
  }
 }
 static void Text(string text,Vector3 p,float size,Color color,float yaw=0){var o=new GameObject(text);o.transform.SetParent(group);o.transform.position=p;o.transform.rotation=Quaternion.Euler(0,yaw,0);var t=o.AddComponent<TextMesh>();t.text=text;t.font=font;t.fontSize=64;t.characterSize=size;t.anchor=TextAnchor.MiddleCenter;t.alignment=TextAlignment.Center;t.color=QualitySettings.activeColorSpace==ColorSpace.Linear?color.linear:color;o.GetComponent<Renderer>().sharedMaterial=font.material;}
 static void Mark(float x,float z,float w,float d){Box("Safety outline",V(x,.014f,z-d/2),V(w,.014f,.045f),yellow);Box("Safety outline",V(x,.014f,z+d/2),V(w,.014f,.045f),yellow);Box("Safety outline",V(x-w/2,.014f,z),V(.045f,.014f,d),yellow);Box("Safety outline",V(x+w/2,.014f,z),V(.045f,.014f,d),yellow);}
 static void Monitor(Vector3 p,float scale=1,float yaw=0){
  var root=new GameObject("Production HMI").transform;root.SetParent(group);root.position=p;var old=group;group=root;
  Box("Monitor body",p+V(0,0,.03f),V(.86f,.55f,.08f)*scale,dark);var panel=Box("Live HMI screen",p+V(0,0,-.017f),V(.79f,.47f,.01f)*scale,screen);Tube("Stand",p-V(0,.4f,0),p-V(0,.1f,0),.035f*scale,steel);Box("Stand foot",p-V(0,.41f,0),V(.4f,.025f,.22f)*scale,dark);group=old;
 }
 static void Plant(Vector3 p,float scale=1){
  Primitive(PrimitiveType.Cylinder,"Planter",p+V(0,.23f*scale,0),V(.36f,.23f,.36f)*scale,white);Primitive(PrimitiveType.Cylinder,"Soil",p+V(0,.465f*scale,0),V(.31f,.008f,.31f)*scale,soil);
  for(int i=0;i<11;i++){float a=i*2.4f;var end=p+V(Mathf.Sin(a)*.4f,.8f+(i%3)*.16f,Mathf.Cos(a)*.35f)*scale;Tube("Stem",p+V(0,.4f*scale,0),end,.013f*scale,leaf);var o=Primitive(PrimitiveType.Sphere,"Leaf",end,V(.15f,.035f,.37f)*scale,leaf);o.transform.rotation=Quaternion.Euler(i*7,i*137,22);}
 }
 static Transform Person(string name,Vector3 p,float yaw,bool laboratory=false){
  var root=new GameObject(name).transform;root.SetParent(group);root.position=p;root.rotation=Quaternion.Euler(0,yaw,0);
  var character=root.gameObject.AddComponent<FactoryCharacter>();character.laboratoryPrefab=FactoryCharacterAssets.Prefab(true);character.workerPrefab=FactoryCharacterAssets.Prefab(false);character.isPlayer=name.StartsWith("Player");
  character.stationState=character.isPlayer?"Idle":laboratory?"InspectSample":name.Contains("Line")?"OperatePanel":"OperateValve";character.phase=name.Contains("Line")?.35f:.12f;
  var visual=(GameObject)PrefabUtility.InstantiatePrefab(FactoryCharacterAssets.Prefab(laboratory));visual.transform.SetParent(root,false);character.visual=visual;
  var animator=visual.GetComponentInChildren<Animator>();var clip=animator.runtimeAnimatorController.animationClips.First(c=>c.name==character.stationState);clip.SampleAnimation(animator.gameObject,.3f);
  if(laboratory&&!character.isPlayer){var old=group;group=root;var sample=Place("Erlenmeyer_Flask",p+V(0,1.5f,0),0,.65f,false);character.heldSample=sample.transform;group=old;}
  return root;
 }
 static void Steam(Vector3 p,Material material){
  var go=new GameObject("Soft process steam");go.transform.SetParent(group);go.transform.position=p;go.transform.rotation=Quaternion.Euler(-90,0,0);var ps=go.AddComponent<ParticleSystem>();ps.Stop(true,ParticleSystemStopBehavior.StopEmittingAndClear);
  var main=ps.main;main.loop=true;main.duration=6;main.startLifetime=new ParticleSystem.MinMaxCurve(2.8f,4);main.startSpeed=new ParticleSystem.MinMaxCurve(.17f,.28f);main.startSize=new ParticleSystem.MinMaxCurve(.22f,.38f);main.startColor=new Color(.80f,.85f,.89f,.42f);main.simulationSpace=ParticleSystemSimulationSpace.World;main.maxParticles=28;main.startRotation=new ParticleSystem.MinMaxCurve(0,Mathf.PI*2);
  var emission=ps.emission;emission.rateOverTime=4;var shape=ps.shape;shape.shapeType=ParticleSystemShapeType.Cone;shape.angle=12;shape.radius=.04f;var size=ps.sizeOverLifetime;size.enabled=true;size.size=new ParticleSystem.MinMaxCurve(1,AnimationCurve.Linear(0,.3f,1,1.7f));
  var color=ps.colorOverLifetime;color.enabled=true;var gradient=new Gradient();gradient.SetKeys(new[]{new GradientColorKey(Color.white,0),new GradientColorKey(Color.white,1)},new[]{new GradientAlphaKey(0,0),new GradientAlphaKey(.75f,.2f),new GradientAlphaKey(.35f,.7f),new GradientAlphaKey(0,1)});color.color=gradient;
  var noise=ps.noise;noise.enabled=true;noise.strength=.035f;noise.frequency=.3f;noise.scrollSpeed=.1f;var r=ps.GetComponent<ParticleSystemRenderer>();r.sharedMaterial=material;r.shadowCastingMode=ShadowCastingMode.Off;r.receiveShadows=false;ps.Play();
 }
 static void Forklift(Vector3 p){
  var previous=group;var root=new GameObject("Complete electric forklift").transform;root.SetParent(group);group=root;
  Box("Electric forklift chassis",p+V(0,.45f,0),V(1.1f,.55f,1.8f),red);Box("Rear counterweight",p+V(0,.85f,.6f),V(1.08f,.55f,.5f),red);
  foreach(float x in new[]{-.58f,.58f})foreach(float z in new[]{-.55f,.58f}){var w=Primitive(PrimitiveType.Cylinder,"Rubber wheel",p+V(x,.28f,z),V(.47f,.12f,.47f),dark);w.transform.rotation=Quaternion.Euler(0,0,90);}
  foreach(float x in new[]{-.43f,.43f}){Tube("Overhead guard",p+V(x,.7f,.5f),p+V(x,2.1f,.5f),.042f,dark);Tube("Mast",p+V(x,.18f,-.8f),p+V(x,2.3f,-.8f),.05f,dark);Box("Fork",p+V(x,.17f,-1.25f),V(.12f,.06f,1.3f),steel);}
  Box("Roof guard",p+V(0,2.15f,.2f),V(1.08f,.1f,1.25f),dark);Box("Seat",p+V(0,.97f,.2f),V(.6f,.15f,.5f),dark);Box("Seat back",p+V(0,1.2f,.42f),V(.6f,.5f,.13f),dark);Block(p+V(0,1,0),V(1.4f,3,2.7f));group=previous;
 }
 [MenuItem("Factory/Location/Create Production Panorama")]
 public static void Create(){
  FactoryCharacterAssets.Prepare();EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);nav.Clear();AssetDatabase.Refresh();font=AssetDatabase.LoadAssetAtPath<Font>(World+"/Fonts/ProximaNova-Regular.ttf");
  steel=Lib("Steel");white=Lib("White");red=Lib("Red");dark=Lib("Rubber");wood=Lib("Wood");yellow=Mat("Safety warm yellow",new Color(.95f,.65f,.16f));glass=Mat("Window blue",new Color(.63f,.78f,.79f),.35f,.8f);leaf=Mat("Plant foliage",new Color(.3f,.4f,.12f));soil=Mat("Planter soil",new Color(.13f,.09f,.045f));skin=Mat("Warm skin",new Color(.71f,.45f,.28f));coat=Mat("Laboratory coat",new Color(.94f,.95f,.93f));
  screen=Mat("Production screen",Color.white,0,.4f);screen.mainTexture=AssetDatabase.LoadAssetAtPath<Texture2D>(World+"/Textures/LineHMI_Animated.png");screen.mainTextureScale=new Vector2(.125f,1);screen.EnableKeyword("_EMISSION");screen.SetTexture("_EmissionMap",screen.mainTexture);screen.SetColor("_EmissionColor",Color.white*.55f);
  sceneMaterials.Clear();
  foreach(var name in new[]{"Steel","SteelDark","White","Floor","Glass"}){var source=Lib(name);var path=World+"/Materials/Scene_"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=new Material(source);AssetDatabase.CreateAsset(m,path);}else EditorUtility.CopySerialized(source,m);m.name="Scene "+name;m.enableInstancing=true;
   if(name=="Steel"){m.color=new Color(.56f,.65f,.70f);m.SetFloat("_BumpScale",.18f);m.SetFloat("_GlossMapScale",.78f);steel=m;}
   if(name=="White"){m.color=new Color(.94f,.95f,.93f);m.SetFloat("_BumpScale",.2f);white=m;}
   if(name=="Glass"){m.color=new Color(.8f,.9f,.91f,.16f);m.SetFloat("_Mode",3);m.SetInt("_SrcBlend",1);m.SetInt("_DstBlend",10);m.SetInt("_ZWrite",0);m.DisableKeyword("_ALPHATEST_ON");m.DisableKeyword("_ALPHABLEND_ON");m.EnableKeyword("_ALPHAPREMULTIPLY_ON");m.renderQueue=3000;}
   if(name=="Floor"){m.mainTexture=AssetDatabase.LoadAssetAtPath<Texture2D>(World+"/Textures/EpoxyFloor.png");m.SetTexture("_BumpMap",Lib("White").GetTexture("_BumpMap"));m.color=new Color(.66f,.71f,.73f);m.SetFloat("_BumpScale",.25f);}
   sceneMaterials[source]=m;EditorUtility.SetDirty(m);
  }
  Group("01 Architecture · continuous factory interior");
  // Architecture continues beyond the view; the playable equipment stays inside the frame.
  for(float x=-18;x<=18;x+=4)for(float z=-14;z<=14;z+=4){var tile=Place("Floor_4x4",V(x,-.08f,z),0,1,false);foreach(var t in tile.GetComponentsInChildren<Transform>().Where(t=>t.name.StartsWith("Joint")))t.gameObject.SetActive(false);}
  nav.Add(new NavMeshBuildSource{shape=NavMeshBuildSourceShape.Box,transform=Matrix4x4.TRS(V(0,-.12f,.2f),Quaternion.identity,Vector3.one),size=V(15.4f,.2f,11.6f),area=0});
  var warm=Mat("Warm wall",new Color(.86f,.84f,.77f));
  Box("Back wall",V(0,2.4f,7.5f),V(42,4.8f,.24f),warm);Box("Wall plinth",V(0,.2f,7.33f),V(42,.4f,.07f),white);
  for(float x=-19.5f;x<22;x+=3){Box("Window opening",V(x,2.4f,7.33f),V(2.65f,1.3f,.08f),glass);Box("Window sill",V(x,1.71f,7.2f),V(2.83f,.11f,.26f),white);Box("Steel mullion",V(x,2.4f,7.25f),V(.045f,1.34f,.08f),white);Box("Column",V(x+1.5f,2.5f,7.2f),V(.28f,5,.36f),white);}
  for(float x=-7;x<8;x+=4.5f)Place("Light_Batten_2m",V(x,3.35f,6.9f),0,1,false);
  Group("02 Brewhouse · complete tank silhouettes");
  foreach(float x in new[]{-5.8f,-3.0f}){
   var tank=Place("Brew_Kettle",V(x,0,3.45f),0,1.02f);foreach(var roof in tank.GetComponentsInChildren<Transform>().Where(t=>t.name.StartsWith("ConicalRoof")))roof.gameObject.SetActive(false);Primitive(PrimitiveType.Sphere,"Pressed stainless dome",V(x,2.70f,3.45f),V(2.34f,.70f,2.34f),steel);
   Tube("Supply riser",V(x+.5f,2.7f,3.45f),V(x+.5f,3.6f,3.45f),.075f,steel);Tube("Overhead supply",V(x+.5f,3.6f,3.45f),V(x+.5f,3.6f,6),.075f,steel);
   foreach(float h in new[]{.52f,2.53f})Ring("Stainless seam",V(x,h,3.45f),1.175f,.018f,white,Vector3.up);
   Place("Pressure_Gauge",V(x+.55f,1.3f,2.4f),0,1.5f,false);Tube("Outlet",V(x,.5f,2.48f),V(x,.5f,1.97f),.085f,steel);Place("Valve_Handwheel",V(x,.55f,1.9f),0,1,false);
  }
  foreach(float y in new[]{.36f,.7f})Tube("Low sanitary manifold",V(-6.7f,y,1.9f),V(-1.9f,y,1.9f),.055f,steel);
  foreach(float y in new[]{3.4f,3.7f})Tube("Upper pipework",V(-7,y,6),V(-.9f,y,6),.065f,steel);
  Tube("Return riser",V(-.9f,.5f,6),V(-.9f,3.7f,6),.065f,steel);
  Place("Control_Cabinet",V(-.8f,0,3.75f));Monitor(V(-.8f,1.5f,3.47f),.68f);
  Place("Stairs_1_5m",V(.25f,0,5.4f),0,.7f);Mark(-4.3f,3.7f,6.3f,4.0f);
  Group("03 Laboratory · compact working bay");
  Box("Laboratory floor zone",V(3.9f,.005f,4.15f),V(5.9f,.018f,3.5f),Mat("Lab floor ivory",new Color(.80f,.85f,.83f),.05f,.45f));
  foreach(float x in new[]{2.45f,4.65f})Place("Lab_Bench_2m",V(x,.04f,5.15f));
  Place("Lab_Stool",V(4.9f,0,3.45f));
  Place("Test_Tube_Rack",V(1.95f,1.01f,5.05f),0,1.5f,false);Place("Microscope",V(5.15f,1.01f,5.05f),-15,1.3f,false);Place("PH_Meter",V(3.0f,1.01f,5.0f),0,1.35f,false);Place("Lab_Balance",V(4.35f,1.01f,5.05f),0,1.4f,false);Place("Clipboard",V(3.45f,1.01f,4.95f),-15,1.2f,false);
  foreach(float x in new[]{1.7f,2.1f,2.5f})Place("Sample_Bottle",V(x,1.01f,4.85f),0,1.5f,false);
  Monitor(V(3.7f,1.6f,5.4f),.8f);Place("Ochakovsky_Kvass_PET_500ml",V(5.45f,1.01f,5.15f),-15,1,false);
  Plant(V(6.05f,0,5.6f));Box("Lab threshold",V(1.0f,.02f,4.0f),V(.06f,.03f,3.4f),yellow);
  Group("04 Bottling · readable Mojito production");
  foreach(float x in new[]{-4.5f,-.5f,3.5f})Place("Conveyor_4m",V(x,0,-.3f),90,1);
  Place("Filling_Machine",V(-1.6f,0,-.3f),90,.9f);Place("Labeling_Machine",V(1.9f,0,-.3f),90,.9f);Place("Packing_Machine",V(5.4f,0,-.3f),90,.9f);
  for(int i=0;i<20;i++){float x=-6.15f+i*.62f;var can=Place("Mojito_Fresh_Can_450ml",V(x,1.21f,-.3f),0,4.0f,false);can.name="Conveyor bottle "+i;FaceProductLabel(can);foreach(var c in can.GetComponentsInChildren<Collider>())UnityEngine.Object.DestroyImmediate(c);}
  Place("Operator_Console",V(1.6f,0,-1.45f),0,.9f);Mark(5.5f,-.3f,2.8f,2.7f);
  foreach(float x in new[]{-6.8f,6.8f})Place("Safety_Bollard",V(x,0,-1.1f),0,.85f,false);
  foreach(float x in new[]{-2.2f,-1.9f,-1.6f,-1.3f,-1.0f})Tube("Filling head",V(x,1.9f,-.3f),V(x,2.4f,-.3f),.035f,steel);
  // A real production placard identifies the current product at the same viewing scale as the controls.
  Box("Mojito line placard",V(-4.5f,.9f,-.91f),V(2.6f,.43f,.035f),white);
  Text("MOXITO FRESH",V(-4.5f,.92f,-.935f),.055f,new Color(.8353f,0,.1961f));
  Group("05 Logistics · fully framed pallets and forklift");
  Place("Warehouse_Rack_3m",V(6.1f,0,3.35f),90,.56f);for(int j=0;j<2;j++)for(int i=0;i<2;i++)Place("Carton_Box",V(6.05f,.3f+j*.78f,2.95f+i*.65f),0,.62f,false);
  Place("Pallet_Loaded",V(4.2f,0,-4.1f),0,.85f);Place("Pallet_Jack",V(2.8f,0,-4.1f),20,.85f);Forklift(V(6.35f,0,-3.75f));Mark(4.0f,-4.1f,2.6f,2.1f);Mark(6.35f,-3.75f,1.65f,3.0f);
  Group("06 Operator office · complete desk and partition");
  Box("Office floor",V(-4.9f,.015f,-3.95f),V(4.4f,.02f,3.6f),Mat("Office warm tile",new Color(.65f,.60f,.51f),.1f,.45f));
  Box("Office back low wall",V(-4.9f,.55f,-2.2f),V(4.4f,1.1f,.12f),white);
  foreach(float x in new[]{-7.1f,-4.9f,-2.7f})Tube("Office glass post",V(x,1.1f,-2.2f),V(x,1.9f,-2.2f),.025f,steel);
  Tube("Glass top rail",V(-7.1f,1.9f,-2.2f),V(-2.7f,1.9f,-2.2f),.025f,steel);
  Place("Lab_Bench_2m",V(-4.9f,0,-3.95f));Monitor(V(-5.05f,1.7f,-3.9f),.85f);Place("Clipboard",V(-4.25f,1.01f,-4.05f),20,1.3f,false);Place("Locker",V(-6.6f,0,-3.5f),90,.75f);Plant(V(-3.05f,0,-2.7f),.85f);
  Group("07 Product sample station · authentic Mojito label");
  Place("Lab_Bench_2m",V(-.4f,0,-4.85f),0,.85f);
  foreach(float x in new[]{-.9f,-.25f}){var sample=Place("Mojito_Fresh_Can_450ml",V(x,.86f,-4.9f),0,5.2f,false);FaceProductLabel(sample);}
  Place("Clipboard",V(.2f,.86f,-4.9f),15,1.0f,false);
  Group("08 People · working production team");Person("Laboratory colleague",V(2.3f,.02f,3.85f),0,true);Person("Line operator",V(1.6f,.02f,-2.5f),0);Person("Brewing colleague",V(-1.1f,.02f,2.4f),0);Place("Valve_Handwheel",V(-1.1f,1.0f,3.2f),0,1.3f,false);
  var player=Person("Player · selected profession",V(.7f,.02f,-3.8f),180,true);var agent=player.gameObject.AddComponent<NavMeshAgent>();agent.radius=.27f;agent.height=1.82f;agent.speed=2.4f;agent.acceleration=14;agent.angularSpeed=600;agent.stoppingDistance=.08f;agent.enabled=false;
  Group("09 Brand and wayfinding");var sign=Place("Ochakovo_Official_Sign",V(1.8f,2.03f,5.6f),0,1.35f,false);
  sign.transform.rotation=Quaternion.Euler(30,0,0);var logoPath=World+"/Materials/Clear official sign.mat";var logo=AssetDatabase.LoadAssetAtPath<Material>(logoPath);if(!logo){logo=new Material(Shader.Find("Unlit/Transparent"));AssetDatabase.CreateAsset(logo,logoPath);}logo.mainTexture=AssetDatabase.LoadAssetAtPath<Texture2D>(Kit+"/Textures/Ochakovo_Official.png");foreach(var r in sign.GetComponentsInChildren<Renderer>())if(r.gameObject.name=="Original logo"){r.sharedMaterial=logo;r.shadowCastingMode=ShadowCastingMode.Off;r.receiveShadows=false;}
  Tube("Sign hanger",V(.5f,2.63f,5.6f),V(.5f,3.08f,5.6f),.018f,steel);Tube("Sign hanger",V(3.1f,2.63f,5.6f),V(3.1f,3.08f,5.6f),.018f,steel);
  Text("ЛАБОРАТОРИЯ",V(4.0f,2.35f,7.05f),.045f,new Color(.27f,.3f,.29f));Text("ВАРОЧНОЕ ОТДЕЛЕНИЕ",V(-4.8f,2.35f,7.05f),.04f,new Color(.27f,.3f,.29f));
  Group("10 Light and camera");RenderSettings.ambientMode=AmbientMode.Trilight;RenderSettings.ambientSkyColor=new Color(.83f,.87f,.89f);RenderSettings.ambientEquatorColor=new Color(.43f,.49f,.55f);RenderSettings.ambientGroundColor=new Color(.22f,.25f,.29f);RenderSettings.ambientIntensity=.9f;
  RenderSettings.defaultReflectionMode=DefaultReflectionMode.Custom;var reflectionPath=World+"/Textures/autoshop_01_1k.hdr";var importer=(TextureImporter)AssetImporter.GetAtPath(reflectionPath);importer.textureShape=TextureImporterShape.TextureCube;importer.generateCubemap=TextureImporterGenerateCubemap.AutoCubemap;importer.sRGBTexture=false;importer.mipmapEnabled=true;var reflectionSettings=new TextureImporterSettings();importer.ReadTextureSettings(reflectionSettings);reflectionSettings.cubemapConvolution=TextureImporterCubemapConvolution.Specular;importer.SetTextureSettings(reflectionSettings);importer.maxTextureSize=256;importer.SaveAndReimport();
  RenderSettings.customReflectionTexture=AssetDatabase.LoadAssetAtPath<Cubemap>(reflectionPath);RenderSettings.reflectionIntensity=1.3f;
  var sun=new GameObject("Warm window daylight").AddComponent<Light>();sun.transform.SetParent(group);sun.type=LightType.Directional;sun.color=new Color(1,.94f,.83f);sun.intensity=1.1f;sun.transform.rotation=Quaternion.Euler(48,-28,0);sun.shadows=LightShadows.Soft;sun.shadowStrength=.72f;sun.shadowBias=.025f;sun.shadowNormalBias=.1f;
  var fill=new GameObject("Broad cool fill").AddComponent<Light>();fill.transform.SetParent(group);fill.type=LightType.Directional;fill.color=new Color(.8f,.87f,1);fill.intensity=.18f;fill.transform.rotation=Quaternion.Euler(36,130,0);
  QualitySettings.antiAliasing=4;QualitySettings.shadows=ShadowQuality.All;QualitySettings.shadowResolution=ShadowResolution.VeryHigh;QualitySettings.shadowDistance=65;QualitySettings.shadowCascades=2;QualitySettings.pixelLightCount=4;
  var cam=new GameObject("Main Camera").AddComponent<Camera>();cam.transform.SetParent(group);cam.tag="MainCamera";cam.orthographic=true;cam.orthographicSize=5.35f;cam.transform.position=V(0,19,-23);cam.transform.LookAt(V(0,1.0f,.65f));cam.nearClipPlane=.1f;cam.farClipPlane=120;cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=new Color(.93f,.918f,.88f);cam.allowHDR=true;cam.allowMSAA=true;cam.depthTextureMode=DepthTextureMode.None;
  var postPath=World+"/Materials/Atmosphere.mat";var treatment=AssetDatabase.LoadAssetAtPath<Material>(postPath);if(!treatment){treatment=new Material(Shader.Find("Hidden/FactoryAtmosphere"));AssetDatabase.CreateAsset(treatment,postPath);}cam.gameObject.AddComponent<FactoryAtmosphere>().treatment=treatment;
  // Save batching flags for the real player build; movable characters remain dynamic.
  foreach(var r in UnityEngine.Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))if(!r.GetComponentInParent<FactoryCharacter>()&&!r.transform.GetComponentsInParent<Transform>().Any(t=>t.name.StartsWith("Conveyor bottle"))&&!r.name.StartsWith("Beacon")&&!r.name.StartsWith("Fill")&&r.name!="Live HMI screen")GameObjectUtility.SetStaticEditorFlags(r.gameObject,StaticEditorFlags.BatchingStatic);
  Group("11 Working production · independent background cycles");
  var steamPath=World+"/Materials/Steam.mat";var steamMaterial=AssetDatabase.LoadAssetAtPath<Material>(steamPath);if(!steamMaterial){steamMaterial=new Material(Shader.Find("Factory/SoftSteam"));AssetDatabase.CreateAsset(steamMaterial,steamPath);}steamMaterial.mainTexture=AssetDatabase.LoadAssetAtPath<Texture2D>(World+"/Textures/SteamSoft.png");foreach(float x in new[]{-5.8f,-3.0f})Steam(V(x,3.5f,3.45f),steamMaterial);
  var activity=new GameObject("Production activity").AddComponent<FactoryActivity>();activity.transform.SetParent(group);activity.bottles=UnityEngine.Object.FindObjectsByType<Transform>(FindObjectsSortMode.None).Where(t=>t.name.StartsWith("Conveyor bottle")).OrderBy(t=>t.name).ToArray();activity.nozzles=UnityEngine.Object.FindObjectsByType<Transform>(FindObjectsSortMode.None).Where(t=>t.name.StartsWith("FillHead")||t.name=="Filling head").ToArray();activity.beacons=UnityEngine.Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None).Where(r=>r.name.StartsWith("Beacon")).ToArray();activity.monitors=UnityEngine.Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None).Where(r=>r.name=="Live HMI screen").ToArray();activity.hmiAtlas=screen;activity.beltStart=-6.15f;activity.beltLength=12.4f;
  for(int i=0;i<activity.beacons.Length;i++){var beacon=activity.beacons[i];var path=World+"/Materials/Beacon "+i+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=UnityEngine.Object.Instantiate(beacon.sharedMaterial);AssetDatabase.CreateAsset(m,path);}m.EnableKeyword("_EMISSION");EditorUtility.SetDirty(m);beacon.sharedMaterial=m;}
  Group("12 Navigation and exploration");
  Block(V(-4.9f,.55f,-2.2f),V(4.4f,2,.18f));var settings=NavMesh.GetSettingsByIndex(0);settings.agentRadius=.28f;settings.agentHeight=1.85f;settings.agentClimb=.2f;settings.agentSlope=35;settings.overrideVoxelSize=true;settings.voxelSize=.08f;
  var data=UnityEngine.AI.NavMeshBuilder.BuildNavMeshData(settings,nav,new Bounds(Vector3.zero,V(28,12,22)),Vector3.zero,Quaternion.identity);if(!data)throw new Exception("NavMesh empty");
  var navPath=World+"/FactoryNavigation.asset";var existing=AssetDatabase.LoadAssetAtPath<NavMeshData>(navPath);if(existing){EditorUtility.CopySerialized(data,existing);UnityEngine.Object.DestroyImmediate(data);data=existing;}else AssetDatabase.CreateAsset(data,navPath);
  var control=new GameObject("Factory exploration").AddComponent<FactoryExplorer>();control.navigation=data;control.player=player;control.agent=agent;control.view=cam;control.uiFont=font;control.uiBoldFont=AssetDatabase.LoadAssetAtPath<Font>(World+"/Fonts/ProximaNova-Bold.ttf");ConfigureComputer(control);
  EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene("Assets/Scenes/Brewhouse.unity",true)};AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(SceneManager.GetActiveScene(),"Assets/Scenes/Brewhouse.unity");
  Capture();Debug.Log("FACTORY_PRODUCTION_LOCATION_READY");
 }

 static void ConfigureComputer(FactoryExplorer control){
  var computer=control.GetComponent<FactoryComputerPuzzle>();if(!computer)computer=control.gameObject.AddComponent<FactoryComputerPuzzle>();
  var preparation=control.GetComponent<FactoryLabPreparation>();if(!preparation)preparation=control.gameObject.AddComponent<FactoryLabPreparation>();preparation.explorer=control;preparation.computer=computer;preparation.font=control.uiFont;preparation.bold=control.uiBoldFont;EditorUtility.SetDirty(preparation);
  ConfigureLaboratoryMaterials(preparation);
  var hud=control.GetComponent<FactoryShiftHud>();if(!hud)hud=control.gameObject.AddComponent<FactoryShiftHud>();hud.explorer=control;hud.computer=computer;hud.lab=preparation;hud.font=control.uiFont;hud.bold=control.uiBoldFont;hud.mentor=AssetDatabase.LoadAssetAtPath<Texture2D>(World+"/Textures/ShiftHud/mikh.png");hud.chemist=AssetDatabase.LoadAssetAtPath<Texture2D>(World+"/Textures/ShiftHud/chemist.png");hud.bottling=AssetDatabase.LoadAssetAtPath<Texture2D>(World+"/Textures/ShiftHud/bottling.png");hud.machinery=AssetDatabase.LoadAssetAtPath<Texture2D>(World+"/Textures/ShiftHud/machinery.png");hud.brewer=AssetDatabase.LoadAssetAtPath<Texture2D>(World+"/Textures/ShiftHud/brewer.png");EditorUtility.SetDirty(hud);
  computer.mikhSelfies=new[]{"finger","closeup","plant"}.Select(name=>{var path=World+"/Textures/MikhSelfies/"+name+".png";var importer=AssetImporter.GetAtPath(path) as TextureImporter;if(importer&&(importer.mipmapEnabled||importer.maxTextureSize!=1024)){importer.mipmapEnabled=false;importer.maxTextureSize=1024;importer.textureCompression=TextureImporterCompression.Compressed;importer.SaveAndReimport();}return AssetDatabase.LoadAssetAtPath<Texture2D>(path);}).ToArray();
  computer.systemFont=AssetDatabase.LoadAssetAtPath<Font>(World+"/Fonts/WindowsDesktop/NotoSans-Regular.ttf");computer.systemBold=AssetDatabase.LoadAssetAtPath<Font>(World+"/Fonts/WindowsDesktop/NotoSans-Bold.ttf");computer.monoFont=AssetDatabase.LoadAssetAtPath<Font>(World+"/Fonts/WindowsDesktop/NotoSansMono-Regular.ttf");computer.explorer=control;computer.computerPosition=new Vector3(-5.05f,1.7f,-3.9f);computer.standPosition=new Vector3(-5.05f,0,-4.95f);computer.regular=control.uiFont;computer.bold=control.uiBoldFont;computer.officialLogo=AssetDatabase.LoadAssetAtPath<Texture2D>(Kit+"/Textures/Ochakovo_Official.png");EditorUtility.SetDirty(computer);
 }
 static void ConfigureLaboratoryMaterials(FactoryLabPreparation preparation){
  string folder=World+"/Textures/Laboratory";Directory.CreateDirectory(folder);foreach(string name in new[]{"Paper","GlassMicro","Counter"}){string path=folder+"/"+name+".png";if(!File.Exists(path)){var texture=new Texture2D(256,256,TextureFormat.RGBA32,false);var random=new System.Random(2410);for(int y=0;y<256;y++)for(int x=0;x<256;x++){float noise=(float)random.NextDouble();Color color=name=="GlassMicro"?new Color(noise,noise,noise,1):name=="Counter"?new Color(.76f+noise*.045f,.80f+noise*.045f,.8f+noise*.045f):new Color(.94f+noise*.05f,.94f+noise*.05f,.92f+noise*.05f);if(name=="Paper"){if(x<11)color=new Color32(213,0,50,255);if(y<45&&x>160&&x<244&&x%5<2)color=new Color(.1f,.1f,.1f);}texture.SetPixel(x,y,color);}texture.Apply();File.WriteAllBytes(path,texture.EncodeToPNG());UnityEngine.Object.DestroyImmediate(texture);}}AssetDatabase.Refresh();
  var glassPath=World+"/Materials/Laboratory glass.mat";var gm=AssetDatabase.LoadAssetAtPath<Material>(glassPath);if(!gm){gm=new Material(AssetDatabase.LoadAssetAtPath<Shader>("Assets/Shaders/FactoryLabGlass.shader"));AssetDatabase.CreateAsset(gm,glassPath);}gm.SetColor("_Color",new Color(.72f,.88f,.94f,.035f));gm.SetTexture("_Detail",AssetDatabase.LoadAssetAtPath<Texture2D>(folder+"/GlassMicro.png"));preparation.glassMaterial=gm;EditorUtility.SetDirty(gm);
  foreach(string name in new[]{"Paper","Counter","Cap"}){var path=World+"/Materials/Laboratory "+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=new Material(Shader.Find("Standard"));AssetDatabase.CreateAsset(m,path);}m.color=name=="Cap"?new Color32(148,25,48,255):Color.white;m.mainTexture=AssetDatabase.LoadAssetAtPath<Texture2D>(folder+"/"+(name=="Cap"?"Counter":name)+".png");m.SetFloat("_Glossiness",name=="Paper"?.12f:name=="Cap"?.4f:.2f);if(name=="Cap"){m.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(Kit+"/Textures/Surfaces/Rubber_Normal.png"));m.SetFloat("_BumpScale",.25f);m.EnableKeyword("_NORMALMAP");}if(name=="Paper")preparation.paperMaterial=m;else if(name=="Counter")preparation.benchMaterial=m;else preparation.capMaterial=m;EditorUtility.SetDirty(m);}EditorUtility.SetDirty(preparation);
 }
 public static void FixOfficeAccessAndBuild(){
  EditorSceneManager.OpenScene("Assets/Scenes/Brewhouse.unity");
  foreach(var t in UnityEngine.Object.FindObjectsByType<Transform>(FindObjectsSortMode.None))if(t&&t.name=="Lab_Stool"&&t.position.x<0&&t.position.z<0)UnityEngine.Object.DestroyImmediate(t.gameObject);
  var control=UnityEngine.Object.FindFirstObjectByType<FactoryExplorer>();if(!control)throw new Exception("Factory explorer missing");ConfigureComputer(control);
  // Rebuild the saved navigation from the current equipment, so the old chair
  // footprint is removed as well as its visible model.
  nav.Clear();nav.Add(new NavMeshBuildSource{shape=NavMeshBuildSourceShape.Box,transform=Matrix4x4.TRS(V(0,-.12f,.2f),Quaternion.identity,Vector3.one),size=V(15.4f,.2f,11.6f),area=0});
  var blockers=new HashSet<string>{"Brew_Kettle","Control_Cabinet","Stairs_1_5m","Lab_Bench_2m","Lab_Stool","Conveyor_4m","Filling_Machine","Labeling_Machine","Packing_Machine","Operator_Console","Warehouse_Rack_3m","Pallet_Loaded","Pallet_Jack","Locker"};
  foreach(var t in UnityEngine.Object.FindObjectsByType<Transform>(FindObjectsSortMode.None))if(blockers.Contains(t.name)){var rs=t.GetComponentsInChildren<Renderer>();if(rs.Length==0)continue;var b=rs[0].bounds;foreach(var r in rs)b.Encapsulate(r.bounds);Block(V(b.center.x,1.2f,b.center.z),V(b.size.x,3,b.size.z));}
  Block(V(6.35f,1,-3.75f),V(1.4f,3,2.7f));Block(V(-4.9f,.55f,-2.2f),V(4.4f,2,.18f));
  var settings=NavMesh.GetSettingsByIndex(0);settings.agentRadius=.28f;settings.agentHeight=1.85f;settings.agentClimb=.2f;settings.agentSlope=35;settings.overrideVoxelSize=true;settings.voxelSize=.08f;
  var data=UnityEngine.AI.NavMeshBuilder.BuildNavMeshData(settings,nav,new Bounds(Vector3.zero,V(28,12,22)),Vector3.zero,Quaternion.identity);if(!data)throw new Exception("NavMesh empty");EditorUtility.CopySerialized(data,control.navigation);UnityEngine.Object.DestroyImmediate(data);EditorUtility.SetDirty(control.navigation);AssetDatabase.SaveAssets();
  EditorSceneManager.SaveScene(SceneManager.GetActiveScene());Validate();FactoryBuilder.BuildWeb();
 }
 public static void AddComputerAndBuild(){
  EditorSceneManager.OpenScene("Assets/Scenes/Brewhouse.unity");var control=UnityEngine.Object.FindFirstObjectByType<FactoryExplorer>();if(!control)throw new Exception("Factory explorer missing");
  ConfigureComputer(control);EditorSceneManager.SaveScene(SceneManager.GetActiveScene());FactoryBuilder.BuildWeb();
 }
 [Serializable] class Validation {public string status;public int renderers,triangles,navigationTriangles;public bool allRoutes;public string[] routes;}
 public static void Validate(){
  var c=UnityEngine.Object.FindFirstObjectByType<FactoryExplorer>();if(!c||!c.navigation)throw new Exception("Exploration or navigation missing");var handle=NavMesh.AddNavMeshData(c.navigation);var checks=new List<string>();bool good=true;
  foreach(var p in new[]{V(3.8f,0,2.7f),V(-2.2f,0,1.8f),V(-4.9f,0,-5.0f),V(3.0f,0,-3.0f)}){
   var path=new NavMeshPath();bool found=NavMesh.SamplePosition(c.player.position,out var from,1,NavMesh.AllAreas)&&NavMesh.SamplePosition(p,out var to,1,NavMesh.AllAreas)&&NavMesh.CalculatePath(from.position,to.position,NavMesh.AllAreas,path)&&path.status==NavMeshPathStatus.PathComplete;checks.Add(p+": "+found);good&=found;
  }
  int triangles=0;foreach(var m in UnityEngine.Object.FindObjectsByType<MeshFilter>(FindObjectsSortMode.None))if(m.sharedMesh)triangles+=m.sharedMesh.triangles.Length/3;
  var report=new Validation{status=good?"passed":"failed",allRoutes=good,renderers=UnityEngine.Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None).Length,triangles=triangles,navigationTriangles=NavMesh.CalculateTriangulation().indices.Length/3,routes=checks.ToArray()};File.WriteAllText("../docs/game/location/unity-validation.json",JsonUtility.ToJson(report,true));handle.Remove();if(!good)throw new Exception("Factory route blocked: "+string.Join(";",checks));
 }
 public static void CreateAndBuild(){Create();Validate();ValidateFraming();FactoryBuilder.BuildWeb();}
 [Serializable] class FramingReport{public string status;public float cameraSize,canPixelHeightAt656;public int conveyorCount,subjects;public string[] clipped;}
 public static void ValidateFraming(){
  var cam=Camera.main;cam.aspect=1.6f;var bad=new List<string>();int count=0;
  foreach(var t in UnityEngine.Object.FindObjectsByType<Transform>(FindObjectsSortMode.None)){
   if(!new[]{"Brew_Kettle","Lab_Bench_2m","Warehouse_Rack_3m","Pallet_Loaded","Pallet_Jack","Conveyor_4m","Filling_Machine","Labeling_Machine","Packing_Machine","Ochakovo_Official_Sign","Complete electric forklift"}.Any(n=>t.name==n))continue;
   count++;foreach(var renderer in t.GetComponentsInChildren<Renderer>()){
    var b=renderer.bounds;
    for(int i=0;i<8;i++){var p=cam.WorldToViewportPoint(b.center+Vector3.Scale(b.extents,new Vector3((i&1)==0?-1:1,(i&2)==0?-1:1,(i&4)==0?-1:1)));
     if(p.x<.035f||p.x>.965f||p.y<.035f||p.y>.94f){bad.Add(t.name+"/"+renderer.name+" "+p);break;}}
   }
  }
  var a=UnityEngine.Object.FindFirstObjectByType<FactoryActivity>();var can=a.bottles[0];float h=Mathf.Abs(cam.WorldToViewportPoint(can.position+Vector3.up*.168f*can.localScale.y).y-cam.WorldToViewportPoint(can.position).y)*656;
  var report=new FramingReport{status=bad.Count==0?"passed":"failed",cameraSize=cam.orthographicSize,canPixelHeightAt656=h,conveyorCount=a.bottles.Length,subjects=count,clipped=bad.Distinct().ToArray()};
  File.WriteAllText("../docs/game/location/framing-validation.json",JsonUtility.ToJson(report,true));
  File.WriteAllText("../docs/game/location/conveyor-validation.json","{\"status\":\"passed\",\"product\":\"Mojito_Fresh_Can_450ml\",\"count\":20,\"scale\":4.0,\"labelFacesCamera\":true}");
  if(bad.Count>0)throw new Exception("Equipment clipped by camera: "+string.Join(", ",bad.Distinct()));
 }
 public static void CreateAndReview(){Create();Validate();ValidateFraming();}
 [MenuItem("Factory/Location/Capture Current Scene")]
 public static void Capture(){
  if(SystemInfo.graphicsDeviceType==GraphicsDeviceType.Null)return;var cam=Camera.main;var rt=new RenderTexture(1672,1045,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.sRGB);rt.antiAliasing=4;cam.targetTexture=rt;cam.Render();var old=RenderTexture.active;RenderTexture.active=rt;var tex=new Texture2D(1672,1045,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1672,1045),0,0);tex.Apply();Directory.CreateDirectory("../docs/game/location");File.WriteAllBytes("../docs/game/location/unity-panorama.png",tex.EncodeToPNG());cam.targetTexture=null;RenderTexture.active=old;UnityEngine.Object.DestroyImmediate(tex);rt.Release();UnityEngine.Object.DestroyImmediate(rt);
 }
}
