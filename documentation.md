# Repository documentation

## Layout

```text
TETRIS/
├── C/            C and Raylib implementation
├── Python/       Python and Pygame implementation
├── JavaScript/   Canvas browser implementation
├── Java/         Java Swing desktop implementation
└── web/          React developer portfolio website
```

The four game implementations are independent. Their board, tetrominoes, seven-bag randomizer, SRS-style kicks, hold and preview, ghost piece, scoring, and level progression follow the same rules. Each implementation's README contains its language-specific setup and controls.

## Game projects

Read the implementation guides:

- [C game](C/README.md)
- [Python game](Python/README.md)
- [JavaScript game](JavaScript/README.md)
- [Java game](Java/README.md)

## Portfolio website

The React website lives in `web/` and does not share source or dependencies with the games.

```sh
cd web
npm install
npm run dev
```

Create a static production build with:

```sh
npm run build
```

The deployable files are written to `web/dist/`. Upload that directory to a static host such as GitHub Pages, Netlify, Vercel, or any web server that serves static files. To preview the production build locally, run `npm run preview` from `web/`.

The GitHub portfolio link uses this repository's owner, `EmmanuelS-dev`. Set `LINKEDIN_URL` in `web/src/data.js` to the correct profile URL before deploying if you want to publish LinkedIn.
