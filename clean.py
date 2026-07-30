import re

with open('d:/jacauto-angren/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix 1: Remove empty rule blocks — }{} becomes }
# This is the "selector expected" error
before = c.count('}{}')
c = re.sub(r'\}\{\}', '}', c)
after = c.count('}{}')
print(f'Empty {{}} blocks removed: {before - after}')

# Fix 2: Also remove any dangling empty blocks like {} at rule boundaries
before2 = c.count('{}')
c = c.replace('{}', '')
after2 = c.count('{}')
print(f'Empty {{}} removed: {before2 - after2}')

# Fix 3: Clean up any double } from above fixes
before3 = c.count('}}')
c = c.replace('}}', '}')
after3 = c.count('}}')
print(f'Double }} fixed: {before3 - after3}')

with open('d:/jacauto-angren/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print(f'Final size: {len(c)} chars')
