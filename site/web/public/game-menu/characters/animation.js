// H.264 stores RGB above its monochrome matte. WebGL restores transparency,
// including in Safari, where ordinary VP9 video alpha is not supported.
const base = new URL('./animation/', import.meta.url);
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
export function mountCharacterAction(host, role, isActive) {
  if(reduced.matches)return {sync(){},destroy(){}};
  const poster = host.querySelector('img');
  const canvas = document.createElement('canvas');
  canvas.width = 432; canvas.height = 768;
  canvas.setAttribute('aria-hidden', 'true');
  const gl = canvas.getContext('webgl', {alpha:true, premultipliedAlpha:false, depth:false, antialias:false});
  if (!gl || reduced.matches) return {sync(){}, destroy(){}};
  const shader = (type, source) => {
    const s=gl.createShader(type); gl.shaderSource(s,source); gl.compileShader(s);
    if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)) throw new Error('Character shader failed');
    return s;
  };
  let program, vertex, fragment;
  try {
    vertex=shader(gl.VERTEX_SHADER, 'attribute vec2 p; varying vec2 uv; void main(){uv=vec2((p.x+1.0)*0.5,(1.0-p.y)*0.5);gl_Position=vec4(p,0.0,1.0);}');
    fragment=shader(gl.FRAGMENT_SHADER, 'precision mediump float; varying vec2 uv; uniform sampler2D frame; void main(){vec3 c=texture2D(frame,vec2(uv.x,uv.y*0.5)).rgb;float a=texture2D(frame,vec2(uv.x,0.5+uv.y*0.5)).r;gl_FragColor=vec4(c,smoothstep(0.04,0.96,a));}');
    program=gl.createProgram();gl.attachShader(program,vertex);gl.attachShader(program,fragment);gl.linkProgram(program);
    if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Character program failed');
  } catch { gl.getExtension('WEBGL_lose_context')?.loseContext(); return {sync(){},destroy(){}}; }
  gl.useProgram(program);
  const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
  gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
  const pos=gl.getAttribLocation(program,'p');gl.enableVertexAttribArray(pos);gl.vertexAttribPointer(pos,2,gl.FLOAT,false,0,0);
  const texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
  const video=document.createElement('video');video.muted=true;video.playsInline=true;video.preload='auto';
  video.src=new URL(role+'.mp4',base).href;
  let dead=false, raf=0, started=false;
  canvas.className='character-action';host.append(canvas);
  function draw(){
    raf=0;if(dead||!isActive()||document.hidden||reduced.matches)return;
    if(video.readyState>=2){
      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,video);
      gl.drawArrays(gl.TRIANGLES,0,6);
      canvas.style.opacity='1';poster.style.visibility='hidden';
      host.dataset.actionState=video.ended?'complete':'playing';
    }
    if(!video.ended)raf=requestAnimationFrame(draw);
  }
  canvas.addEventListener('webglcontextlost',()=>{if(dead)return;video.pause();cancelAnimationFrame(raf);canvas.style.opacity='0';poster.style.visibility='';host.dataset.actionState='static';});
  function sync(){
    if(dead)return;
    const active=isActive()&&!document.hidden&&!reduced.matches;
    if(!active){video.pause();cancelAnimationFrame(raf);raf=0;
      if(reduced.matches){canvas.style.opacity='0';poster.style.visibility='';}
      return;
    }
    if(!video.ended){video.play().then(()=>{started=true;if(!raf)draw();}).catch(()=>{host.dataset.actionState='static';});}
    else if(started)draw();
  }
  video.addEventListener('loadeddata',sync);video.addEventListener('ended',draw);
  video.addEventListener('error',()=>{canvas.style.opacity='0';poster.style.visibility='';host.dataset.actionState='static';});
  reduced.addEventListener('change',sync);
  sync();
  return {sync,destroy(){dead=true;cancelAnimationFrame(raf);video.pause();video.removeAttribute('src');video.load();
    reduced.removeEventListener('change',sync);gl.deleteTexture(texture);gl.deleteBuffer(buffer);gl.deleteProgram(program);gl.deleteShader(vertex);gl.deleteShader(fragment);gl.getExtension('WEBGL_lose_context')?.loseContext();canvas.remove();}};
}
