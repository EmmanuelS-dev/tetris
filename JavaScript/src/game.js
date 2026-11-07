export const WIDTH = 10, HEIGHT = 20, QUEUE_SIZE = 5;
export const TYPES = ['I', 'O', 'T', 'S', 'Z', 'J', 'L'];
export const SHAPES = {
  I: ['....','IIII','....','....'], O: ['.OO.','.OO.','....','....'],
  T: ['.T..','TTT.','....','....'], S: ['.SS.','SS..','....','....'],
  Z: ['ZZ..','.ZZ.','....','....'], J: ['J...','JJJ.','....','....'], L: ['..L.','LLL.','....','....']
};
export const COLORS = { I:'#71aeb7', O:'#c9a75f', T:'#927bad', S:'#73a887', Z:'#c97978', J:'#708db7', L:'#ce9361' };
const JLSTZ = [
 [[0,0],[-1,0],[-1,-1],[0,2],[-1,2]], [[0,0],[1,0],[1,1],[0,-2],[1,-2]],
 [[0,0],[1,0],[1,1],[0,-2],[1,-2]], [[0,0],[-1,0],[-1,-1],[0,2],[-1,2]],
 [[0,0],[1,0],[1,-1],[0,2],[1,2]], [[0,0],[-1,0],[-1,1],[0,-2],[-1,-2]],
 [[0,0],[-1,0],[-1,1],[0,-2],[-1,-2]], [[0,0],[1,0],[1,-1],[0,2],[1,2]]
];
const IKICKS = [
 [[0,0],[-2,0],[1,0],[-2,-1],[1,2]], [[0,0],[-1,0],[2,0],[-1,2],[2,-1]],
 [[0,0],[-1,0],[2,0],[-1,2],[2,-1]], [[0,0],[2,0],[-1,0],[2,1],[-1,-2]],
 [[0,0],[2,0],[-1,0],[2,1],[-1,-2]], [[0,0],[1,0],[-2,0],[1,-2],[-2,1]],
 [[0,0],[1,0],[-2,0],[1,-2],[-2,1]], [[0,0],[-2,0],[1,0],[-2,-1],[1,2]]
];

export function cells(kind, rotation=0) {
  const shape=SHAPES[kind]; if (!shape) throw new Error(`Unknown piece ${kind}`);
  let out=[];
  shape.forEach((row,y)=>[...row].forEach((ch,x)=>{if(ch!=='.')out.push([x,y]);}));
  for(let i=0;i<((rotation%4)+4)%4;i++) out=out.map(([x,y])=>[y,3-x]);
  return out;
}
export class SevenBag {
  constructor(random=Math.random){this.random=random;this.bag=[];}
  next(){if(!this.bag.length){this.bag=[...TYPES];for(let i=6;i>0;i--){const j=Math.floor(this.random()*(i+1));[this.bag[i],this.bag[j]]=[this.bag[j],this.bag[i]];}}return this.bag.pop();}
}
export class Game {
  constructor({random=Math.random,highScore=0}={}){this.random=random;this.highScore=highScore;this.start();this.state='menu';}
  start(){const best=this.highScore;this.grid=Array.from({length:HEIGHT},()=>Array(WIDTH).fill(null));this.bag=new SevenBag(this.random);this.queue=Array.from({length:QUEUE_SIZE},()=>this.bag.next());this.held=null;this.holdUsed=false;this.score=0;this.lines=0;this.level=1;this.gravityTimer=0;this.state='playing';this.active=this.takeNext();this.highScore=best;}
  takeNext(){const kind=this.queue.shift();this.queue.push(this.bag.next());this.holdUsed=false;return {kind,x:3,y:-1,rotation:0};}
  get gravityInterval(){return Math.max(.05,.8-(this.level-1)*.065);}
  pieceCells(p=this.active){return cells(p.kind,p.rotation).map(([x,y])=>[p.x+x,p.y+y]);}
  canPlace(p){return this.pieceCells(p).every(([x,y])=>x>=0&&x<WIDTH&&y<HEIGHT&&(y<0||this.grid[y][x]===null));}
  move(dx,dy){if(this.state!=='playing')return false;const p={...this.active,x:this.active.x+dx,y:this.active.y+dy};if(!this.canPlace(p))return false;this.active=p;return true;}
  rotate(dir=1){if(this.state!=='playing'||!dir)return false;if(this.active.kind==='O')return true;const from=this.active.rotation,to=(from+(dir>0?1:3))%4,kicks=(this.active.kind==='I'?IKICKS:JLSTZ)[from*2+(dir>0?0:1)];for(const [dx,dy] of kicks){const p={...this.active,x:this.active.x+dx,y:this.active.y+dy,rotation:to};if(this.canPlace(p)){this.active=p;return true;}}return false;}
  ghost(){const p={...this.active};while(this.canPlace({...p,y:p.y+1}))p.y++;return p;}
  addScore(n){this.score+=n;this.highScore=Math.max(this.score,this.highScore);}
  softDrop(){if(!this.move(0,1))return false;this.addScore(1);return true;}
  hardDrop(){if(this.state!=='playing')return 0;let d=0;while(this.move(0,1))d++;this.addScore(d*2);this.lock();return d;}
  hold(){if(this.state!=='playing'||this.holdUsed)return false;const old=this.active.kind;if(this.held===null){this.held=old;this.active=this.takeNext();}else{this.active={kind:this.held,x:3,y:-1,rotation:0};this.held=old;if(!this.canPlace(this.active)){this.state='gameover';return false;}}this.holdUsed=true;this.gravityTimer=0;return true;}
  lock(){if(this.state!=='playing')return 0;if(!this.canPlace(this.active)){this.state='gameover';return 0;}let topout=false;for(const [x,y] of this.pieceCells()){if(y<0)topout=true;else this.grid[y][x]=this.active.kind;}if(topout){this.state='gameover';return 0;}const before=this.grid.length;this.grid=this.grid.filter(row=>row.some(cell=>cell===null));const cleared=HEIGHT-this.grid.length;while(this.grid.length<HEIGHT)this.grid.unshift(Array(WIDTH).fill(null));if(cleared){this.addScore([0,100,300,500,800][Math.min(cleared,4)]*this.level);this.lines+=cleared;this.level=1+Math.floor(this.lines/10);}this.active=this.takeNext();this.gravityTimer=0;if(!this.canPlace(this.active))this.state='gameover';return cleared;}
  update(dt){if(this.state!=='playing'||dt<=0)return;this.gravityTimer+=Math.min(dt,.25);while(this.gravityTimer>=this.gravityInterval&&this.state==='playing'){this.gravityTimer-=this.gravityInterval;if(!this.move(0,1)){this.lock();break;}}}
  togglePause(){if(this.state==='playing')this.state='paused';else if(this.state==='paused')this.state='playing';}
}
