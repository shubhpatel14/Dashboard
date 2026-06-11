from pathlib import Path

path = Path("app/core/config.py")

text = path.read_text()


if "def app_name" not in text:

    text = text.replace(

        'def cache_ttl_seconds(self):\n\n        return self.CACHE_TTL_SECONDS',

        '''def cache_ttl_seconds(self):

        return self.CACHE_TTL_SECONDS


    @property
    def app_name(self):

        return self.APP_NAME'''

    )


path.write_text(text)

print("app_name compatibility added")

