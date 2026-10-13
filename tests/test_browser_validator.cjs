const test=require("node:test");
const assert=require("node:assert/strict");
const {validateBundle}=require("../web/validator.js");
const bundle=(type,entry=[])=>({resourceType:"Bundle",type,entry});
test("valid collection and resolved reference",()=>{
  const b=bundle("collection",[
    {fullUrl:"urn:uuid:pat",resource:{resourceType:"Patient",id:"pat"}},
    {fullUrl:"urn:uuid:obs",resource:{resourceType:"Observation",id:"obs",subject:{reference:"Patient/pat"}}}
  ]);
  assert.equal(validateBundle(b).valid,true);
  assert.equal(validateBundle(b).warningCount,0);
});
test("invalid root, type, and entry",()=>{
  assert.equal(validateBundle(null).valid,false);
  assert.equal(validateBundle(bundle("wrong")).valid,false);
  assert.equal(validateBundle({...bundle("collection"),entry:{}}).valid,false);
});
test("document and message invariants",()=>{
  const d=validateBundle(bundle("document",[{resource:{resourceType:"Patient"}}]));
  assert.deepEqual(d.issues.map(i=>i.code).filter(c=>c.startsWith("bdl-")).sort(),["bdl-10","bdl-11","bdl-9"]);
  assert.equal(validateBundle(bundle("message",[{resource:{resourceType:"Patient"}}])).valid,false);
});
test("request, response, and search requirements",()=>{
  assert.equal(validateBundle(bundle("transaction",[{resource:{resourceType:"Patient"}}])).issues.some(i=>i.code==="bdl-3"),true);
  assert.equal(validateBundle(bundle("batch-response",[{response:{status:"200 OK"}}])).valid,true);
  assert.equal(validateBundle(bundle("collection",[{search:{mode:"match"},response:{status:"200"}}])).errorCount,2);
});
test("duplicate fullUrl, versioned fullUrl, and external reference warning",()=>{
  const r={fullUrl:"urn:uuid:one",resource:{resourceType:"Patient",id:"p"}};
  assert.equal(validateBundle(bundle("collection",[r,r])).issues.some(i=>i.code==="bdl-7"),true);
  const v={fullUrl:"https://example.org/Patient/p/_history/1",resource:{resourceType:"Patient",id:"p"}};
  assert.equal(validateBundle(bundle("collection",[v])).issues.some(i=>i.code==="bdl-8"),true);
  const ext=bundle("collection",[{resource:{resourceType:"Observation",subject:{reference:"Patient/missing"}}}]);
  assert.equal(validateBundle(ext).valid,true);
  assert.equal(validateBundle(ext).warningCount,1);
});
test("resource id and total are validated",()=>{
  const b=bundle("collection",[{resource:{resourceType:"Patient",id:"invalid/id"}}]);
  b.total=2;
  assert.equal(validateBundle(b).errorCount,2);
});
