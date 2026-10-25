using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

/// <summary>Editor-only asset preparation. Never modifies Brewhouse or build settings.</summary>
public static class FactoryAssetLibrary
{
    const string Kit = "Assets/FactoryKit";
    const string ThirdParty = "Assets/ThirdParty/Kenney";
    [Serializable] public class Catalog { public Entry[] assets; }
    [Serializable] public class Entry {
        public string id, category, label, path, collision, lodPath;
        public float[] size;
        public int triangles, renderers;
    }
    [Serializable] public class ProductCatalog { public Entry[] assets; public ProductMaterial[] materials; }
    [Serializable] public class ProductMaterial { public string name, texture; public float[] color; public float metallic, smoothness; }
    [Serializable] class Check {
        public string id, path;
        public int triangles, renderers, colliders;
        public Vector3 size;
    }
    [Serializable] class Verification {
        public int originalPrefabs, thirdPartyPrefabs;
        public string unityVersion, status;
        public Check[] originals;
        public string[] errors;
    }
    static readonly Dictionary<string, Color> Colors = new Dictionary<string, Color> {
        {"Steel", new Color(.56f,.62f,.64f)}, {"SteelDark", new Color(.20f,.25f,.27f)},
        {"White",new Color(.88f,.87f,.83f)}, {"Red",new Color(213/255f,0,50/255f)},
        {"Rubber",new Color(.028f,.033f,.038f)}, {"Glass",new Color(.48f,.73f,.75f)},
        {"Screen",new Color(.025f,.13f,.17f)}, {"ScreenLight",new Color(.30f,.78f,.76f)},
        {"Amber",new Color(.29f,.085f,.018f)}, {"Wood",new Color(.48f,.29f,.12f)},
        {"Cardboard",new Color(.66f,.46f,.25f)}, {"SafetyYellow",new Color(.95f,.57f,.035f)},
        {"Green",new Color(.15f,.31f,.075f)}, {"Grape",new Color(.14f,.06f,.19f)},
        {"Floor",new Color(.69f,.67f,.61f)}
    };
    static readonly Dictionary<string,string> Surfaces = new Dictionary<string,string> {
        {"Steel","BrushedSteel"},{"SteelDark","BrushedSteel"},{"Floor","FactoryTile"},
        {"White","PaintedMetal"},{"Red","PaintedMetal"},{"Rubber","Rubber"},
        {"Wood","WoodGrain"},{"Cardboard","KraftCardboard"}
    };
    static void ApplySurface(Material mat,string surface) {
        var path=Kit+"/Textures/Surfaces/"+surface;
        var albedo=AssetDatabase.LoadAssetAtPath<Texture2D>(path+"_Albedo.png");
        var normal=AssetDatabase.LoadAssetAtPath<Texture2D>(path+"_Normal.png");
        var packed=AssetDatabase.LoadAssetAtPath<Texture2D>(path+"_MetallicSmoothness.png");
        if(!albedo || !normal || !packed)throw new Exception("Missing PBR surface maps: "+surface);
        mat.mainTexture=albedo;mat.SetTexture("_BumpMap",normal);mat.SetFloat("_BumpScale",1);
        mat.SetTexture("_MetallicGlossMap",packed);mat.SetFloat("_GlossMapScale",1);
        mat.EnableKeyword("_NORMALMAP");mat.EnableKeyword("_METALLICGLOSSMAP");
        EditorUtility.SetDirty(mat);
    }

