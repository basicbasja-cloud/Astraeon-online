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
  townObjects: [
    {id:'guild-hall',art:'guild',x:8,y:15,w:254,h:292,building:true},
    {id:'market-shop',art:'shop',x:22,y:15.4,w:225,h:294,building:true},
    {id:'moon-shrine',art:'shrine',x:7,y:24,w:225,h:250,building:true},
    {id:'residence',art:'shop',x:26,y:23,w:185,h:245,building:true},
    {id:'north-gate',art:'gate',x:14.5,y:4.5,w:270,h:290,building:true},
    {id:'south-gate',art:'gate',x:14.5,y:25.5,w:232,h:247,building:true},
    {id:'astral-fountain',art:'fountain',x:14.5,y:14.8,w:145,h:180},
    {id:'cloth-market',art:'stall',x:19.2,y:13.4,w:142,h:157},
    {id:'food-market',art:'stall',x:24.3,y:16,w:133,h:147},
    {id:'caravan-cart',art:'cart',x:20.8,y:20.5,w:125,h:137},
    {id:'guild-supplies',art:'cart',x:5.7,y:17,w:104,h:114},
    ...[[3,5],[7,6],[23,4],[27,7],[3,17],[6,20],[25,19],[27,25],[10,25],[4,25],[20,24],[25,9]].map(([x,y],i)=>({id:'tree-'+i,art:'tree',x,y,w:116+(i%3)*13,h:138+(i%3)*15,tree:true}))
  ],
  townRoads: [
    {points:[[14.5,-6],[14.5,9],[14.5,15],[14.5,22],[14.5,34]],width:3.2},
    {points:[[-5,17],[7,17],[11,16.5],[14.5,16],[20,17],[28,14],[36,14]],width:2.5},
    {points:[[17,15],[19,12],[23,12],[26,16]],width:1.5},
    {points:[[8,16],[8,21],[9,25]],width:1.4}
  ],
  walkers: [
    {id:'guard-1',route:[[12,21],[12,12],[17,12],[17,21]],pace:.7,tint:0},
    {id:'guard-2',route:[[17,21],[17,12],[12,12],[12,21]],pace:.66,tint:0},
    {id:'customer-1',route:[[16,18],[20,17],[19,14],[16,15]],pace:.53,tint:45},
    {id:'traveler-1',route:[[11,22],[12,18],[10,16],[10,19]],pace:.6,tint:-30},
    {id:'artisan-1',route:[[21,20],[20,18],[23,17],[22,20]],pace:.46,tint:80}
  ]
});
