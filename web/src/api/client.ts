import type { Health, System, VerifiedAnswer } from "../types";
export const health = () => fetch("/api/health").then(r => r.json() as Promise<Health>);
export const ask = (question:string, system:System) => fetch("/api/ask", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({question,system})}).then(r=>r.json() as Promise<VerifiedAnswer>);
export const compare = (question:string) => fetch("/api/compare", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({question})}).then(r=>r.json() as Promise<Record<System,VerifiedAnswer>>);
