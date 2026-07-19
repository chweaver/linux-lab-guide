# Linux Lab Guide

An exhaustive, hands-on Linux homelab guide built with [Astro](https://astro.build) + [Starlight](https://starlight.astro.build). Seven chained labs that build one coherent multi-server network: SSH hardening, an AD-joined Samba file server, a BIND9 resolver, automated rsync backups, centralized rsyslog logging, Prometheus + Grafana monitoring on Docker, and automated patching with a rehearsed rollback. Per-phase status is published with the site and drives a live network-topology view here and on the [portfolio](https://github.com/chweaver/portfolio).

Live at `https://chweaver.github.io/linux-lab-guide/`.

## The seven labs

1. **SSH Hardening + Key Auth** (Ubuntu, Rocky appendix). The ed25519 keys here are reused by Lab 4.
2. **Samba File Server, domain-joined** (Ubuntu joins `corp.lab`). The bridge from Linux into Active Directory.
3. **Local DNS with BIND9** (Rocky). Caching/forwarding resolver that conditionally forwards `corp.lab` to the AD DNS.
4. **Backup Automation with rsync + cron** (Rocky as backup server). Incremental, restore-tested backups over the hardened SSH from Lab 1.
5. **Centralized Logging with rsyslog** (new `ops01` collector). TCP forwarding with disk-backed queues from the fleet, addressed by the Lab 3 DNS names, read like a SOC would.
6. **Monitoring with node_exporter + Prometheus** (Docker Compose on `ops01`). Grafana dashboards, source-scoped firewall rules, and a failure-detection test that gets proven, not assumed.
7. **Automated Patching + Snapshot Rollback** (all hosts). `unattended-upgrades` and `dnf-automatic` for nightly security fixes, a snapshot-first window for the rest, audited through the Lab 5 logs.

The order is a deliberate dependency chain. See the [Overview](src/content/docs/index.mdx) for how the labs link together.

## Local development

```bash
npm install
npm run dev      # http://localhost:4321/linux-lab-guide/
```

Other scripts:

| Command | What it does |
| --- | --- |
| `npm run build` | Runs `scripts/gen_status.py`, then `astro build` into `dist/`. |
| `npm run status` | Regenerates `public/lab-status.json` only (needs Python 3). |
| `npm run preview` | Serves the built `dist/` locally. |
| `npm run check` | `astro check` type-check. |

> The dev server serves under the `/linux-lab-guide/` base path (matching GitHub Pages). The bare `http://localhost:4321/` will 404; use the `/linux-lab-guide/` URL.

## How progress tracking works

This mirrors the [ad-lab-guide](https://github.com/chweaver/ad-lab-guide) mechanism exactly. There is **no** client-side database, login, or localStorage: just a status line in Markdown that flows all the way to the portfolio.

1. **Every phase carries a `**Status:**` line.** In each lab MDX, under a `## Phase X: ...` heading, a literal line such as:

   ```md
   **Status:** Not started.
   ```

   Recognised values (case-insensitive, text before the first `.` is used): `not started` -> planned, `in progress` -> next, `done` -> done, `next` -> next, `stretch` -> stretch. Same vocabulary and `normalize_status()` logic as the AD lab guide.

2. **`scripts/gen_status.py` parses those lines** and writes `public/lab-status.json` (labs, phases, and a summary). It runs automatically as part of `npm run build`. Each lab's `labId` and `labOrder` come from its MDX frontmatter.

3. **`lab-status.json` is served at** `https://chweaver.github.io/linux-lab-guide/lab-status.json` (Astro copies `public/` to the site root). The guide's status board and topology read it; the portfolio fetches the same URL live on load.

### To mark a phase done

Flip its `**Status:**` line (for example `Not started.` -> `Done.`) and push. The deploy regenerates `lab-status.json`, and the next time anyone opens the portfolio it reflects the change. Because the portfolio fetches at runtime, **there is no separate sync step and no rebuild trigger** between the two repos.

`public/lab-status.json` is committed so local dev and the portfolio's view work before a fresh build; it is regenerated on every deploy, so do not hand-edit it.

## Editing content

- **Lab pages:** `src/content/docs/labs/NN-*.mdx`. Keep the `## Phase X:` headings and one `**Status:**` line per phase (the parser keys off both). Use Expressive Code frames: a `title="/path"` for config files, plain `bash`/`text` for terminal blocks.
- **Landing / topology pages:** `src/content/docs/index.mdx`, `src/content/docs/topology.mdx`.
- **Topology model and IPs:** `src/data/topology.ts` is the single source for nodes, subnets, edges, and every IP. Values marked `VERIFY` are placeholders (the IoT segment, and the AD addresses that come from the AD lab). `labs: ['ssh', 'samba']` on a node means it lights up when those labs are complete.
- **Theme:** `src/styles/theme.css` overrides Starlight's CSS variables to the dark cyan palette shared with the portfolio.

## Deploy

`.github/workflows/deploy.yml` builds and deploys to GitHub Pages on push to `main`:

1. In the repo's **Settings -> Pages**, set **Source: GitHub Actions** (one-time).
2. Push to `main`. The workflow installs Node and Python, runs `npm run build` (which regenerates `lab-status.json` and builds Astro), and deploys `dist/`.

`astro.config.mjs` sets `site: 'https://chweaver.github.io'` and `base: '/linux-lab-guide'`, which is what makes every internal link and the `lab-status.json` fetch resolve under the Pages path.

## Portfolio integration

The [portfolio](https://github.com/chweaver/portfolio) (same origin, `chweaver.github.io`) reads `lab-status.json` from this site at runtime via its shared `useLabStatus` hook:

- A **Linux homelab, live status** section (overall bar + four per-lab cards + per-phase lists).
- The **network topology** lights up each Linux server when its lab(s) are complete, read from the same JSON.

No tokens, no `repository_dispatch`, no cross-repo rebuild: the portfolio just fetches the live JSON, so finishing a lab and pushing this guide updates the portfolio on the next visit.

## Stack

Astro 5 + Starlight, TypeScript, Expressive Code (terminal/file frames with copy buttons), a small Python status script, and a bespoke inline-SVG topology (no graph library). Deployed to GitHub Pages via GitHub Actions.
