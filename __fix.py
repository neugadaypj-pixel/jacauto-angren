with open('d:/jacauto-angren/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Use the same logo as the favicon — but the RIGHT URL (from 2026/01/, not 2024/08/)
old_img = 'https://jacauto.uz/wp-content/uploads/2024/08/cropped-Untitled_design__73_-removebg-preview-192x192.png'
new_img = 'https://jacauto.uz/wp-content/uploads/2026/01/cropped-Untitled_design__73_-removebg-preview-192x192.png'

c = c.replace(old_img, new_img)

with open('d:/jacauto-angren/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Fixed URL. Count:', c.count(new_img))
