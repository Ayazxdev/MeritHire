# UPDATED DESIGN - Text Left, Object Right

## New Layout:

```
┌─────────────────────────────────────────────────────────────┐
│  FAIR HIRING NETWORK            Navigation at TOP    [ MENU ]│ ← Navbar (visible from start)
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  LEFT SIDE (STICKY)              RIGHT SIDE (MOVING)         │
│                                                               │
│  ┌─────────────────┐            ┌──────────────────┐        │
│  │ FAIR            │            │                  │        │
│  │                 │            │   [3D OBJECT]    │        │
│  │ HIRING          │            │  starts below,   │        │
│  │                 │            │  moves upward    │        │
│  │ VERIFIED        │            │  with rotation   │        │
│  │                 │            │                  │        │
│  │ SKILLS          │            │                  │        │
│  │                 │            │                  │        │
│  │ ┌─────────────┐ │            └──────────────────┘        │
│  │ │NO BIAS •    │ │                                        │
│  │ │ONLY SKILL   │ │                                        │
│  │ └─────────────┘ │                                        │
│  └─────────────────┘                                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Key Changes:

### ✅ **1. Layout Split**
- **Left 50%**: Text content (FIXED/STICKY - doesn't move)
- **Right 50%**: 3D object canvas (MOVES upward)

### ✅ **2. Hero Text - Left Side**
- Title words stacked vertically:
  - FAIR
  - HIRING
  - VERIFIED
  - SKILLS
- Badge below: "NO BIAS • ONLY SKILL"
- Text STAYS IN PLACE while scrolling
- Reduced size for better vertical fit: `clamp(4rem, 10vw, 12rem)`

### ✅ **3. 3D Object - Right Side**
- Positioned on right half of screen
- Starts from BELOW (`y: 80vh`)
- Moves UPWARD to `-30vh` as you scroll
- Rotates 360° simultaneously
- Movement is scroll-driven

### ✅ **4. Navbar**
- **Visible from START** (no fade-in animation)
- Always at top
- Product name (left) + Menu button (right)

### ✅ **5. Content Removed**
- ❌ Removed subtitle "Agent-driven hiring..."
- ❌ Removed "Skills First" section
- ❌ Removed "Bias Detection" section  
- ❌ Removed "Fair Opportunity" section
- Clean, minimal design - just hero

## Scroll Behavior:

```
Scroll: 0%
├─ Text: STICKY on left (stays visible)
├─ Object: y = 80vh (below screen, on right)
└─ Rotation: 0°

Scroll: 50%
├─ Text: STICKY on left (same position)
├─ Object: y = 25vh (moving up, on right)
└─ Rotation: 180°

Scroll: 100%
├─ Text: STICKY on left (same position)
├─ Object: y = -30vh (above starting, on right)
└─ Rotation: 360°

Post-scroll:
├─ Object becomes STICKY at top
└─ Overlaps any future sections
```

## Typography Adjustments:

| Element | Previous | Current |
|---------|----------|---------|
| Title Words | clamp(6rem, 14vw, 18rem) | clamp(4rem, 10vw, 12rem) |
| Line Height | 0.85 | 0.9 |
| Letter Spacing | -0.03em | -0.02em |

## File Changes:

1. ✅ **Hero.jsx**: Text on left, stacked vertically, no subtitle
2. ✅ **Navbar.jsx**: No animation, visible from start
3. ✅ **ParallaxObject.jsx**: Positioned right side (`w-1/2 right-0`)
4. ✅ **App.jsx**: Removed all content sections
5. ✅ **globals.css**: Adjusted title word sizing for vertical layout

## What's Different:

**BEFORE:**
- Title words in 4 corners
- Object centered
- Subtitle present
- Content sections below
- Navbar animates in

**NOW:**
- Title words stacked LEFT
- Object on RIGHT
- No subtitle
- No content sections
- Navbar always visible

---

**Dev server running at**: `http://localhost:5173/`

**Test it**: Scroll slowly to see text stay LEFT while object rises on RIGHT with rotation! 🎯
