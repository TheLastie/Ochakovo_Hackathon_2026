using System;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;

public partial class FactoryWindowsDesktop {
 string photoId="";bool photoZoom;int photoAngle;
 public string CurrentPhoto=>photoId;
 public bool PhotoZoomed=>photoZoom;
 public int PhotoAngle=>photoAngle;
 void OpenPhoto(string id,bool preserveView=false){
  var e=Find(id);var texture=PhotoTexture(e);if(!texture){Notice("Фотографии","Не удалось открыть изображение.");return;}
  if(!preserveView){photoZoom=false;photoAngle=0;}photoId=id;
  var app=App(e.name+" — Фотографии",205,50,760,526,"photos");
  Panel(app,"Photo toolbar",0,32,760,44,new Color32(244,244,244,255));
  B(app,"Previous photo",10,38,88,32,"← Назад",()=>StepPhoto(-1),Color.white,ink,14);
  B(app,"Next photo",106,38,88,32,"Далее →",()=>StepPhoto(1),Color.white,ink,14);
  B(app,"Photo zoom",208,38,136,32,photoZoom?"Вписать":"Приблизить",()=>{photoZoom=!photoZoom;OpenPhoto(photoId,true);},Color.white,ink,14);
  B(app,"Rotate photo",352,38,124,32,"Повернуть",()=>{photoAngle=(photoAngle+90)%360;OpenPhoto(photoId,true);},Color.white,ink,14);
  B(app,"Restore photo",488,38,260,32,e.deleted?"Восстановить в Документы":"Показать в Документах",()=>{if(e.deleted){e.deleted=false;e.parent=e.originalParent;RefreshFiles();OpenPhoto(photoId,true);}else{DestroyApp();Navigate(e.parent);}},Color.white,ink,14);
  var viewport=Panel(app,"Photo viewport",1,77,758,374,new Color32(27,27,27,255));viewport.gameObject.AddComponent<RectMask2D>();
  float size=photoZoom?640:374;var picture=R(viewport,"Mikhalych selfie",(758-size)/2,(374-size)/2,size,size);picture.pivot=new Vector2(.5f,.5f);picture.anchoredPosition+=new Vector2(size/2,-size/2);picture.localRotation=Quaternion.Euler(0,0,photoAngle);var raw=picture.gameObject.AddComponent<RawImage>();raw.texture=texture;raw.raycastTarget=false;
  T(app,e.text,18,461,724,42,15).alignment=TextAnchor.MiddleCenter;
  T(app,e.deleted?"Корзина · Неудачный дубль":"Документы · Фото восстановлено",18,505,724,18,12,false,gray).alignment=TextAnchor.MiddleCenter;
 }
 void StepPhoto(int direction){var photos=entries.Where(e=>e.kind=="photo").ToList();int index=photos.FindIndex(e=>e.id==photoId);if(photos.Count>0)OpenPhoto(photos[(index+direction+photos.Count)%photos.Count].id);}
}
