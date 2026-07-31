with open('d:/jacauto-angren/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

favicon = '    <link rel="icon" href="https://jacauto.uz/wp-content/uploads/2026/01/cropped-Untitled_design__73_-removebg-preview-32x32.png" sizes="32x32">\n    <link rel="icon" href="https://jacauto.uz/wp-content/uploads/2026/01/cropped-Untitled_design__73_-removebg-preview-192x192.png" sizes="192x192">\n    <link rel="apple-touch-icon" href="https://jacauto.uz/wp-content/uploads/2026/01/cropped-Untitled_design__73_-removebg-preview-180x180.png">\n'

c = c.replace('<link rel="stylesheet" href="css/style.css">', favicon + '    <link rel="stylesheet" href="css/style.css">')

with open('d:/jacauto-angren/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Favicon added. Count:', c.count('apple-touch-icon'))
