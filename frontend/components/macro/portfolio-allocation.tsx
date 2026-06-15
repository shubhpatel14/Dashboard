"use client";

export default function PortfolioAllocation({
  data,
}: {
  data:any;
}) {

  const portfolio =
    data?.portfolio_allocation;

  if (!portfolio?.allocation)
    return null;


  return (

    <div className="
      rounded-xl
      border
      border-line
      bg-surface
      p-5
    ">


      <div className="mb-4">

        <h2 className="
          text-lg
          font-semibold
        ">
          Portfolio Allocation
        </h2>


        <p className="
          text-sm
          text-muted
        ">
          {portfolio.explanation}
        </p>

      </div>



      <div className="space-y-3">

        {
          Object.entries(
            portfolio.allocation
          )
          .map(([asset,value]:any)=>(


            <div key={asset}>


              <div className="
                flex
                justify-between
                text-sm
              ">

                <span>
                  {asset}
                </span>

                <span>
                  {value}%
                </span>

              </div>



              <div className="
                mt-1
                h-2
                rounded-full
                bg-canvas
                overflow-hidden
              ">

                <div
                  className="
                    h-full
                    bg-terminal
                    rounded-full
                  "

                  style={{
                    width:
                    `${value}%`
                  }}
                />


              </div>


            </div>


          ))
        }

      </div>


    </div>

  );
}
