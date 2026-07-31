with open('d:/jacauto-angren/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Header logo → text "JAC MOTORS ANGREN"
old_logo = '<a href="#" class="logo">\n    <img src="https://jacauto.uz/wp-content/uploads/2024/08/Untitled-design-2.png" alt="JAC" class="logo-dark">\n    <img src="https://jacauto.uz/wp-content/uploads/2024/08/Untitled-design-2.png" alt="JAC" class="logo-light">\n</a>'
new_logo = '<a href="#" class="logo"><span class="logo-text-link">JAC<span class="logo-accent">MOTORS</span></span></a>'
c = c.replace(old_logo, new_logo)

# 2. Preloader → ring + "JAC MOTORS"
old_pre = '<div class="preloader" id="preloader"><div class="loader-ring"></div></div>'
new_pre = '<div class="preloader" id="preloader"><div class="loader-ring"></div><div class="loader-logo">JAC MOTORS</div></div>'
c = c.replace(old_pre, new_pre)

# 3. Favicon → keep JAC icon
old_fav = '''<link rel="icon" href="https://jacauto.uz/wp-content/uploads/2026/01/cropped-Untitled_design__73_-removebg-preview-32x32.png" sizes="32x32">
    <link rel="icon" href="https://jacauto.uz/wp-content/uploads/2026/01/cropped-Untitled_design__73_-removebg-preview-192x192.png" sizes="192x192">
    <link rel="apple-touch-icon" href="https://jacauto.uz/wp-content/uploads/2026/01/cropped-Untitled_design__73_-removebg-preview-180x180.png">
'''
new_fav = '<link rel="icon" href="https://jacauto.uz/wp-content/uploads/2026/01/cropped-Untitled_design__73_-removebg-preview-32x32.png" sizes="32x32">\n'
c = c.replace(old_fav, new_fav)

with open('d:/jacauto-angren/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('JAC MOTORS branding applied everywhere')
