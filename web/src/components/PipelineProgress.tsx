const stages=["retrieving","generating","extracting_claims","verifying","checking_attributions"];
const labels=["Retrieving verses","Generating answer","Extracting claims","Verifying","Checking attributions"];
export function PipelineProgress({active,loading}:{active?:string;loading:boolean}) { if(!loading&&!active)return null; const position=Math.max(0,stages.indexOf(active||"retrieving")); return <ol className="pipeline" aria-label="Pipeline progress">{labels.map((label,index)=><li className={index<=position?"complete":""} key={label}><i/>{label}</li>)}</ol>; }
