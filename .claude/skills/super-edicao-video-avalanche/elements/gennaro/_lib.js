/* Shared animation helpers for deterministic seek rendering. Exposes only window.__lib. */
(function(){
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const lerp=(a,b,p)=>a+(b-a)*p;
const seg=(t,t0,d)=>clamp((t-t0)/d);
const E={
  outCubic:p=>1-Math.pow(1-p,3),
  inOutCubic:p=>p<.5?4*p*p*p:1-Math.pow(-2*p+2,3)/2,
  outQuint:p=>1-Math.pow(1-p,5),
  outBack:(p,s=1.7)=>{const c1=s,c3=c1+1;return 1+c3*Math.pow(p-1,3)+c1*Math.pow(p-1,2);},
  outExpo:p=>p>=1?1:1-Math.pow(2,-10*p),
};
function win(t,t0,inD,hold,outD,easeIn=E.outCubic,easeOut=E.inOutCubic){
  const t1=t0+inD, t2=t1+hold, t3=t2+outD;
  if(t<t0) return 0;
  if(t<t1) return easeIn(seg(t,t0,inD));
  if(t<t2) return 1;
  if(t<t3) return 1-easeOut(seg(t,t2,outD));
  return 0;
}
function riseIn(p, dist=70){ return { o: E.outCubic(clamp(p*1.15)), ty: (1-E.outCubic(p))*dist }; }
function place(el,{ty=0,tx=0,scale=1,cx=true}={}){
  el.style.transform=`translateX(${cx?'-50%':'0'}) translate(${tx}px,${ty}px) scale(${scale})`;
}
function show(el,o){ el.style.opacity=o; }
function fmtBR(n,{prefix='',suffix=''}={}){
  return prefix + Math.round(n).toLocaleString('pt-BR') + suffix;
}
function count(p,a,b,ease=E.outExpo){ return lerp(a,b,ease(clamp(p))); }
window.__lib={clamp,lerp,seg,E,win,riseIn,place,show,fmtBR,count};
})();
