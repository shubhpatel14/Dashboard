

from app.core.cache import cache



# ==================================
# Warm terminal cache
# ==================================


def warm_cache(
    dashboard=None
):


    if dashboard:


        cache.set(

        "macro_dashboard",

        dashboard

        )


    return True



