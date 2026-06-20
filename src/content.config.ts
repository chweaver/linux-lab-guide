import { defineCollection, z } from 'astro:content';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

// Starlight's docs schema, extended with two optional fields the lab pages use.
// `labId` is the stable key the topology and lab-status.json map against
// (ssh, samba, bind9, rsync). `labOrder` controls ordering in lab-status.json.
// scripts/gen_status.py reads both from the MDX frontmatter.
export const collections = {
  docs: defineCollection({
    loader: docsLoader(),
    schema: docsSchema({
      extend: z.object({
        labId: z.string().optional(),
        labOrder: z.number().optional(),
      }),
    }),
  }),
};