    static ProductCatalog ReadProducts() => File.Exists(Kit+"/Products/catalog.json") ? JsonUtility.FromJson<ProductCatalog>(File.ReadAllText(Kit+"/Products/catalog.json")) : null;
    static Catalog ReadCatalog() {
        var c=JsonUtility.FromJson<Catalog>(File.ReadAllText(Kit+"/catalog.json"));
        var products=ReadProducts();
        if(products!=null)c.assets=c.assets.Concat(products.assets).ToArray();
        return c;
    }
    static void Folder(string path) { Directory.CreateDirectory(path); }
    static Material MakeMaterial(string path, Color color, float metallic=0, float smooth=.4f, Texture texture=null) {
        var m=AssetDatabase.LoadAssetAtPath<Material>(path);
        if (!m) { m=new Material(Shader.Find("Standard")); AssetDatabase.CreateAsset(m,path); }
        m.color=color; m.SetFloat("_Metallic",metallic); m.SetFloat("_Glossiness",smooth);
        m.mainTexture=texture;
        EditorUtility.SetDirty(m);
        return m;
    }
    static Bounds BoundsOf(GameObject root) {
        var renderers=root.GetComponentsInChildren<MeshRenderer>();
        if (renderers.Length==0) throw new Exception("No renderable mesh: "+root.name);
        var b=renderers[0].bounds;
        foreach (var r in renderers.Skip(1)) b.Encapsulate(r.bounds);
        return b;
    }
    static void SimplifiedCollision(GameObject root) {
        var b=BoundsOf(root);
        var c=root.AddComponent<BoxCollider>(); c.center=b.center-root.transform.position; c.size=b.size;
    }
    static GameObject Wrap(string source,string name,Dictionary<string,Material> mats,Material overrideMaterial=null) {
        var model=AssetDatabase.LoadAssetAtPath<GameObject>(source);
        if (!model) throw new Exception("FBX import failed: "+source);
        var root=new GameObject(name);
        var child=(GameObject)PrefabUtility.InstantiatePrefab(model); child.name="Visual"; child.transform.SetParent(root.transform,false);
        // Blender FBX import faces +Z; project equipment faces the visitor along -Z.
        if(source.StartsWith(Kit+"/Models/") || source.StartsWith(Kit+"/Products/Models/")) child.transform.localRotation=Quaternion.Euler(0,180,0)*child.transform.localRotation;
        foreach (var r in root.GetComponentsInChildren<Renderer>()) {
            r.sharedMaterials=r.sharedMaterials.Select(m=>overrideMaterial ? overrideMaterial : m && mats.ContainsKey(m.name) ? mats[m.name] : m).ToArray();
            r.shadowCastingMode=ShadowCastingMode.On; r.receiveShadows=true;
        }
        return root;
    }

