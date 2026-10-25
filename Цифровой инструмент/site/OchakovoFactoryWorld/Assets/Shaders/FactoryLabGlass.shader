Shader "Factory/LaboratoryGlass" {
 Properties { _Color("Glass tint",Color)=(.72,.88,.94,.08) _Detail("Fine glass surface",2D)="white"{} }
 SubShader { Tags {"Queue"="Transparent+10" "RenderType"="Transparent"} Blend SrcAlpha OneMinusSrcAlpha ZWrite Off Cull Back
 Pass { CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "UnityCG.cginc"
 struct a{float4 vertex:POSITION;float3 normal:NORMAL;float2 uv:TEXCOORD0;};
 struct v{float4 vertex:SV_POSITION;float3 normal:TEXCOORD0;float3 world:TEXCOORD1;float2 uv:TEXCOORD2;};
 fixed4 _Color;sampler2D _Detail;
 v vert(a i){v o;o.vertex=UnityObjectToClipPos(i.vertex);o.world=mul(unity_ObjectToWorld,i.vertex).xyz;o.normal=UnityObjectToWorldNormal(i.normal);o.uv=i.uv;return o;}
 fixed4 frag(v i):SV_Target{float3 n=normalize(i.normal),view=normalize(_WorldSpaceCameraPos-i.world);float edge=pow(1-saturate(dot(n,view)),3);float highlight=pow(saturate(dot(reflect(-normalize(float3(-.4,.8,-.6)),n),view)),55);float grain=tex2D(_Detail,i.uv*3).r;float3 color=lerp(_Color.rgb,float3(.96,.99,1),edge*.7)+highlight*.55;return fixed4(color,saturate(_Color.a+edge*.46+highlight*.36+(grain-.5)*.012));}
 ENDCG }
 } }
