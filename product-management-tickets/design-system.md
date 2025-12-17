## Learning Jungle Mini System

Lightweight design guardrails inspired by `product-management-tickets/image.png`, ready for reuse across child and parent flows. Keep tone friendly but focused, mirroring the hand-drawn grass, wiggles, and chunky lettering from the inspiration art.

### Palette

| Token | Hex | Usage |
| --- | --- | --- |
| `--color-canopy-emerald` | `#1DA97A` | Primary actions, headlines, progress |
| `--color-lilac-glow` | `#C89BFF` | Secondary surfaces, helper cards |
| `--color-deep-violet` | `#5E21B6` | Text on light backgrounds, focus rings |
| `--color-sky-explorer` | `#2C7BEA` | Links, info banners |
| `--color-banana-beam` | `#F7C948` | Rewards, treasure states |
| `--color-jungle-mist` | `#F2F5F7` | Page background |
| `--color-tree-trunk` | `#8C5A2B` | Neutral dividers, subtle labels |

- Use at most two saturated hues per screen.  
- Reserve Banana Beam for the treasure chest moment to keep the emotional peak unique.

### Typography

- **Display**: `Baloo 2`, weights 600/700, sizes 36 / 28 / 22 px with 120% line-height.  
- **Body / UI**: `Nunito`, size 18 px for copy, 16 px for helper text.  
- Avoid italics. Emphasize via color blocks (Emerald, Violet) or pill chips.

### Layout & Spacing

- Base grid: 8 px. Section spacing: 32 px vertical.  
- Cards: 24 px inner padding, 8 px radius.  
- Screen shell: full-height column, background gradient `linear-gradient(0deg, #F2F5F7 0%, #E3F8ED 60%, #F2F5F7 100%)` referencing the sketch’s grass halo.  
- Keep one primary action per screen, button width ≥ 280 px on tablet, full width on small screens.

### Key Components

- **CTA Button**: Emerald background, white text, 8 px radius, shadow `0 4px 12px rgba(29, 169, 122, 0.25)`. Disabled tone `#9FD9C2`.  
- **Secondary Button / Link**: text-only in Sky Explorer with Violet focus outline.  
- **Card**: white surface, 2 px Emerald top edge, faint wiggle SVG watermark (30% opacity) derived from the inspiration doodles.  
- **Answer Option**: block label containing radio + letter bubble. Selected state: Lilac Glow fill at 20%, Deep Violet text, 2 px Violet border.  
- **Status Chip**: pill, 12 px vertical padding, text 14 px. Banana Beam for “Unlocked”, Sky Explorer for info states.  
- **Treasure Chest Tile**: square card with chest icon; unlocked state adds Banana Beam halo and 200 ms scale animation (respect `prefers-reduced-motion`).

### Patterns

1. **Start Screen**: hero header (`Baloo`), three-step list, single CTA. Use wiggle pattern across top edge. Include help text (“Need your grown-up?”) in Nunito 16 px.  
2. **Question Screen**: progress eyebrow, prompt, stacked answer cards, inline alert if no selection (Sky Explorer background, Deep Violet text).  
3. **Result Screen**: rank badge (circle using Lilac outline + Emerald fill for Bronze/Silver/Gold variants), percentage subtext, treasure card, single CTA back home.  
4. **Parent Screen**: reuse tokens but keep surfaces in Jungle Mist and typography weights lighter to signal utilitarian context.

### Accessibility

- Ensure minimum contrast 4.5:1 (Emerald on white, Violet on Lilac).  
- Focus ring: 3 px Deep Violet outline with Sky Explorer glow for keyboard states.  
- Provide motion-safe mode by disabling treasure bounce when `prefers-reduced-motion: reduce`.  
- Copy stays under 80 characters per line; use icons sparingly and always with text labels.

### CSS Token Snippet

```css
:root {
  --color-canopy-emerald: #1DA97A;
  --color-lilac-glow: #C89BFF;
  --color-deep-violet: #5E21B6;
  --color-sky-explorer: #2C7BEA;
  --color-banana-beam: #F7C948;
  --color-jungle-mist: #F2F5F7;
  --color-tree-trunk: #8C5A2B;
  --radius-card: 8px;
  --shadow-cta: 0 4px 12px rgba(29, 169, 122, 0.25);
  --font-display: 'Baloo 2', system-ui, sans-serif;
  --font-body: 'Nunito', system-ui, sans-serif;
}
```

### Usage Notes

- Keep illustration light; let color + wiggle pattern nod to the original child artwork without literal copies.  
- Treasure chest unlock is the single emotional spike—save Banana Beam halos and micro-animations for that state only.  
- Maintain copy style: short sentences, friendly reassurance, no metrics beyond what is required by the product brief.  
- Reassure children with helper text (“Takes about 10 minutes”) and remind them to involve their grown-up for tricky moments.
