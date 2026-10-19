#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');

const repository = path.resolve(__dirname, '../..');
const definitionPath = path.resolve(process.argv[2] || path.join(repository, 'assets/characters/swordsman-male-v3/sprite.json'));
if (!definitionPath.startsWith(repository + path.sep)) {
  throw new Error('Runtime definition must stay inside the repository');
}
const api = require(path.join(repository, 'modular-sprites.js'));
const definition = JSON.parse(fs.readFileSync(definitionPath, 'utf8'));
const errors = api.validateDefinition(definition);
let decodedAtlasBytes = 0;
for (const [id, atlas] of Object.entries(definition.atlases || {})) {
  const atlasPath = path.resolve(repository, atlas.file);
  if (!atlasPath.startsWith(repository + path.sep) || !fs.existsSync(atlasPath)) {
    errors.push(`Missing or unsafe atlas file ${id}`);
    continue;
  }
  decodedAtlasBytes += atlas.width * atlas.height * 4;
}
const report = {
  passed: errors.length === 0,
  definition: path.relative(repository, definitionPath),
  character_id: definition.characterId,
  canvas: definition.canvas,
  directions: definition.directions,
  action_count: Object.keys(definition.clips || {}).length,
  decoded_atlas_bytes: decodedAtlasBytes,
  errors,
};
console.log(JSON.stringify(report, null, 2));
if (errors.length) process.exitCode = 1;
