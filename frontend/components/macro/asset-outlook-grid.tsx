"use client";

import { formatLabel, formatNumber } from "@/lib/format";

export default function AssetOutlookGrid({
  data,
}: {
  data:any;
}) {

  const assets =
    data?.asset_outlooks;


  if (!assets)
    return null;


  return (

    <div className="
      rounded-xl
      border
      border-line
      bg-surface
      p-5
    ">


      <div className="mb-5">

        <h2 className="
        text-lg
        font-semibold
        ">
          Asset Macro Outlook
        </h2>


        <p className="
        text-sm
        text-muted
        ">
          Macro impact across asset classes
        </p>

      </div>



      <div className="
      grid
      gap-4
      md:grid-cols-2
      xl:grid-cols-3
      ">


      {Object.entries(assets)
      .map(([name,item]:any)=>(


        <div
        key={name}
        className="
        rounded-lg
        bg-canvas
        p-4
        "
        >


          <div className="
          flex
          justify-between
          ">


            <span className="
            font-medium
            ">
              {formatLabel(name)}
            </span>


            <span className="tabular-nums">
              {formatNumber(item.score)}
            </span>


          </div>



          <div className="
          mt-2
          h-2
          overflow-hidden
          rounded-full
          bg-black/20
          ">


            <div

            className="
            h-full
            rounded-full
            bg-terminal
            "

            style={{
              width:
              `${item.score}%`
            }}

            />


          </div>



          <div className="
          mt-3
          text-xs
          text-muted
          ">

            {formatLabel(item.bias)}

          </div>



          <div className="
          mt-3
          space-y-1
          text-xs
          text-muted
          ">


            {
              item.drivers
              ?.slice(0,2)
              .map(
              (driver:string)=>(

                <div key={driver}>

                  • {formatLabel(driver)}

                </div>

              ))

            }


          </div>


        </div>


      ))}


      </div>


    </div>

  );
}
