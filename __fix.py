with open('d:/jacauto-angren/css/style.css', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix: logo-dark should be visible by default with invert filter (white on dark bg)
# logo-light should be hidden. On scroll, swap.
old_logo_css = '''.logo{display:flex;align-items:center}
.logo img{height:28px;width:auto;max-width:150px;display:none}
.logo-light{display:none}
.header.scrolled .logo-dark{display:none}
.header.scrolled .logo-light{display:block}
.home .logo-dark{display:block}'''

new_logo_css = '''.logo{display:flex;align-items:center}
.logo img{height:28px;width:auto;max-width:150px}
.logo-dark{display:block;filter:brightness(0) invert(1)}
.logo-light{display:none}
.header.scrolled .logo-dark{display:none}
.header.scrolled .logo-light{display:block;filter:brightness(1) invert(0)}'''

c = c.replace(old_logo_css, new_logo_css)

with open('d:/jacauto-angren/css/style.css', 'w', encoding='utf-8') as f:
    f.write(c)

print('CSS fixed — logo-dark visible by default')

# Now fix favicon — use jacauto.uz favicon
with open('d:/jacauto-angren/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_fav = '<link rel="icon" href="logo-nav.webp" sizes="32x32">'
new_fav = '<link rel="icon" href="https://jacauto.uz/wp-content/uploads/2026/01/cropped-Untitled_design__73_-removebg-preview-32x32.png" sizes="32x32"><link rel="icon" href="https://jacauto.uz/wp-content/uploads/2026/01/cropped-Untitled_design__73_-removebg-preview-192x192.png" sizes="192x192"><link rel="apple-touch-icon" href="https://jacauto.uz/wp-content/uploads/2026/01/cropped-Untitled_design__73_-removebg-preview-180x180.png">'
html = html.replace(old_fav, new_fav)

with open('d:/jacauto-angren/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Favicon restored from jacauto.uz')
