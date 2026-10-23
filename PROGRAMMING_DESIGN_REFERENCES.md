# Programming Design Reference Defaults

Use these as persistent starting references when planning and implementing future SPIDER NET websites, mobile WebView apps, dashboards, and other interface projects. Re-check the live documentation before using code from a library; these are reference sources, not a mandate to install every dependency.

## Preferred reference sources

1. **React Bits** — https://www.reactbits.dev/  
   Use for visual exploration: restrained animated components, backgrounds, micro-interactions, typography, and compositional ideas. Main source: https://github.com/DavidHDev/react-bits
2. **IT Tools** — https://it-tools.tech/  
   Use for product UX inspiration: compact utility cards, clear information hierarchy, search and categories, minimal steps, privacy-minded local processing, and accessible tool organization. Main source: https://github.com/CorentinTh/it-tools

## Implementation rules

- Do not copy the whole sites or import a heavy framework just because a reference uses it. Select a specific component/pattern, inspect its source and current license, and adapt only what is suitable for the target stack.
- For plain HTML/CSS/JavaScript and Android WebView projects, prefer native CSS and small vanilla-JS implementations. Do not introduce React/Tailwind/build tooling unless the project actually needs it.
- Prioritize mobile-first responsive layout, accessibility, keyboard/focus support, readable Arabic RTL, touch-sized controls, safe colors/contrast, and predictable navigation.
- Prefer subtle transitions, clear states, and restrained background effects. Respect `prefers-reduced-motion`; avoid animations that slow data entry or distract in accounting/admin tools.
- Keep operational interfaces fast and lightweight. No remote fonts, large animation packages, external trackers, unnecessary network calls, or runtime CDN dependencies by default.
- Preserve existing business logic, data schema, local persistence, validation, backup/restore flows, and platform/browser compatibility. Never redesign by removing a working feature.
- For financial interfaces, optimize readability and error prevention above visual spectacle: amounts and dates remain obvious; risky actions get confirmation; input errors are explicit; no made-up balances.
- Verify builds and run suitable smoke checks after changes. A successful build is not proof that the app was tested on the user's device.
- Keep the license attribution and notices required by any code or assets reused from external sources. Use ideas as inspiration where copying source code is unnecessary.
 
## SPIDER NET current brand direction

- Arabic RTL by default; mobile-first.
- Dark navy foundation with neon-lime and cyan accents, polished panels, clear type hierarchy, subtle glows, crisp dividers, and limited motion.
- The light theme remains available for users who prefer it.
- App interfaces must still work offline unless the user explicitly requests online services.

## How to apply these references

Before writing code: state which reference pattern is useful and why. Then adapt it to the project's technology instead of wholesale importing it. After coding: confirm critical interactions, mobile layout, backup/data safety, and build status, while clearly distinguishing automated build checks from device-level testing.
