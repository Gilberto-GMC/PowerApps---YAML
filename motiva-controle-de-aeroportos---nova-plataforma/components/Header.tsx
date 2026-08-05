
import React from 'react';
import { Search, Bell, User } from 'lucide-react';

interface HeaderProps {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ searchQuery, setSearchQuery }) => {
  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-100 px-8 py-5 flex items-center justify-between shadow-none">
      <div className="md:hidden font-bold text-slate-800 flex items-center gap-2 tracking-normal uppercase">
        <span className="text-[#391694] font-black">Motiva</span>
      </div>

      <div className="flex-1 max-w-2xl">
        <div className="relative group">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-slate-300 group-focus-within:text-[#391694] transition-colors" />
          </div>
          <input
            type="text"
            className="block w-full pl-12 pr-4 py-3 border border-slate-100 rounded-none leading-5 bg-slate-50 text-slate-900 placeholder-slate-400 font-medium focus:outline-none focus:bg-white focus:ring-4 focus:ring-[#391694]/5 focus:border-[#391694] transition-all duration-200 sm:text-sm"
            placeholder="Buscar módulo ou ferramenta..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <div className="flex items-center justify-end ml-8 gap-6">
        <button 
          title="Abrir Relato de Prevenção"
          className="hidden sm:flex items-center justify-center h-9 px-5 bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white rounded-lg text-xs font-black tracking-[0.15em] border border-white/20 transition-all hover:scale-105 active:scale-95 leading-none shadow-lg shadow-blue-900/20"
        >
          RELPREV
        </button>

        <button className="relative p-2 text-slate-400 hover:text-[#391694] transition-colors rounded-none hover:bg-[#F5F3FF]">
          <Bell className="w-6 h-6" strokeWidth={1.5} />
          <span className="absolute top-2.5 right-2.5 block h-2.5 w-2.5 rounded-full bg-[#391694] ring-4 ring-white"></span>
        </button>
        
        <div className="hidden md:flex items-center gap-4 pl-8 border-l border-slate-100">
          <div className="text-right">
            <p className="text-sm font-bold text-slate-800 tracking-normal">Guilherme Biasin Scopel</p>
            <p className="text-[8px] text-slate-400 font-bold uppercase tracking-widest">Especialista em Processos Aeroportuários</p>
          </div>
          <div className="h-12 w-12 rounded-none bg-slate-50 flex items-center justify-center border border-slate-100 shadow-sm shrink-0 overflow-hidden text-slate-400 hover:border-[#391694] transition-all cursor-pointer">
            <User className="w-6 h-6" strokeWidth={1.5} />
          </div>
        </div>
      </div>
    </header>
  );
};
