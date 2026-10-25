using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

public static class FactoryCharacterAssets {
 const string Root="Assets/FactoryWorld/Characters";
 static Material Surface(string name,Color color,string image=null,bool fabric=false){
  var path=Root+"/Materials/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=new Material(Shader.Find("Standard"));AssetDatabase.CreateAsset(m,path);}m.color=color;m.SetFloat("_Metallic",0);m.SetFloat("_Glossiness",.12f);m.SetFloat("_SpecularHighlights",0);m.enableInstancing=true;
  if(image!=null)m.mainTexture=AssetDatabase.LoadAssetAtPath<Texture2D>(Root+"/Textures/"+image);
  if(fabric){m.mainTexture=AssetDatabase.LoadAssetAtPath<Texture2D>(Root+"/Textures/FabricWeave.png");m.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(Root+"/Textures/FabricNormal.png"));m.SetFloat("_BumpScale",.15f);m.EnableKeyword("_NORMALMAP");}EditorUtility.SetDirty(m);return m;
 }
 public static GameObject Prefab(bool laboratory)=>AssetDatabase.LoadAssetAtPath<GameObject>(Root+"/Prefabs/"+(laboratory?"chemist":"bottling")+".prefab");
 public static void Prepare(){
  Directory.CreateDirectory(Root+"/Materials");Directory.CreateDirectory(Root+"/Prefabs");AssetDatabase.Refresh();
  foreach(var file in Directory.GetFiles(Root+"/Textures","*.png")){var ti=(TextureImporter)AssetImporter.GetAtPath(file);ti.maxTextureSize=1024;ti.mipmapEnabled=true;ti.filterMode=FilterMode.Trilinear;ti.anisoLevel=4;if(file.EndsWith("FabricNormal.png"))ti.textureType=TextureImporterType.NormalMap;ti.SaveAndReimport();}
  var fabrics=new System.Collections.Generic.Dictionary<string,Material>{
   {"Coat fabric",Surface("Coat fabric",new Color(.88f,.90f,.89f),null,true)}, {"Work fabric",Surface("Work fabric",new Color(.09f,.14f,.20f),null,true)},
   {"Red fabric",Surface("Red fabric",new Color(.70f,.008f,.055f),null,true)}, {"Boot rubber",Surface("Boot rubber",new Color(.035f,.04f,.05f))},
   {"Reflective fabric",Surface("Reflective fabric",new Color(.62f,.65f,.67f),null,true)}, {"Badge paper",Surface("Badge paper",new Color(.94f,.94f,.89f))},
   {"Eyes",Surface("Eyes",Color.white,"T_Eye_Brown.png")}, {"Hair",Surface("Hair",new Color(.16f,.075f,.035f),"T_Hair_2_BaseColor.png")},
   {"Skin_Female",Surface("Skin_Female",Color.white,"T_Superhero_Female_Light_BaseColor.png")}, {"Skin_Male",Surface("Skin_Male",Color.white,"T_Superhero_Male_Ligh.png")}
  };
  foreach(var id in new[]{"chemist","bottling"}){
   var path=Root+"/Models/"+id+".fbx";var importer=(ModelImporter)AssetImporter.GetAtPath(path);importer.animationType=ModelImporterAnimationType.Generic;importer.avatarSetup=ModelImporterAvatarSetup.CreateFromThisModel;importer.importAnimation=true;importer.preserveHierarchy=true;importer.importCameras=false;importer.importLights=false;importer.animationCompression=ModelImporterAnimationCompression.Off;
   var definitions=importer.defaultClipAnimations;foreach(var clip in definitions){clip.name=clip.name.Split('|').Last();clip.loopTime=true;clip.loopPose=true;clip.lockRootPositionXZ=true;clip.lockRootRotation=true;clip.keepOriginalPositionXZ=true;clip.keepOriginalPositionY=true;clip.lockRootHeightY=true;}
   importer.clipAnimations=definitions;importer.SaveAndReimport();
   var clips=AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__")).ToArray();
   var controllerPath=Root+"/"+id+".controller";var controller=AssetDatabase.LoadAssetAtPath<AnimatorController>(controllerPath)??AnimatorController.CreateAnimatorControllerAtPath(controllerPath);var sm=controller.layers[0].stateMachine;foreach(var child in sm.states)sm.RemoveState(child.state);
   foreach(var name in new[]{"Idle","Walk","InspectSample","OperatePanel","OperateValve"}){var clip=clips.FirstOrDefault(c=>c.name==name||c.name.EndsWith("|"+name));if(!clip)throw new Exception("Missing animation "+name+" on "+id+": "+string.Join(",",clips.Select(c=>c.name)));var state=sm.AddState(name);state.motion=clip;if(name=="Idle")sm.defaultState=state;}
   var root=new GameObject(id+" · rigged workwear");var model=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path));model.transform.SetParent(root.transform,false);var animator=model.GetComponent<Animator>()??model.AddComponent<Animator>();animator.runtimeAnimatorController=controller;animator.applyRootMotion=false;animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;
   foreach(var r in model.GetComponentsInChildren<Renderer>()){r.sharedMaterials=r.sharedMaterials.Select(m=>m&&fabrics.ContainsKey(m.name)?fabrics[m.name]:m).ToArray();r.shadowCastingMode=UnityEngine.Rendering.ShadowCastingMode.On;}
   // Normalize the selected source body's adult height, including work footwear.
   var renderers=model.GetComponentsInChildren<Renderer>();var bounds=renderers[0].bounds;foreach(var r in renderers)bounds.Encapsulate(r.bounds);float scale=1.82f/bounds.size.y;root.transform.localScale=Vector3.one*scale;
   PrefabUtility.SaveAsPrefabAsset(root,Root+"/Prefabs/"+id+".prefab");UnityEngine.Object.DestroyImmediate(root);EditorUtility.SetDirty(controller);
  }AssetDatabase.SaveAssets();Debug.Log("FACTORY_RIGGED_CHARACTERS_READY");
 }
 [Serializable] class CharacterCheck {public string id;public int skinnedMeshes,triangles;public string[] clips;public bool avatarValid;public float walkDeformation;}
 [Serializable] class CharacterReport {public string status;public CharacterCheck[] characters;}
 public static void Validate(){
  var checks=new System.Collections.Generic.List<CharacterCheck>();
  foreach(var id in new[]{"chemist","bottling"}){
   var root=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Root+"/Prefabs/"+id+".prefab"));var animator=root.GetComponentInChildren<Animator>();var skins=root.GetComponentsInChildren<SkinnedMeshRenderer>();var walk=animator.runtimeAnimatorController.animationClips.First(c=>c.name=="Walk");var sample=new Mesh();float distance=0;int n=0;
   walk.SampleAnimation(animator.gameObject,.15f);var first=skins.Select(s=>{var m=new Mesh();s.BakeMesh(m);var v=m.vertices;UnityEngine.Object.DestroyImmediate(m);return v;}).ToArray();
   walk.SampleAnimation(animator.gameObject,.65f);for(int i=0;i<skins.Length;i++){skins[i].BakeMesh(sample);var second=sample.vertices;for(int j=0;j<second.Length;j++){distance+=Vector3.Distance(first[i][j],second[j]);n++;}}
   var check=new CharacterCheck{id=id,skinnedMeshes=skins.Length,triangles=skins.Sum(r=>r.sharedMesh.triangles.Length/3),clips=animator.runtimeAnimatorController.animationClips.Select(c=>c.name).Distinct().OrderBy(c=>c).ToArray(),avatarValid=animator.avatar&&animator.avatar.isValid,walkDeformation=distance/Mathf.Max(1,n)};checks.Add(check);UnityEngine.Object.DestroyImmediate(sample);UnityEngine.Object.DestroyImmediate(root);
   if(!check.avatarValid||check.clips.Length!=5||check.walkDeformation<.005f)throw new Exception("Character deformation validation failed: "+id+" "+JsonUtility.ToJson(check));
  }
  File.WriteAllText("../docs/game/location/character-validation.json",JsonUtility.ToJson(new CharacterReport{status="passed",characters=checks.ToArray()},true));Debug.Log("FACTORY_CHARACTER_DEFORMATION_PASSED");
 }

}
