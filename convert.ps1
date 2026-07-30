$c = Get-Content "d:/jacauto-angren/jacauto-clone.html" -Raw -Encoding UTF8;

Write-Output ("Original size: " + $c.Length + " chars");

# Replace branding
$c = $c -replace "JAC АВТОСАЛОН", "JAC MOTORS ANGREN";
$c = $c -replace "JAC автосалон", "JAC MOTORS ANGREN";
$c = $c -replace "JAC - JAC MOTORS ANGREN", "JAC MOTORS ANGREN";

# Fix meta tags
$c = $c -replace '<title>.*?</title>', '<title>JAC MOTORS ANGREN — Официальный дистрибьютор JAC</title>';
$c = $c -replace '<meta property="og:title" content="[^"]*"', '<meta property="og:title" content="JAC MOTORS ANGREN"';
$c = $c -replace '<meta property="og:site_name" content="[^"]*"', '<meta property="og:site_name" content="JAC MOTORS ANGREN"';
$c = $c -replace '<meta name="description" content="[^"]*"', '<meta name="description" content="JAC MOTORS ANGREN — Официальный дистрибьютор автомобилей марки JAC в Узбекистане."';
$c = $c -replace '<meta property="og:description" content="[^"]*"', '<meta property="og:description" content="JAC MOTORS ANGREN — Официальный дистрибьютор автомобилей марки JAC в Узбекистане."';

# Remove canonical, yoast schema, litespeed cache comments, speculation rules, translatepress template
$c = $c -replace '<link rel="canonical" href="[^"]*" */?>', '';
$c = $c -replace '<script type="application/ld\+json" class="yoast-schema-graph">.*?</script>', '';
$c = $c -replace '<!-- Page cached by LiteSpeed Cache.*?-->', '';
$c = $c -replace '<!-- Page optimized by LiteSpeed Cache.*?-->', '';
$c = $c -replace '<script type="speculationrules">.*?</script>', '';
$c = $c -replace '<template id="tp-language".*?</template>', '';
$c = $c -replace '<script.*?litespeed.*?</script>', '';

# Remove elementor-device-mode span
$c = $c -replace '<span id="elementor-device-mode".*?</span>', '';

Write-Output ("New size: " + $c.Length + " chars");
[System.IO.File]::WriteAllText("d:/jacauto-angren/index.html", $c, [System.Text.UTF8Encoding]::new($false));
Write-Output "Done - index.html written";
