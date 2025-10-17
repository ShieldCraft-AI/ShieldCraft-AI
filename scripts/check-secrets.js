const fs = require('fs');
const path = require('path');

const REPO_ROOT = path.resolve(__dirname, '..');

// heuristics
const awsKeyRegex = /AKIA[0-9A-Z]{16}/g;
const awsSecretRegex = /(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40,}(?![A-Za-z0-9/+=])/g;
const privateKeyRegex = /-----BEGIN (?:RSA |EC |)PRIVATE KEY-----/g;
const githubTokenRegex = /\b(?:ghp|gho|ghu)_[A-Za-z0-9_]{36,255}\b|\bgithub_pat_[A-Za-z0-9_\-]{20,}\b/g;
const slackTokenRegex = /xox[baprs]-[A-Za-z0-9-]{10,}/g;
// generic candidate: long alpha-num strings (but we'll apply stronger vetting before flagging)
const genericApiKeyRegex = /(?<![A-Za-z0-9])[A-Za-z0-9_\-]{32,}(?![A-Za-z0-9])/g;

// whitelist of extensions to scan (only source/config/text files)
const EXT_WHITELIST = new Set(['.ts', '.js', '.py', '.env', '.txt', '.json', '.yaml', '.yml', '.md']);

// small per-path allowlist to ignore known doc/context/test fixtures that commonly contain long hashes
const PATH_ALLOWLIST = [
  'ShieldCraft-AI-Context.txt',
  'mteb_results.json',
  'docs-site',
  'tests/',
  'nox_sessions/',
];

function isPathAllowlisted(rel) {
  if (!rel) return false;
  return PATH_ALLOWLIST.some((p) => rel.includes(p));
}

function looksLikeBase64(s) {
  // Require a reasonable minimum length and only base64 chars.
  // Additionally: prefer patterns that look like JWT (three dot-separated base64 parts)
  if (!s || s.length < 40) return false;
  // If it looks like a JWT (xx.yy.zz), prefer that as an explicit token
  const parts = s.split('.');
  if (parts.length === 3 && parts.every((p) => /^[A-Za-z0-9-_]{10,}$/.test(p))) return true;
  // Otherwise require base64 charset and padding characteristics
  if (!/^[A-Za-z0-9+/=\r\n]+$/.test(s)) return false;
  // Common padding or length constraints: many secrets end with '=' padding
  if (s.includes('=')) return true;
  // Finally, check that the string has sufficiently high entropy via character variety
  const uniq = new Set(s.replace(/\s+/g, ''));
  return uniq.size >= Math.min(32, Math.floor(s.length / 4));
}

function scanFile(filePath) {
  // Avoid reading huge or binary files
  try {
    const stats = fs.statSync(filePath);
    if (!stats.isFile() || stats.size > 2 * 1024 * 1024) return []; // skip files >2MB
  } catch (e) {
    return [];
  }
  let text;
  try {
    text = fs.readFileSync(filePath, 'utf8');
  } catch (e) {
    return [];
  }
  const findings = [];
  const rel = path.relative(REPO_ROOT, filePath).replace(/\\/g, '/');
  // if file path matched allowlist (docs/tests/datasets), skip detailed heuristics
  if (isPathAllowlisted(rel)) return [];
  if (awsKeyRegex.test(text)) findings.push('AWS_ACCESS_KEY_ID-like token');
  if (privateKeyRegex.test(text)) findings.push('PRIVATE KEY block');
  if (githubTokenRegex.test(text)) findings.push('GitHub token-like string');
  if (slackTokenRegex.test(text)) findings.push('Slack token-like string');
  // generic long base64-like strings but with additional checks to reduce false positives
  const longMatches = text.match(genericApiKeyRegex) || [];
  for (const m of longMatches) {
    // require either JWT-like structure, explicit nearby context (key names), or base64 padding/entropy
    const before = text.indexOf(m) - 200;
    const ctx = text.substring(Math.max(0, before), text.indexOf(m) + m.length + 200).toLowerCase();
    const contextHints = ['secret', 'password', 'token', 'api_key', 'client_secret', 'id_token', 'access_token', 'private_key'];
    const hasHint = contextHints.some((h) => ctx.includes(h));
    if (m.length >= 40 && looksLikeBase64(m) && hasHint) {
      findings.push('Long base64-like string near auth-related key (possible secret)');
      break;
    }
    // also allow explicit aws secret-like pattern
    if (awsSecretRegex.test(m) && hasHint) {
      findings.push('AWS-secret-like string near key (possible secret)');
      break;
    }
  }
  // also check for aws secret candidate but only if surrounding context suggests a secret key
  const possibleSecrets = text.match(awsSecretRegex) || [];
  if (possibleSecrets.length > 0) {
    const joined = possibleSecrets.join(' ');
    const ctx = text.substring(0, 1000).toLowerCase();
    if (ctx.includes('secret') || ctx.includes('aws_secret') || ctx.includes('aws_secret_access_key') || ctx.includes('client_secret')) {
      findings.push('Long base64-like strings (possible secrets)');
    }
  }
  return [...new Set(findings)];
}

