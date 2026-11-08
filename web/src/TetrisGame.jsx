import { useEffect, useRef, useState } from 'react';
import { BOARD_HEIGHT, BOARD_WIDTH, PIECE_COLORS, pieceCells, TetrisGame as GameModel } from './tetris-engine.js';
import './tetris.css';

function loadBest(){try{return Number(localStorage.getItem('emmanuel-tetris-best'))||0;}catch{return 0;}}
function MiniPiece({kind,label}){
  const set=new Set(kind?pieceCells(kind).map(([x,y])=>`${x},${y}`):[]);
  return <div className="mini-piece" role="img" aria-label={label}>{Array.from({length:16},(_,i)=>{const x=i%4,y=Math.floor(i/4),filled=set.has(`${x},${y}`);return <i key={i} className={filled?'filled':''} style={filled?{'--piece':PIECE_COLORS[kind]}:{}}/>})}</div>;
}

export default function TetrisGame(){
  const gameRef=useRef(null);if(!gameRef.current)gameRef.current=new GameModel({highScore:loadBest()});
  const [,refresh]=useState(0);const [muted,setMuted]=useState(true);const audioRef=useRef(null);const savedRef=useRef(loadBest());
  const game=gameRef.current;
  const beep=(frequency=440)=>{if(muted)return;try{audioRef.current??=new AudioContext();const audio=audioRef.current,osc=audio.createOscillator(),gain=audio.createGain();osc.frequency.value=frequency;gain.gain.setValueAtTime(.035,audio.currentTime);gain.gain.exponentialRampToValueAtTime(.001,audio.currentTime+.09);osc.connect(gain).connect(audio.destination);osc.start();osc.stop(audio.currentTime+.09);}catch{}};
  const update=()=>refresh(value=>value+1);
  const start=()=>{game.start();update();};
  useEffect(()=>{
    let frame,last=performance.now();
    const animate=now=>{const dt=Math.min(.25,(now-last)/1000);last=now;game.update(dt);if(game.highScore>savedRef.current){savedRef.current=game.highScore;try{localStorage.setItem('emmanuel-tetris-best',String(game.highScore));}catch{}}update();frame=requestAnimationFrame(animate);};
    frame=requestAnimationFrame(animate);
    const keydown=e=>{
      const key=e.code,keys=['ArrowLeft','ArrowRight','ArrowDown','ArrowUp','Space','KeyA','KeyD','KeyS','KeyX','KeyZ','KeyC','ShiftLeft','ShiftRight','KeyP','Escape','KeyR','KeyM','Enter'];
      if(!keys.includes(key))return;e.preventDefault();if(e.repeat&&['ArrowUp','KeyX','KeyZ','Space','KeyC','ShiftLeft','ShiftRight'].includes(key))return;
      if(key==='KeyM'){setMuted(value=>!value);return;}
      if(key==='KeyR'){start();return;}
      if(key==='KeyP'||key==='Escape'){game.togglePause();update();return;}
      if(game.state==='ready'){if(key==='Enter')start();return;}
      if(game.state==='paused'){if(key==='Enter')game.togglePause();update();return;}
      if(game.state==='gameover'){if(key==='Enter')start();return;}
      let played=false;
      if(key==='ArrowLeft'||key==='KeyA')game.move(-1,0);
      else if(key==='ArrowRight'||key==='KeyD')game.move(1,0);
      else if(key==='ArrowDown'||key==='KeyS')game.softDrop();
      else if(key==='ArrowUp'||key==='KeyX'){game.rotate(1);beep(540);played=true;}
      else if(key==='KeyZ'){game.rotate(-1);beep(420);played=true;}
      else if(key==='Space'){game.hardDrop();beep(260);played=true;}
      else if(key==='KeyC'||key==='ShiftLeft'||key==='ShiftRight'){game.hold();beep(340);played=true;}
      if(played||key!=='ArrowDown'&&key!=='KeyS')update();
    };
    window.addEventListener('keydown',keydown);
    return()=>{cancelAnimationFrame(frame);window.removeEventListener('keydown',keydown);};
  },[game,muted]);

  const activeCells=new Set(game.active?game.cells().filter(([,y])=>y>=0).map(([x,y])=>`${x},${y}`):[]);
  const ghost=game.active?game.ghost():null,ghostCells=new Set(ghost?game.cells(ghost).filter(([,y])=>y>=0).map(([x,y])=>`${x},${y}`):[]);
  return <section className="tetris-wrap" aria-label="Playable Tetris game">
    <div className="game-toolbar"><div><span className="game-overline"><i/> PLAYABLE IN YOUR BROWSER</span><h2>Take a moment.<br/><em>Clear a line.</em></h2></div><div className="game-actions"><button type="button" className="sound-toggle" onClick={()=>setMuted(value=>!value)}>{muted?'SOUND OFF':'SOUND ON'} <span aria-hidden="true">{muted?'◌':'♪'}</span></button><button type="button" className="new-game" onClick={start}>{game.state==='ready'?'START GAME':'NEW GAME'} <span aria-hidden="true">↻</span></button></div></div>
    <div className="game-frame">
      <aside className="game-side hold-side"><div className="side-label">HOLD <span>{game.holdUsed?'USED':'C / SHIFT'}</span></div><div className="preview-box"><MiniPiece kind={game.held} label={game.held?`Held ${game.held} piece`:'No held piece'}/></div><div className="side-label control-label">CONTROLS</div><ul className="key-list"><li><kbd>←</kbd><kbd>→</kbd><span>Move</span></li><li><kbd>↓</kbd><span>Soft drop</span></li><li><kbd>↑</kbd><kbd>X</kbd><span>Rotate</span></li><li><kbd>Z</kbd><span>Rotate back</span></li><li><kbd>SPACE</kbd><span>Hard drop</span></li><li><kbd>C</kbd><span>Hold</span></li><li><kbd>P</kbd><span>Pause</span></li></ul></aside>
      <div className="board-column"><div className="board-caption"><span>10 × 20 BOARD</span><span>LEVEL {String(game.level).padStart(2,'0')}</span></div><div className="board-shell"><div className="game-board" role="grid" aria-label="Tetris board">
        {Array.from({length:BOARD_HEIGHT*BOARD_WIDTH},(_,i)=>{const x=i%BOARD_WIDTH,y=Math.floor(i/BOARD_WIDTH),key=`${x},${y}`,kind=game.board[y][x]||(game.active&&activeCells.has(key)?game.active.kind:null),isGhost=!kind&&ghostCells.has(key);return <div role="gridcell" aria-label={kind?`${kind} block`:isGhost?'Landing position':'Empty'} key={i} className={`board-cell${kind?' occupied':''}${isGhost?' ghost':''}`} style={kind?{'--piece':PIECE_COLORS[kind]}:{}}/>;})}
      </div>
      {game.state!=='playing'&&<div className="game-overlay"><span className="overlay-kicker">{game.state==='ready'?'YOUR BOARD IS READY':game.state==='paused'?'TAKE A BREATH':'THAT’S THE ROUND'}</span><h3>{game.state==='ready'?'Tetris':game.state==='paused'?'Paused':'Game over'}</h3>{game.state==='ready'&&<p>One more piece?</p>}{game.state==='gameover'&&<p>Score <b>{game.score.toLocaleString()}</b></p>}<button type="button" onClick={game.state==='paused'?()=>{game.togglePause();update();}:start}>{game.state==='ready'?'START':game.state==='paused'?'RESUME':'PLAY AGAIN'} <span>→</span></button><small>{game.state==='ready'?'PRESS ENTER TO START':game.state==='paused'?'PRESS ENTER OR P TO RESUME':'PRESS ENTER TO RESTART'}</small></div>}
      </div><div className="board-hint">GHOST PIECE SHOWS YOUR LANDING POSITION</div></div>
      <aside className="game-side score-side"><div className="side-label">UP NEXT <span>5 PIECES</span></div><div className="next-list">{game.nextQueue.slice(0,4).map((kind,i)=><div className="next-piece" key={`${kind}-${i}`}><MiniPiece kind={kind} label={`Next ${kind} piece`}/><span>{String(i+1).padStart(2,'0')}</span></div>)}</div><div className="stat-grid"><div><span>SCORE</span><b>{game.score.toLocaleString()}</b></div><div><span>BEST</span><b>{game.highScore.toLocaleString()}</b></div><div><span>LINES</span><b>{String(game.lines).padStart(2,'0')}</b></div><div><span>LEVEL</span><b>{String(game.level).padStart(2,'0')}</b></div></div></aside>
      {game.state==='paused'&&<button className="mobile-resume" type="button" onClick={()=>{game.togglePause();update();}}>RESUME GAME</button>}
    </div>
    <div className="game-footnote"><span>ONE MORE PIECE?</span><span>ARROW KEYS / WASD TO MOVE <i/> M TO TOGGLE SOUND</span></div>
  </section>;
}
