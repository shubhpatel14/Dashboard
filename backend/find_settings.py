import os

for root, dirs, files in os.walk("app"):
    for f in files:
        if f.endswith(".py"):
            path=os.path.join(root,f)

            with open(path,"r",encoding="utf-8") as file:
                txt=file.read()

                if "BaseSettings" in txt:
                    print(path)
                    print("----------------")
                    for line in txt.splitlines():
                        if "BaseSettings" in line:
                            print(line)
                    print()

