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
  townBlocks:[{x:3.6,y:10,w:5.8,h:4.6},{x:20.5,y:9.8,w:5.2,h:4.9},{x:24.5,y:19.5,w:5.5,h:4.6},{x:3.9,y:20,w:5.2,h:5.6},{x:3,y:1,w:7,h:5},{x:30,y:10,w:5,h:4.3},{x:32,y:21,w:5,h:5},{x:23,y:31,w:5,h:4},{x:34,y:30,w:5,h:5}],
  districts:[{name:'Consortium Terrace',x:8,y:7},{name:'Wayfarer Plaza',x:14.5,y:16},{name:'Lantern Market',x:23,y:16},{name:'Artisan Lane',x:34,y:25},{name:'Willow Quarter',x:28,y:34},{name:'Caravan Gate',x:42,y:16}],
  townObjects: [
    {id:'planter-a',pack:'secondary',art:'planter',x:11,y:12,w:100,h:103},
    {id:'planter-b',pack:'secondary',art:'planter',x:18.2,y:12,w:100,h:103},
    {id:'planter-c',pack:'secondary',art:'planter',x:11,y:20.5,w:91,h:94},
    {id:'planter-d',pack:'secondary',art:'planter',x:18,y:22,w:91,h:94},
    {id:'bench-a',pack:'secondary',art:'bench',x:10,y:18,w:70,h:80},
    {id:'bench-b',pack:'secondary',art:'bench',x:17.4,y:18,w:70,h:80},
    {id:'market-crates',pack:'secondary',art:'crates',x:23,y:18.2,w:85,h:76},
    {id:'guild-board',pack:'secondary',art:'board',x:12.3,y:18.5,w:57,h:69},
    {id:'west-house',art:'shop',x:-2,y:15,w:207,h:270,building:true},
    {id:'east-house',art:'shop',x:32,y:15.4,w:275,h:412,building:true},
    {id:'north-house',art:'guild',x:7,y:7,w:500,h:573,building:true},
    {id:'east-garden',art:'tree',x:33,y:24,w:147,h:178,tree:true},
    {id:'west-garden',art:'tree',x:-3,y:24,w:147,h:178,tree:true},
    {id:'guild-hall',art:'guild',x:8,y:15,w:420,h:481,building:true},
    {id:'market-shop',art:'shop',x:22,y:15.4,w:315,h:472,building:true},
    {id:'moon-shrine',art:'shrine',x:7,y:27,w:306,h:466,building:true},
    {id:'residence',art:'shop',x:26,y:25,w:280,h:419,building:true},
    {id:'north-gate',art:'gate',x:14.5,y:3.7,w:310,h:386,building:true},
    {id:'south-gate',art:'gate',x:14.5,y:38,w:330,h:411,building:true},
    {id:'astral-fountain',art:'fountain',x:14.5,y:14.8,w:130,h:185},
    {id:'cloth-market',art:'stall',x:22,y:16.5,w:175,h:249},
    {id:'food-market',art:'stall',x:27,y:17,w:155,h:220},
    {id:'caravan-cart',art:'cart',x:28,y:20,w:140,h:186},
    {id:'guild-supplies',art:'cart',x:5.7,y:17,w:104,h:114},
    {id:'caravan-gate',art:'gate',x:42,y:16.6,w:365,h:454,building:true},
    {id:'artisan-workshop',art:'shop',x:34,y:26.2,w:300,h:449,building:true},
    {id:'willow-house',art:'shop',x:26,y:35.8,w:270,h:404,building:true},
    {id:'east-inn',art:'shop',x:36,y:35.8,w:296,h:443,building:true},
    {id:'east-cart',art:'cart',x:39,y:18.3,w:140,h:186},
    ...[[33,5],[40,8],[40,25],[19,31],[31,31],[40,35],[6,34],[15,35]].map(([x,y],i)=>({id:'district-tree-'+i,art:'tree',x,y,w:192+i%3*18,h:229+i%3*22,tree:true})),
    ...[[3,5],[7,6],[23,4],[27,7],[3,17],[6,20],[25,19],[27,25],[10,25],[4,25],[20,24],[25,9]].map(([x,y],i)=>({id:'tree-'+i,art:'tree',x,y,w:170+(i%3)*13,h:203+(i%3)*15,tree:true}))
  ],
  townRoads: [
    {points:[[14.5,-6],[14.5,9],[14.5,15],[14.5,22],[14.5,46]],width:3.6},
    {points:[[-5,17],[7,17],[11,16.5],[14.5,16],[20,17],[28,16],[36,16],[50,16]],width:3.1},
    {points:[[17,17],[19,18.5],[24,18.5],[29,19],[31,24],[31,29],[31,36]],width:1.6},
    {points:[[10.8,16],[10.8,22],[11,28],[14.5,31],[21,31],[30,29],[40,29]],width:1.5}
  ],
  walkers: [
    {id:'guard-1',route:[[12,21],[12,12],[17,12],[17,21]],pace:.7,tint:0},
    {id:'guard-2',route:[[17,21],[17,12],[12,12],[12,21]],pace:.66,tint:0},
    {id:'customer-1',route:[[16,18],[20,17],[19,14],[16,15]],pace:.53,tint:45},
    {id:'traveler-1',route:[[11,22],[12,18],[10,16],[10,19]],pace:.6,tint:-30},
    {id:'artisan-1',route:[[21,20],[20,18],[23,17],[22,20]],pace:.46,tint:80}
  ]
});
