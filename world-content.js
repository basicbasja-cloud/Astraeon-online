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
  goldenScene:{name:'Wayfarer Court',concept:'A Shenzhou frontier town whose Consortium court gathers adventurers and trade onto the eastern road to Goldenfield.',hero:'warrior',landmark:'guild-hall',center:[14.5,16.5],plaza:[[10.8,12.2],[18.2,12.2],[19.4,16],[18.5,20.4],[10.5,20.4],[9.8,16]],palette:{stone:'#b5ad95',roof:'jade slate / muted clay',timber:'#654c38',cloth:'#699b9b',green:'#667753',magic:'#8bc2b4'},sun:'upper left, shadows southeast',focal:['Consortium Hall','Astral fountain','adventurer'],axis:[[10.5,17.8],[14.5,17.8],[22,17.8],[36,16],[42,16]],approval:'pending'},
  townBlocks:[{x:3.6,y:10,w:5.8,h:4.6},{x:20.5,y:9.8,w:5.2,h:4.9},{x:27,y:25,w:5.5,h:4.6},{x:1,y:30.5,w:4.5,h:4.5},{x:13.4,y:14.4,w:2.2,h:1.3,kind:'fountain'},{x:3,y:1,w:7,h:5},{x:30,y:10,w:5,h:4.3},{x:32,y:21,w:5,h:5},{x:23,y:31,w:5,h:4},{x:34,y:30,w:5,h:5}],
  districts:[{name:'Consortium Terrace',x:8,y:7},{name:'Wayfarer Plaza',x:14.5,y:16},{name:'Lantern Market',x:23,y:16},{name:'Artisan Lane',x:34,y:25},{name:'Willow Quarter',x:28,y:34},{name:'Caravan Gate',x:42,y:16}],
  townObjects: [
    {id:'planter-a',pack:'secondary',art:'planter',x:10.9,y:12.6,w:83,h:86},
    {id:'planter-b',pack:'secondary',art:'planter',x:18.0,y:12.6,w:83,h:86},
    {id:'bench-a',pack:'secondary',art:'bench',x:10.4,y:19.9,w:64,h:74},
    {id:'bench-b',pack:'secondary',art:'bench',x:18.2,y:19.9,w:64,h:74},
    {id:'market-crates',pack:'secondary',art:'crates',x:24.8,y:19.0,w:73,h:65},
    {id:'guild-board',pack:'secondary',art:'board',x:10.7,y:17.3,w:57,h:69},
    {id:'west-house',art:'shop',x:-2,y:15,w:207,h:270,building:true},
    {id:'east-house',art:'shop',x:32,y:15.4,w:275,h:412,building:true},
    {id:'north-house',art:'guild',x:7,y:7,w:500,h:573,building:true},
    {id:'east-garden',art:'tree',x:33,y:24,w:147,h:178,tree:true},
    {id:'west-garden',art:'tree',x:-3,y:24,w:147,h:178,tree:true},
    {id:'guild-hall',art:'guild',x:8,y:15,w:478,h:437,building:true},
    {id:'market-shop',art:'shop',x:22,y:15.4,w:315,h:472,building:true},
    {id:'moon-shrine',art:'shrine',x:3.3,y:35,w:306,h:466,building:true},
    {id:'residence',art:'shop',x:29,y:29,w:280,h:419,building:true},
    {id:'north-gate',art:'gate',x:14.5,y:3.7,w:310,h:386,building:true},
    {id:'south-gate',art:'gate',x:14.5,y:38,w:330,h:411,building:true},
    {id:'astral-fountain',art:'fountain',x:14.5,y:14.8,w:130,h:185},
    {id:'food-market',art:'stall',x:24,y:18.6,w:145,h:206},
    {id:'caravan-cart',art:'cart',x:26.7,y:20.8,w:113,h:150},
    {id:'caravan-gate',art:'gate',x:42,y:16.6,w:365,h:454,building:true},
    {id:'artisan-workshop',art:'shop',x:34,y:26.2,w:300,h:449,building:true},
    {id:'willow-house',art:'shop',x:26,y:35.8,w:270,h:404,building:true},
    {id:'east-inn',art:'shop',x:36,y:35.8,w:296,h:443,building:true},
    {id:'east-cart',art:'cart',x:39,y:18.3,w:140,h:186},
    ...[[33,5],[40,8],[40,25],[19,31],[31,31],[40,35],[6,34],[15,35]].map(([x,y],i)=>({id:'district-tree-'+i,art:'tree',x,y,w:192+i%3*18,h:229+i%3*22,tree:true})),
    ...[[3,5],[7,6],[23,4],[27,7],[5.4,16.5],[5.8,19],[26,22.5],[28,25],[1.5,33.5],[5.3,34.4],[20,25],[25,9]].map(([x,y],i)=>({id:'tree-'+i,art:'tree',x,y,w:170+(i%3)*13,h:203+(i%3)*15,tree:true}))
  ],
  townRoads: [
    {role:'street',points:[[14.5,-6],[14.5,12.2]],width:2.6},
    {role:'street',points:[[14.5,20.4],[14.5,46]],width:2.6},
    {role:'avenue',points:[[9.8,17.8],[19.1,17.8],[28,17.2],[36,16],[41.5,16]],width:3.8},
    {role:'street',points:[[-5,17.8],[9.8,17.8]],width:2.6},
    {role:'field',points:[[42.6,16],[50,16]],width:1.9},
    {role:'service',points:[[20.3,19.1],[24.7,20.4],[29,22],[31,26],[31,36]],width:1.1},
    {role:'service',points:[[10.2,20.4],[10.2,28],[3.3,31],[3.3,35]],width:1.1},
    {role:'street',points:[[10.2,28],[14.5,31],[21,31],[30,29],[40,29]],width:1.9}
  ],
  walkers: [
    {id:'guard-1',route:[[11.7,19],[11.7,13.4],[17.3,13.4],[17.3,19]],pace:.58,tint:0},
    {id:'guard-2',route:[[17.3,19],[17.3,13.4],[11.7,13.4],[11.7,19]],pace:.54,tint:0},
    {id:'customer-1',route:[[20.4,19],[22.4,20.5],[22.3,22],[19.8,20.5]],pace:.46,tint:45}
  ]
});
