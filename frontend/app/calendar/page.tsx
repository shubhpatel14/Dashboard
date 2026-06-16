"use client";

import { useEffect, useState } from "react";


type CalendarEvent = {

  date?: string;
  time?: string;
  country?: string;

  event: string;

  importance?: string;

  actual?: string | number | null;
  forecast?: string | number | null;
  previous?: string | number | null;

  source?: string;

};



export default function CalendarPage() {


  const [data,setData] =
    useState<any>(null);


  const [impact,setImpact] =
    useState("All");


  const [dateFilter,setDateFilter] =
    useState("All");


  const [fromDate,setFromDate] =
    useState("");


  const [toDate,setToDate] =
    useState("");





  useEffect(()=>{


    fetch(
      "http://127.0.0.1:8000/calendar"
    )
      .then(
        r=>r.json()
      )
      .then(
        setData
      );


  },[]);






  if(!data){


    return (

      <main className="p-6">

        Loading Economic Calendar...

      </main>

    );

  }







  let rows:CalendarEvent[] = [

    ...(data.upcoming || []),

    ...(data.released || [])

  ];





  // =========================
  // FILTERS
  // =========================


  const today =
    new Date();


  const tomorrow =
    new Date();


  tomorrow.setDate(
    today.getDate()+1
  );





  rows = rows.filter(
    (e)=>{


      // impact filter

      if(
        impact !== "All" &&
        e.importance !== impact
      ){

        return false;

      }




      if(
        !e.date
      ){

        return false;

      }



      const d =
        new Date(
          e.date
        );





      if(
        dateFilter === "Today"
      ){


        return (
          d.toDateString()
          ===
          today.toDateString()
        );

      }





      if(
        dateFilter === "Tomorrow"
      ){


        return (
          d.toDateString()
          ===
          tomorrow.toDateString()
        );

      }






      if(
        dateFilter === "Custom"
      ){


        if(
          fromDate &&
          d < new Date(fromDate)
        ){

          return false;

        }



        if(
          toDate &&
          d > new Date(toDate)
        ){

          return false;

        }


      }




      return true;


    }
  );








  const impactStars = (
    impact?:string
  )=>{


    if(
      impact==="High"
    ){

      return "★★★";

    }



    if(
      impact==="Medium"
    ){

      return "★★";

    }



    return "★";


  };










  return (


    <main className="space-y-5">



      {/* HEADER */}


      <header>


        <p className="text-xs font-semibold uppercase text-muted">

          TRISHULA CAPITAL TERMINAL

        </p>


        <h1 className="text-2xl font-bold">

          Economic Calendar

        </h1>



        <p className="text-sm text-muted">

          Live macro events powered by Investing.com

        </p>


      </header>









      {/* SUMMARY */}


      <div className="grid grid-cols-3 gap-4">



        <div className="rounded-xl border border-line bg-panel p-4">

          <p className="text-xs text-muted">
            Total Events
          </p>

          <h2 className="text-xl font-bold">

            {rows.length}

          </h2>

        </div>




        <div className="rounded-xl border border-line bg-panel p-4">

          <p className="text-xs text-muted">
            Filter
          </p>

          <h2 className="text-xl font-bold">

            {impact}

          </h2>

        </div>




        <div className="rounded-xl border border-line bg-panel p-4">

          <p className="text-xs text-muted">
            Source
          </p>

          <h2 className="text-xl font-bold">

            Investing.com

          </h2>

        </div>



      </div>









      {/* FILTER BAR */}


      <div className="flex flex-wrap gap-3 rounded-xl border border-line bg-panel p-4">



        <select

          value={impact}

          onChange={
            e=>setImpact(e.target.value)
          }

          className="rounded border bg-background p-2"
        >


          <option>All</option>

          <option>High</option>

          <option>Medium</option>

          <option>Low</option>


        </select>






        <select

          value={dateFilter}

          onChange={
            e=>setDateFilter(e.target.value)
          }

          className="rounded border bg-background p-2"

        >


          <option>All</option>

          <option>Today</option>

          <option>Tomorrow</option>

          <option>Custom</option>


        </select>







        {
          dateFilter==="Custom" && (

            <>


              <input

                type="date"

                value={fromDate}

                onChange={
                  e=>setFromDate(e.target.value)
                }

                className="rounded border bg-background p-2"

              />




              <input

                type="date"

                value={toDate}

                onChange={
                  e=>setToDate(e.target.value)
                }

                className="rounded border bg-background p-2"

              />


            </>

          )
        }



      </div>









      {/* TABLE */}


      <section className="overflow-hidden rounded-xl border border-line bg-panel">


        <table className="w-full text-sm">



          <thead className="border-b border-line bg-background">


          <tr>

            <th className="p-3 text-left">Date</th>

            <th className="p-3 text-left">Time</th>

            <th className="p-3 text-left">Country</th>

            <th className="p-3 text-left">Event</th>

            <th className="p-3 text-center">Impact</th>

            <th className="p-3 text-right">Actual</th>

            <th className="p-3 text-right">Forecast</th>

            <th className="p-3 text-right">Previous</th>

          </tr>


          </thead>






          <tbody>


          {rows.map(
            (e,index)=>(


            <tr

              key={index}

              className="border-b border-line hover:bg-background"

            >


              <td className="p-3 text-muted">

                {e.date}

              </td>



              <td className="p-3">

                {e.time}

              </td>




              <td className="p-3">

                🇺🇸 {e.country}

              </td>





              <td className="p-3 font-medium">

                {e.event}


                <div className="text-xs text-muted">

                  {e.source}

                </div>


              </td>






              <td className="p-3 text-center">


                <span

                  className={
                    e.importance==="High"
                    ?"text-red-500"
                    :"text-orange-400"
                  }

                >

                  {impactStars(e.importance)}

                </span>


              </td>






              <td className="p-3 text-right font-semibold">

                {e.actual ?? "-"}

              </td>




              <td className="p-3 text-right">

                {e.forecast ?? "-"}

              </td>




              <td className="p-3 text-right text-muted">

                {e.previous ?? "-"}

              </td>




            </tr>


          ))}



          </tbody>


        </table>


      </section>



    </main>


  );

}