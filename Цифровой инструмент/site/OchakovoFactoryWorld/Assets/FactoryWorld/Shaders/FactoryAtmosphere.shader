Shader "Hidden/FactoryAtmosphere" {
 Properties { _MainTex("Scene",2D)="white"{} }
 SubShader { Cull Off ZWrite Off ZTest Always Pass {
 CGPROGRAM
 #pragma vertex vert_img
 #pragma fragment frag
 #include "UnityCG.cginc"
 sampler2D _MainTex, _CameraDepthNormalsTexture; float4 _MainTex_TexelSize;
 float edge(float2 uv,float depth,float3 normal){float d;float3 n;
  DecodeDepthNormal(tex2D(_CameraDepthNormalsTexture,uv),d,n);
  // World depth and geometric normals: no animated noise or ambient-occlusion crawl.
  return max(smoothstep(.10,.25,abs(d-depth)*_ProjectionParams.z),smoothstep(.35,.65,length(n-normal)));
 }
 fixed4 frag(v2f_img i):SV_Target {
  float3 c=tex2D(_MainTex,i.uv).rgb;
  c*=1.02; c=saturate((c*(2.51*c+.03))/(c*(2.43*c+.59)+.14));
  c=max(0,(c-.18)*1.12+.18);
  float d;float3 n;DecodeDepthNormal(tex2D(_CameraDepthNormalsTexture,i.uv),d,n);
  float2 px=abs(_MainTex_TexelSize.xy)*.85;
  float contour=max(max(edge(i.uv+float2(px.x,0),d,n),edge(i.uv-float2(px.x,0),d,n)),max(edge(i.uv+float2(0,px.y),d,n),edge(i.uv-float2(0,px.y),d,n)));
  c=lerp(c,c*float3(.42,.49,.53),contour*.45);
  return float4(c,1);
 }
 ENDCG
 }} Fallback Off
}
