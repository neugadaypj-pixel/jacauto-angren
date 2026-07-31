with open('d:/jacauto-angren/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace the JAC|auto uzbekistan logo with the clean JAC logo
c = c.replace('photo_2026-02-03_11-41-51.png', 'Untitled-design-2.png')

with open('d:/jacauto-angren/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Clean JAC logo restored. Count:', c.count('Untitled-design-2.png'))
