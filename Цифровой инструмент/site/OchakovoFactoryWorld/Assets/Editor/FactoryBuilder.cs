using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;
using System.IO;
using System.Security.Cryptography;

/// <summary>Builds the saved WebGL scene without generating or replacing scene objects.</summary>
public static class FactoryBuilder {
 [MenuItem("Factory/Build WebGL")]
 public static void BuildWeb(){
  var result=BuildPipeline.BuildPlayer(EditorBuildSettings.scenes,"Builds/WebGL",BuildTarget.WebGL,BuildOptions.None);
  if(result.summary.result!=BuildResult.Succeeded)throw new System.Exception("WebGL build failed");
  VersionFiles();
  Debug.Log("FACTORY_WEBGL_BUILT");
 }
 // A cached framework, wasm and data must always belong to the same build.
 public static void VersionFiles(){
  const string root="Builds/WebGL";
  var indexPath=Path.Combine(root,"index.html");var html=File.ReadAllText(indexPath);
  foreach(var suffix in new[]{"data","wasm","framework.js","loader.js"}){
   var name="WebGL."+suffix;var source=Path.Combine(root,"Build",name);
   if(!File.Exists(source))continue; // Already versioned publication is safe to repeat.
   var bytes=File.ReadAllBytes(source);string hash;
   using(var sha=SHA256.Create())hash=System.BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-","").ToLowerInvariant().Substring(0,16);
   var versioned="WebGL."+hash+"."+suffix;
   File.WriteAllBytes(Path.Combine(root,"Build",versioned),bytes);
   html=html.Replace("Build/"+name,"Build/"+versioned);
   File.Delete(source);
  }
  File.WriteAllText(indexPath,html);
 }
}
