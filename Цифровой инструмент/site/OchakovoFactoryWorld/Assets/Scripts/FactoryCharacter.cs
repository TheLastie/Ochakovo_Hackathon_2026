using UnityEngine;

/// <summary>Rigged workwear characters, in-place locomotion and station motion clips.</summary>
public class FactoryCharacter : MonoBehaviour {
 public GameObject laboratoryPrefab,workerPrefab;
 public GameObject visual;
 public bool isPlayer;
 public string stationState="Idle";
 public float phase;
 public Transform heldSample;
 Animator animator; string current="";Transform hand;
 public string CurrentState=>current;
 public float AnimationTime=>animator&&animator.isInitialized?animator.GetCurrentAnimatorStateInfo(0).normalizedTime:0;
 void Start(){if(!visual)SelectRole("chemist");else Bind();if(!isPlayer)Play(stationState,phase);}
 public void SelectRole(string role){var prefab=role=="chemist"?laboratoryPrefab:workerPrefab;if(!prefab)return;if(visual)Destroy(visual);visual=Instantiate(prefab,transform,false);visual.name="Animated workwear character";Bind();Play("Idle",0);}
 void Bind(){animator=visual.GetComponentInChildren<Animator>();if(animator){animator.applyRootMotion=false;animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;}
  hand=null;current="";
 }
 void Play(string state,float offset=0){if(!animator||current==state)return;current=state;animator.Play(state,0,offset);animator.Update(0);}
 public void SetMovement(float speed,float input){if(!isPlayer||!animator)return;float movement=Mathf.Max(speed,input*2.4f);var target=movement>.08f?"Walk":"Idle";if(target!=current){animator.CrossFadeInFixedTime(target,.15f);current=target;}animator.speed=target=="Walk"?Mathf.Clamp(movement/1.4f,.65f,2):1;}
 void LateUpdate(){if(!heldSample||!visual)return;if(!hand){var bones=visual.GetComponentsInChildren<Transform>();Transform left=null,right=null;foreach(var b in bones){if(b.name=="hand_l")left=b;if(b.name=="hand_r")right=b;}hand=left&&right?(left.position.y>right.position.y?left:right):left?left:right;}
  if(hand){heldSample.position=hand.position+Vector3.up*.035f;heldSample.rotation=Quaternion.Euler(0,0,Mathf.Sin(Time.time*.8f)*8);}
 }
}
