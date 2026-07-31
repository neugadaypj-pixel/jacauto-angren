models = [
    ("crossovers", "JAC JS8", "313 650 000 сум", "js8"),
    ("crossovers", "JAC T8", "330 330 000 сум", "t8"),
    ("crossovers", "JAC T9", "419 265 000 сум", "t9"),
    ("sedans", "JAC J7", "235 000 000 сум", "j7"),
    ("sedans", "JAC RF8", "444 675 000 сум", "rf8"),
    ("commercial", "JAC X200 БОРТОВОЙ", "248 640 000 сум", "x200b"),
    ("commercial", "JAC X200 ТЕНТОВКА", "255 360 000 сум", "x200t"),
    ("commercial", "JAC X200 ПРОМТОВАРНЫЙ", "275 520 000 сум", "x200p"),
    ("commercial", "JAC M3 VAN", "209 034 000 сум", "m3"),
    ("commercial", "JAC M3 Luxe", "226 233 000 сум", "m3l"),
    ("commercial", "JAC M4 REFINE", "255 339 000 сум", "m4"),
    ("commercial", "SUNRAY VAN", "383 670 000 сум", "sunrayv"),
    ("commercial", "SUNRAY BUS", "416 745 000 сум", "sunrayb"),
]

for cat, name, price, slug in models:
    icon = "fa-truck" if cat == "commercial" else "fa-car"
    link = f"car.html?model={slug}"
    print(f"<div class=\"model-card\" data-cat=\"{cat}\"><div class=\"model-img\"><div class=\"model-placeholder\"><i class=\"fas {icon}\"></i></div></div><div class=\"model-info\"><h3>{name}</h3><p>{price}</p><a href=\"{link}\" class=\"model-link\">Подробнее <i class=\"fas fa-arrow-right\"></i></a></div></div>")
