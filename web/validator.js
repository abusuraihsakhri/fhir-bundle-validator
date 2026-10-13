/* Partial FHIR R4 Bundle structural checks. Not a full profile or terminology validator. */
(function(root,factory) {
  const api=factory();
  if (typeof module==="object" && module.exports) module.exports=api;
  root.FHIRBundleValidator=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";
  const TYPES=new Set(["document","message","transaction","transaction-response","batch","batch-response","history","searchset","collection"]);
  const REQ=new Set(["transaction","batch","history"]);
  const RESP=new Set(["transaction-response","batch-response","history"]);
  const isObj=v=>v!==null&&typeof v==="object"&&!Array.isArray(v);
  const nonempty=v=>typeof v==="string"&&v.trim().length>0;
  const ID=/^[A-Za-z0-9.-]{1,64}$/;
  function validateBundle(bundle){
    const issues=[],ids=new Set(),seen=new Set();
    let entries=[],resourceCount=0;
    const add=(severity,path,code,message)=>issues.push({severity,path,code,message});
    const err=(path,code,message)=>add("error",path,code,message);
    const warn=(path,code,message)=>add("warning",path,code,message);
    if(!isObj(bundle)){
      err("$","STRUCTURE","Expected a JSON object representing a FHIR Bundle.");
      return {valid:false,resourceCount:0,errorCount:1,warningCount:0,issues};
    }
    if(bundle.resourceType!=="Bundle") err("$.resourceType","RESOURCE_TYPE","resourceType must be Bundle.");
    if(!TYPES.has(bundle.type)) err("$.type","BUNDLE_TYPE","Unknown FHIR R4 Bundle type.");
    if(bundle.id!==undefined&&(typeof bundle.id!=="string"||!ID.test(bundle.id))) err("$.id","FHIR_ID","Invalid Bundle id; expected 1–64 letters, numbers, hyphens, or periods.");
    if(bundle.entry!==undefined&&!Array.isArray(bundle.entry)) err("$.entry","ENTRY_TYPE","entry must be an array.");
    if(Array.isArray(bundle.entry)) entries=bundle.entry;
    if(bundle.total!==undefined){
      if(!["history","searchset"].includes(bundle.type)) err("$.total","bdl-1","total is allowed only for searchset/history.");
      if(!Number.isInteger(bundle.total)||bundle.total<0) err("$.total","TOTAL","total must be a non-negative integer.");
    }
    if(bundle.type==="document"){
      if(!isObj(bundle.identifier)||!nonempty(bundle.identifier.system)||!nonempty(bundle.identifier.value))
        err("$.identifier","bdl-9","Document requires identifier.system and identifier.value.");
      if(!nonempty(bundle.timestamp)) err("$.timestamp","bdl-10","Document requires timestamp.");
      if(!isObj(entries[0])||!isObj(entries[0].resource)||entries[0].resource.resourceType!=="Composition")
        err("$.entry[0].resource","bdl-11","First document entry must contain Composition.");
    }
    if(bundle.type==="message"&&(!isObj(entries[0])||!isObj(entries[0].resource)||entries[0].resource.resourceType!=="MessageHeader"))
      err("$.entry[0].resource","bdl-12","First message entry must contain MessageHeader.");
    entries.forEach((entry,i)=>{
      const path="$.entry["+i+"]";
      if(!isObj(entry)){err(path,"ENTRY_TYPE","Entry must be an object.");return;}
      const request=Object.hasOwn(entry,"request"),response=Object.hasOwn(entry,"response"),resource=Object.hasOwn(entry,"resource");
      if(!resource&&!request&&!response) err(path,"bdl-5","Entry needs resource, request, or response.");
      if(request!==REQ.has(bundle.type)) err(path+".request","bdl-3","Invalid request presence for Bundle.type.");
      if(response!==RESP.has(bundle.type)) err(path+".response","bdl-4","Invalid response presence for Bundle.type.");
      if(entry.search!==undefined&&bundle.type!=="searchset") err(path+".search","bdl-2","entry.search only allowed in searchset.");
      if(request&&(!isObj(entry.request)||!["GET","HEAD","POST","PUT","DELETE","PATCH"].includes(entry.request.method)||!nonempty(entry.request.url)))
        err(path+".request","REQUEST","request requires a recognized HTTP method and URL.");
      if(response&&(!isObj(entry.response)||!nonempty(entry.response.status)))
        err(path+".response","RESPONSE","response.status is required.");
      if(entry.fullUrl!==undefined){
        if(!nonempty(entry.fullUrl)) err(path+".fullUrl","FULL_URL","fullUrl must be a nonempty string.");
        else {
          if(entry.fullUrl.includes("/_history/")) err(path+".fullUrl","bdl-8","fullUrl may not be version-specific.");
          const ver=isObj(entry.resource)&&isObj(entry.resource.meta)?entry.resource.meta.versionId:undefined;
          const key=entry.fullUrl+"|"+(ver===undefined?"":String(ver));
          if(bundle.type!=="history"&&seen.has(key)) err(path+".fullUrl","bdl-7","Duplicate fullUrl and resource version.");
          seen.add(key);ids.add(entry.fullUrl);
        }
      }
      if(resource){
        if(!isObj(entry.resource)||!nonempty(entry.resource.resourceType))
          err(path+".resource.resourceType","RESOURCE_TYPE","resourceType must be a nonempty string.");
        else {
          resourceCount++;
          if(entry.resource.id!==undefined&&(typeof entry.resource.id!=="string"||!ID.test(entry.resource.id))) err(path+".resource.id","FHIR_ID","Invalid resource id.");
          if(nonempty(entry.resource.id)) ids.add(entry.resource.resourceType+"/"+entry.resource.id);
        }
      }
    });
    entries.forEach((entry,i)=>{
      if(!isObj(entry)||!isObj(entry.resource)) return;
      const contained=new Set(Array.isArray(entry.resource.contained)?
        entry.resource.contained.filter(isObj).map(r=>r.id).filter(nonempty):[]);
      function visit(value,path,depth){
        if(depth>40||!value||typeof value!=="object") return;
        if(Array.isArray(value)){value.forEach((v,j)=>visit(v,path+"["+j+"]",depth+1));return;}
        if(nonempty(value.reference)){
          const ref=value.reference;
          if(ref.startsWith("#")&&!contained.has(ref.slice(1))) warn(path+".reference","CONTAINED_REF","Unresolved contained reference.");
          else if((/^urn:(uuid|oid):/i.test(ref)||/^[A-Z][A-Za-z0-9]+\/[A-Za-z0-9.-]+$/.test(ref))&&!ids.has(ref))
            warn(path+".reference","EXTERNAL_REF","Unresolved within this Bundle; external references may be valid.");
        }
        Object.keys(value).forEach(k=>{if(k!=="contained")visit(value[k],path+"."+k,depth+1);});
      }
      visit(entry.resource,"$.entry["+i+"].resource",0);
    });
    const errorCount=issues.filter(i=>i.severity==="error").length;
    return {valid:errorCount===0,resourceCount,errorCount,warningCount:issues.length-errorCount,issues};
  }
  return {validateBundle};
});
