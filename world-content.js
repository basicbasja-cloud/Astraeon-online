/* Authored region content. Coordinates are ordinary Cartesian ground units. */
window.AstraeonContent = Object.freeze({
  region: {id:'shenzhou', name:'Shenzhou', zones:['town','meadow','moonbamboo','moonveil']},
  futureRegions: ['Valeria','Yamato','Helion','Veyr Reach'],
  atlas: {
    guild:{rect:[0,0,447,512],anchor:[.47,.94]},
    shop:{rect:[447,0,342,512],anchor:[.48,.94]},
    shrine:{rect:[789,0,336,512],anchor:[.5,.94]},
    gate:{rect:[1125,0,411,512],anchor:[.5,.93]},
    tree:{rect:[0,512,430,512],anchor:[.5,.87]},
    stall:{rect:[430,512,360,512],anchor:[.5,.86]},
    fountain:{rect:[790,512,360,512],anchor:[.5,.87]},
    cart:{rect:[1150,512,386,512],anchor:[.5,.84]}
  },
  secondaryAtlas:{
    planter:{rect:[25,75,365,375],anchor:[.5,.95]},bench:{rect:[410,72,340,395],anchor:[.5,.96]},crates:{rect:[770,88,410,365],anchor:[.5,.96]},board:{rect:[1160,10,376,452],anchor:[.5,.97]},
    bamboo:{rect:[0,466,380,523],anchor:[.55,.97]},arch:{rect:[350,477,453,522],anchor:[.5,.98]},terrace:{rect:[775,531,474,460],anchor:[.5,.97]},pillar:{rect:[1200,489,330,515],anchor:[.5,.98]}
  },
  goldenScene:{name:'Wayfarer Court',concept:'A Shenzhou frontier town whose Consortium court gathers adventurers and trade onto the eastern road to Goldenfield.',hero:'warrior',landmark:'guild-hall',palette:{stone:'#b5ad95',roof:'blue civic slate / muted clay',timber:'#654c38',cloth:'#699b9b',green:'#667753',magic:'#8bc2b4'},sun:'upper left, shadows southeast',focal:['Consortium Hall','Astral fountain','adventurer'],approval:'pending'}
});
