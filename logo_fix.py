for f in ['index.html', 'car.html']:
    path = 'd:/jacauto-angren/' + f
    with open(path, 'r', encoding='utf-8') as file:
        c = file.read()
    old = c.count('photo_2026-02-03_11-41-51.png')
    c = c.replace('photo_2026-02-03_11-41-51.png', 'Untitled-design-2.png')
    with open(path, 'w', encoding='utf-8') as file:
        file.write(c)
    new = c.count('Untitled-design-2.png')
    print(f'{f}: {old} -> {new}')
