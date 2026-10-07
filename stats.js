/* Pure stat calculation. Percent modifiers use fractions: .1 means +10%. */
(() => {
'use strict';
const defaults=window.AstraeonProgressionConfig;
function freeze(value){if(value&&typeof value==='object'){Object.values(value).forEach(freeze);Object.freeze(value)}return value}
function add(target,values,scale=1){
 if(!values||typeof values!=='object'||Array.isArray(values))throw new TypeError('Expected a stat map');
 for(const [key,value] of Object.entries(values)){
  if(!Object.hasOwn(target,key))throw new TypeError(`Unknown stat: ${key}`);
  if(!Number.isFinite(value))throw new RangeError(`Invalid modifier for ${key}`);
  target[key]+=value*scale;if(!Number.isFinite(target[key]))throw new RangeError(`Stat overflow: ${key}`);
 }
}
function calculate(input={},config=defaults){
 const d=config.derived,primary=Object.fromEntries(config.primary.keys.map(key=>[key,input.primaryStats?.[key]??config.primary.initial]));
 for(const [key,value] of Object.entries(primary))if(!Number.isFinite(value)||value<0)throw new RangeError(`Invalid primary stat: ${key}`);
 window.AstraeonProgression.integer(input.baseLevel??1,'Base Level',1,config.progression.storedLevelLimit);
 const modifiers=[...(input.equipmentModifiers||[]),...(input.passiveModifiers||[]),...(input.temporaryEffectModifiers||[])];
 const flat=Object.fromEntries(Object.keys(d.base).map(key=>[key,0])),rates={...flat};
 for(const modifier of modifiers){
  if(!modifier||typeof modifier!=='object'||Array.isArray(modifier))throw new TypeError('Invalid modifier');
  for(const key of Object.keys(modifier))if(!['id','primary','add','multiply'].includes(key))throw new TypeError(`Unknown modifier operation: ${key}`);
  if(modifier.primary)add(primary,modifier.primary);
  if(modifier.add)add(flat,modifier.add);
  if(modifier.multiply)add(rates,modifier.multiply);
 }
 for(const key of config.primary.keys)primary[key]=Math.max(0,primary[key]);
 const derived={...d.base};add(derived,input.characterBase||{});
 add(derived,d.perBaseLevel,(input.baseLevel??1)-config.progression.base.initialLevel);
 for(const key of config.primary.keys)add(derived,d.primary[key]||{},primary[key]-config.primary.initial);
 // Hooks return additive conversions. Frozen copies protect the shared calculation inputs.
 const context=freeze({baseLevel:input.baseLevel??1,primaryStats:{...primary},derived:{...derived}});
 for(const convert of input.conversionHooks||[])add(derived,convert(context));
 add(derived,flat);
 for(const key of Object.keys(derived)){
  let value=derived[key]*(1+rates[key]);if(!Number.isFinite(value))throw new RangeError(`Stat overflow: ${key}`);
  const [min,max]=d.limits[key];value=Math.max(min,Math.min(max,value));
  derived[key]=d.integer.includes(key)?Math.floor(value):Number(value.toFixed(d.precision));
 }
 return freeze(derived);
}
window.AstraeonStats=Object.freeze({calculate,freeze});
})();
