
const fs = require('fs-extra');
const path = require('path');
const { unified } = require('unified');
const remarkParse = require('remark-parse');
const remarkStringify = require('remark-stringify');
const remarkGfm = require('remark-gfm');
const remarkRehype = require('remark-rehype');
const rehypeRaw = require('rehype-raw');

// Use absolute paths so script can be run from any folder

const BASE_DIR = path.resolve(__dirname, '../docs');

async function convertAllFiles() {
    try {
        // Recursively find all .md files (excluding .converted.md)
        const files = await fs.readdir(BASE_DIR, { withFileTypes: true });
        const mdFiles = [];
        async function walk(dir) {
            const entries = await fs.readdir(dir, { withFileTypes: true });
            for (const entry of entries) {
                const fullPath = path.join(dir, entry.name);
                if (entry.isDirectory()) {
                    await walk(fullPath);
                } else if (entry.isFile() && entry.name.endsWith('.md') && !entry.name.endsWith('.converted.md')) {
                    mdFiles.push(fullPath);
                }
            }
        }
        await walk(BASE_DIR);

        for (const srcFile of mdFiles) {
            const srcDir = path.dirname(srcFile);
            const outDir = path.join(srcDir, 'converted');
            await fs.ensureDir(outDir);
            const outFile = path.join(outDir, path.basename(srcFile).replace('.md', '.converted.md'));
            try {
                const input = await fs.readFile(srcFile, 'utf8');
                const processor = unified()
                    .use(remarkParse)
                    .use(remarkGfm)
                    .use(remarkRehype, { allowDangerousHtml: true })
                    .use(rehypeRaw)
                    .use(remarkStringify);
                const result = await processor.process(input);
                await fs.writeFile(outFile, result.value);
                console.log(`✅ Converted: ${srcFile} -> ${outFile}`);
            } catch (err) {
                console.error(`Error converting ${srcFile}:`, err.message);
                if (err.stack) {
                    console.error(err.stack);
                }
            }
        }
        console.log(`Batch conversion complete. Converted ${mdFiles.length} files.`);
    } catch (err) {
        console.error('Batch conversion failed:', err.message);
        if (err.stack) {
            console.error(err.stack);
        }
    }
}

convertAllFiles();