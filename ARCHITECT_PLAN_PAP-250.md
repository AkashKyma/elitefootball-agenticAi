# ARCHITECT PLAN — PAP-250

## Ticket
PAP-250 — Build a fashion product showcase using HTML and CSS

## Role
Architect — planning/design only. No implementation code in this phase.

## Goal
Plan a stylish, elegant, responsive fashion-product showcase section built with static HTML and CSS.

The deliverable should present:
- outfit or product cards
- pricing
- quick-shop buttons
- refined visual hierarchy
- a polished, modern editorial/fashion feel

---

## Memory Review Completed
Reviewed before planning:
- `memory/project_context.md`
- `memory/progress.md`
- `memory/decisions.md`

Repo inspection completed:
- `calculator.html`
- `styles.css`
- `package.json`

---

## Current Repo State
The current frontend surface in this repo is extremely lightweight:
- one static HTML page (`calculator.html`)
- one shared stylesheet (`styles.css`)
- optional JS/testing artifacts from earlier work

There is no frontend framework, no bundler, and no design system. That means PAP-250 should be delivered as a simple static HTML/CSS artifact rather than as a React/Vue/Streamlit feature.

### Important architectural implication
PAP-250 should be implemented as a standalone static showcase page and should not be coupled into the Python backend or dashboard code.

---

## Root Cause / Gap
The repo does not yet contain any fashion/product showcase UI. The current static surface is calculator-oriented and visually utilitarian rather than editorial or commerce-inspired.

The gap is not technical complexity — it is design structure and polish:
- no hero/section framing for product discovery
- no reusable card layout for products
- no pricing/promo treatment
- no quick-shop CTA pattern
- no responsive visual rhythm tailored to fashion content

---

## Architectural Recommendation
Keep this ticket fully static and self-contained.

### Recommended shape
Create a new standalone page, for example:
- `fashion-showcase.html`

And either:
1. add a dedicated stylesheet such as `fashion-showcase.css`, or
2. carefully append a scoped section of styles to an existing stylesheet only if selector names are isolated.

### Recommendation
Prefer a dedicated stylesheet:
- `fashion-showcase.css`

Why:
- avoids collisions with calculator styles
- keeps visual design isolated
- easier for Grunt/Pedant to review
- safer for future static UI additions

---

## Product/Design Direction
The section should feel more like a boutique/editorial landing strip than a generic ecommerce grid.

### Desired mood
- elegant
- modern
- premium
- light luxury
- clean and breathable

### Visual characteristics
- warm neutral palette or monochrome with one accent tone
- strong typography contrast between headings and body copy
- generous whitespace
- rounded corners, but not cartoonishly large
- subtle shadows and card depth
- refined hover motion rather than flashy animation

---

## Recommended Page Structure

### 1. Section wrapper
A centered section with generous vertical spacing and a constrained content width.

Suggested content:
- eyebrow label, e.g. `New Edit` or `Curated Looks`
- section heading, e.g. `Fashion That Moves With You`
- short supporting description

### 2. Product card grid
Use a responsive grid with 3–4 cards on desktop, 2 on tablet, 1 on mobile.

Each card should include:
- product image area
- category/tag line
- product title
- short descriptor or styling cue
- price row
- optional original price / sale badge
- quick shop button

### 3. Optional highlight treatment
To increase visual interest, one featured card can span more space or carry a slightly differentiated style.

This is optional but recommended if it stays simple.

---

## Card Content Contract
Each card should contain enough content to feel real without requiring JavaScript.

### Minimum fields per card
- image
- title
- price
- quick shop CTA

### Recommended extra fields
- category label (`Outerwear`, `Evening`, `Essentials`)
- short line like `Tailored linen blend` or `Soft structured silhouette`
- rating or limited-stock badge only if it does not clutter the design

### Recommendation
Avoid fake ecommerce overload. Keep cards clean and fashion-forward.

---

## Image Strategy
Because this is static HTML/CSS, images should be simple and reliable.

### Recommended options
1. use royalty-free remote placeholder/fashion images
2. use gradient/image placeholders if asset sourcing is uncertain
3. use solid card media blocks with overlay text if no real images are available

### Best implementation recommendation
If Grunt can rely on stable remote image URLs, use them.
If not, use elegant gradient media blocks so the page still looks polished without broken assets.

The plan should not depend on JavaScript for image behavior.

---

## CSS Layout Strategy

### Section container
- max-width around `1100px–1200px`
- centered with horizontal padding
- large top/bottom spacing

