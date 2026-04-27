# TunedPC.com Frontend Reference

> Design system and patterns to replicate for KSpider's web frontend.

---

## Tech Stack
- Next.js 16.2.2 + React 19.2.4
- Tailwind CSS 4 (PostCSS-based, `@theme` block)
- Framer Motion 12.38.0
- TypeScript 5 (strict)
- Fonts: Inter (body), Plus Jakarta Sans (headings), JetBrains Mono (code/numbers)

---

## Color Palette

| Token | Value | Usage |
|---|---|---|
| `--color-charcoal` | #1A1A2E | Primary text, dark backgrounds |
| `--color-ivory` | #F5F0EB | Page background, light text on dark |
| `--color-teal` | #00D4AA | Primary CTA, accents, highlights |
| `--color-teal-dark` | #00B894 | Hover states |
| `--color-teal-light` | rgba(0,212,170,0.1) | Badge backgrounds |
| `--color-soft-gray` | #E8E4DF | Dividers, borders |
| `--color-midnight` | #16213E | Dark alternative sections |
| `--color-orange` | #FF6B35 | Secondary accent, "before" numbers |
| `--color-success` | #4ADE80 | Success states |

---

## Layout Patterns

### Container
```
max-w-7xl mx-auto px-4 sm:px-6 lg:px-8
```

### Section Spacing
```
py-20 lg:py-28
```

### Page Section Order (Landing)
1. PromoBar (dismissible top banner)
2. Navigation (sticky header)
3. HeroSection (headline + badge + CTA + trust bar)
4. SocialProofStrip (marquee scrolling)
5. PainPointsSection (4 cards, dark background)
6. HowItWorks (3-column steps)
7. BenchmarkSection (4 cards, dark)
8. PricingSection (2 tiers)
9. TestimonialsSection (4 cards, grid)
10. FAQSection (accordion)
11. FinalCTA (background image)
12. Footer (multi-column)

---

## Key Components

### Button (4 variants, 3 sizes)
- `primary`: teal bg, white text, glow
- `secondary`: charcoal bg
- `outline`: border only
- `ghost`: transparent, hover underline
- Sizes: sm (px-4 py-2), md (px-6 py-3), lg (px-8 py-4)

### AnimatedSection (scroll-triggered)
```tsx
initial={{ opacity: 0, y: 32 }}
whileInView={{ opacity: 1, y: 0 }}
viewport={{ once: true, margin: "-80px" }}
transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
```

### Section Heading
```tsx
<h2 className="font-heading text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight">
```

---

## Animation Patterns (Framer Motion)

### Hero Entrance
```tsx
initial={{ opacity: 0, y: 24 }}
animate={{ opacity: 1, y: 0 }}
transition={{ duration: 0.6, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
```

### Marquee
```tsx
animate={{ x: ["0%", "-50%"] }}
transition={{ repeat: Infinity, duration: 30, ease: "linear" }}
```

### FAQ Accordion
```tsx
animate={{ height: isOpen ? "auto" : 0, opacity: isOpen ? 1 : 0 }}
transition={{ duration: 0.3 }}
```

---

## Typography

| Element | Classes |
|---|---|
| H1 (Hero) | `text-6xl lg:text-7xl font-bold font-heading tracking-tight` leading 1.1 |
| H2 (Section) | `text-3xl sm:text-4xl lg:text-5xl font-bold font-heading tracking-tight` |
| Body | `text-base lg:text-lg text-charcoal/60 leading-relaxed` |
| Caption | `text-xs sm:text-sm text-charcoal/40 uppercase tracking-wider` |

## Opacity Hierarchy
- Full: `text-charcoal`
- Primary: `text-charcoal/80`
- Secondary: `text-charcoal/60`
- Tertiary: `text-charcoal/40`
- Subtle: `text-charcoal/20`

---

## Data Architecture
- Content separated into `lib/data.ts` (arrays of marketing content)
- Types in `lib/types.ts` (interfaces for Testimonial, BenchmarkResult, PricingPlan, etc.)
- Inline SVG icons (no external library), themed with `className="text-teal"`

---

## Responsive Breakpoints
- `sm:` (640px) — mobile landscape
- `md:` (768px) — tablet
- `lg:` (1024px) — desktop
- `xl:` (1280px) — wide desktop
