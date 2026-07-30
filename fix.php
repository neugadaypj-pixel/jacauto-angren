<?php
$file = 'd:/jacauto-angren/index.html';
$c = file_get_contents($file);

// Fix the dirty charset
$c = preg_replace('/<meta charset[^>]*>/', '', $c);
$c = str_replace('<head>', '<head><meta charset="UTF-8">', $c);

// Remove trailing whitespace before </body>
$c = preg_replace('/\s+<\/body>/', '</body>', $c);

// Remove empty lines at end
$c = rtrim($c) . "\n";

file_put_contents($file, $c);
echo "Fixed. Charset now at position: " . strpos($c, 'meta charset') . "\n";
echo "File size: " . strlen($c) . " chars\n";
