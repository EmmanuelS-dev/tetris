import { useEffect, useState } from 'react';
import { GITHUB_URL, LINKEDIN_URL, projects, tetrisProject } from './data.js';
import TetrisGame from './TetrisGame.jsx';

const currentPage = () => ['about', 'works'].includes(location.hash.slice(1)) ? location.hash.slice(1) : 'home';
function Arrow({ up = false }) { return <span className="arrow" aria-hidden="true">{up ? '↗' : '→'}</span>; }

function Header({ page }) {
  return <header className="header">
    <a className="brand" href="#home"><b className="brand-game">▦</b><span>TETRIS<span className="slash">/</span>WEB</span></a>
    <nav aria-label="Main navigation"><a className={page === 'about' ? 'selected' : ''} href="#about">About</a><a className={page === 'works' ? 'selected' : ''} href="#works">Other works</a></nav>
    <span className="header-note">A SMALL GAME FOR A CLEAR MIND</span>
  </header>;
}

function ProjectCard({ project }) {
  return <article className="project-card">
    <div className={`project-art ${project.tone}`}><span className="art-id">{project.number} / PROJECT</span><span className="art-mark" aria-hidden="true">{project.mark}</span><span className="art-note">{project.note}</span></div>
    <div className="project-label"><span>{project.category}</span><span>PROJECT / {project.number}</span></div>
    <h3>{project.name}</h3><p>{project.description}</p>
  </article>;
}

function Orbit() {
  return <div className="orbit" aria-hidden="true"><div className="orbit-grid"/><div className="oval oval-a"/><div className="oval oval-b"/><div className="orbit-center"><small>01</small><b>IDEA</b><i>↘</i></div><span className="orbit-caption top">THINK / MAKE</span><span className="orbit-caption bottom">ITERATE — REPEAT</span></div>;
}

function Home() {
  return <main className="home-page">
    <TetrisGame />
    <section className="home-note wrap"><span className="eyebrow">ONE GAME · FOUR IMPLEMENTATIONS</span><p>The same classic rules, rebuilt in C, Python, JavaScript, and Java.<br/><span>Different languages. Different looks. Same next piece.</span></p><a className="under-link" href="#works">See the other projects <Arrow/></a></section>
  </main>;
}

function About() {
  return <main className="wrap inner-page">
    <div className="page-label"><span className="eyebrow">ABOUT / 01</span><span>THE PERSON BEHIND THE PROJECTS</span></div>
    <section className="about-hero"><div><h1>Hi, I’m<br/><em>Emmanuel.</em></h1><p className="lead">A developer drawn to the moment a clear idea becomes something you can use, explore, or play.</p></div><div className="stamp"><span>CURIOUS BY NATURE</span><b>e.</b><span>BUILT WITH INTENTION</span></div></section>
    <section className="story"><span className="eyebrow">A SHORT INTRODUCTION</span><div><h2>I enjoy giving an idea<br/>a useful shape.</h2><p>That has taken me from building a Tetris game across four languages to exploring a full-stack CMS for novels, logic through truth tables, and the foundations of computer architecture. I like moving between the visible interface and the rules underneath it.</p><p>This portfolio is a snapshot of that exploration. I’m always learning, refining, and looking for the next interesting problem to work through.</p></div></section>
    <section className="focus"><span className="eyebrow">AREAS I KEEP EXPLORING</span><div className="focus-list"><div><span>01</span><b>Interactive software</b><small>Games, interfaces, and responsive experiences</small></div><div><span>02</span><b>Publishing tools</b><small>Thoughtful systems for writing and content</small></div><div><span>03</span><b>Logic &amp; systems</b><small>How programs reason and machines execute</small></div></div></section>
    <section className="social"><div><span className="eyebrow">ELSEWHERE</span><h2>Find me<br/><em>around the web.</em></h2></div><div className="social-list"><a href={GITHUB_URL} target="_blank" rel="noreferrer">GitHub <Arrow up/></a><a href={LINKEDIN_URL} target="_blank" rel="noreferrer">LinkedIn <Arrow up/></a></div></section>
  </main>;
}

function Works() {
  return <main className="wrap inner-page">
    <div className="page-label"><span className="eyebrow">OTHER WORKS / 02</span><span>PROJECTS &amp; EXPERIMENTS</span></div>
    <section className="works-intro"><h1>Work with<br/><em>a point of view.</em></h1><p className="lead">A selection of projects across stories, logic, and the inner workings of computers.</p></section>
    <section className="works-grid" aria-label="Other projects">{projects.map(project=><ProjectCard key={project.number} project={project}/>)}</section>
    <section className="works-tetris"><span className="eyebrow">ALSO IN THIS REPOSITORY</span><div><h2>Tetris,<br/><em>four ways.</em></h2><p>{tetrisProject.description}</p><a className="under-link" href={`${GITHUB_URL}/tetris`} target="_blank" rel="noreferrer">Explore the repository <Arrow up/></a></div></section>
  </main>;
}

function Footer() {
  return <footer className="footer"><div className="wrap footer-top"><a className="brand" href="#home"><b>e.</b><span>EMMANUEL<span className="slash">/</span>DEV</span></a><p>MADE WITH CURIOSITY<br/>AND A LOT OF ITERATION.</p><div><a href={GITHUB_URL} target="_blank" rel="noreferrer">GITHUB <Arrow up/></a><a href={LINKEDIN_URL} target="_blank" rel="noreferrer">LINKEDIN <Arrow up/></a></div></div><div className="wrap footer-bottom"><span>© {new Date().getFullYear()} EMMANUEL</span><a href="#home">BACK TO TOP ↑</a><span>BUILT TO KEEP GROWING</span></div></footer>;
}

export default function App() {
  const [page,setPage]=useState(currentPage);
  useEffect(()=>{const update=()=>setPage(currentPage());window.addEventListener('hashchange',update);return()=>window.removeEventListener('hashchange',update);},[]);
  useEffect(()=>{window.scrollTo({top:0,behavior:'smooth'});},[page]);
  return <div className="app"><Header page={page}/>{page==='about'?<About/>:page==='works'?<Works/>:<Home/>}<Footer/></div>;
}
