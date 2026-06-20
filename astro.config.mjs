// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// Served from https://chweaver.github.io/linux-lab-guide/ on GitHub Pages.
// `site` + `base` make every internal link and the lab-status.json fetch resolve
// correctly under the /linux-lab-guide/ path prefix.
export default defineConfig({
  site: 'https://chweaver.github.io',
  base: '/linux-lab-guide',
  trailingSlash: 'always',
  // Snappy doc-to-doc navigation without pulling in a client router that would
  // fight Starlight's own layout. Prefetch on hover/viewport is enough polish here.
  prefetch: { prefetchAll: true, defaultStrategy: 'viewport' },
  integrations: [
    starlight({
      title: 'Linux Lab Guide',
      description:
        'An exhaustive, hands-on Linux homelab build: SSH hardening, AD-joined Samba, BIND9 DNS, and automated rsync backups. One coherent multi-server network, not four disconnected tutorials.',
      tagline: 'SSH, Samba, BIND9, and backups, built as one coherent network.',
      customCss: ['./src/styles/theme.css'],
      social: {
        github: 'https://github.com/chweaver/linux-lab-guide',
      },
      editLink: {
        baseUrl: 'https://github.com/chweaver/linux-lab-guide/edit/main/',
      },
      lastUpdated: true,
      sidebar: [
        { label: 'Overview', link: '/' },
        {
          label: 'The four labs',
          items: [
            { label: '1. SSH Hardening + Key Auth', link: '/labs/01-ssh-hardening/' },
            { label: '2. Samba, Domain-Joined', link: '/labs/02-samba-domain/' },
            { label: '3. Local DNS with BIND9', link: '/labs/03-bind9-dns/' },
            { label: '4. Backups: rsync + cron', link: '/labs/04-rsync-backups/' },
          ],
        },
        { label: 'Live network topology', link: '/topology/' },
      ],
    }),
  ],
});
