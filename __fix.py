with open('d:/jacauto-angren/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

old = '<a href="#" class="logo"><span class="logo-jac">JAC</span><span class="logo-subtitle">MOTORS ANGREN</span></a>'
new = '<a href="#" class="logo"><img src="https://jacauto.uz/wp-content/uploads/2024/08/Untitled-design-2.png" alt="JAC" class="logo-dark"><img src="https://jacauto.uz/wp-content/uploads/2024/08/Untitled-design-2.png" alt="JAC" class="logo-light"></a>'

c = c.replace(old, new)

with open('d:/jacauto-angren/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('OLD found:', old in c)
print('logo-dark count:', c.count('logo-dark'))
print('logo-light count:', c.count('logo-light'))
