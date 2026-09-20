'use strict';
const samples={clean:{as_of:'2026-09-19',rows:[{asset:'DEMO',date:'2026-09-18',acquired_on:'2026-09-19',close:100}]},issues:{as_of:'2026-09-19',rows:[{asset:'DEMO',date:'2026-09-18',acquired_on:'2026-09-19',close:100},{asset:'DEMO',date:'2026-09-18',acquired_on:'2026-09-19',close:101},{asset:'OTHER',date:'2026-09-20',acquired_on:'2026-09-19',close:-5}]}};
function validDate(v){return typeof v==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(v)&&Number.isFinite(Date.parse(v))&&new Date(v).toISOString().slice(0,10)===v;}
function validate(payload){
 if(!payload||Array.isArray(payload)||!Array.isArray(payload.rows))throw Error('Expected an object containing rows');
 if(payload.rows.length<1||payload.rows.length>1000)throw Error('Expected 1–1000 rows');
 if(!validDate(payload.as_of))throw Error('as_of must be a valid YYYY-MM-DD date');
 const seen=new Set(),issues=[];
 payload.rows.forEach((row,index)=>{const codes=[];
  if(!row||typeof row!=='object'||Array.isArray(row)){issues.push({row:index,codes:['invalid_row']});return;}
  if(typeof row.asset!=='string'||!row.asset.trim()||[...row.asset].length>32)codes.push('invalid_asset');
  if(typeof row.close!=='number'||!Number.isFinite(row.close)||row.close<=0)codes.push('invalid_close');
  if(!validDate(row.date)||!validDate(row.acquired_on))codes.push('invalid_date');
  else {if(row.date>row.acquired_on||row.acquired_on>payload.as_of)codes.push('invalid_temporal_order');
   if(typeof row.asset==='string'){const key=JSON.stringify([row.asset,row.date]);if(seen.has(key))codes.push('duplicate_asset_date');seen.add(key);}}
  if(codes.length)issues.push({row:index,codes});
 });
 return {schema_version:1,as_of:payload.as_of,rows:payload.rows.length,valid_rows:payload.rows.length-issues.length,issues,status:issues.length?'FAIL':'PASS'};
}
if(typeof document!=='undefined'){
 const input=document.querySelector('#payload'),output=document.querySelector('#result');
 function load(){input.value=JSON.stringify(samples[document.querySelector('#scenario').value],null,2);output.textContent='Ready. Run validation to inspect this sample.';}
 document.querySelector('#scenario').addEventListener('change',load);
 document.querySelector('#run').addEventListener('click',()=>{try{if(new TextEncoder().encode(input.value).length>262144)throw Error('Object exceeds 256 KiB size limit');output.textContent=JSON.stringify(validate(JSON.parse(input.value)),null,2);}catch(error){output.textContent='Input error: '+error.message;}});load();
}
if(typeof module!=='undefined')module.exports={validate,samples};
