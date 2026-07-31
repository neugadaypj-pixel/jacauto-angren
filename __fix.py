with open('d:/jacauto-angren/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace the header logo with the favicon JAC logo (the car icon)
favicon_logo = 'cropped-Untitled_design__73_-removebg-preview-192x192.png'
old_logo = 'Untitled-design-2.png'
c = c.replace(old_logo, favicon_logo)

with open('d:/jacauto-angren/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Logo replaced with favicon. Count:', c.count(favicon_logo))
