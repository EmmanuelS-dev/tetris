# Emmanuel / Dev portfolio

React Tetris website built with Vite. The Home page opens directly into a playable game with hold, next-piece preview, ghost piece, scoring, levels, pause, and local high-score storage. About and Other Works are supporting pages with developer details, social links, and project summaries.

## Run locally

Requires Node.js 20.19+ or 22.12+.

```sh
npm install
npm run dev
```

## Production deployment

```sh
npm run build
npm run preview
```

Upload the generated `dist/` directory to a static web host. Profile links and project summaries are maintained in `src/data.js`. Game rules are in `src/tetris-engine.js`; the React game surface is in `src/TetrisGame.jsx`.
