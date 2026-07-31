with open('d:/jacauto-angren/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace the plain JAC logo with the JAC | auto uzbekistan logo
c = c.replace('Untitled-design-2.png', 'photo_2026-02-03_11-41-51.png')

with open('d:/jacauto-angren/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Count:', c.count('photo_2026-02-03_11-41-51.png'))
