const test = require("node:test");
const assert = require("node:assert/strict");
const vm = require("node:vm");
const fs = require("node:fs");
const { validateBundle } = require("../web/validator.js");

test("browser input, validation, report and reset workflow", () => {
  const nodes = new Map();
  class Element {
    constructor(id) { this.id=id; this.value=""; this.textContent=""; this.disabled=id==="download"; this.files=[]; this.children=[]; this.listeners={}; }
    addEventListener(name, fn) { this.listeners[name]=fn; }
    click() { if(this.listeners.click) this.listeners.click(); this.clicked=true; }
    append(...items) { this.children.push(...items); }
    replaceChildren(...items) { this.children=items; }
  }
  const document = {
    getElementById(id) { if(!nodes.has(id)) nodes.set(id,new Element(id)); return nodes.get(id); },
    createElement(tag) { return new Element(tag); }
  };
  let revoked=false,downloadTriggered=false;
  const URL = {
    createObjectURL() { return "blob:test"; },
    revokeObjectURL() { revoked=true; }
  };
  const realCreate = document.createElement;
  document.createElement = function(tag) {
    const element=realCreate(tag);
    if(tag==="a") element.click=()=>{ downloadTriggered=true; };
    return element;
  };
  const app=fs.readFileSync(require.resolve("../web/app.js"),"utf8");
  vm.runInNewContext(app,{ document, Blob, URL, setTimeout:fn=>fn(),
    FHIRBundleValidator:{validateBundle}, JSON, Error, SyntaxError });
  const get=id=>document.getElementById(id);
  get("sample").click();
  assert.match(get("payload").value,/"resourceType": "Bundle"/);
  get("validate").click();
  assert.match(get("summary").textContent,/Passed implemented structural checks/);
  assert.equal(get("download").disabled,false);
  assert.equal(get("results").children.length,1);
  get("download").click();
  assert.equal(downloadTriggered,true);
  assert.equal(revoked,true);
  get("payload").value="not json";
  get("validate").click();
  assert.match(get("summary").textContent,/Could not validate/);
  assert.equal(get("download").disabled,true);
  get("clear").click();
  assert.equal(get("payload").value,"");
  assert.equal(get("results").children.length,0);
});
