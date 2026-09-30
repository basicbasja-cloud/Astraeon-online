/* Original UI pictograms; shared strokes replace platform-dependent emoji. */
(() => {
'use strict';
const paths={
 sword:'M5 19 18 6l1-3-3 1L3 17m2-4 6 6m-8 2 3-3',
 bow:'M6 3c13 1 13 17 0 18L6 3zm0 9h15m-4-3 4 3-4 3',
 staff:'M6 22 15 7m-3-5 5 1 3 4-4 4-5-3z',
 shield:'M12 3 3 7l1 8 8 6 8-6 1-8-9-4zm0 4v10',
 heart:'M12 20C-2 12 4 2 12 8c8-6 14 4 0 12zM8 13h8m-4-4v8',
 burst:'m12 2 2 7 7 3-7 2-2 8-2-8-8-2 8-3z',
 dodge:'M3 8h8m-8 4h6m-6 4h4m5-10 8 6-8 6m7-6H9',
 flask:'M9 3h6m-5 0v6L5 18c-1 2 1 3 3 3h8c2 0 4-1 3-3l-5-9V3M7 15h10',
 hand:'M8 12V5a1.5 1.5 0 0 1 3 0v7-9a1.5 1.5 0 0 1 3 0v9-7a1.5 1.5 0 0 1 3 0v8-5a1.5 1.5 0 0 1 3 0v8c0 4-2 7-6 7-3 0-5-2-7-4l-3-4c-1-2 1-3 2-2l2 2',
 journal:'M5 3h14v18H5V3zm3 4h8m-8 4h8m-8 4h5M3 5h3m-3 5h3m-3 5h3',
 character:'M12 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM4 21v-3a8 8 0 0 1 16 0v3',
 inventory:'M7 6h10l3 5v10H4V11l3-5zm2 0V3h6v3M4 12h16m-10 0v4h4v-4',
 map:'m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6zm6-3v15m6-12v15',
 systems:'M4 6h16M4 12h16M4 18h16M8 3v6m8 0v6m-6 0v6'
};
function icon(name){return `<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="${paths[name]||paths.burst}"/></svg>`}
function action(id,archetype){return icon(id==='attack'?archetype==='ranger'?'bow':archetype==='mage'?'staff':'sword':id==='skill2'?'shield':id==='skill3'?'heart':id==='skill4'?'burst':id==='skill1'?archetype==='ranger'?'bow':archetype==='mage'?'staff':'sword':id==='potion'?'flask':id==='interact'?'hand':id)}
window.AstraeonIcons={icon,action};
})();
