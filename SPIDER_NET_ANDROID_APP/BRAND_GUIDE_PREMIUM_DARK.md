# SPIDER NET — Premium Dark Visual Identity

## Direction
Premium Dark: a restrained financial-workspace identity built around deep navy, clear cyan interaction accents, and cool silver surfaces. Arabic RTL remains the primary reading direction.

## Color tokens

| Token | Dark | Light |
|---|---|---|
| Background | #071321 | #EDF3F8 |
| Surface | #0D1E30 | #FFFFFF |
| Raised surface | #11283E | #F5F8FB |
| Border | #29445C | #D8E2EB |
| Primary text | #EDF5FB | #142C42 |
| Secondary text | #A4B6C8 | #61788D |
| Accent cyan | #35C4E4 | #087F9E |
| Silver accent | #9DB2C5 | #718DA5 |
| Spider glow | #53D7EE | #14A9C9 |

## Visual rules
- Keep the existing spider emblem and wordmark; render the emblem in cool silver with a controlled cyan glow.
- Use navy gradients only for the shell and navigation, not for every card.
- Reserve cyan for primary actions, selected navigation, focus states, and meaningful data emphasis.
- Use silver for secondary controls, borders, and supporting information.
- Preserve high contrast, keyboard focus visibility, touch target sizing, RTL alignment, responsive breakpoints, and reduced-motion preferences.
- Keep print output white and legible; identity overrides are screen-only.

## Engineering boundary
This change is a CSS/theme layer only. It does not modify JavaScript, data schemas, local storage, backup/restore, accounting calculations, transaction workflows, or Android bridge code. Regression and on-device print/save checks remain required before release.
