
import React from 'react';
import logoMotiva from '../src/assets/images/regenerated_image_1778428990774.png';
import { 
  Home,
  Plane,
  Settings, 
  LogOut,
  Siren,
  Lock,
  BookOpen,
  Lightbulb,
  Shield,
  Building2,
  Palette,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

interface SidebarProps {
  activePage: string;
  onNavigate: (page: string) => void;
  isCollapsed: boolean;
  toggleSidebar: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activePage, onNavigate, isCollapsed, toggleSidebar }) => {
  return (
    <aside className={`hidden md:flex flex-col h-screen bg-[#391694] text-white fixed left-0 top-0 border-r border-white/10 z-50 transition-all duration-300 ${isCollapsed ? 'w-[80px]' : 'w-[280px]'}`}>
      <div className={`p-6 flex items-center gap-3 border-b border-white/10 ${isCollapsed ? 'justify-center' : ''}`}>
        <div className="bg-white/20 p-2 rounded-none shrink-0 overflow-hidden flex items-center justify-center">
          <img 
            src={logoMotiva} 
            alt="Logo Motiva" 
            className="w-8 h-8 object-contain" 
          />
        </div>
        {!isCollapsed && (
          <div className="animate-in fade-in duration-300">
            <h1 className="font-bold text-lg leading-[1.1]">
              <span className="block">Motiva</span>
              <span className="block">Aeroportos</span>
            </h1>
            <p className="text-[10px] text-indigo-200 mt-1 font-medium uppercase tracking-wider">Controle Aeroportuário</p>
          </div>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto py-6 px-3">
        <div className="space-y-1">
          {!isCollapsed && <p className="px-3 text-[10px] font-bold text-indigo-200 uppercase tracking-widest mb-2 animate-in fade-in duration-300">Principal</p>}
          <NavItem 
            active={activePage === 'home'} 
            onClick={() => onNavigate('home')}
            icon={Home} 
            label="Página Inicial" 
            isCollapsed={isCollapsed}
          />
        </div>

        <div className="mt-8 space-y-1">
          {!isCollapsed && <p className="px-3 text-[10px] font-bold text-indigo-200 uppercase tracking-widest mb-2 animate-in fade-in duration-300">Áreas</p>}
          <NavItem 
            active={activePage === 'operations'} 
            onClick={() => onNavigate('operations')}
            icon={Plane} 
            label="Operações Aeroportuárias" 
            isCollapsed={isCollapsed}
          />
          <NavItem 
            active={activePage === 'terminal'} 
            onClick={() => onNavigate('terminal')}
            icon={Building2} 
            label="Terminal de Passageiros" 
            isCollapsed={isCollapsed}
          />
          <NavItem 
            active={activePage === 'safety'} 
            onClick={() => onNavigate('safety')}
            icon={Shield} 
            label="Segurança Operacional" 
            isCollapsed={isCollapsed}
          />
          <NavItem 
            active={activePage === 'emergency'} 
            onClick={() => onNavigate('emergency')}
            icon={Siren} 
            label="Resposta à Emergência Aeroportuária" 
            isCollapsed={isCollapsed}
          />
          <NavItem 
            active={activePage === 'avsec'} 
            onClick={() => onNavigate('avsec')}
            icon={Lock} 
            label="AvSec" 
            isCollapsed={isCollapsed}
          />
        </div>

        <div className="mt-8 space-y-1">
          {!isCollapsed && <p className="px-3 text-[10px] font-bold text-indigo-200 uppercase tracking-widest mb-2 animate-in fade-in duration-300">Gestão do Conhecimento</p>}
          <NavItem 
            active={activePage === 'library'} 
            onClick={() => onNavigate('library')}
            icon={BookOpen} 
            label="Biblioteca de Procedimentos" 
            isCollapsed={isCollapsed}
          />
          <NavItem 
            active={activePage === 'lessons'} 
            onClick={() => onNavigate('lessons')}
            icon={Lightbulb} 
            label="Lições Aprendidas" 
            isCollapsed={isCollapsed}
          />
        </div>

        <div className="mt-8 space-y-1">
          {!isCollapsed && <p className="px-3 text-[10px] font-bold text-indigo-200 uppercase tracking-widest mb-2 animate-in fade-in duration-300">Sistema</p>}
          <NavItem 
            active={activePage === 'icons'} 
            onClick={() => onNavigate('icons')}
            icon={Palette} 
            label="Ícones do Sistema" 
            isCollapsed={isCollapsed}
          />
          <NavItem 
            active={activePage === 'settings'} 
            onClick={() => onNavigate('settings')}
            icon={Settings} 
            label="Configurações" 
            isCollapsed={isCollapsed}
          />
        </div>
      </nav>

      <div className="p-4 border-t border-white/10 flex flex-col gap-2">
        <button 
          onClick={toggleSidebar}
          className={`flex items-center gap-3 w-full px-3 py-2 text-xs font-bold text-indigo-100 hover:text-white hover:bg-white/10 rounded-none transition-colors ${isCollapsed ? 'justify-center' : 'text-left'} uppercase tracking-wide`}
          title={isCollapsed ? "Expandir menu" : "Recolher menu"}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          {!isCollapsed && <span>Recolher</span>}
        </button>

        <button className={`flex items-center gap-3 w-full px-3 py-2 text-xs font-bold text-indigo-100 hover:text-white hover:bg-white/10 rounded-none transition-colors ${isCollapsed ? 'justify-center' : 'text-left'} uppercase tracking-wide`}>
          <LogOut className="w-4 h-4" />
          {!isCollapsed && <span>Sair</span>}
        </button>
      </div>
    </aside>
  );
};

interface NavItemProps {
  icon: React.ElementType;
  label: string;
  active?: boolean;
  onClick: () => void;
  isCollapsed?: boolean;
}

const NavItem: React.FC<NavItemProps> = ({ icon: Icon, label, active, onClick, isCollapsed }) => (
  <button 
    onClick={onClick}
    title={isCollapsed ? label : undefined}
    className={`w-full flex items-center ${isCollapsed ? 'justify-center px-2' : 'text-left px-3'} gap-3 py-2.5 rounded-none transition-all duration-200 group ${
      active 
        ? 'bg-white/20 text-white shadow-none' 
        : 'text-white hover:bg-white/10'
    }`}
  >
    <Icon className="w-4 h-4 shrink-0 text-white" />
    {!isCollapsed && <span className="text-[13px] font-semibold leading-tight animate-in fade-in duration-200">{label}</span>}
  </button>
);