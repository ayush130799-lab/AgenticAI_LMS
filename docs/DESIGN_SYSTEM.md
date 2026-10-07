# Visual reference: Traininglobe-inspired design system

Source: a screenshot of traininglobe.com's homepage. Recreate the *visual
language*, not the content — this product is "Agentic AI LMS", not
Traininglobe, and teaches AI/agents, not trading/astrology.

## What the reference looks like
- Thin top utility bar: phone + email on the left, small social icons on the
  right, tiny text, light gray background.
- Main navbar below it: logo + name on the left, a pill-shaped nav link group
  in the center (the active item, e.g. "Home", sits in a filled cyan rounded
  pill; other items are plain dark text with a small dropdown chevron where
  relevant), and on the right a "Log in" text link plus a solid blue rounded
  "Sign up" button.
- Hero section, two columns on desktop:
  - Left: a small rounded pill badge with an icon + "Trusted by 10,000+
    learners" style social proof text, in cyan-tinted text on a very light
    cyan pill background.
  - Large bold black headline (~64px), 2-3 lines, with one key phrase in the
    headline colored bright cyan/blue instead of black.
  - A secondary line (e.g. "Students | Professionals | Entrepreneurs") in
    medium-bold dark gray.
  - A paragraph of supporting text with 2-3 key terms colored (cyan, magenta,
    purple) to draw the eye.
  - Two CTA buttons: primary solid blue rounded-pill button with an arrow,
    secondary white/outline rounded-pill button.
  - A small floating "social proof" card near the bottom-left of the hero
    image (avatar + name + short activity text + relative time), with a
    colored dot "online" indicator.
  - Right: a large rounded-corner photo/video panel. Floating pill-shaped
    "feature chips" overlap the image edges (e.g. an icon + short label in a
    white rounded card with soft shadow — "Expert Mentors"), plus a dark
    "badge" card in a bottom corner advertising something live/urgent (colored
    accent tag like "LIVE" and a seats-left countdown in red).

## Translate this into the Agentic AI LMS
- Colors: white base, primary blue `#2563eb`-ish for buttons/links, cyan
  accent `#06b6d4`-ish for highlights/pills, very light cyan/blue tint
  (`#eff9fb` / `#eef6ff`) for section backgrounds and badge pills, near-black
  `#0f172a` for headline text, slate gray `#475569` for body text.
- Typography: bold, large sans-serif headlines (Inter/system-ui), generous
  line-height, tight letter-spacing on headlines.
- Shape language: rounded-2xl cards, rounded-full pills/buttons, soft
  `shadow-lg` with low opacity, generous whitespace.
- Hero badge: "Trusted by 10,000+ learners building with AI agents" (or
  similar), cyan pill.
- Headline: **"Master Agentic AI. Learn Smarter. Build Better."** — with
  "Agentic AI" or "Smarter" in cyan.
- Subheadline: "Students | Builders | Engineers"
- Supporting copy mentions Python, LLMs, RAG, AI Agents, LangGraph with 2-3
  of those terms colored (cyan/purple/magenta) inline.
- Primary CTA: "Start Learning" (→ /signup). Secondary CTA: "Explore
  Curriculum" (→ /courses).
- Floating chips over the hero visual: "AI Personalized Learning", "AI
  Tutor", "Skill Tracking", "Agent Projects" — small white rounded cards with
  an icon, positioned absolutely at the corners of the hero image, like the
  reference's "Expert Mentors" chip.
- Small floating social-proof card bottom-left of hero: avatar + "Priya S.
  enrolled in RAG Knowledge Assistant · 2h ago" style, subtle, with online dot.
- Nav: Home | Courses | How It Works | AI Learning | Projects | Resources |
  About | Contact, with the current route shown in a filled cyan pill; Log in
  text link + solid blue "Sign up" button on the right.

## Component tone across the whole app (not just landing)
- Dashboard/course/lesson pages: white cards on a very light gray/blue page
  background, rounded-xl, subtle border + shadow, blue/cyan for progress
  bars, chips, and active states. Skill mastery bars use a gradient from
  amber (low mastery) → cyan → blue (high mastery), never red/green alone
  (keep it consistent with the brand palette; use a small icon instead of
  pure red for "weak").
- Keep the same rounded-pill button style everywhere (primary blue solid,
  secondary outline).
- Reuse one `Badge`/`Chip` component for skill tags, difficulty tags, and
  "AI Recommended" tags.
