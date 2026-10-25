using UnityEngine;
[ExecuteAlways,RequireComponent(typeof(Camera))]
public class FactoryAtmosphere : MonoBehaviour {
 public Material treatment;
 void OnEnable(){GetComponent<Camera>().depthTextureMode=DepthTextureMode.DepthNormals;}
 void OnRenderImage(RenderTexture source,RenderTexture destination){if(treatment)Graphics.Blit(source,destination,treatment);else Graphics.Blit(source,destination);}
}
