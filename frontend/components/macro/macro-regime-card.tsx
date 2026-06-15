"use client";

export default function MacroRegimeCard({
  data,
}: {
  data: any;
}) {

  if (!data?.regime_detail) return null;


  const regime = data.regime_detail;


  return (

    <div className="
      rounded-xl
      border
      border-neutral-800
      bg-neutral-950
      p-5
    ">


      <div className="flex justify-between">

        <div>

          <p className="text-sm text-neutral-400">
            Current Regime
          </p>


          <h2 className="
            text-2xl
            font-bold
            text-orange-400
          ">
            {regime.regime}
          </h2>


        </div>


        <div className="text-right">

          <p className="text-sm text-neutral-400">
            Confidence
          </p>

          <p className="text-xl font-bold">
            {regime.confidence}%
          </p>

        </div>

      </div>



      <p className="mt-4 text-neutral-300">

        {regime.description}

      </p>




      <div className="
        grid
        grid-cols-5
        gap-3
        mt-5
      ">

        {Object.entries(
          regime.inputs ?? {}
        ).map(([key,value]) => (

          <div
            key={key}
            className="
            bg-neutral-900
            rounded-lg
            p-3
            "
          >

            <p className="
              text-xs
              capitalize
              text-neutral-500
            ">
              {key}
            </p>


            <p className="
              text-lg
              font-semibold
            ">
              {String(value)}
            </p>


          </div>

        ))}

      </div>


    </div>
  );
}