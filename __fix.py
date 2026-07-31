with open('d:/jacauto-angren/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix 1: Replace favicon icon in header with the proper JAC text logo (Untitled-design-2.png = JAC wordmark)
c = c.replace('cropped-Untitled_design__73_-removebg-preview-192x192.png', 'Untitled-design-2.png')

# Fix 2: Remove preloader completely — just show a simple ring
old_preloader = '<div class="preloader" id="preloader"><div class="loading-container"><div class="loading"></div><div id="loading-icon"><img src="https://jacauto.uz/wp-content/uploads/2024/08/tg_image_293401856-removebg-preview.png" alt="JAC" width="160"></div></div></div>'
new_preloader = '<div class="preloader" id="preloader"><div class="loader-ring"></div></div>'
c = c.replace(old_preloader, new_preloader)

with open('d:/jacauto-angren/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Header logo: JAC wordmark restored')
print('Preloader: simplified to ring only')
