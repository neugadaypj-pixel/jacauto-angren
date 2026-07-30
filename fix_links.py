import re
with open('d:/jacauto-angren/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace all onclick hrefs with car.html links
models = ['js8', 'js6', 'j7', 'q7', 'x200', 'm3']
for m in models:
    old_pattern = 'href="#" onclick="openDetail(\'' + m + '\')"'
    new_link = 'href="car.html?model=' + m + '"'
    c = c.replace(old_pattern, new_link)

print('Remaining openDetail:', c.count('openDetail'))
print('car.html links:', c.count('car.html'))

with open('d:/jacauto-angren/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done')
