"use client";


export default function MacroSurpriseMonitor({
 data,
}:{
 data:any;
}){


 const events =
 data?.macro_surprises;


 if(!events || events.length===0)
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
 Economic Surprise Monitor
 </h2>


 <p className="
 text-sm
 text-muted
 ">
 Actual vs forecast economic releases
 </p>

 </div>




 <div className="
 overflow-x-auto
 ">


 <table className="
 w-full
 text-sm
 ">


 <thead>

 <tr className="
 text-muted
 border-b
 border-line
 ">

 <th className="text-left pb-2">
 Event
 </th>

 <th>
 Actual
 </th>

 <th>
 Forecast
 </th>

 <th>
 Previous
 </th>

 <th>
 Signal
 </th>


 </tr>

 </thead>




 <tbody>


 {events.map((e:any)=>(

 <tr
 key={e.name}
 className="
 border-b
 border-line/50
 "
 >

 <td className="
 py-3
 font-medium
 ">
 {e.name}
 </td>


 <td className="text-center">
 {e.actual}
 </td>


 <td className="text-center">
 {e.forecast}
 </td>


 <td className="text-center">
 {e.previous}
 </td>


 <td className="
 text-center
 font-semibold
 ">
 {e.bias}
 </td>


 </tr>


 ))}



 </tbody>


 </table>


 </div>



 </div>


 );


}
