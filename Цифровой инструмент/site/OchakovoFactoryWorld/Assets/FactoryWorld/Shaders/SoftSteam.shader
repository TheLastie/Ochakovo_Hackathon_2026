Shader "Factory/SoftSteam" {
 Properties { _MainTex("Soft particle",2D)="white"{} }
 SubShader { Tags { "Queue"="Transparent" "RenderType"="Transparent" "IgnoreProjector"="True" } Blend SrcAlpha OneMinusSrcAlpha ZWrite Off Cull Off
 Pass { CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "UnityCG.cginc"
 sampler2D _MainTex;
 struct appdata{float4 vertex:POSITION;fixed4 color:COLOR;float2 uv:TEXCOORD0;};struct output{float4 vertex:SV_POSITION;fixed4 color:COLOR;float2 uv:TEXCOORD0;};
 output vert(appdata v){output o;o.vertex=UnityObjectToClipPos(v.vertex);o.color=v.color;o.uv=v.uv;return o;}
 fixed4 frag(output i):SV_Target{return tex2D(_MainTex,i.uv)*i.color;}
 ENDCG }
 } Fallback Off
}
