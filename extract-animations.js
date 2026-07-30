/* ============================================
   COPY THIS ENTIRE SCRIPT.
   Open https://jacauto.uz/ in Chrome/Edge.
   Press F12 → go to "Console" tab.
   Paste this entire script → press Enter.
   A file "jacauto-animations.json" will download automatically.
   Send that file to me.
   ============================================ */

(async () => {
    const result = { keyframes: [], animationCSS: [], headingAnimations: [], aosSettings: [] };

    // 1. Extract all @keyframes from all stylesheets
    try {
        for (const sheet of document.styleSheets) {
            try {
                for (const rule of sheet.cssRules) {
                    if (rule.name && rule.name.startsWith('keyframes')) {
                        result.keyframes.push(rule.cssText);
                    }
                    if (rule.selectorText && (
                        rule.selectorText.includes('animation') ||
                        rule.selectorText.includes('at-heading') ||
                        rule.selectorText.includes('at-animation') ||
                        rule.selectorText.includes('heading-animation') ||
                        rule.selectorText.includes('fadeIn') ||
                        rule.selectorText.includes('elementor-invisible')
                    )) {
                        result.animationCSS.push(rule.cssText);
                    }
                }
            } catch (e) { /* cross-origin sheet, skip */ }
        }
    } catch (e) {}

    // 2. Extract all inline styles with animation names
    document.querySelectorAll('style').forEach(s => {
        const text = s.textContent;
        // Extract @keyframes blocks
        const kfRegex = /@keyframes\s+[\w-]+\s*\{[^}]*\{[^}]*\}[^}]*\}/gs;
        const matches = text.match(kfRegex);
        if (matches) result.keyframes.push(...matches);

        // Extract heading animation classes
        const headingLines = text.split('}').filter(line =>
            line.includes('at-heading') || line.includes('heading-anim') ||
            line.includes('anim-heading') || line.includes('at-animation')
        );
        if (headingLines.length) result.headingAnimations.push(...headingLines);

        // Extract any animation-related rules
        const animLines = text.split('}').filter(line =>
            line.includes('animation:') || line.includes('animation-name:') ||
            line.includes('@keyframes')
        );
        if (animLines.length) result.animationCSS.push(...animLines);
    });

    // 3. Extract Elementor animation data from data-settings
    document.querySelectorAll('[data-settings]').forEach(el => {
        try {
            const settings = JSON.parse(el.dataset.settings);
            if (settings._animation || settings.entrance_animation || settings.ekit_we_effect_on) {
                result.aosSettings.push({
                    tag: el.tagName,
                    class: el.className,
                    settings: settings
                });
            }
        } catch (e) {}
    });

    // 4. Extract CSS variables related to animation
    const styles = getComputedStyle(document.documentElement);
    const animVars = {};
    for (let i = 0; i < styles.length; i++) {
        const prop = styles[i];
        if (prop.includes('anim') || prop.includes('transit') || prop.includes('ease') || prop.includes('duration')) {
            animVars[prop] = styles.getPropertyValue(prop);
        }
    }
    result.cssVars = animVars;

    // 5. Copy the full external CSS used by Elementor for animations
    const externalCSS = [];
    document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
        externalCSS.push(link.href);
    });
    result.externalCSS = externalCSS;

    // Download
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'jacauto-animations.json';
    a.click();
    URL.revokeObjectURL(url);
    console.log('✅ Downloaded jacauto-animations.json — send this file to me!');
    console.log('Found:', result.keyframes.length, 'keyframes,', result.animationCSS.length, 'animation rules,', result.headingAnimations.length, 'heading anim blocks,', result.aosSettings.length, 'Elementor widgets with animations');
})();
