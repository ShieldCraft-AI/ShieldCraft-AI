- Typography: uses clamp-based responsive scale. See src/styles/typography.css and TypeRamp.md for usage.
- Accessibility: reduced-motion respected; high-contrast support via color-accessibility.css.
<!-- create src/components/README_COMPONENTS.md -->
# Component Notes - R30
- LandingHero: hero with right-side facts card. z-index must be > MotionLayer.
- PlatformArchitecture: left column is scrollable layers (ScrollLeftColumn).
- ButtonPremium: single central CTA style for enterprise actions.
- MotionLayer: non-interactive decorative SVG animated softly.
- AccessibilityHints: small footer-level hints for keyboard users.

# Component Notes - R36
- R36: Full Recomposition applied. See README_R36 for details.
- R36: decomposed and recomposed layout for production splines. Validate locally using `yarn start` and visually inspect arch section for heading overlap.
