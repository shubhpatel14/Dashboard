from pathlib import Path

path=Path("app/core/config.py")

text=path.read_text()


if "cache_ttl_seconds" not in text:

    text=text.replace(

        'REDIS_URL: str = "redis://localhost:6379"',

        '''REDIS_URL: str = "redis://localhost:6379"


    CACHE_TTL_SECONDS: int = 300


    @property
    def cache_ttl_seconds(self):

        return self.CACHE_TTL_SECONDS'''

    )


path.write_text(text)


print("config patched")

