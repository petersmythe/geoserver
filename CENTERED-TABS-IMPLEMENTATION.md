# Centered Navigation Tabs Implementation

## Overview

Added CSS styling to center the navigation tabs (User Manual, Developer Guide, Documentation Guide, API Reference) in the header for better visual balance.

## Changes Made

### File Modified
- `doc/themes/geoserver/stylesheets/extra.css`

### CSS Added

```css
/* 
 * Center Navigation Tabs
 * 
 * Centers the horizontal navigation tabs (User Manual, Developer Guide, etc.)
 * in the header for better visual balance.
 */

/* Center the tabs list */
.md-tabs__list {
  justify-content: center !important;
}

/* Optional: Add some spacing between tabs for better visual separation */
.md-tabs__item {
  margin: 0 0.5rem;
}

/* Ensure tabs container uses flexbox for centering */
.md-tabs {
  display: flex;
  justify-content: center;
}

.md-tabs .md-grid {
  display: flex;
  justify-content: center;
  width: 100%;
}
```

## How It Works

1. **Flexbox Centering**: Uses CSS flexbox with `justify-content: center` to center the tabs horizontally
2. **Tab Spacing**: Adds 0.5rem margin on each side of tabs for better visual separation
3. **Container Alignment**: Ensures both the tabs container and grid use flexbox centering

## Visual Effect

### Before
```
[Logo]  User Manual  Developer Guide  Documentation Guide  API Reference                    [Search]
```

### After
```
[Logo]                User Manual  Developer Guide  Documentation Guide  API Reference                [Search]
```

The tabs are now centered in the available space between the logo and search box.

## Browser Compatibility

This CSS uses standard flexbox properties supported by all modern browsers:
- Chrome/Edge (Chromium)
- Firefox
- Safari
- Mobile browsers

## Testing

To see the centered tabs:

1. **Local Testing**:
   ```bash
   source .venv/Scripts/activate
   mkdocs serve
   ```
   Then visit: http://localhost:8000/en/user/

2. **Deployed Site**:
   After pushing changes, the centered tabs will appear at:
   https://petersmythe.github.io/geoserver/3.0.x/en/user/

## Responsive Behavior

The centering works across all screen sizes:
- **Desktop**: Tabs centered with good spacing
- **Tablet**: Tabs remain centered, may wrap if needed
- **Mobile**: Material theme handles responsive behavior automatically

## Customization Options

If you want to adjust the spacing between tabs, modify the margin value:

```css
.md-tabs__item {
  margin: 0 0.5rem;  /* Change 0.5rem to your preferred spacing */
}
```

Common values:
- `0.25rem` - Tighter spacing
- `0.5rem` - Default (current)
- `0.75rem` - Wider spacing
- `1rem` - Maximum spacing

## Next Steps

1. Commit the CSS changes
2. Push to trigger deployment
3. Verify centered tabs on deployed site
4. Adjust spacing if needed

## Related Files

- CSS: `doc/themes/geoserver/stylesheets/extra.css`
- Theme: `doc/themes/geoserver/`
- Config: `mkdocs.yml` (theme.custom_dir setting)
