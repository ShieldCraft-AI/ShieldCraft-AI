import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';


import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

function getFrontmatterTitle(filePath: string): string {
  const content = fs.readFileSync(filePath, 'utf8');
  const match = content.match(/^---\s*([\s\S]*?)---/);
  if (match) {
    try {
      const frontmatter = yaml.load(match[1]);
      if (frontmatter && typeof frontmatter === 'object' && 'title' in frontmatter) {
        return (frontmatter as any).title as string;
      }
    } catch (e) {
      // ignore parse errors
    }
  }
  // fallback to filename if no title
  return path.basename(filePath);
}

function getSortedSidebarItems(dir: string) {
  const files = fs.readdirSync(dir)
    .filter((file) => file.endsWith('.mdx') || file.endsWith('.md'));
  const fileObjs = files.map((file) => {
    const filePath = path.join(dir, file);
    return {
      file,
      title: getFrontmatterTitle(filePath),
    };
  });
  fileObjs.sort((a, b) => a.title.localeCompare(b.title));
  return fileObjs.map(({ file }) => ({ type: 'doc' as const, id: file.replace(/\.(mdx|md)$/, '') }));
}

const sidebars: SidebarsConfig = {
  tutorialSidebar: getSortedSidebarItems(path.resolve(__dirname, 'docs/site')),
};

export default sidebars;
