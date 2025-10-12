Run docs-site unit tests

These tests focus on the Docusaurus /docs-site portion of the repository (auth flows, header components, etc.). They use Jest + ts-jest and run in a jsdom environment.

From the workspace root run:

```bash
# clear jest cache (recommended)
npx jest --clearCache

# run only tests under docs-site
npx jest "**/docs-site/src/**/__tests__/**/*.test.(ts|tsx)" --colors --runInBand
```

Why use --runInBand? It avoids multi-process issues in constrained CI/dev environments and makes output easier to follow locally.

If you see TypeScript errors from ts-jest about esModuleInterop you can set `esModuleInterop: true` in `tsconfig.json` to quiet those warnings.
