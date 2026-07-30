for filename in ['index.html', 'car.html']:
    with open('d:/jacauto-angren/' + filename, 'r', encoding='utf-8') as f:
        c = f.read()
    old = c.count('781131008') + c.count('78 113 10 08')
    c = c.replace('781131008', '712007711')
    c = c.replace('78 113 10 08', '71 200 77 11')
    new = c.count('712007711')
    with open('d:/jacauto-angren/' + filename, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f'{filename}: {old} old phones -> {new} new phones')
