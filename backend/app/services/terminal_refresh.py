
from app.services.snapshot_service import (
save_macro_snapshot
)

from app.services.engine_registry import (
build_dashboard
)


def refresh_terminal():

    data = build_dashboard()

    save_macro_snapshot(data)


    return {

    "status":"updated",

    "macro_score":
    data.get(
    "macro_score"
    )

    }


