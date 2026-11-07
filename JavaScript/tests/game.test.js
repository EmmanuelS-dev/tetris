import test from 'node:test';
import assert from 'node:assert/strict';
import {Game,TYPES,HEIGHT,cells,SevenBag} from '../src/game.js';

test('all seven pieces have four cells and four rotation states',()=>{
  for(const kind of TYPES){assert.equal(cells(kind).length,4);for(let r=0;r<4;r++)assert.equal(cells(kind,r).length,4);}
});
test('seven-bag has each type exactly once',()=>{
  const bag=new SevenBag(()=>0.31);assert.deepEqual(Array.from({length:7},()=>bag.next()).sort(),[...TYPES].sort());
});
test('movement, collisions, ghost and drops',()=>{
  const g=new Game();g.start();g.active={kind:'O',x:-1,y:0,rotation:0};assert.equal(g.move(-1,0),false);assert.equal(g.move(1,0),true);const ghost=g.ghost();assert.equal(g.canPlace(ghost),true);assert.equal(g.hardDrop(),18);assert.equal(g.score,36);
});
test('line scoring and level progression',()=>{
  const g=new Game();g.start();g.active={kind:'O',x:3,y:18,rotation:0};g.grid[19]=Array(10).fill('J');g.grid[19][4]=null;g.grid[19][5]=null;assert.equal(g.lock(),1);assert.equal(g.score,100);g.lines=9;g.level=1;g.grid=Array.from({length:20},()=>Array(10).fill(null));g.grid[19]=Array(10).fill('T');g.grid[19][4]=null;g.grid[19][5]=null;g.active={kind:'O',x:3,y:18,rotation:0};g.lock();assert.equal(g.level,2);
});
test('single through four-line scoring matches the shared table',()=>{
  for(let count=1;count<=4;count++){const g=new Game();g.start();for(let y=HEIGHT-count;y<HEIGHT;y++){g.grid[y]=Array(10).fill('J');g.grid[y][4]=null;}g.active={kind:'I',x:3,y:16,rotation:1};assert.equal(g.lock(),count);assert.equal(g.score,[0,100,300,500,800][count]);}
});
test('I-piece SRS kick rescues a turn against the left wall',()=>{const g=new Game();g.start();g.active={kind:'I',x:-1,y:5,rotation:1};assert.equal(g.canPlace(g.active),true);assert.equal(g.rotate(-1),true);assert.equal(g.canPlace(g.active),true);});
test('hold is limited to once per active piece',()=>{const g=new Game();g.start();assert.equal(g.hold(),true);assert.equal(g.hold(),false);g.hardDrop();assert.equal(g.holdUsed,false);});
test('gravity advances using elapsed seconds',()=>{const g=new Game();g.start();const y=g.active.y;g.update(.25);g.update(.25);g.update(.25);assert.equal(g.active.y,y);g.update(.06);assert.equal(g.active.y,y+1);});
