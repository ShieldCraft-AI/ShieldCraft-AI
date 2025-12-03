R61 - Full Non-Destructive Architecture Rebuild

Summary:
- Created backups of all critical files as *.bak.R61 for rollback.
- Isolated layout rules in PlatformArchitecture.layout.css and debug helpers in PlatformArchitecture.debug.css.
- Updated PlatformArchitecture.module.css to reference layout helpers and append visual overrides and responsive rules.
- Replaced outer wrapper in PlatformArchitecture.tsx with new semantic structure, preserving all logic and event handlers.
- Ensured AwsServiceSelector block is protected and visually stable in index.tsx and index.module.css.
- Added utility layout-helpers.css for global helpers.
- Appended responsive and fallback CSS for visual stability.
- Added explicit QA and smoke-test comments for manual validation.

Rollback:
- Restore any file from its corresponding *.bak.R61 backup.
- For partial failures, revert appended blocks and re-evaluate.
