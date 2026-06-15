"use client";


export default function RegimeTimeline({
 data,
}:{
 data:any
}){


 const history =
 data?.regime_history;


 if(!history)
 return null;



 return (


 <div className="
 rounded-xl
 border
 border-line
 bg-surface
 p-5
 ">


 <h2 className="
 text-lg
 font-semibold
 ">
 Regime Timeline
 </h2>



 <div className="
 mt-5
 flex
 items-center
 justify-between
 ">



 <div>

 <p className="
 text-sm
 text-muted
 ">
 Previous
 </p>

 <h3 className="
 font-bold
 ">
 {history.previous_regime}
 </h3>

 </div>




 <div className="
 text-muted
 ">
 →
 </div>




 <div>

 <p className="
 text-sm
 text-muted
 ">
 Current
 </p>

 <h3 className="
 font-bold
 ">
 {history.current_regime}
 </h3>

 </div>



 </div>



 <div className="
 mt-5
 text-sm
 text-muted
 ">


 Stable for {" "}

 <span className="
 font-semibold
 ">
 {history.days_in_regime}
 </span>

 {" "} days


 </div>




 <div className="
 mt-3
 ">


 {history.changed ? (

 <span className="
 text-orange-400
 ">
 Regime transition detected
 </span>


 ):(


 <span className="
 text-green-400
 ">
 No transition detected
 </span>


 )}


 </div>



 </div>


 );


}
