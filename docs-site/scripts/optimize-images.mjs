#!/usr/bin/env node

import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';
import ICO from 'icojs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const staticDir = path.resolve(__dirname, '..', 'static');

const assets = [
  {
    input: path.join(staticDir, 'img', 'logo.png'),
    variants: [
      { suffix: '-sm', width: 140 },
      { suffix: '-lg', width: 280 },
    ],
  },
  {
    input: path.join(staticDir, 'img', 'aws-certified-solutions-architect-associate.png'),
    variants: [
      { suffix: '-sm', width: 200 },
      { suffix: '-lg', width: 360 },
    ],
  },
  {
    input: path.join(staticDir, 'img', 'aws-certified-ai-practitioner.png'),
    variants: [
      { suffix: '-sm', width: 200 },
      { suffix: '-lg', width: 360 },
    ],
  },
];

const outputs = [];

for (const asset of assets) {
  let buffer;
  try {
    buffer = await fs.readFile(asset.input);
  } catch {
    console.warn(`⚠️  Skipping missing source ${asset.input}`);
    continue;
  }

  let sourceBuffer = buffer;
  if (ICO.isICO(buffer)) {
    try {
      const images = await ICO.parseICO(buffer, 'image/png');
      if (images.length) {
        const best = images.reduce((prev, current) => (current.width > prev.width ? current : prev));
        sourceBuffer = Buffer.from(best.buffer);
      }
    } catch (err) {
      console.warn(`⚠️  Failed to parse ICO source ${asset.input}:`, err);
    }
  }

  const srcName = path.basename(asset.input, path.extname(asset.input));
  const dir = path.dirname(asset.input);

  for (const variant of asset.variants) {
    const width = variant.width;
    const webpTarget = path.join(dir, `${srcName}${variant.suffix}.webp`);
    const avifTarget = path.join(dir, `${srcName}${variant.suffix}.avif`);

    await sharp(sourceBuffer)
      .resize({ width, fit: 'inside', withoutEnlargement: true })
      .toFormat('webp', { quality: 82 })
      .toFile(webpTarget);
    outputs.push(webpTarget);

    await sharp(sourceBuffer)
      .resize({ width, fit: 'inside', withoutEnlargement: true })
      .toFormat('avif', { quality: 55 })
      .toFile(avifTarget);
    outputs.push(avifTarget);
  }
}

if (outputs.length) {
  console.log(`✅ Generated ${outputs.length} optimized variants:\n - ${outputs.map((f) => path.relative(process.cwd(), f)).join('\n - ')}`);
} else {
  console.log('ℹ️  No outputs were generated.');
}