// Analyze file and return detailed matches for triage
function analyzeFile(filePath) {
  let text;
  try {
    text = fs.readFileSync(filePath, 'utf8');
  } catch (e) {
    return [];
  }
  const rel = path.relative(REPO_ROOT, filePath).replace(/\\/g, '/');
  const results = [];

  function pushMatch(type, match, idx) {
    // prepare context snippet
    const start = Math.max(0, idx - 80);
    const end = Math.min(text.length, idx + match.length + 80);
    const ctx = text.substring(start, end);
    const line = text.substring(0, idx).split('\n').length;
    results.push({ type, match, index: idx, line, context: ctx });
  }

  // private keys
  let m;
  while ((m = privateKeyRegex.exec(text)) !== null) pushMatch('PRIVATE_KEY', m[0], m.index);
  while ((m = awsKeyRegex.exec(text)) !== null) pushMatch('AWS_ACCESS_KEY_ID', m[0], m.index);
  while ((m = githubTokenRegex.exec(text)) !== null) pushMatch('GITHUB_TOKEN', m[0], m.index);
  while ((m = slackTokenRegex.exec(text)) !== null) pushMatch('SLACK_TOKEN', m[0], m.index);
  // jwt-like
  const jwtRegex = /\b[A-Za-z0-9-_]{10,}\\.[A-Za-z0-9-_]{10,}\\.[A-Za-z0-9-_]{6,}\b/g;
  while ((m = jwtRegex.exec(text)) !== null) pushMatch('JWT', m[0], m.index);
  // aws-secret-ish and generic long
  while ((m = awsSecretRegex.exec(text)) !== null) pushMatch('LONG_BASE64', m[0], m.index);
  const generic = text.match(genericApiKeyRegex) || [];
  for (const g of generic) {
    const idx = text.indexOf(g);
    if (idx >= 0) {
      // require looksLikeBase64 and nearby auth keywords
      const before = Math.max(0, idx - 200);
      const ctx = text.substring(before, idx + g.length + 200).toLowerCase();
      const hints = ['secret', 'password', 'token', 'api_key', 'client_secret', 'id_token', 'access_token', 'private_key'];
      const hasHint = hints.some((h) => ctx.includes(h));
      if (looksLikeBase64(g) && hasHint) pushMatch('LONG_BASE64_HINTED', g, idx);
    }
  }

  // If path is allowlisted, tag results as low-confidence and return
  if (isPathAllowlisted(rel) && results.length > 0) {
    return results.map((r) => ({ ...r, allowlisted: true }));
  }

  return results;
}

function maskString(s) {
  if (!s) return s;
  if (s.includes('.')) {
    // mask JWT-style parts
    const parts = s.split('.');
    return parts.map((p) => {
      if (p.length <= 8) return '***';
      return p.slice(0, 4) + '...' + p.slice(-4);
    }).join('.');
  }
  if (s.length <= 16) return s.replace(/./g, '*');
  return s.slice(0, 8) + '...' + s.slice(-8);
}

