(function(){
"use strict";
const text=document.getElementById("payload"),file=document.getElementById("file"),results=document.getElementById("results"),summary=document.getElementById("summary"),download=document.getElementById("download");
let report=null;
const SAMPLE={resourceType:"Bundle",type:"collection",id:"example-collection",entry:[
  {fullUrl:"urn:uuid:11111111-1111-4111-8111-111111111111",resource:{resourceType:"Patient",id:"example"}},
  {fullUrl:"urn:uuid:22222222-2222-4222-8222-222222222222",resource:{resourceType:"Observation",id:"obs",status:"final",code:{text:"Demonstration"},subject:{reference:"Patient/example"}}}
]};
function reset(){report=null;summary.textContent="No validation run yet.";results.replaceChildren();download.disabled=true;}
function issue(severity,path,code,message){
  const li=document.createElement("li");li.className=severity==="error"?"error":"warning";
  const head=document.createElement("strong"),loc=document.createElement("code"),body=document.createElement("span");
  head.textContent=severity.toUpperCase()+" · "+code;loc.textContent=path;body.textContent=message;
  li.append(head,loc,body);return li;
}
document.getElementById("sample").addEventListener("click",()=>{text.value=JSON.stringify(SAMPLE,null,2);reset();});
document.getElementById("clear").addEventListener("click",()=>{text.value="";file.value="";reset();});
document.getElementById("validate").addEventListener("click",()=>{
  try{
    if(new Blob([text.value]).size>5*1024*1024) throw Error("Input exceeds 5 MiB.");
    report=FHIRBundleValidator.validateBundle(JSON.parse(text.value));
    summary.textContent=(report.valid?"Passed implemented structural checks":"Structural errors detected")+" · "+report.resourceCount+" resources · "+report.errorCount+" errors · "+report.warningCount+" warnings";
    results.replaceChildren();
    if(!report.issues.length){const li=document.createElement("li");li.textContent="No issues found by the implemented checks.";results.append(li);}
    report.issues.forEach(i=>results.append(issue(i.severity,i.path,i.code,i.message)));
    download.disabled=false;
  }catch(err){
    report=null;summary.textContent="Could not validate input.";download.disabled=true;
    results.replaceChildren(issue("error","$","INPUT",err instanceof SyntaxError?"Invalid JSON: "+err.message:err.message));
  }
});
file.addEventListener("change",async()=>{
  if(!file.files.length)return;
  if(file.files[0].size>5*1024*1024){summary.textContent="File exceeds the 5 MiB limit.";file.value="";return;}
  try{text.value=await file.files[0].text();reset();}catch(err){summary.textContent="Unable to read file.";}
});
download.addEventListener("click",()=>{
  if(!report)return;
  const url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)+"\n"],{type:"application/json"}));
  const a=document.createElement("a");a.href=url;a.download="fhir-validation-report.json";a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
});
})();
