import shutil, os

for filename in ['car.html']:
    path = os.path.join('d:/jacauto-angren', filename)
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # Replace old logo URL with local logo
    count1 = c.count('Untitled-design-2.png')
    c = c.replace('https://jacauto.uz/wp-content/uploads/2024/08/Untitled-design-2.png', 'logo-nav.webp')
    count2 = c.count('logo-nav.webp')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    
    print(f'{filename}: logo replaced ({count1} -> {count2})')
