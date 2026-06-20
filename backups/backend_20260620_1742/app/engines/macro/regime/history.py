from __future__ import annotations

import json
import os

from datetime import datetime
from typing import Any



# =====================================
# STORAGE
# =====================================

BASE_DIR = os.path.dirname(
    __file__
)


FILE = os.path.join(
    BASE_DIR,
    "regime_history.json"
)



# =====================================
# HELPERS
# =====================================

def load_history() -> dict[str, Any]:


    if not os.path.exists(FILE):

        return {}


    try:

        with open(
            FILE,
            "r"
        ) as f:

            return json.load(f)


    except Exception:

        return {}




def save_history(
    data: dict[str, Any]
):


    with open(
        FILE,
        "w"
    ) as f:

        json.dump(
            data,
            f,
            indent=2
        )




def days_between(
    start
):


    try:

        old = datetime.fromisoformat(
            start
        )


        return (
            datetime.now()
            -
            old
        ).days


    except Exception:

        return 0





# =====================================
# CHANGE EXPLANATION ENGINE
# =====================================

def detect_changes(
    old: dict,
    new: dict
):


    changes = []


    old_inputs = old.get(
        "inputs",
        {}
    )


    new_inputs = new.get(
        "inputs",
        {}
    )



    for key in new_inputs:


        before = old_inputs.get(
            key
        )


        after = new_inputs.get(
            key
        )


        if before is None:

            continue



        diff = (
            after
            -
            before
        )


        if abs(diff) < 5:

            continue



        direction = (
            "improved"
            if diff > 0
            else "deteriorated"
        )


        changes.append(
            f"{key.title()} {direction}"
        )



    return changes





# =====================================
# MAIN ENGINE
# =====================================

def update_regime_history(
    current: dict[str, Any]
):


    old = load_history()



    now = datetime.now().isoformat()



    # FIRST RUN

    if not old:


        save_history(
            {
                **current,
                "started_at": now
            }
        )


        return {


            "previous_regime":
                None,


            "current_regime":
                current["regime"],


            "changed":
                False,


            "days_in_regime":
                0,


            "changes":
                []

        }




    old_regime = old.get(
        "regime"
    )


    new_regime = current.get(
        "regime"
    )



    changed = (
        old_regime
        !=
        new_regime
    )



    # regime changed

    if changed:


        changes = detect_changes(
            old,
            current
        )


        save_history(
            {
                **current,
                "started_at": now
            }
        )


        days = 0



    else:


        changes = []


        days = days_between(
            old.get(
                "started_at"
            )
        )




    return {


        "previous_regime":
            old_regime,


        "current_regime":
            new_regime,


        "changed":
            changed,


        "days_in_regime":
            days,


        "changes":
            changes

    }