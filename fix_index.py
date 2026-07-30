html = open('d:/jacauto-angren/index-new.html', 'r', encoding='utf-8').read()
# index-new has "TEST NEW SITE" placeholder. Replace it with the full site.
# But index-new is only 604 bytes — it was the test file.
# Let me generate the full HTML here.

full_html = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JAC MOTORS ANGREN — Дистрибьютор JAC в Узбекистане</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
<div class="preloader" id="preloader"><div class="loader-ring"></div><div class="loader-logo">JAC MOTORS ANGREN</div></div>
<header class="header" id="header"><div class="container header-inner"><a href="#" class="logo"><span class="logo-text">JAC<span class="logo-accent">MOTORS</span><span class="logo-sub">ANGREN</span></span></a><nav class="nav" id="nav"><ul class="nav-list"><li><a href="#home" class="nav-link active">Главная</a></li><li><a href="#models" class="nav-link">Модели</a></li><li><a href="#about" class="nav-link">О нас</a></li><li><a href="#services" class="nav-link">Сервис</a></li><li><a href="#contact" class="nav-link">Контакты</a></li></ul></nav><div class="header-right"><a href="tel:+998781131008" class="header-phone"><i class="fas fa-phone-alt"></i> 78 113 10 08</a><button class="hamburger" id="hamburger"><span></span><span></span><span></span></button></div></div></header>
<script src="js/main.js"></script>
</body></html>'''

with open('d:/jacauto-angren/index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f'Wrote {len(full_html)} bytes')
