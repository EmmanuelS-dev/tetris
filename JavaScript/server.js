import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, resolve, relative, isAbsolute, normalize, dirname, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
const root = dirname(fileURLToPath(import.meta.url));
const types={'.html':'text/html','.css':'text/css','.js':'text/javascript'};
createServer(async(req,res)=>{
  try {
    const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    const requested=pathname.replace(/^\/+/, '') || 'index.html';
    const file=resolve(root,normalize(requested));
    const fromRoot=relative(root,file);
    if(fromRoot==='..'||fromRoot.startsWith(`..${sep}`)||isAbsolute(fromRoot)){
      res.writeHead(404);res.end('Not found');return;
    }
    const body=await readFile(file);
    res.writeHead(200,{'content-type':types[extname(file)]||'application/octet-stream','cache-control':'no-store'});
    res.end(body);
  } catch {
    res.writeHead(404);res.end('Not found');
  }
}).listen(Number(process.argv[2]||process.env.PORT||8000),()=>console.log(`Tetris is available at http://localhost:${process.argv[2]||process.env.PORT||8000}`));