    [MenuItem("Factory/Assets/Rebuild Library")]
    public static void RebuildLibrary() {
        if (!Application.isBatchMode && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
        var setup=EditorSceneManager.GetSceneManagerSetup();
        try {
            Folder(Kit+"/Materials"); Folder(Kit+"/Prefabs"); Folder(Kit+"/Scenes");
            AssetDatabase.Refresh();
            var mats=new Dictionary<string,Material>();
            foreach (var kv in Colors) {
                bool metal=kv.Key.StartsWith("Steel");
                mats[kv.Key]=MakeMaterial(Kit+"/Materials/"+kv.Key+".mat",kv.Value,metal?.72f:.05f,metal?.68f:.4f);
                if(Surfaces.ContainsKey(kv.Key))ApplySurface(mats[kv.Key],Surfaces[kv.Key]);
            }
            var productData=ReadProducts();
            if(productData!=null)foreach(var s in productData.materials) {
                var color=new Color(s.color[0],s.color[1],s.color[2]);
                var m=MakeMaterial(Kit+"/Materials/"+s.name+".mat",color,s.metallic,s.smoothness);
                m.enableInstancing=true;
                if(!string.IsNullOrEmpty(s.texture)) {
                    m.mainTexture=AssetDatabase.LoadAssetAtPath<Texture2D>(Kit+"/Products/Textures/"+s.texture+"_Albedo.png");
                    m.SetTexture("_MetallicGlossMap",AssetDatabase.LoadAssetAtPath<Texture2D>(Kit+"/Products/Textures/"+s.texture+"_MetallicSmoothness.png"));
                    m.SetFloat("_GlossMapScale",1);m.EnableKeyword("_METALLICGLOSSMAP");
                    m.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(Kit+"/Textures/Surfaces/PaintedMetal_Normal.png"));
                    m.SetFloat("_BumpScale",.15f);m.EnableKeyword("_NORMALMAP");
                }
                mats[s.name]=m;
            }
            foreach (var a in ReadCatalog().assets) {
                Folder(Kit+"/Prefabs/"+a.category);
                var root=Wrap(Kit+"/"+a.path,a.id,mats);
                if(!string.IsNullOrEmpty(a.lodPath)) {
                    var low=Wrap(Kit+"/"+a.lodPath,"Lower detail",mats);
                    var visual=low.transform.GetChild(0);visual.SetParent(root.transform,false);visual.name="Visual_LOD1";
                    UnityEngine.Object.DestroyImmediate(low);
                    var group=root.AddComponent<LODGroup>();
                    group.SetLODs(new[]{new LOD(.08f,root.transform.Find("Visual").GetComponentsInChildren<Renderer>()),new LOD(.008f,visual.GetComponentsInChildren<Renderer>())});
                    group.RecalculateBounds();
                }
                if(a.collision=="capsule") {
                    var b=BoundsOf(root);var collider=root.AddComponent<CapsuleCollider>();
                    collider.center=b.center;collider.height=b.size.y;collider.radius=Mathf.Max(b.size.x,b.size.z)/2;
                } else if (a.collision!="none") SimplifiedCollision(root);
                PrefabUtility.SaveAsPrefabAsset(root,Kit+"/Prefabs/"+a.category+"/"+a.id+".prefab");
                UnityEngine.Object.DestroyImmediate(root);
            }
            foreach (var pack in new[]{"FactoryKit","CityIndustrial"}) {
                Folder(ThirdParty+"/"+pack+"/Prefabs");
                var texture=AssetDatabase.LoadAssetAtPath<Texture2D>(ThirdParty+"/"+pack+"/Models/Textures/colormap.png");
                if (!texture) throw new Exception("Missing Kenney colormap: "+pack);
                var mat=MakeMaterial(Kit+"/Materials/Kenney_"+pack+".mat",Color.white,0,.25f,texture);
                // Keep the author's palette UV0; use separate metre-scale UV1 for surface relief.
                mat.SetTexture("_DetailNormalMap",AssetDatabase.LoadAssetAtPath<Texture2D>(Kit+"/Textures/Surfaces/PaintedMetal_Normal.png"));
                mat.SetFloat("_DetailNormalMapScale",1);mat.SetFloat("_UVSec",1);mat.EnableKeyword("_DETAIL_MULX2");
                foreach (var path in Directory.GetFiles(ThirdParty+"/"+pack+"/Models","*.fbx").OrderBy(p=>p)) {
                    var name=Path.GetFileNameWithoutExtension(path);
                    var root=Wrap(path,name,mats,mat);
                    SimplifiedCollision(root);
                    PrefabUtility.SaveAsPrefabAsset(root,ThirdParty+"/"+pack+"/Prefabs/"+name+".prefab");
                    UnityEngine.Object.DestroyImmediate(root);
                }
            }
            AssetDatabase.SaveAssets(); AssetDatabase.Refresh();
            CreateBrandSign(); CreateGallery(); CreateAssembly();
            if(productData!=null) CreateProductShowcase();
            ValidateLibrary();
            Debug.Log("FACTORY_ASSET_LIBRARY_READY");
        } finally {
            if (setup.Length>0) EditorSceneManager.RestoreSceneManagerSetup(setup);
        }
    }

    static void CreateProductShowcase() {
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        var products=ReadProducts();
        for(int i=0;i<products.assets.Length;i++) Place(products.assets[i].id,new Vector3(i*.11f,0,0));
        var floor=GameObject.CreatePrimitive(PrimitiveType.Cube);floor.name="Studio floor";
        floor.transform.position=new Vector3(0,-.0055f,0);floor.transform.localScale=new Vector3(10,.01f,10);
        floor.GetComponent<Renderer>().sharedMaterial=AssetDatabase.LoadAssetAtPath<Material>(Kit+"/Materials/White.mat");
        var cam=Lighting(new Vector3(.12f,.32f,-.65f),new Vector3(.055f,.11f,0),.16f);
        cam.nearClipPlane=.001f;cam.farClipPlane=20;
        // Force LOD0 for the review image; automatic LOD returns after capture.
        foreach(var g in UnityEngine.Object.FindObjectsByType<LODGroup>(FindObjectsSortMode.None))g.ForceLOD(0);
        Capture(cam,"../docs/game/asset-library/products/unity-products-preview.png");
        foreach(var g in UnityEngine.Object.FindObjectsByType<LODGroup>(FindObjectsSortMode.None))g.ForceLOD(-1);
        EditorSceneManager.SaveScene(SceneManager.GetActiveScene(),Kit+"/Scenes/ProductShowcase.unity");
    }

