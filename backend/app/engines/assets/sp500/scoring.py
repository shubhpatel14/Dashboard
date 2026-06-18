from app.engines.assets.scorecard import (
    build_scorecard
)




def build_sp500_score(
    macro
):


    score = (


        # liquidity drives multiples

        macro["liquidity"]
        *
        0.35


        +


        # earnings cycle

        macro["growth"]
        *
        0.30


        +


        # credit conditions

        macro["credit"]
        *
        0.20


        +


        # rates pressure

        macro["rates"]
        *
        0.15


    )




    return build_scorecard(


        asset=
            "S&P 500",


        score=
            score,


        drivers={


            "liquidity":

                macro["liquidity"],


            "growth":

                macro["growth"],


            "credit":

                macro["credit"],


            "rates":

                macro["rates"]


        }


    )



def build_sp500_engine(macro):

    return build_sp500_score(macro)

