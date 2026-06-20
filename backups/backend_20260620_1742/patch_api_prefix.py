from pathlib import Path

path = Path("app/core/config.py")

text = path.read_text()


if "def api_prefix" not in text:

    text = text.replace(

        'def app_name(self):\n\n        return self.APP_NAME',

        '''def app_name(self):

        return self.APP_NAME


    @property
    def api_prefix(self):

        return "/api"'''

    )


path.write_text(text)

print("api_prefix compatibility added")

