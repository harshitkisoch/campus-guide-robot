# Phase 6 – Mobile-First HMI Dashboard Redesign

## 1. Objective
To completely overhaul the web-based Human-Machine Interface (HMI). The previous version suffered from severe UX issues due to desktop-scaling on mobile devices. The goal was to build a premium, responsive, app-like terminal optimized specifically for touch interaction on phones.

## 2. Problem Statement
The legacy dashboard simply shrunk desktop layouts to fit mobile screens. This resulted in:
- Overlapping UI components and text overflow.
- Fixed-width cards that broke viewport boundaries.
- Massive empty spaces pushing critical controls off-screen.
- Unusable D-Pad controls due to microscopic touch targets.

## 3. Design Principles Enforced
- **Mobile-First Approach:** Base styling targets `<768px` viewports as a single vertical stack, progressively enhancing for tablets/desktops.
- **Ergonomics:** 48px minimum size for buttons, 56px minimum for directional D-Pad keys to ensure accurate touch inputs.
- **Grid System:** Strict adherence to an 8px spacing scale.
- **Aesthetic:** A "Dark Cybernetic" theme inspired by Tesla and Nothing OS interfaces.

## 4. Module Breakdown

### Module A: Design Tokens & Typography
- **CSS Variables:** Centralized theming in `style.css` (Surfaces: `#0e1014`, Primary: `#e82127`, Cyber Cyan: `#00e5ff`).
- **Typography:** Uses CSS `clamp()` for fluid scaling. Font stack pairs 'Plus Jakarta Sans' (UI) with 'JetBrains Mono' (Data).

### Module B: Layout & Navigation
- Implemented a 12-column responsive grid.
- Replaced top-bars with a sticky, bottom-anchored mobile taskbar featuring 5 sections: Status, Chat, Control, History, Setup. Includes smooth scroll-to-section behaviors.

### Module C: Interaction Card (Chat)
- Replicates modern AI interfaces. Features a text input alongside large, 48px target areas for Voice (Mic) and Send actions.
- Integrates browser Web Speech API for real-time speech-to-text (`interimResults: true`).
- Distinct chat bubble UI differentiating User (right/red) vs Robot (left/dark).

### Module D: Hardware Controller
- D-Pad uses a 3x3 CSS grid. Keys are specifically sized to 56px for thumb use.
- Drive speed slider (10-100%).
- Head angle slider (0-180°) for the servo.
- Toggle switch for autonomous face-tracking mode.

### Module E: Telemetry & QR Code
- A 2-column grid displaying live system health (Gemini Status, Ping, Battery mock).
- A compact connection card displaying the QR code, copy-link function, and download button.

### Module F: System Settings
- Tabbed interface (General, Audio, Network, Advanced) allowing runtime configuration of the `OUTPUT_DEVICE` and system reboots.

### Module G: JavaScript Architecture (`app.js`)
- Entirely encapsulated in an ES6 `RobotDashboard` class.
- Manages WebSocket lifecycle, ping/pong latency calculations, D-pad event binding, slider synchronization, and DOM updates for chat bubbles.

## 5. Viewport Architecture

```text
+-----------------------+
|  Status / Telemetry   |  <-- Module E
+-----------------------+
|                       |
|   Chat & AI Output    |  <-- Module C
|                       |
+-----------------------+
|       [ ^ ]           |
|   [ < ]   [ > ]       |  <-- Module D (D-Pad)
|       [ v ]           |
+-----------------------+
| [ Chat | Ctrl | Set ] |  <-- Module B (Nav Bar)
+-----------------------+
```

## 6. Files Created / Modified

| Filename | Purpose |
| :--- | :--- |
| `static/css/style.css` | Complete rewrite utilizing CSS grid, flexbox, and variables. |
| `templates/index.html` | Complete semantic HTML5 rewrite. |
| `static/js/app.js` | Complete logic rewrite encapsulating HMI behavior. |
