from pathlib import Path

path = Path("app/services/engine_registry.py")

text = path.read_text(encoding="utf-8")


replacements = {

"from engines.bitcoin import":
"from app.engines.assets.bitcoin.scoring import",

"from engines.gold import":
"from app.engines.assets.gold.scoring import",

"from engines.sp500 import":
"from app.engines.assets.sp500.scoring import",

"from engines.nasdaq import":
"from app.engines.assets.nasdaq.scoring import",

"from engines.dollar import":
"from app.engines.assets.dollar.scoring import",

"from engines.bonds import":
"from app.engines.assets.bonds.scoring import",


"from engines.inflation import":
"from app.engines.macro.inflation.scoring import",

"from engines.labor import":
"from app.engines.macro.labor.scoring import",

"from engines.liquidity import":
"from app.engines.macro.liquidity.scoring import",

"from engines.growth import":
"from app.engines.macro.growth.scoring import",

"from engines.rates import":
"from app.engines.macro.rates.scoring import",

"from engines.recession import":
"from app.engines.macro.recession.scoring import",

}


for old,new in replacements.items():
    text=text.replace(old,new)


path.write_text(text,encoding="utf-8")


print("engine registry fixed")
