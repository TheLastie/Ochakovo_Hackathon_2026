using UnityEngine;

/// <summary>Background production motion. All cycles respect the shared pause.</summary>
public class FactoryActivity : MonoBehaviour {
 public Transform[] bottles,nozzles;
 public Renderer[] beacons,monitors;
 public Material hmiAtlas;
 public float beltSpeed=.48f,beltStart=-6.15f,beltLength=12.4f;
 Vector3[] bottleOrigins,nozzleOrigins;
 MaterialPropertyBlock block;
 public int CurrentFrame{get;private set;}
 public float ProductionTime=>Time.time;
 void Start(){block=new MaterialPropertyBlock();bottleOrigins=new Vector3[bottles.Length];for(int i=0;i<bottles.Length;i++)bottleOrigins[i]=bottles[i].position;nozzleOrigins=new Vector3[nozzles.Length];for(int i=0;i<nozzles.Length;i++)nozzleOrigins[i]=nozzles[i].localPosition;}
 void Update(){float t=Time.time;
  for(int i=0;i<bottles.Length;i++){var p=bottleOrigins[i];p.x=beltStart+Mathf.Repeat(bottleOrigins[i].x-beltStart+t*beltSpeed,beltLength);bottles[i].position=p;}
  for(int i=0;i<nozzles.Length;i++)nozzles[i].localPosition=nozzleOrigins[i]+Vector3.up*(Mathf.SmoothStep(0,1,(Mathf.Sin(t*1.8f)+1)/2)*.085f);
  for(int i=0;i<beacons.Length;i++){float glow=Mathf.Pow(Mathf.Max(0,Mathf.Sin(t*2.3f+i*1.4f)),3);block.Clear();block.SetColor("_EmissionColor",new Color(1,.09f,.015f)*(.12f+glow*1.3f));beacons[i].SetPropertyBlock(block);}
  CurrentFrame=(int)(t*3)%8;foreach(var monitor in monitors){block.Clear();block.SetVector("_MainTex_ST",new Vector4(.125f,1,CurrentFrame*.125f,0));block.SetVector("_EmissionMap_ST",new Vector4(.125f,1,CurrentFrame*.125f,0));monitor.SetPropertyBlock(block);}
 }
}
