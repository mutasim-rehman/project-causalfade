# CausalFade Research Observatory

The observatory is a static Next.js application. It reads the frozen JSON files in `public/data/`. Start here for the cohort archive, final CF-TP1 analysis, interactive causal lab and classroom presentation.

## Local development

Use Node.js 22 or newer and npm. From the repository root:

```sh
cd dashboard
npm ci
npm run dev
```

Open [the local development site](http://localhost:3000/). The application uses the committed snapshot on startup.

## Production build and offline demonstration

```sh
npm run build
npm start
```

`npm start` uses Python 3 to serve the static export. On Windows with the Python launcher, run `py -m http.server 4173 --bind 127.0.0.1 --directory out` from `dashboard`. Open [the local demonstration](http://127.0.0.1:4173/) or [Presentation Mode](http://127.0.0.1:4173/presentation/).

Build on a connected machine or copy a previously built `out/` directory to the classroom machine. The export contains the fonts, chart code and frozen datasets needed for the demo. Pinned repository documents and original artifact links require GitHub access.

Presentation controls include left and right arrow navigation, Escape to exit or close the embedded lab, a browser full-screen toggle and speaker notes. The `slide` query parameter bookmarks a position.

## Rebuild the frozen data

Run from the repository root with Git and Python 3.10 or newer. The extractor uses the standard library. The committed dashboard snapshot uses `01728ada407e8e5d59d6d7918dcd71dc0532b706` as its research input revision.

```sh
CAUSALFADE_SOURCE_REF=01728ada407e8e5d59d6d7918dcd71dc0532b706 python dashboard/scripts/build_data.py
python dashboard/scripts/verify/verify_data.py --check-only
```

PowerShell with the Python launcher:

```powershell
$env:CAUSALFADE_SOURCE_REF = '01728ada407e8e5d59d6d7918dcd71dc0532b706'
py dashboard/scripts/build_data.py
py dashboard/scripts/verify/verify_data.py --check-only
```

The working research directories must match the requested revision. The rebuild writes dashboard datasets, the checksum manifest and the verification report. Source checksums use committed Git blob bytes. Extraction and verification timestamps change when the pipeline runs.

## Tests

Run `npm run typecheck` and `npm test` in `dashboard`. For browser checks against the built export, start the local demonstration, run `npx playwright install chromium` once and run `npm run test:browser`. Set `CAUSALFADE_BROWSER_CHANNEL=chrome` to use an installed Chrome, or set `CAUSALFADE_BASE_URL` to test on another local port.

## Static deployment configuration

For an authorized deployment, select `dashboard` as the project root, use the Next.js framework preset, run `npm ci` for installation and `npm run build` for the build. A generic static host can serve `dashboard/out/` with directory index support. Review the export and permissions for the manuscript and response archives before publishing.

- [Data dictionary](DATA_DICTIONARY.md)
- [Snapshot manifest](DATA_MANIFEST.json)
- [Verification report](VERIFICATION_REPORT.md)
- [Implementation status](IMPLEMENTATION_STATUS.md)
