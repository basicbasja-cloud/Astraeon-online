/* Shared runtime semantic checks; the Python entry also checks JSON Schema and pixels. */
'use strict';
const fs=require('node:fs'),path=require('node:path');
const {validateDefinition}=require('../modular-sprites.js');
const root=path.resolve(__dirname,'..'),base=path.join(root,'assets/characters');
const files=process.argv.slice(2);
if(!files.length)for(const entry of fs.readdirSync(base,{withFileTypes:true}))if(entry.isDirectory()&&entry.name!=='schemas')files.push(path.join(base,entry.name,'sprite.json'));
if(!files.length)throw Error('No sprite definitions');
let failures=0;
for(const file of files){
 try{const errors=validateDefinition(JSON.parse(fs.readFileSync(file,'utf8')));if(errors.length){failures+=errors.length;console.error(file+'\n'+errors.join('\n'))}else console.log('PASS metadata '+path.relative(root,file))}
 catch(error){failures++;console.error(file+': '+error.message)}
}
process.exitCode=failures?1:0;
