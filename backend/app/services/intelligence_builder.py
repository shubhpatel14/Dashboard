
from app.services.engine_registry import (
    MACRO_BUILDERS,
    ASSET_BUILDERS
)

from app.engines.macro.macro.scoring import (
    build_macro_engine
)

from app.services.intelligence_store import (
    save_macro_category,
    save_macro_dashboard,
    save_asset
)



def rebuild_intelligence():

    results = {}


    # ======================
    # MACRO CATEGORIES
    # ======================

    for name, builder in MACRO_BUILDERS.items():


        try:

            data = builder()


            if name == "macro":

                save_macro_dashboard(
                    data
                )


            else:

                save_macro_category(
                    name,
                    data
                )


            results[name]="saved"


        except Exception as e:

            results[name]=str(e)




    # ======================
    # ASSETS
    # ======================


    macro = build_macro_engine()


    for name,builder in ASSET_BUILDERS.items():


        try:


            data = builder(
                macro
            )


            save_asset(
                name,
                data
            )


            results[name]="saved"



        except Exception as e:

            results[name]=str(e)



    return results


