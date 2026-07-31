with open('d:/jacauto-angren/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace favicon with local jac-motors-logo.png
old = '<link rel="icon" href="https://jacmotors.uz/logo-nav.png" sizes="32x32"><link rel="apple-touch-icon" href="https://jacmotors.uz/logo-nav.png">'
new = '<link rel="icon" href="jac-motors-logo.png" sizes="32x32"><link rel="apple-touch-icon" href="jac-motors-logo.png">'
c = c.replace(old, new)

with open('d:/jacauto-angren/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Favicon: jac-motors-logo.png')
