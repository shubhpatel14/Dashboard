from app.data.history.fred_history import (
    fetch_fred_history
)

from app.database.repository import (
    save_macro_history
)

from app.data.history.transforms import (
    percent_change
)



SERIES = {


    "CPI_YOY": (
        "CPIAUCSL",
        12
    ),


    "CORE_CPI_YOY": (
        "CPILFESL",
        12
    ),


    "M2": (
        "M2SL",
        12
    ),


    "WALCL": (
        "WALCL",
        52
    ),



    "FEDFUNDS": (
        "FEDFUNDS",
        None
    ),


    "REAL_YIELD": (
        "DFII10",
        None
    ),


    "GDP": (
        "GDP",
        4
    ),

}




for name,item in SERIES.items():


    code, transform = item


    print(
        "Loading",
        name
    )


    rows = fetch_fred_history(
        code
    )


    if transform:


        rows = percent_change(
            rows,
            transform
        )



    save_macro_history(
        name,
        rows
    )



print(
    "DONE"
)