    static void CreateBrandSign() {
        Folder(Kit+"/Prefabs/Branding");
        var texture=AssetDatabase.LoadAssetAtPath<Texture2D>(Kit+"/Textures/Ochakovo_Official.png");
        if(!texture)throw new Exception("Missing original Ochakovo logo");
        var mat=MakeMaterial(Kit+"/Materials/Ochakovo_Official.mat",Color.white,0,0,texture);
        mat.SetFloat("_Mode",1);mat.SetFloat("_Cutoff",.3f);mat.EnableKeyword("_ALPHATEST_ON");mat.renderQueue=2450;
        mat.SetOverrideTag("RenderType","TransparentCutout");
        var root=new GameObject("Ochakovo_Official_Sign");
        var board=GameObject.CreatePrimitive(PrimitiveType.Cube);board.name="Board";board.transform.SetParent(root.transform,false);
        board.transform.localPosition=new Vector3(0,.32f,0);board.transform.localScale=new Vector3(2.2f,.64f,.04f);
        board.GetComponent<Renderer>().sharedMaterial=AssetDatabase.LoadAssetAtPath<Material>(Kit+"/Materials/White.mat");
        var logo=GameObject.CreatePrimitive(PrimitiveType.Quad);logo.name="Original logo";logo.transform.SetParent(root.transform,false);
        logo.transform.localPosition=new Vector3(0,.32f,-.025f);logo.transform.localScale=new Vector3(2,.475f,1);
        UnityEngine.Object.DestroyImmediate(logo.GetComponent<Collider>());logo.GetComponent<Renderer>().sharedMaterial=mat;
        logo.GetComponent<Renderer>().shadowCastingMode=ShadowCastingMode.Off;
        PrefabUtility.SaveAsPrefabAsset(root,Kit+"/Prefabs/Branding/Ochakovo_Official_Sign.prefab");
        UnityEngine.Object.DestroyImmediate(root);AssetDatabase.SaveAssets();
    }