function scoreTriage(fileRel, item) {
  // base score
  let score = 0;
  const fn = (str) => (str || '').toLowerCase();
  if (item.type === 'PRIVATE_KEY') score += 4;
  if (item.type === 'AWS_ACCESS_KEY_ID') score += 3;
  if (item.type === 'GITHUB_TOKEN' || item.type === 'SLACK_TOKEN') score += 3;
  if (item.type === 'JWT') score += 2;
  if (item.type && item.type.startsWith('LONG')) score += 1;
  // context hints
  const ctx = fn(item.context);
  const hints = ['secret', 'password', 'token', 'api_key', 'client_secret', 'id_token', 'access_token', 'aws_secret'];
  if (hints.some((h) => ctx.includes(h))) score += 2;
  // penalize docs/tests/datasets
  if (isPathAllowlisted(fileRel)) score -= 3;
  const ext = path.extname(fileRel).toLowerCase();
  if (ext === '.md' || ext === '.txt' || fileRel.startsWith('tests/')) score -= 2;
  return Math.max(-2, score);
}

function triageSuggestion(score) {
  if (score >= 4) return { confidence: 'high', action: 'rotate-and-scrub' };
  if (score >= 2) return { confidence: 'medium', action: 'verify-and-redact' };
  return { confidence: 'low', action: 'likely-false-positive-add-to-allowlist' };
}

function walk(dir) {
  const results = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const ent of entries) {
    const full = path.join(dir, ent.name);
    if (ent.isDirectory()) {
      // skip common generated/vendor/cache/build directories to avoid noise
      const ignoreDirs = new Set([
        '.git',
        'node_modules',
        '.next',
        '.venv',
        '__pycache__',
        '.mypy_cache',
        '.nox',
        'cdk.out',
        'dist',
        'build',
        '.docusaurus',
        '.cache',
        '.pytest_cache',
        '.ruff_cache',
        '.tox',
      ]);
      if (ignoreDirs.has(ent.name)) continue;
      // also skip any path that contains /.nox/ or /node_modules/ as a segment
      const norm = full.replace(/\\/g, '/');
      if (norm.includes('/.nox/') || norm.includes('/node_modules/') || norm.includes('/cdk.out/')) continue;
      results.push(...walk(full));
    } else {
      // skip large/binary or common vendored files that contain long hashes
      const base = path.basename(full).toLowerCase();
      if (base === 'package-lock.json' || base.endsWith('.lock')) continue;
      // skip files under cdk.out or docs-site build artifacts regardless of extension
      if (full.indexOf(path.join('cdk.out', '')) !== -1) continue;
      if (full.indexOf(path.join('docs-site', 'build')) !== -1) continue;
      results.push(full);
    }
  }
  return results;
}

function main() {
  const files = walk(REPO_ROOT).filter((f) => {
    // only scan whitelisted extensions to avoid vendor noise
    const ext = path.extname(f).toLowerCase();
    return EXT_WHITELIST.has(ext);
  });
  const report = [];
  for (const f of files) {
    try {
      const findings = scanFile(f);
      const rel = path.relative(REPO_ROOT, f).replace(/\\/g, '/');
      if (findings.length) {
        // run detailed analysis to produce triage items
        const details = analyzeFile(f);
        const triaged = details.map((d) => {
          const score = scoreTriage(rel, d);
          const suggestion = triageSuggestion(score);
          return {
            type: d.type,
            line: d.line,
            masked: maskString(d.match),
            confidence_score: score,
            suggestion,
          };
        });
        report.push({ file: rel, findings, triage: triaged });
      }
    } catch (e) {
      // ignore binary files etc
    }
  }

  if (report.length === 0) {
    console.log('No obvious secrets found.');
    // write empty JSON for tooling
    try { fs.writeFileSync(path.join(REPO_ROOT, 'scripts', 'scan-secrets.json'), JSON.stringify({ findings: [] }, null, 2)); } catch (e) {}
    process.exit(0);
  }

  console.log('Potential secrets found:');
  for (const r of report) {
    console.log('-', r.file, ':', r.findings.join(', '));
    if (r.triage && r.triage.length) {
      for (const t of r.triage) {
        console.log('   >', t.type, 'line', t.line, 'masked', t.masked, 'confidence', t.confidence_score, '->', t.suggestion.action);
      }
    }
  }
  try {
    const out = { findings: report };
    fs.writeFileSync(path.join(REPO_ROOT, 'scripts', 'scan-secrets.json'), JSON.stringify(out, null, 2));
    console.log('Wrote scripts/scan-secrets.json');
  } catch (e) {
    /* ignore */
  }
  process.exit(2);
}

if (require.main === module) main();