### Grid
Use CSS Grid:
- desktop: `repeat(3, minmax(0, 1fr))` or `repeat(4, minmax(0, 1fr))`
- tablet: 2 columns
- mobile: 1 column

### Card anatomy
- media block at top
- content stack below
- price + CTA aligned cleanly
- full-height cards so rows feel even

### Hover behavior
Subtle only:
- translateY by a few pixels
- shadow deepens slightly
- image/media scales minimally
- button color/contrast improves

---

## Typography Recommendation
Use system fonts unless the next role wants a safe hosted font import.

### Recommended hierarchy
- heading: bold/high-contrast serif or elegant sans pairing
- body/meta text: restrained sans-serif
- prices: slightly larger and bolder than description text

### Safe option
Use a CSS-only font stack such as:
- headings: `"Georgia", "Times New Roman", serif`
- body: `"Inter", "Segoe UI", Arial, sans-serif` fallback-friendly stack

If external font imports are added later, they should remain optional.

---

## Color and Theming Recommendation
Prefer a soft, premium palette.

### Suggested palette direction
- background: ivory / off-white / very light beige
- card background: white or warm white
- text: charcoal / soft black
- muted text: taupe / gray-brown
- accent: black, espresso, muted rose, or gold-beige

### CTA styling
Quick shop buttons should be visually clear but tasteful:
- filled dark button on light cards, or
- outlined neutral button with strong hover state

Recommendation: avoid neon or saturated ecommerce colors.

---

## Accessibility / UX Requirements
Even though this is a visual ticket, implementation should still meet basic usability standards.

### Must-have
- semantic headings
- buttons/links with readable contrast
- visible hover/focus states
- alt text for images if `<img>` tags are used
- tap-friendly CTA sizing on mobile

### Avoid
- text over busy imagery without overlays
- tiny price/button text
- hover-only affordances with no visible resting CTA

---

## Responsive Behavior Requirements
This ticket specifically benefits from a mobile-first layout.

### Mobile
- cards stack to one column
- headings wrap cleanly
- price and CTA should not collide
- section padding should reduce but remain breathable

### Tablet
- two-card grid
- maintain equal card heights if possible

### Desktop
- three or four cards depending on chosen visual density

---

## Implementation Plan For Grunt

### Step 1 — create page files
Recommended new files:
- `fashion-showcase.html`
- `fashion-showcase.css`

### Step 2 — build semantic section structure
Include:
- section intro
- product grid
- 3 to 6 product cards

### Step 3 — implement scoped styling
Use dedicated class names such as:
- `.showcase`
- `.showcase__header`
- `.product-grid`
- `.product-card`
- `.product-card__media`
- `.product-card__content`
- `.product-card__price`
- `.product-card__button`

This avoids collisions with existing calculator styles.

### Step 4 — make it responsive
Add breakpoints for:
- mobile default
- tablet (`min-width: 640px` or similar)
- desktop (`min-width: 960px` or similar)

### Step 5 — refine polish
Add:
- subtle shadows
- hover lift
- clear price emphasis
- elegant spacing rhythm

### Step 6 — sanity-check output
Grunt should verify:
- no broken layout at narrow widths
- card buttons remain visible and aligned
- no CSS leakage into calculator styles if both pages coexist

---

## Recommended Non-Goals
Do not add:
- cart logic
- modal quick view
- JS filtering/sorting
- backend integration
- framework setup

This ticket is HTML + CSS only.

---

## Suggested Acceptance Criteria
PAP-250 should count as complete when:
1. a standalone fashion showcase section/page exists
2. it contains multiple elegant product cards
3. prices and quick shop CTAs are clearly visible
4. the layout is responsive across desktop/tablet/mobile
5. the visual style feels polished and intentional, not generic
6. implementation does not disturb existing static assets unnecessarily

---

## Pedant Review Checklist
Pedant should review:
- responsive breakpoints and card behavior
- spacing consistency
- contrast and readability
- whether the CTA/buttons feel balanced rather than oversized
- whether selectors are properly scoped
- whether the design looks polished without requiring JavaScript

---

## Recommended Next Issue
If the team wants to continue this static-frontend track, a natural follow-up would be:
- add a matching hero/banner section or collection filter bar
- or create a second page for product detail styling

---

## Artifact For Next Role
Grunt should implement a standalone, responsive static fashion showcase page with elegant product cards, pricing, and quick-shop buttons using dedicated scoped HTML/CSS files, keeping the design self-contained and visually polished.
