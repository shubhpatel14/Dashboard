from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict


from app.core.cache import (
    clear_cache,
)


from app.engines.macro.category_final_score import (
    build_category_final_score,
)


from app.services.macro_score_normalizer import (
    normalize_macro_scores,
)


from app.services.engine_registry import (
    MACRO_BUILDERS,
    get_macro_category,
    get_macro_engine,
    get_trend_engine,
    refresh_engine_cache,
)


from app.services.transformers import (
    MACRO_LABELS,
    clean_label,
    indicators_from_engine,
    macro_category_intelligence,
    macro_category_history,
    macro_summary,
)


from app.services.macro_interpreter import (
    build_macro_interpretation,
)


from app.engines.macro.macro_surprise.scoring import (
    build_macro_surprise,
)


from app.engines.assets.macro_impact import (
    macro_asset_impact,
)


from app.engines.assets.allocation import (
    build_allocation,
)


from app.engines.macro.regime.engine import (
    build_macro_regime,
)


from app.engines.macro.final_score import (
    build_final_macro_score,
)


from app.engines.macro.regime.history import (
    update_regime_history,
)


from app.services.intelligence_reader import (
    get_latest_macro,
    get_latest_category,
    get_all_assets,
    get_macro_history,
)


from app.services.intelligence_builder import (
    rebuild_intelligence,
)



router = APIRouter(
    prefix="/macro",
    tags=["macro"]
)


logger=logging.getLogger(__name__)




# ==================================================
# MODELS
# ==================================================

class MacroCategoryResponse(BaseModel):

    model_config=ConfigDict(
        extra="allow"
    )

    success:bool=True

    data_status:str="connected"

    name:str="Macro"

    score:float=50

    bias:str="Neutral"

    core_score:Optional[float]=None

    surprise_score:Optional[float]=None

    surprise_events:Any=[]

    trend:str="Stable"

    summary:Any=""

    interpretation:str=""

    explanation:str=""

    drivers:Any=[]

    indicators:Any=[]

    history:Any=[]

    data:Any=[]





class MacroDashboardResponse(BaseModel):

    model_config=ConfigDict(
        extra="allow"
    )

    success:bool=True




# ==================================================
# HELPERS
# ==================================================

def _safe_score(
    value,
    default=50
):

    try:

        return float(value)

    except Exception:

        return default





def _driver_dict(
    indicators
):

    result={}


    for i in indicators:

        result[
            i.get(
                "name",
                "Unknown"
            )
        ]={

            "score":

            i.get(
                "score",
                50
            )

        }


    return result






# ==================================================
# UPDATE
# ==================================================

@router.post(
    "/update-economic-data"
)
def update_economic_data():


    clear_cache()

    refresh_engine_cache()


    result=rebuild_intelligence()


    clear_cache()


    return {

        "status":"updated",

        "saved":result

    }






# ==================================================
# CATEGORY API
# ==================================================

@router.get(
    "/{category}",
    response_model=MacroCategoryResponse
)
def macro_category(
    category:str
):


    slug=(

        category.lower()
        .replace(
            "-",
            "_"
        )

    )


    # ==========================================
    # DATABASE MODE
    # ==========================================

    stored=get_latest_category(
        slug
    )


    if stored:


        raw=(

            stored.get(
                "indicators"
            )

            or

            stored.get(
                "data"
            )

            or {}

        )


        if isinstance(
            raw,
            dict
        ):

            raw=normalize_macro_scores(

                {
                    "data":raw
                }

            ).get(
                "data",
                raw
            )



        indicators=indicators_from_engine(

            {
                "data":raw
            }

        )



        interpretation=(

            stored.get(
                "interpretation"
            )

            or

            build_macro_interpretation(

                slug,

                stored.get(
                    "score",
                    50
                ),

                _driver_dict(
                    indicators
                )

            )

        )



        return {


            "success":True,

            "data_status":"database",


            "name":

            stored.get(
                "name",
                clean_label(slug)
            ),


            "score":

            round(
                float(
                    stored.get(
                        "score",
                        50
                    )
                ),
                2
            ),



            "bias":

            stored.get(
                "bias",
                "Neutral"
            ),



            "trend":

            stored.get(
                "trend",
                "Stable"
            ),



            "summary":

            stored.get(
                "summary",
                interpretation
            ),



            "interpretation":

            interpretation,



            "explanation":

            interpretation,



            "core_score":

            stored.get(
                "core_score",
                stored.get(
                    "score",
                    50
                )
            ),



            "surprise_score":

            stored.get(
                "surprise_score"
            ),



            "surprise_events":

            stored.get(
                "surprise_events",
                []
            ),



            "drivers":

            stored.get(
                "drivers",
                []
            ),



            "indicators":

            indicators,



            "data":

            indicators,



            "history":

            get_macro_history(
                slug
            ),

        }





    # ==========================================
    # ENGINE MODE
    # ==========================================

    if slug not in MACRO_BUILDERS:


        raise HTTPException(
            404,
            "Macro category not found"
        )



    engine=get_macro_category(
        slug
    ) or {}



    engine=normalize_macro_scores(
        engine
    )



    surprise=build_macro_surprise()



    engine=build_category_final_score(
        slug,
        engine,
        surprise
    )


    score=_safe_score(

        engine.get(
            "score"
        )

    )



    indicators=indicators_from_engine(
        engine
    )


    name=MACRO_LABELS.get(
        slug,
        clean_label(slug)
    )



    intelligence=macro_category_intelligence(

        name,

        score,

        engine.get(
            "bias",
            "Neutral"
        ),

        indicators

    )



    interpretation=(

        intelligence.get(
            "interpretation"
        )

        or

        build_macro_interpretation(

            slug,

            score,

            _driver_dict(
                indicators
            )

        )

    )



    return {


        "success":True,


        "data_status":"engine",


        "name":name,


        "score":score,


        "bias":

        engine.get(
            "bias",
            "Neutral"
        ),



        "core_score":

        engine.get(
            "core_score"
        ),



        "surprise_score":

        engine.get(
            "surprise_score"
        ),



        "surprise_events":

        engine.get(
            "surprise_events",
            []
        ),



        "trend":

        intelligence.get(
            "trend",
            "Stable"
        ),



        "summary":

        intelligence.get(
            "summary",
            interpretation
        ),



        "interpretation":

        interpretation,



        "explanation":

        interpretation,



        "drivers":

        intelligence.get(
            "drivers",
            []
        ),



        "indicators":

        indicators,



        "data":

        indicators,



        "history":

        macro_category_history(
            slug,
            score
        )

    }