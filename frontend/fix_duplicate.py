from pathlib import Path
import re

file = Path("app/layout.tsx")

text = file.read_text(encoding="utf-8")

text = re.sub(
    r"\nconst macroCategories = \[[\s\S]*?\];\n",
    "\n",
    text,
    count=1
)

file.write_text(
    text,
    encoding="utf-8"
)

print("duplicate macroCategories removed")
