/* Compile executable descriptors separately from ownership and runtime clocks. */
(() => {
'use strict';
const D=window.AstraeonItemDefinitions,freeze=D.freeze;
const finite=value=>Number.isFinite(value)&&value>=0;
const fail=code=>freeze({ok:false,code});
function validConfig(config){return !!config&&finite(config.itemCooldown)&&finite(config.globalCooldown)&&config.fullResourcePolicy==='reject'&&!!config.groups&&typeof config.groups==='object'&&!Array.isArray(config.groups)&&Object.values(config.groups).every(finite)}
function compile(itemId,catalog=D,config=window.AstraeonActionItemConfig){
 const definition=catalog.getDefinition(itemId);if(!definition)return fail('UNKNOWN_ITEM');
 if(definition.kind!=='consumable'||!definition.stackable)return fail('NOT_CONSUMABLE');
 const effects=window.AstraeonItemEffects.compile(definition.effects);if(!effects.ok)return effects;
 if(!validConfig(config))return fail('INVALID_ACTION_ITEM_CONFIG');
 const action=definition.actionItem;
 if(!action||action.actionKind!=='resourceRestore'||action.target!=='self'||!Array.isArray(action.usableStates)||!action.usableStates.length||!action.usableStates.every(state=>['town','field','dungeon'].includes(state)))return fail('INVALID_ACTION_ITEM');
 const cooldownDuration=action.cooldownDuration??config.itemCooldown,cooldownGroup=action.cooldownGroup;
 if(!finite(cooldownDuration)||(cooldownGroup!==null&&(typeof cooldownGroup!=='string'||!Object.hasOwn(config.groups,cooldownGroup))))return fail('INVALID_ACTION_ITEM');
 return freeze({ok:true,descriptor:{itemId,source:'actionItem',actionKind:action.actionKind,target:action.target,effects:effects.effects,cooldownDuration,cooldownGroup,groupCooldown:cooldownGroup===null?0:config.groups[cooldownGroup],usableStates:[...action.usableStates],tags:['actionItem','consumable'],metadata:{balance:'provisional'}}});
}
window.AstraeonActionItem=freeze({compile,validConfig});
})();
