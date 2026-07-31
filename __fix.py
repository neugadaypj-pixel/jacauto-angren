with open('d:/jacauto-angren/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace header logo images with local logo-nav.webp
old_src = 'https://jacauto.uz/wp-content/uploads/2024/08/Untitled-design-2.png'
new_src = 'logo-nav.webp'
c = c.replace(old_src, new_src)

# Replace favicon with logo-nav.webp
old_fav = '<link rel="icon" href="https://jacauto.uz/wp-content/uploads/2026/01/cropped-Untitled_design__73_-removebg-preview-32x32.png" sizes="32x32">'
new_fav = '<link rel="icon" href="logo-nav.webp" sizes="32x32">'
c = c.replace(old_fav, new_fav)

with open('d:/jacauto-angren/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Logo replaced. logo-nav.webp count:', c.count('logo-nav.webp'))
