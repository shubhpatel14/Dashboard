from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict


from app.core.cache import (
    cached,
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



# ==================================
# DATABASE INTELLIGENCE
# ==================================

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


logger = logging.getLogger(
    __name__
)




# ==================================
# RESPONSE MODELS
# ==================================

class MacroDashboardResponse(BaseModel):

    model_config = ConfigDict(
        extra="allow"
    )


    success: bool=True

    data_status:str="connected"

    macro_score:float=50

    regime:str="Neutral"

    regime_detail:dict[str,Any]={}

    regime_history:dict[str,Any]={}

    trend:str="Neutral"

    summary:list[str]=[]

    asset_outlooks:dict[str,Any]={}

    portfolio_allocation:dict[str,Any]={}

    macro_surprises:list[dict[str,Any]]=[]

    category_scores:dict[str,Any]={}

    history:list[dict[str,Any]]=[]




class MacroCategoryResponse(BaseModel):

    model_config = ConfigDict(
        extra="allow"
    )


    success: bool = True

    data_status: str = "connected"

    name: str = "Macro"

    score: float = 50

    bias: str = "Neutral"

    core_score: Optional[float] = None

    surprise_score: Optional[float] = None


    surprise_events: Any = []


    trend: str = "Stable"


    summary: Any = ""


    drivers: Any = []


    indicators: Any = []


    explanation: str = ""


    history: Any = []


    data: Any = []



# ==================================
# HELPERS
# ==================================

def _safe_score(
    value,
    default=50
):

    try:

        return float(
            value
        )

    except Exception:

        return default





def _empty_category(
    slug,
    message=""
):

    return {


        "success":True,

        "data_status":"fallback",

        "name":MACRO_LABELS.get(
            slug,
            clean_label(slug)
        ),


        "score":50,


        "bias":"Neutral",


        "summary":message,


        "drivers":[],


        "indicators":[],


        "history":[
            {
            "date":"Current",
            "score":50
            }
        ],

        "data":[]

    }






# ==================================
# UPDATE DATA
# ==================================

@router.post(
    "/update-economic-data"
)
def update_economic_data():


    clear_cache()


    refresh_engine_cache()



    result = rebuild_intelligence()



    clear_cache()



    return {


        "status":"updated",


        "message":

        "Economic data refreshed and intelligence database rebuilt",



        "saved":

        result

    }







# ==================================
# DASHBOARD
# ==================================

@router.get(
    "/dashboard",
    response_model=MacroDashboardResponse
)
def macro_dashboard():


    # =========================
    # DATABASE FAST PATH
    # =========================

    stored = get_latest_macro()


    if stored:


        score = stored.get(
            "score",
            stored.get(
                "macro_score",
                50
            )
        )


        return {


            "success": True,


            "data_status": "database",



            "macro_score": score,



            "regime":

                stored.get(
                    "risk_status",
                    "Neutral"
                ),



            "regime_detail": {


                "regime":

                    stored.get(
                        "risk_status",
                        "Neutral"
                    ),


                "confidence":

                    score

            },



            "regime_history": {},



            "trend":

                stored.get(
                    "bias",
                    "Neutral"
                ),



            "risk_status":

                stored.get(
                    "risk_status",
                    "Neutral"
                ),



            "category_scores":

                stored.get(
                    "scores",
                    {}
                ),



            "categories":

                stored.get(
                    "categories",
                    {}
                ),



           "asset_outlooks":

            get_all_assets(),


            "portfolio_allocation":

                stored.get(
                    "portfolio_allocation",
                    {}
                ),



            "macro_surprises":

                stored.get(
                    "macro_surprises",
                    []
                ),



            "summary":[

                "Macro intelligence loaded from PostgreSQL"

            ],



            "history":[

                {

                    "date":"Current",

                    "score":score

                }

            ],



            "raw":stored

        }






    # =========================
    # ENGINE FALLBACK
    # =========================

    try:


        macro = get_macro_engine() or {}


        trend = get_trend_engine() or {}


        surprise = build_macro_surprise()



        final_macro = build_final_macro_score(
            macro,
            surprise
        )


        score = final_macro[
            "score"
        ]



        asset_scores = macro_asset_impact(
            surprise,
            macro
        )



        regime_detail = build_macro_regime(
            macro
        )



        regime_history = update_regime_history(
            regime_detail
        )



        portfolio = build_allocation(
            asset_scores,
            regime_detail
        )



        return {


            "success":True,


            "data_status":"engine",


            "macro_score":score,


            "regime":

                regime_detail.get(
                    "regime",
                    "Neutral"
                ),


            "regime_detail":

                regime_detail,


            "regime_history":

                regime_history,


            "trend":

                clean_label(
                    trend.get(
                        "trend",
                        "Neutral"
                    )
                ),



            "summary":

                macro_summary(
                    macro
                ),



            "asset_outlooks":

                asset_scores,



            "portfolio_allocation":

                portfolio,



            "macro_surprises":

                surprise.get(
                    "events",
                    []
                ),



            "category_scores":

                macro.get(
                    "scores",
                    {}
                ),



            "history":

                macro_category_history(
                    "trend",
                    score
                )

        }



    except Exception as e:


        logger.exception(e)


        return {

            "success":False,

            "data_status":"error",

            "macro_score":50

        }
# ==================================
# CATEGORY
# ==================================

@router.get(
    "/{category}",
    response_model=MacroCategoryResponse
)
def macro_category(
    category:str
):


    slug=(

        category.lower()
        .replace("-","_")

    )

     # DATABASE FIRST

    stored = get_latest_category(
        slug
    )


    if stored:


        raw_data = (

            stored.get(
                "indicators"
            )

            or

            stored.get(
                "data"
            )

            or

            stored.get(
                "components"
            )

            or {}

        )


        indicators = []


        if isinstance(
            raw_data,
            dict
        ):


            for key, value in raw_data.items():


                item = dict(
                    value
                )


                item[
                    "name"
                ] = key


                item[
                    "indicator"
                ] = key 


                item["percentile"] = item.get(
                    "percentile",
                    50
                )


                item["z_score"] = item.get(
                    "z_score",
                    0
                )


                item["distance_average"] = item.get(
                    "distance_average",
                    item.get(
                        "distance_avg",
                        0
                    )
                )

                indicators.append(
                    item
                )


        elif isinstance(
            raw_data,
            list
        ):


            indicators = raw_data



        return {


            "success": True,


            "data_status": "database",


            "name":

                stored.get(
                    "name",
                    clean_label(slug)
                ),


            "score":

                stored.get(
                    "score",
                    50
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

            "summary":

                stored.get(
                    "summary",
                    ""
                ),


            "explanation":

                stored.get(
                    "explanation",
                    ""
                ),

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
                    "surprise_score",
                    50
                ),


            "raw":

                stored

        }


    # ENGINE FALLBACK

    # ENGINE FALLBACK

    if slug not in MACRO_BUILDERS:


        raise HTTPException(

            status_code=404,

            detail="Macro category not found"

        )




    try:


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



        "drivers":

            intelligence[
            "drivers"
            ],


        "summary":

            intelligence[
            "summary"
            ],


        "indicators":

            indicators,


        "history":

            macro_category_history(
            slug,
            score
            ),


        "data":

            indicators

        }




    except Exception as e:


        return _empty_category(
            slug,
            str(e)
        )