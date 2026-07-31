with open('d:/jacauto-angren/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace favicon with jacmotors.uz logo-nav.png
old_fav = '<link rel="icon" href="https://jacauto.uz/wp-content/uploads/2026/01/cropped-Untitled_design__73_-removebg-preview-32x32.png" sizes="32x32"><link rel="icon" href="https://jacauto.uz/wp-content/uploads/2026/01/cropped-Untitled_design__73_-removebg-preview-192x192.png" sizes="192x192"><link rel="apple-touch-icon" href="https://jacauto.uz/wp-content/uploads/2026/01/cropped-Untitled_design__73_-removebg-preview-180x180.png">'
new_fav = '<link rel="icon" href="https://jacmotors.uz/logo-nav.png" sizes="32x32"><link rel="apple-touch-icon" href="https://jacmotors.uz/logo-nav.png">'
c = c.replace(old_fav, new_fav)

with open('d:/jacauto-angren/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Favicon from jacmotors.uz applied')
