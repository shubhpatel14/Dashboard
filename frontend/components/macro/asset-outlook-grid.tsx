"use client";

import { formatLabel, formatNumber } from "@/lib/format";


export default function AssetOutlookGrid({
  data,
}: {
  data:any;
}) {


  const assets = Object.values(
    data?.asset_outlooks || {}
  );


  if (!assets.length)
    return null;



  return (

    <div
    className="
    rounded-xl
    border
    border-line
    bg-surface
    p-5
    "
    >


      <div className="mb-5">

        <h2
        className="
        text-lg
        font-semibold
        "
        >
          Asset Macro Outlook
        </h2>


        <p
        className="
        text-sm
        text-muted
        "
        >
          Macro impact across asset classes
        </p>

      </div>



      <div
      className="
      grid
      gap-4
      md:grid-cols-2
      xl:grid-cols-3
      "
      >


      {
      assets.map((item:any)=>(


        <div
        key={item.asset}
        className="
        rounded-lg
        bg-canvas
        p-4
        "
        >


          <div
          className="
          flex
          justify-between
          "
          >


            <span
            className="
            font-medium
            "
            >

              {formatLabel(
                item.asset
              )}

            </span>



            <span
            className="
            tabular-nums
            "
            >

              {
              formatNumber(
                item.asset_score ??
                item.score ??
                50
              )
              }

            </span>


          </div>



          <div
          className="
          mt-2
          h-2
          overflow-hidden
          rounded-full
          bg-black/20
          "
          >


            <div

            className="
            h-full
            rounded-full
            bg-terminal
            "


            style={{

              width:
              `${
              item.asset_score ??
              item.score ??
              50
              }%`

            }}

            />


          </div>




          <div
          className="
          mt-3
          text-xs
          text-muted
          "
          >

            Bias:
            {" "}
            {formatLabel(
              item.bias
            )}

          </div>



          <div
          className="
          mt-3
          space-y-1
          text-xs
          text-muted
          "
          >


            <div>

            🟢 Bullish

            </div>


            {
            item.bullish_drivers
            ?.slice(0,2)
            .map(
            (d:any)=>(


              <div
              key={d.name}
              >

              + {formatLabel(d.name)}
              ({formatNumber(d.score)})

              </div>

            ))
            }



            <div
            className="pt-2"
            >

            🔴 Bearish

            </div>



            {
            item.bearish_drivers
            ?.slice(0,2)
            .map(
            (d:any)=>(


              <div
              key={d.name}
              >

              - {formatLabel(d.name)}
              ({formatNumber(d.score)})

              </div>

            ))
            }



          </div>



        </div>


      ))
      }


      </div>


    </div>

  );

}