import { Moon, Sun } from "lucide-react";
export function ThemeToggle({dark,onToggle}:{dark:boolean;onToggle:()=>void}) { return <button className="theme" aria-label="Toggle theme" onClick={onToggle}>{dark?<Sun size={18}/>:<Moon size={18}/>}</button>; }
