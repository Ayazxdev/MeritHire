# UPDATED SCROLL BEHAVIOR - Studio Dialect Style

## Changes Implemented:

### 1. HERO SECTION (300vh height)
```
┌─────────────────────────────────────────┐
│  FAIR            (top-left)     HIRING  │ ← Title words in corners
│                                  (top-right)
│                                         │
│  FAIR HIRING NETWORK ← (left-center)   │
│                                         │
│         [3D OBJECT]                     │ ← Starts from BELOW
│      (small part visible)               │
│                           [ MENU ] →    │ ← (right-center)
│                                         │
│  VERIFIED        (bottom-left)  SKILLS  │ ← Title words in corners
│       (bottom-right)                    │
│                                         │
│     [ NO BIAS • ONLY SKILL ]           │ ← Badge subtext
│                                         │
│  "Agent-driven hiring infrastructure"   │ ← Subtitle
└─────────────────────────────────────────┘
     ▼ Hero is STICKY (pinned)
     ▼ Object MOVES UPWARD + ROTATES 360°
```

### 2. SCROLL PHASE (0 → 300vh)
- Hero container: **STICKY/PINNED** (doesn't move)
- 3D Object: Starts at `y: 80vh` (below viewport)
- As you scroll:
  - Object moves from `80vh` → `-20vh` (upward)
  - Object rotates `0°` → `360°` on Y-axis
  - Title words stay visible in corners
  - Object moves THROUGH the text space

### 3. POST-HERO PHASE
- Object becomes **STICKY** at top
- Object **OVERLAPS** next sections
- Navbar **FADES IN** smoothly
- Fixed labels (FAIR HIRING NETWORK, MENU) fade out

## Key Differences from Before:

**BEFORE:**
- Object was static in center
- Title was one big block (covered by object)
- Hero scrolled normally

**NOW (Studio Dialect Style):**
- ✅ Object starts BELOW viewport
- ✅ Title split into 4 words in corners (FAIR, HIRING, VERIFIED, SKILLS)
- ✅ Text visible around object
- ✅ Hero is PINNED while object moves through it
- ✅ Subtext badge: "NO BIAS • ONLY SKILL"
- ✅ Object overlaps subsequent sections

## Animation Timeline:

```
Scroll: 0%    → Object at bottom (y: 80vh), rotation: 0°
        ↓
Scroll: 50%   → Object moving up (y: 30vh), rotation: 180°
        ↓
Scroll: 100%  → Object at top (y: -20vh), rotation: 360°
        ↓
Post-hero     → Object STICKY, overlaps next sections
        ↓
                Navbar appears
```

## Font Setup Reminder:

Add these files to `public/fonts/`:
- NeueMontreal-Bold.woff2
- NeueMontreal-Bold.woff
- NeueMontreal-Medium.woff2
- NeueMontreal-Medium.woff

The app will work without them but typography won't match exactly.
