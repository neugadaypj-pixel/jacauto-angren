/* ============================================
   FULL JACAUTO.UZ DOWNLOAD SCRIPT
   ============================================
   1. Open https://jacauto.uz/ in Chrome/Edge
   2. Press F12 → Console tab
   3. Paste this ENTIRE script → Enter
   4. A ZIP file downloads — send it to me
   ============================================ */

(async () => {
    console.clear();
    console.log('%c🚀 DOWNLOADING JACAUTO.UZ (FULL)...', 'font-size:18px;color:#FF3600;');

    const result = {
        url: location.href,
        timestamp: new Date().toISOString(),
        // 1 — Full HTML
        html: document.documentElement.outerHTML,
        // 2 — All inline <style> blocks
        inlineStyles: [],
        // 3 — All external CSS text
        externalCSS: [],
        // 4 — All @keyframes from all sheets
        keyframes: [],
        // 5 — Elementor data-settings for every widget
        elementorSettings: [],
        // 6 — Every element with animations
        animatedElements: [],
        // 7 — Computed styles for key elements
        computed: {},
        // 8 — CSS variables (root)
        cssVariables: {}
    };

    // --- 1. Inline <style> blocks ---
    document.querySelectorAll('style').forEach((s, i) => {
        result.inlineStyles.push({ index: i, id: s.id || '', content: s.textContent });
    });

    // --- 2. External CSS — fetch text content ---
    const cssLinks = [...document.querySelectorAll('link[rel="stylesheet"]')].map(l => l.href);
    for (const url of cssLinks) {
        try {
            const res = await fetch(url);
            if (res.ok) {
                const text = await res.text();
                result.externalCSS.push({ url, size: text.length, content: text });

                // Extract @keyframes
                const kfRegex = /@(?:-webkit-)?keyframes\s+([\w-]+)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}/gs;
                let match;
                while ((match = kfRegex.exec(text)) !== null) {
                    result.keyframes.push({ name: match[1], full: match[0] });
                }
            }
        } catch (e) {
            result.externalCSS.push({ url, error: e.message });
        }
    }

    // --- 3. All Elementor widgets with data-settings ---
    document.querySelectorAll('[data-settings]').forEach(el => {
        try {
            const settings = JSON.parse(el.dataset.settings);
            result.elementorSettings.push({
                tag: el.tagName,
                id: el.dataset.id || '',
                class: el.className.replace(/\s+/g, ' ').substring(0, 200),
                settings: settings
            });
        } catch (e) {}
    });

    // --- 4. Every animated/invisible element ---
    document.querySelectorAll('.elementor-invisible, [class*="animated"], [class*="animation"], [class*="fadeIn"], [class*="at-heading"], [class*="at-image"], [class*="at-animation"]').forEach(el => {
        const style = getComputedStyle(el);
        result.animatedElements.push({
            tag: el.tagName,
            class: el.className.replace(/\s+/g, ' ').substring(0, 300),
            animation: style.animation,
            animationName: style.animationName,
            animationDuration: style.animationDuration,
            animationDelay: style.animationDelay,
            animationFillMode: style.animationFillMode,
            transform: style.transform,
            opacity: style.opacity,
            visibility: style.visibility
        });
    });

    // --- 5. CSS custom properties from :root ---
    const rootStyles = getComputedStyle(document.documentElement);
    for (let i = 0; i < rootStyles.length; i++) {
        const prop = rootStyles[i];
        if (prop.startsWith('--')) {
            result.cssVariables[prop] = rootStyles.getPropertyValue(prop).trim();
        }
    }

    // --- 6. Key computed styles ---
    const hero = document.querySelector('.elementor-element-9edbf4d, [data-id="9edbf4d"]');
    const heading1 = document.querySelector('h1');
    const header = document.querySelector('header, .header-version-3');

    if (hero) result.computed.hero = { background: getComputedStyle(hero).background, minHeight: getComputedStyle(hero).minHeight };
    if (heading1) result.computed.heading1 = { fontSize: getComputedStyle(heading1).fontSize, fontWeight: getComputedStyle(heading1).fontWeight, color: getComputedStyle(heading1).color, fontFamily: getComputedStyle(heading1).fontFamily };
    if (header) result.computed.header = { background: getComputedStyle(header).background, height: getComputedStyle(header).height, position: getComputedStyle(header).position };

    // --- Download ---
    const jsonStr = JSON.stringify(result, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'jacauto-full-dump.json';
    a.click();
    URL.revokeObjectURL(url);

    // --- Summary ---
    console.log('%c✅ DOWNLOAD COMPLETE!', 'font-size:16px;color:#00cc66;');
    console.log('📦 File: jacauto-full-dump.json');
    console.log('📊 Stats:');
    console.log('  HTML size:', (result.html.length / 1024).toFixed(0), 'KB');
    console.log('  External CSS files:', result.externalCSS.length);
    console.log('  @keyframes extracted:', result.keyframes.length);
    console.log('  Inline style blocks:', result.inlineStyles.length);
    console.log('  Elementor widgets:', result.elementorSettings.length);
    console.log('  Animated elements:', result.animatedElements.length);
    console.log('  CSS variables:', Object.keys(result.cssVariables).length);
    console.log('%c📨 Send this file to me!', 'font-size:14px;color:#FF3600;');
})();
