// convert-mdx.js
// ShieldCraft AI: Test conversion for a single file (aws_stack_architecture.md)

const fs = require('fs-extra');
const path = require('path');
const { unified } = require('unified');
const remarkParse = require('remark-parse');
const remarkStringify = require('remark-stringify');
// Removed remarkAdmonition and remarkMermaid for compatibility and to avoid missing dependencies

// Hardcoded source and output file for focused testing
const SRC_FILE = path.resolve(__dirname, '../docs/aws_stack_architecture.md');
const OUT_FILE = path.resolve(__dirname, '../docs/converted/aws_stack_architecture.converted.md');

async function convertFile() {
    try {
        await fs.ensureDir(path.dirname(OUT_FILE));
        const input = await fs.readFile(SRC_FILE, 'utf8');
        const output = await unified()
            .use(remarkParse)
            .use(remarkStringify)
            .use({ settings: { bullet: '*', fences: true, listItemIndent: 'one' } })
            .process(input);
        await fs.writeFile(OUT_FILE, output.value);
        console.log(`✅ Converted: ${SRC_FILE} -> ${OUT_FILE}`);
    } catch (err) {
        console.error(`❌ Error converting ${SRC_FILE}:`, err.message);
        if (err.stack) {
            console.error(err.stack);
        }
    }
}

convertFile();
