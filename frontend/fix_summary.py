from pathlib import Path

file = Path("app/page.tsx")

text = file.read_text(encoding="utf-8")


old = """{macro.summary.map((line) => ("""

new = """{(Array.isArray(macro.summary) ? macro.summary : [macro.summary]).map((line) => ("""


text = text.replace(old,new)


file.write_text(
    text,
    encoding="utf-8"
)

print("macro summary fixed")