    static GameObject Place(string id,Vector3 position,float rotation=0) {
        var a=ReadCatalog().assets.First(x=>x.id==id);
        var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(Kit+"/Prefabs/"+a.category+"/"+id+".prefab");
        var o=(GameObject)PrefabUtility.InstantiatePrefab(prefab);
        o.transform.position=position; o.transform.rotation=Quaternion.Euler(0,rotation,0);
        return o;
    }
    static Camera Lighting(Vector3 position,Vector3 target,float ortho) {
        RenderSettings.ambientMode=AmbientMode.Trilight;
        RenderSettings.ambientSkyColor=new Color(.8f,.83f,.87f);
        RenderSettings.ambientEquatorColor=new Color(.64f,.63f,.60f);
        RenderSettings.ambientGroundColor=new Color(.40f,.39f,.37f);
        // Reflective steel needs an actual environment, not only ambient diffuse light.
        var environment=AssetDatabase.LoadAssetAtPath<Cubemap>(Kit+"/Materials/StudioReflection.cubemap");
        if(!environment) {
            const int resolution=64;environment=new Cubemap(resolution,TextureFormat.RGBAHalf,true);
            for(int face=0;face<6;face++) {
                var pixels=new Color[resolution*resolution];
                for(int y=0;y<resolution;y++)for(int x=0;x<resolution;x++) {
                    float u=(x+.5f)/resolution*2-1,v=(y+.5f)/resolution*2-1;
                    var directions=new[]{new Vector3(1,-v,-u),new Vector3(-1,-v,u),new Vector3(u,1,v),new Vector3(u,-1,-v),new Vector3(u,-v,1),new Vector3(-u,-v,-1)};
                    var d=directions[face].normalized;
                    float softbox=Mathf.Pow(Mathf.Max(0,Vector3.Dot(d,new Vector3(-.3f,.6f,-.7f).normalized)),18)*1.2f;
                    float brightness=Mathf.Lerp(.30f,.85f,(d.y+1)*.5f)+softbox;
                    pixels[y*resolution+x]=new Color(brightness,brightness*.99f,brightness*.98f,1);
                }
                environment.SetPixels(pixels,(CubemapFace)face);
            }
            environment.Apply(true);AssetDatabase.CreateAsset(environment,Kit+"/Materials/StudioReflection.cubemap");
        }
        RenderSettings.defaultReflectionMode=DefaultReflectionMode.Custom;RenderSettings.customReflection=environment;RenderSettings.reflectionIntensity=1;
        var key=new GameObject("Warm daylight").AddComponent<Light>();key.type=LightType.Directional;key.intensity=1.2f;
        key.color=new Color(1,.98f,.94f);key.transform.rotation=Quaternion.Euler(48,-35,0);key.shadows=LightShadows.Soft;
        var fill=new GameObject("Soft fill").AddComponent<Light>();fill.type=LightType.Directional;fill.intensity=.35f;
        fill.transform.rotation=Quaternion.Euler(30,120,0);
        var cam=new GameObject("Preview Camera").AddComponent<Camera>();cam.tag="MainCamera";
        cam.transform.position=position;cam.transform.LookAt(target);cam.orthographic=true;cam.orthographicSize=ortho;
        cam.nearClipPlane=.1f;cam.farClipPlane=200;cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=new Color(.965f,.961f,.949f);
        cam.allowHDR=false;cam.allowMSAA=true;
        return cam;
    }
    static void CreateGallery() {
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        var catalog=ReadCatalog();
        for (int i=0;i<catalog.assets.Length;i++) {
            var o=Place(catalog.assets[i].id,new Vector3((i%8)*5,0,(i/8)*6));
            o.name=(i+1).ToString("D2")+" "+catalog.assets[i].label+" ["+catalog.assets[i].id+"]";
        }
        Lighting(new Vector3(58,57,-38),new Vector3(17,0,23),32);
        EditorSceneManager.SaveScene(SceneManager.GetActiveScene(),Kit+"/Scenes/AssetGallery.unity");
    }
    static void CreateAssembly() {
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        foreach (float x in new[]{-6f,-2f,2f,6f}) {
            foreach(float z in new[]{-4f,0f,4f}) Place("Floor_4x4",new Vector3(x,0,z));
            Place("Wall_Window_4m",new Vector3(x,0,6));
        }
        foreach(float z in new[]{-4f,0f,4f}) Place("Wall_4m",new Vector3(-8,0,z),90);
        foreach(float x in new[]{-6f,-3.1f}) Place("Brew_Kettle",new Vector3(x,0,3.8f));
        Place("Fermentation_Tank",new Vector3(-6,0,0));Place("CIP_Skid",new Vector3(-3.3f,0,.2f));Place("Control_Cabinet",new Vector3(-.9f,0,4.9f));
        foreach(float z in new[]{-2f,2f}) Place("Conveyor_2m",new Vector3(1,0,z));
        Place("Filling_Machine",new Vector3(1,0,0));Place("Packing_Machine",new Vector3(1,0,-3.5f));
        foreach(float z in new[]{-2.5f,-1.7f,1.3f,2.1f}) Place("Bottle_Tray_12",new Vector3(1,1,z));
        foreach(float x in new[]{3.7f,6f}) {Place("Lab_Bench_2m",new Vector3(x,0,4.6f));Place("Lab_Stool",new Vector3(x,0,3.5f));}
        Place("Microscope",new Vector3(3.1f,.96f,4.5f));Place("PH_Meter",new Vector3(4,.96f,4.5f));
        Place("Erlenmeyer_Flask",new Vector3(5.5f,.96f,4.3f));Place("Test_Tube_Rack",new Vector3(6.1f,.96f,4.6f));Place("Lab_Balance",new Vector3(6.5f,.96f,4.5f));
        Place("Warehouse_Rack_3m",new Vector3(5.3f,0,-.3f));Place("Pallet_Loaded",new Vector3(5,0,-3.2f));Place("Pallet_Jack",new Vector3(6.4f,0,-3.4f));Place("Euro_Pallet",new Vector3(4.8f,.25f,-.3f));
        Place("Operator_Console",new Vector3(-.4f,0,-.4f));Place("Safety_Bollard",new Vector3(2.3f,0,-4.8f));
        var sign=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Kit+"/Prefabs/Branding/Ochakovo_Official_Sign.prefab"));
        sign.transform.position=new Vector3(-3,3.1f,5.85f);
        foreach(float x in new[]{-1.2f,2.5f}) Place("Floor_Marking_2m",new Vector3(x,0,-3));
        var cam=Lighting(new Vector3(19,24,-25),new Vector3(0,.5f,0),9);
        EditorSceneManager.SaveScene(SceneManager.GetActiveScene(),Kit+"/Scenes/AssemblyExample.unity");
        Capture(cam,"../docs/game/asset-library/unity-assembly-preview.png");
    }
    static void Capture(Camera cam,string path) {
        if (SystemInfo.graphicsDeviceType==GraphicsDeviceType.Null) { Debug.Log("Preview skipped: null graphics device");return; }
        var rt=new RenderTexture(1600,1000,24);rt.antiAliasing=4;cam.targetTexture=rt;cam.Render();
        var previous=RenderTexture.active;RenderTexture.active=rt;
        var image=new Texture2D(1600,1000,TextureFormat.RGB24,false);image.ReadPixels(new Rect(0,0,1600,1000),0,0);image.Apply();
        File.WriteAllBytes(path,image.EncodeToPNG());cam.targetTexture=null;RenderTexture.active=previous;
        UnityEngine.Object.DestroyImmediate(image);rt.Release();UnityEngine.Object.DestroyImmediate(rt);
    }

    [MenuItem("Factory/Assets/Validate Library")]
    public static void ValidateLibrary() {
        var errors=new List<string>();var checks=new List<Check>();
        foreach(var a in ReadCatalog().assets) {
            var path=Kit+"/Prefabs/"+a.category+"/"+a.id+".prefab";
            var p=AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (!p) { errors.Add("Missing prefab: "+a.id); continue; }
            var instance=(GameObject)PrefabUtility.InstantiatePrefab(p);
            var b=BoundsOf(instance);
            float tolerance=a.category=="Products"?.001f:.035f;
            for(int axis=0;axis<3;axis++) if(Mathf.Abs(b.size[axis]-a.size[axis])>tolerance) errors.Add(a.id+" wrong metre scale on axis "+axis+": "+b.size);
            foreach(var renderer in instance.GetComponentsInChildren<Renderer>()) {
                if(renderer.sharedMaterials.Any(m=>!m || m.shader.name!="Standard")) errors.Add(a.id+" invalid Built-in material");
            }
            int colliders=instance.GetComponentsInChildren<Collider>().Length;
            if ((a.collision=="none" && colliders!=0)||(a.collision!="none" && colliders!=1)) errors.Add(a.id+" collider policy failed");
            var meshes=instance.GetComponentsInChildren<MeshFilter>();
            if(a.category=="Products") {
                var group=instance.GetComponent<LODGroup>();
                if(!group || group.GetLODs().Length!=2)errors.Add(a.id+" needs two detail levels");
                if(!instance.GetComponent<CapsuleCollider>())errors.Add(a.id+" needs capsule collider");
                var label=instance.GetComponentsInChildren<Renderer>().SelectMany(r=>r.sharedMaterials).FirstOrDefault(m=>m.name.Contains("Label"));
                if(!label || !label.mainTexture)errors.Add(a.id+" missing genuine product artwork");
            }
            checks.Add(new Check{id=a.id,path=path,size=b.size,triangles=meshes.Sum(m=>m.sharedMesh.triangles.Length/3),renderers=meshes.Length,colliders=colliders});
            UnityEngine.Object.DestroyImmediate(instance);
        }
        var thirdParty=AssetDatabase.FindAssets("t:Prefab",new[]{ThirdParty});
        foreach(var guid in thirdParty) {
            var path=AssetDatabase.GUIDToAssetPath(guid);var p=AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if(!p.GetComponentsInChildren<MeshRenderer>().Any() || p.GetComponentsInChildren<Renderer>().Any(r=>r.sharedMaterials.Any(m=>!m || !m.mainTexture))) errors.Add("Invalid third-party material/mesh: "+path);
        }
        foreach(var kv in Surfaces) {
            var m=AssetDatabase.LoadAssetAtPath<Material>(Kit+"/Materials/"+kv.Key+".mat");
            if(!m || !m.mainTexture || !m.GetTexture("_BumpMap") || !m.GetTexture("_MetallicGlossMap"))errors.Add("Missing PBR maps: "+kv.Key);
            else {
                var importer=(TextureImporter)AssetImporter.GetAtPath(AssetDatabase.GetAssetPath(m.GetTexture("_BumpMap")));
                if(importer.textureType!=TextureImporterType.NormalMap)errors.Add("Normal map imported as colour: "+kv.Key);
            }
        }
        var report=new Verification{originalPrefabs=checks.Count,thirdPartyPrefabs=thirdParty.Length,unityVersion=Application.unityVersion,status=errors.Count==0?"passed":"failed",originals=checks.ToArray(),errors=errors.ToArray()};
        File.WriteAllText("../docs/game/asset-library/unity-validation.json",JsonUtility.ToJson(report,true));
        if(errors.Count>0)throw new Exception(string.Join("\n",errors));
        Debug.Log("FACTORY_ASSETS_VALIDATED: "+checks.Count+" original, "+thirdParty.Length+" third-party prefabs");
    }
}

