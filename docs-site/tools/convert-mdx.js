const fs = require('fs-extra');
const path = require('path');
const { unified } = require('unified');
const remarkParse = require('remark-parse');
const remarkStringify = require('remark-stringify');

// Use absolute paths so script can be run from any folder
const BASE_DIR = path.resolve(__dirname, '../docs');
const SRC_FILE = path.join(BASE_DIR, 'aws_stack_architecture.md');
const OUT_DIR = path.join(BASE_DIR, 'converted');
const OUT_FILE = path.join(OUT_DIR, 'aws_stack_architecture.converted.md');

async function convertFile() {
    try {
        await fs.ensureDir(OUT_DIR);
        const input = await fs.readFile(SRC_FILE, 'utf8');
        const processor = unified()
            .use(remarkParse)
            .use(remarkStringify);
        const result = await processor.process(input);
        await fs.writeFile(OUT_FILE, result.value);
        console.log(`✅ Converted: ${SRC_FILE} -> ${OUT_FILE}`);
    } catch (err) {
        console.error(`Error converting ${SRC_FILE}:`, err.message);
        if (err.stack) {
            console.error(err.stack);
        }
    }
}

convertFile();