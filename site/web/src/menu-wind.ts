/** A single textured quad. Only foliage pixels are displaced; typography stays in HTML. */
export function animateFoliage(canvas: HTMLCanvasElement, image: HTMLImageElement): () => void {
  const gl = canvas.getContext('webgl', { alpha: false, antialias: false, depth: false, preserveDrawingBuffer: false });
  if (!gl) return () => {};
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const vertex = 'attribute vec2 p; varying vec2 uv; void main(){uv=vec2((p.x+1.)*.5,(1.-p.y)*.5);gl_Position=vec4(p,0.,1.);}';
  const fragment = `
    precision mediump float;
    varying vec2 uv;
    uniform sampler2D scene;
    uniform float time;
    uniform float moving;
    float region(vec2 p,vec2 a,vec2 b,float feather){
      return smoothstep(a.x,a.x+feather,p.x)*(1.-smoothstep(b.x-feather,b.x,p.x))*
        smoothstep(a.y,a.y+feather,p.y)*(1.-smoothstep(b.y-feather,b.y,p.y));
    }
    void main(){
      // Right plant above/beside the bottle; never warp the bottle or the notebook.
      float right=region(uv,vec2(.735,-.08),vec2(1.06,.425),.045);
      float bottle=region(uv,vec2(.846,.10),vec2(.972,.68),.008);
      right*=1.-bottle;
      float left=region(uv,vec2(-.10,.64),vec2(.215,1.1),.08);
      float leaves=max(right,left);
      float gust=sin(time*.85)+.38*sin(time*1.47+.8);
      vec2 breeze=vec2(sin(uv.y*19.+time*1.1)*.0018+gust*.0013,
        sin(uv.x*21.+time*.9)*.0009);
      vec2 sampleUV=clamp(uv+breeze*leaves*moving,vec2(.001),vec2(.999));
      gl_FragColor=texture2D(scene,sampleUV);
    }`;
  const compile = (kind: number, source: string) => {
    const shader = gl.createShader(kind)!;
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      gl.deleteShader(shader);
      throw new Error('Menu shader compilation failed');
    }
    return shader;
  };
  let shaders: WebGLShader[] = [];
  const program = gl.createProgram()!;
  const buffer = gl.createBuffer();
  const texture = gl.createTexture();
  try {
    shaders = [compile(gl.VERTEX_SHADER, vertex), compile(gl.FRAGMENT_SHADER, fragment)];
    shaders.forEach(shader => gl.attachShader(program, shader));
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error('Menu shader link failed');
    gl.useProgram(program);
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
    const position = gl.getAttribLocation(program, 'p');
    gl.enableVertexAttribArray(position);
    gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
  } catch {
    gl.deleteProgram(program);
    gl.deleteBuffer(buffer);
    gl.deleteTexture(texture);
    shaders.forEach(shader => gl.deleteShader(shader));
    return () => {};
  }
  const time = gl.getUniformLocation(program, 'time');
  const moving = gl.getUniformLocation(program, 'moving');
  let tick = 0;
  let disposed = false;
  let inView = false;
  let previous = -Infinity;
  const draw = (now: number) => {
    tick = 0;
    if (disposed || gl.isContextLost()) return;
    if (now - previous >= 1000 / 30 || reduced.matches) {
      previous = now;
      const width = Math.min(1920, Math.round(canvas.clientWidth * Math.min(devicePixelRatio, 1.5)));
      const height = Math.round(width * image.naturalHeight / image.naturalWidth);
      if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
        gl.viewport(0, 0, width, height);
      }
      gl.uniform1f(time, now / 1000);
      gl.uniform1f(moving, reduced.matches ? 0 : 1);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      canvas.classList.add('is-ready');
    }
    if (inView && !document.hidden && !reduced.matches) tick = requestAnimationFrame(draw);
  };
  const resume = () => {
    cancelAnimationFrame(tick);
    tick = 0;
    if (inView && !document.hidden && !disposed) tick = requestAnimationFrame(draw);
  };
  const observer = new IntersectionObserver(([entry]) => { inView = entry.isIntersecting; resume(); });
  observer.observe(canvas);
  const resize = new ResizeObserver(() => { previous = -Infinity; resume(); });
  resize.observe(canvas);
  document.addEventListener('visibilitychange', resume);
  reduced.addEventListener('change', resume);
  const lost = () => { canvas.classList.remove('is-ready'); cancelAnimationFrame(tick); };
  canvas.addEventListener('webglcontextlost', lost);
  return () => {
    disposed = true;
    cancelAnimationFrame(tick);
    observer.disconnect();
    resize.disconnect();
    document.removeEventListener('visibilitychange', resume);
    reduced.removeEventListener('change', resume);
    canvas.removeEventListener('webglcontextlost', lost);
    gl.deleteTexture(texture);
    gl.deleteBuffer(buffer);
    gl.deleteProgram(program);
    shaders.forEach(shader => gl.deleteShader(shader));
    gl.getExtension('WEBGL_lose_context')?.loseContext();
  };
}