public class FactoryAssetImportSettings : AssetPostprocessor {
    void OnPostprocessModel(GameObject root) {
        if(!assetPath.StartsWith("Assets/ThirdParty/Kenney/"))return;
        foreach(var filter in root.GetComponentsInChildren<MeshFilter>()) {
            var mesh=filter.sharedMesh;var positions=mesh.vertices;var normals=mesh.normals;
            var uv=new Vector2[positions.Length];
            for(int i=0;i<positions.Length;i++) {
                var p=filter.transform.TransformPoint(positions[i]);var n=normals.Length>i?normals[i]:Vector3.up;
                int axis=Mathf.Abs(n.x)>Mathf.Abs(n.y)?0:1;
                if(Mathf.Abs(n.z)>Mathf.Abs(n[axis]))axis=2;
                uv[i]=axis==0?new Vector2(p.z,p.y):axis==1?new Vector2(p.x,p.z):new Vector2(p.x,p.y);
            }
            mesh.uv2=uv;
        }
    }
    void OnPreprocessModel() {
        if(!assetPath.StartsWith("Assets/FactoryKit/Models/") && !assetPath.StartsWith("Assets/FactoryKit/Products/Models/") && !assetPath.StartsWith("Assets/ThirdParty/Kenney/"))return;
        var importer=(ModelImporter)assetImporter;
        importer.importAnimation=false;importer.importCameras=false;importer.importLights=false;
        importer.isReadable=false;importer.addCollider=false;importer.globalScale=1;
        importer.meshCompression=ModelImporterMeshCompression.Off;
        importer.materialImportMode=ModelImporterMaterialImportMode.ImportStandard;
        importer.importNormals=ModelImporterNormals.Import;
    }
    void OnPreprocessTexture() {
        bool product=assetPath.StartsWith("Assets/FactoryKit/Products/Textures/");
        bool original=assetPath.StartsWith("Assets/FactoryKit/Textures/") || product;
        if(!original && !assetPath.StartsWith("Assets/ThirdParty/Kenney/"))return;
        var importer=(TextureImporter)assetImporter;
        importer.filterMode=original?FilterMode.Trilinear:FilterMode.Point;importer.mipmapEnabled=true;importer.maxTextureSize=1024;
        importer.textureCompression=TextureImporterCompression.Uncompressed;
        if(original) {
            importer.wrapMode=TextureWrapMode.Repeat;importer.anisoLevel=4;
            if(product)importer.maxTextureSize=2048;
            if(assetPath.EndsWith("_Normal.png")) {importer.textureType=TextureImporterType.NormalMap;importer.sRGBTexture=false;}
            else if(assetPath.EndsWith("_MetallicSmoothness.png") || assetPath.EndsWith("_Roughness.png"))importer.sRGBTexture=false;
            if(assetPath.EndsWith("Ochakovo_Official.png")) {importer.alphaIsTransparency=true;importer.wrapMode=TextureWrapMode.Clamp;importer.mipmapEnabled=false;}
        }
    }
}
