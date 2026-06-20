import os
import importlib

errors=[]

for root,dirs,files in os.walk("app"):

    dirs[:] = [
        d for d in dirs
        if d != "__pycache__"
    ]

    for f in files:

        if f.endswith(".py"):

            path=os.path.join(root,f)

            module = (
                path[:-3]
                .replace("\\",".")
                .replace("/",".")
            )

            try:

                importlib.import_module(module)

                print("?",module)

            except Exception as e:

                print("?",module)
                print(e)
                errors.append((module,e))


print()
print("================")
print("Errors:",len(errors))
print("================")

for x in errors:
    print(x)

