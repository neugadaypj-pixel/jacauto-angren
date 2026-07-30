/* ============================================
   JACAUTO.UZ — ПОЛНОЕ КОПИРОВАНИЕ САЙТА
   ============================================
   1. Открой https://jacauto.uz/
   2. F12 → Console
   3. Вставь ВЕСЬ этот скрипт → Enter
   4. Скачается файл jacauto-full-clone.html (один файл, весь сайт)
   ============================================ */

(async () => {
    console.clear();
    console.log('%c🔄 КОПИРУЮ ВЕСЬ САЙТ...', 'font-size:20px;color:#FF3600;font-weight:bold;');

    // ===== Шаг 1: Загружаем весь внешний CSS и встраиваем в <style> =====
    console.log('📦 Загружаю CSS файлы...');
    const cssLinks = [...document.querySelectorAll('link[rel="stylesheet"]')];
    let allCSS = '';

    for (const link of cssLinks) {
        try {
            const res = await fetch(link.href);
            if (res.ok) {
                const css = await res.text();
                // Исправляем относительные URL в CSS на абсолютные
                const base = link.href.substring(0, link.href.lastIndexOf('/') + 1);
                const fixed = css.replace(/url\((['"]?)(?!data:|https?:)([^)'"]+)(['"]?)\)/g, (_, q1, url, q2) => {
                    if (url.startsWith('//')) return `url(${q1}https:${url}${q2})`;
                    return `url(${q1}${new URL(url, base).href}${q2})`;
                });
                allCSS += `/* ${link.href} */\n${fixed}\n`;
                console.log('  ✅ CSS:', link.href.substring(0, 80) + '...');
            }
        } catch (e) {
            console.warn('  ⚠️ Не удалось загрузить:', link.href.substring(0, 60));
        }
    }

    // ===== Шаг 2: Собираем инлайн <style> блоки =====
    document.querySelectorAll('style').forEach(s => {
        allCSS += `/* inline style */\n${s.textContent}\n`;
    });
    console.log('✅ Всего CSS:', Math.round(allCSS.length / 1024), 'KB');

    // ===== Шаг 3: Клонируем DOM =====
    console.log('📄 Клонирую HTML...');
    const clone = document.documentElement.cloneNode(true);

    // Удаляем все <script> (они не нужны в статической копии)
    clone.querySelectorAll('script').forEach(s => s.remove());

    // Удаляем все внешние <link rel="stylesheet">
    clone.querySelectorAll('link[rel="stylesheet"]').forEach(l => l.remove());

    // Удаляем data-атрибуты lazy loading чтобы картинки загрузились
    clone.querySelectorAll('[data-src]').forEach(el => {
        if (!el.src || el.src.includes('data:') || el.src.includes('svg')) {
            el.src = el.dataset.src;
        }
    });
    clone.querySelectorAll('[data-lazyloaded]').forEach(el => el.removeAttribute('data-lazyloaded'));

    // Вставляем ВЕСЬ CSS в один <style> в <head>
    const megaStyle = document.createElement('style');
    megaStyle.id = 'all-css';
    megaStyle.textContent = allCSS;
    const head = clone.querySelector('head');
    if (head) {
        // Вставляем ПЕРЕД остальными элементами head
        head.insertBefore(megaStyle, head.firstChild);
    }

    // ===== Шаг 4: Удаляем preloader и лишние оверлеи =====
    const preloader = clone.querySelector('.preloader');
    if (preloader) preloader.remove();

    const magicCursor = clone.querySelector('#magic-cursor');
    if (magicCursor) magicCursor.remove();

    // Делаем все elementor-invisible видимыми
    clone.querySelectorAll('.elementor-invisible').forEach(el => {
        el.classList.remove('elementor-invisible');
        el.style.visibility = 'visible';
        el.style.animation = 'none';
        el.style.opacity = '1';
        el.style.transform = 'none';
    });

    // Убираем анимации (статичная копия)
    clone.querySelectorAll('[class*="animated"]').forEach(el => {
        el.style.animation = 'none';
        el.style.opacity = '1';
        el.style.transform = 'none';
        el.style.visibility = 'visible';
    });

    // ===== Шаг 5: Собираем финальный HTML =====
    console.log('💾 Собираю финальный HTML...');
    const finalHTML = '<!DOCTYPE html>\n' + clone.outerHTML;

    // ===== Шаг 6: Скачиваем =====
    const blob = new Blob([finalHTML], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'jacauto-full-clone.html';
    a.click();
    URL.revokeObjectURL(url);

    console.log('%c✅ ГОТОВО!', 'font-size:18px;color:#00cc66;font-weight:bold;');
    console.log('📁 Файл: jacauto-full-clone.html');
    console.log('📊 Размер:', Math.round(finalHTML.length / 1024), 'KB');
    console.log('📊 CSS встроено:', Math.round(allCSS.length / 1024), 'KB');
    console.log('%c📨 Отправь этот файл мне!', 'font-size:14px;color:#FF3600;');
})();
