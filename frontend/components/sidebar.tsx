"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  BarChart3,
  BriefcaseBusiness,
  CalendarDays,
  Database,
  Gauge,
  Globe2,
  Landmark,
  LineChart,
} from "lucide-react";

import clsx from "clsx";

import {
  assetLabels,
  assetSlugs,
  macroCategories,
} from "@/lib/api";



function NavLink({
  href,
  active,
  children,
}: {
  href: string;
  active?: boolean;
  children: React.ReactNode;
}) {


  return (

    <Link

      href={href}

      className={clsx(

        "flex h-8 items-center gap-2 border px-2 text-sm transition-colors",

        active
          ? "border-ink bg-ink text-white dark:bg-terminal dark:text-canvas"
          : "border-transparent text-muted hover:border-line hover:bg-canvas hover:text-ink"

      )}

    >

      {children}

    </Link>

  );

}



export function Sidebar() {


  const [
    location,
    setLocation
  ] = useState({

    pathname: "",

    selectedMacro: "liquidity",

  });



  useEffect(() => {


    function syncLocation() {


      const params =
        new URLSearchParams(
          window.location.search
        );


      setLocation({

        pathname:
          window.location.pathname,


        selectedMacro:
          params.get("category")
          ?? "liquidity",

      });


    }


    syncLocation();


    window.addEventListener(
      "popstate",
      syncLocation
    );


    return () =>
      window.removeEventListener(
        "popstate",
        syncLocation
      );


  },[]);



  const {
    pathname,
    selectedMacro
  } = location;



  return (


    <aside className="border-r border-line bg-surface p-4">



      {/* LOGO */}

      <div className="border-b border-line p-4">


        <div className="flex h-50 items-center justify-center rounded-xl border border-line bg-white p-3">


          <img

            src="/logo.png"

            alt="Trishula Capital"

            className="h-full w-full object-contain scale-[1.6]"

          />


        </div>


      </div>




      <nav className="space-y-5">



        {/* DASHBOARD */}

        <div>


          <NavLink
            href="/"
            active={pathname === "/"}
          >

            <BarChart3 className="h-4 w-4" />

            Dashboard


          </NavLink>


        </div>





        {/* MACRO */}

        <div>


          <div className="mb-2 border-t border-line pt-4 text-xs font-semibold uppercase text-muted">


            Macro Intelligence


          </div>



          <div className="space-y-1">



            {/* <NavLink

              href="/macro"

              active={
                pathname === "/macro"
                &&
                selectedMacro === "liquidity"
              }

            >


              <Gauge className="h-4 w-4" />

              Overview


            </NavLink> */}




            {macroCategories.map(
              ([label, slug]) => (


              <NavLink

                key={slug}

                href={`/macro?category=${slug}`}

                active={
                  pathname === "/macro"
                  &&
                  selectedMacro === slug
                }

              >


                {
                  slug === "global_liquidity"
                  ?

                  <Globe2 className="h-4 w-4" />

                  :

                  <Gauge className="h-4 w-4" />
                }



                {
                  label === "Labor"
                  ? "Labor Market"

                  : label === "Recession"
                  ? "Recession Monitor"

                  : label
                }



              </NavLink>


            ))}


          </div>


        </div>





        {/* ECONOMIC CALENDAR */}

        <div>


          <div className="mb-2 border-t border-line pt-4 text-xs font-semibold uppercase text-muted">

            Macro Events

          </div>



          <NavLink

            href="/calendar"

            active={
              pathname === "/calendar"
            }

          >


            <CalendarDays className="h-4 w-4" />


            Economic Calendar


          </NavLink>



        </div>







        {/* MARKET */}

        <div>


          <div className="mb-2 border-t border-line pt-4 text-xs font-semibold uppercase text-muted">


            Market Intelligence


          </div>




          <div className="space-y-1">



            {/* <NavLink
              href="/"
              active={false}
            >


              <LineChart className="h-4 w-4" />


              Asset Dashboard


            </NavLink> */}


            {assetSlugs.map(
              (slug)=>(


              <NavLink

                key={slug}

                href={`/asset/${slug}`}

                active={
                  pathname === `/asset/${slug}`
                }

              >


                <LineChart className="h-4 w-4" />


                {
                  slug === "bitcoin"
                  ? "Crypto"
                  : assetLabels[slug]
                }



              </NavLink>


            ))}


          </div>


        </div>






        {/* INSTITUTION */}

        <div>



          <div className="mb-2 border-t border-line pt-4 text-xs font-semibold uppercase text-muted">


            Institutional Positioning


          </div>




          <NavLink

            href="/institutional"

            active={
              pathname === "/institutional"
            }

          >


            <Landmark className="h-4 w-4" />


            CFTC Positioning



          </NavLink>




        </div>



      </nav>





      {/* FOOTER */}

      <div className="mt-8 border-t border-line pt-4 text-xs text-muted">



        <div className="mb-2 flex items-center gap-2">


          <Database className="h-4 w-4" />


          PostgreSQL ready


        </div>




        <div className="flex items-center gap-2">


          <BriefcaseBusiness className="h-4 w-4" />


          Cached FastAPI


        </div>



      </div>




    </aside>


  );


}