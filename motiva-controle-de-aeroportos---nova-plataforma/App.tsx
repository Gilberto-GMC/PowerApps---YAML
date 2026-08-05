
import React, { useState, useMemo } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ModuleCard } from './components/ModuleCard';
import { LoginPage } from './components/LoginPage';
import { AISComplianceModule } from './components/AISComplianceModule';
import { AISWebModule } from './components/AISWebModule_v2';
import { AmbuliftModule } from './components/AmbuliftModule';
import { AmbuliftInspectionModule } from './components/AmbuliftInspectionModule';
import { OverloadControlModule } from './components/OverloadControlModule';
import { EngineTestModule } from './components/EngineTestModule';
import { NotamModule } from './components/NotamModule';
import { IconsLibraryModule } from './components/IconsLibraryModule';
import { LeakageModule } from './components/LeakageModule';
import { FODModule } from './components/FODModule';
import { FODamageModule } from './components/FODamageModule';
import { JetBlastModule } from './components/JetBlastModule';
import { GroundOccurrenceModule } from './components/GroundOccurrenceModule';
import { VehicleCollisionModule } from './components/VehicleCollisionModule';
import { ConstructionEventsModule } from './components/ConstructionEventsModule';
import { OtherOccurrencesModule } from './components/OtherOccurrencesModule';
import { FaunaInteractionModule } from './components/FaunaInteractionModule';
import { FaunaPresenceModule } from './components/FaunaPresenceModule';
import { FaunaAttractionModule } from './components/FaunaAttractionModule';
import { ProcedureLibraryModule } from './components/ProcedureLibraryModule';
import { TacticalOverviewModule } from './components/TacticalOverviewModule';
import { AvopModule } from './components/AvopModule';
import { ExternalInterferenceModule } from './components/ExternalInterferenceModule';
import { FirePrincipleModule } from './components/FirePrincipleModule';
import { ThirdPartyAccessModule } from './components/ThirdPartyAccessModule';
import { ExplanationVideoModal } from './components/ExplanationVideoModal';
import { CATEGORIES, MODULES } from './constants';
import { ModuleItem } from './types';
import { 
  Sparkles, 
  LayoutGrid, 
  List as ListIcon, 
  ArrowRight,
  HelpCircle
} from 'lucide-react';

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activePage, setActivePage] = useState('home');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedModule, setSelectedModule] = useState<ModuleItem | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isExplanationVideoOpen, setIsExplanationVideoOpen] = useState(false);

  React.useEffect(() => {
    const handleOpenHelp = () => {
      setIsExplanationVideoOpen(true);
    };
    window.addEventListener('open-module-help', handleOpenHelp);
    return () => {
      window.removeEventListener('open-module-help', handleOpenHelp);
    };
  }, []);

  const filteredModules = useMemo(() => {
    let result = MODULES;
    if (activeFilter !== 'all') {
      result = result.filter(m => m.category === activeFilter);
    }
    if (searchQuery.trim()) {
      const lowerQuery = searchQuery.toLowerCase();
      result = result.filter(m => 
        m.title.toLowerCase().includes(lowerQuery) || 
        m.category.toLowerCase().includes(lowerQuery)
      );
    }
    return result;
  }, [searchQuery, activeFilter]);

  const groupedModules = useMemo(() => {
    const groups: Record<string, ModuleItem[]> = {};
    const categoriesToShow = activeFilter === 'all' 
      ? CATEGORIES 
      : CATEGORIES.filter(c => c.id === activeFilter);
    categoriesToShow.forEach(cat => {
      groups[cat.id] = filteredModules.filter(m => m.category === cat.id);
    });
    return groups;
  }, [filteredModules, activeFilter]);

  const handleModuleClick = (module: ModuleItem) => {
    setSelectedModule(module);
  };

  const handleBackToDashboard = () => {
    setSelectedModule(null);
  };

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const renderListItem = (module: ModuleItem) => {
    const Icon = module.icon;
    let iconColorClass = "";
    let iconBgClass = "";
    
    switch (module.category) {
      case 'inspections':
        iconColorClass = "text-[#D95D39]";
        iconBgClass = "bg-[#FFF5F0]";
        break;
      case 'operational':
        iconColorClass = "text-[#0891b2]";
        iconBgClass = "bg-[#F0FDFF]";
        break;
      case 'fauna':
        iconColorClass = "text-[#166534]";
        iconBgClass = "bg-[#EEFFE6]";
        break;
      case 'safety_events':
        iconColorClass = "text-[#c026d3]";
        iconBgClass = "bg-[#FDF4FF]";
        break;
      case 'aeronautical_info':
        iconColorClass = "text-[#391694]";
        iconBgClass = "bg-[#F5F3FF]";
        break;
      case 'orientation_program':
        iconColorClass = "text-[#858316]";
        iconBgClass = "bg-[#FFFD8A]";
        break;
      default:
        iconColorClass = "text-slate-600";
        iconBgClass = "bg-slate-50";
    }

    return (
      <div 
        key={module.id}
        onClick={() => handleModuleClick(module)}
        className="group flex items-center gap-6 p-6 bg-white border border-[#C9C5E6] hover:bg-[#F5F3FF] transition-all cursor-pointer border-t-0 first:border-t"
      >
        <div className={`p-3 rounded-none ${iconBgClass} ${iconColorClass} transition-colors shrink-0 duration-300`}>
          <Icon className="w-6 h-6" strokeWidth={1.5} />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-slate-800 text-lg mb-1 truncate tracking-normal transition-colors group-hover:text-[#391694]">{module.title}</h4>
          <p className="text-sm text-slate-400 font-normal line-clamp-1 leading-relaxed">
            {module.description}
          </p>
        </div>
        <ArrowRight className="w-6 h-6 text-slate-900 group-hover:text-[#391694] transition-colors shrink-0" strokeWidth={1} />
      </div>
    );
  };

  const renderContent = () => {
    if (selectedModule) {
      return (
        <div className="flex-1 flex flex-col w-full animate-in fade-in slide-in-from-bottom-4 duration-300 overflow-hidden bg-white">
          <div className="max-w-6xl mx-auto w-full px-4 flex-1 flex flex-col min-h-0">
            <div className="flex py-4 shrink-0 justify-between items-center pr-1">
              <button 
                onClick={handleBackToDashboard}
                className="flex items-center gap-4 transition-all group"
              >
                <div className="w-10 h-10 bg-black text-white rounded-full flex items-center justify-center transition-transform group-hover:scale-110 shadow-lg">
                  <ArrowRight className="w-5 h-5 rotate-180" />
                </div>
                <div className="flex flex-col items-start">
                  <span className="text-[11px] font-black text-slate-400 uppercase tracking-widest leading-none">Voltar ao Painel</span>
                </div>
              </button>

              <button
                onClick={() => setIsExplanationVideoOpen(true)}
                className="flex items-center gap-2.5 px-5 py-2.5 bg-[#DD511A] hover:bg-[#c44312] text-white text-xs font-black uppercase tracking-widest rounded-none shadow-md transition-all duration-300 group hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-[#DD511A]/40 border border-[#DD511A] shrink-0"
              >
                <span>Instruções em Vídeo</span>
              </button>
            </div>
            
            <div className="flex-1 bg-white rounded-none border border-slate-100 shadow-[0_4px_30px_rgba(0,0,0,0.04)] overflow-hidden relative flex flex-col mb-4">
              <div className="flex-1 flex flex-col overflow-hidden">
                <div className="flex-1 overflow-hidden">
                  {selectedModule.id === 'aero-3' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <AISComplianceModule />
                    </div>
                  ) : selectedModule.id === 'aero-1' ? (
                    <AISWebModule />
                  ) : selectedModule.id === 'aero-2' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <NotamModule />
                    </div>
                  ) : selectedModule.id === 'insp-6' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <AmbuliftInspectionModule />
                    </div>
                  ) : selectedModule.id === 'ops-2' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <EngineTestModule />
                    </div>
                  ) : selectedModule.id === 'ops-6' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <AmbuliftModule />
                    </div>
                  ) : selectedModule.id === 'ops-7' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <OverloadControlModule />
                    </div>
                  ) : selectedModule.id === 'ops-8' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <ThirdPartyAccessModule />
                    </div>
                  ) : selectedModule.id === 'safe-1' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <LeakageModule />
                    </div>
                  ) : selectedModule.id === 'safe-2' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <FODModule />
                    </div>
                  ) : selectedModule.id === 'safe-10' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <FODamageModule />
                    </div>
                  ) : selectedModule.id === 'safe-3' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <JetBlastModule />
                    </div>
                  ) : selectedModule.id === 'safe-4' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <GroundOccurrenceModule />
                    </div>
                  ) : selectedModule.id === 'safe-5' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <VehicleCollisionModule />
                    </div>
                  ) : selectedModule.id === 'safe-6' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <ExternalInterferenceModule />
                    </div>
                  ) : selectedModule.id === 'safe-7' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <ConstructionEventsModule />
                    </div>
                  ) : selectedModule.id === 'safe-8' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <OtherOccurrencesModule />
                    </div>
                  ) : selectedModule.id === 'safe-9' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <FirePrincipleModule />
                    </div>
                  ) : selectedModule.id === 'fauna-1' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <FaunaInteractionModule />
                    </div>
                  ) : selectedModule.id === 'fauna-5' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <FaunaPresenceModule />
                    </div>
                  ) : selectedModule.id === 'fauna-6' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <FaunaAttractionModule />
                    </div>
                  ) : selectedModule.id === 'aero-4' ? (
                    <div className="h-full overflow-y-auto px-10 pt-12 pb-10">
                      <AvopModule />
                    </div>
                  ) : (
                    <div className="h-full px-10 pb-8 overflow-y-auto pt-6">
                      <div className="p-12 bg-slate-50 rounded-none border border-dashed border-slate-300 flex flex-col items-center justify-center text-slate-400 gap-4 mt-4">
                        <Sparkles className="w-10 h-10" strokeWidth={1.5} />
                        <p className="font-medium tracking-normal">O formulário para "{selectedModule.title}" está em desenvolvimento.</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }
    
    if (activePage === 'icons') {
      return (
        <div className="h-full w-full animate-in fade-in duration-500 overflow-hidden flex flex-col">
          <IconsLibraryModule />
        </div>
      );
    }

    if (activePage === 'library') {
      return (
        <div className="h-full w-full animate-in fade-in duration-500 overflow-hidden flex flex-col">
          <ProcedureLibraryModule />
        </div>
      );
    }

    if (activePage === 'home') {
      return (
        <div className="max-w-7xl mx-auto w-full animate-in fade-in duration-500 bg-white">
          <TacticalOverviewModule 
            onSelectModuleById={(id) => {
              const mod = MODULES.find(m => m.id === id);
              if (mod) setSelectedModule(mod);
            }}
            onNavigateToOperations={() => setActivePage('operations')}
          />
        </div>
      );
    }

    if (activePage === 'operations') {
      return (
        <div className="max-w-6xl mx-auto w-full space-y-12 animate-in fade-in duration-500 bg-white">
          <div className="space-y-6 pt-6">
            <div className="flex flex-col sm:flex-row justify-between items-end sm:items-center gap-4">
               {!searchQuery ? (
                  <div>
                    <h2 className="text-3xl font-bold text-slate-800 tracking-normal mb-1 uppercase">Operações Aeroportuárias</h2>
                    <p className="text-slate-500 text-lg font-medium tracking-normal">Acesse os módulos especializados de gestão e controle.</p>
                  </div>
               ) : (
                  <div>
                    <h2 className="text-2xl font-bold text-slate-800 tracking-normal mb-1">Resultados da busca</h2>
                    <p className="text-slate-500 text-sm font-medium">{filteredModules.length} módulos encontrados</p>
                  </div>
               )}
               <div className="bg-white p-1 rounded-none border border-[#C9C5E6] flex shadow-sm shrink-0 h-fit self-end">
                  <button onClick={() => setViewMode('list')} className={`p-2 rounded-none transition-colors ${viewMode === 'list' ? 'bg-[#F5F3FF] text-[#391694]' : 'text-slate-400 hover:bg-slate-50'}`}><ListIcon className="w-5 h-5" /></button>
                  <button onClick={() => setViewMode('grid')} className={`p-2 rounded-none transition-colors ${viewMode === 'grid' ? 'bg-[#F5F3FF] text-[#391694]' : 'text-slate-400 hover:bg-slate-50'}`}><LayoutGrid className="w-5 h-5" /></button>
               </div>
            </div>

            <div className="flex flex-wrap gap-4">
              <button onClick={() => setActiveFilter('all')} className={`px-6 py-2 rounded-none text-xs font-black uppercase tracking-widest transition-all duration-300 border ${activeFilter === 'all' ? 'bg-[#391694] text-white border-[#391694]' : 'bg-white text-slate-500 border-[#C9C5E6]'}`}>Todos</button>
              {CATEGORIES.map(category => (
                <button key={category.id} onClick={() => setActiveFilter(category.id)} className={`px-6 py-2 rounded-none text-xs font-black uppercase tracking-widest transition-all duration-300 border ${activeFilter === category.id ? 'bg-[#391694] text-white border-[#391694] shadow-md shadow-indigo-200' : 'bg-white text-slate-500 border-[#C9C5E6]'}`}>{category.label}</button>
              ))}
            </div>
          </div>

          {CATEGORIES.map((category) => {
            if (activeFilter !== 'all' && activeFilter !== category.id) return null;
            const modules = groupedModules[category.id] || [];
            if (modules.length === 0) return null;
            return (
              <section key={category.id} className="scroll-mt-24">
                <div className="flex items-center gap-6 mb-8 group w-full">
                  <div className="flex items-center gap-4 shrink-0">
                    <div className="w-1.5 h-8 rounded-none" style={{ backgroundColor: category.themeColor }}></div>
                    <h2 className="text-2xl font-bold text-slate-800 whitespace-nowrap tracking-normal uppercase">{category.label}</h2>
                  </div>
                  <div className="flex-1 h-px bg-slate-100"></div>
                  <span className={`text-[10px] font-black px-4 py-1 rounded-none border shrink-0 ${category.colorClass} uppercase tracking-widest`}>{modules.length} Módulos</span>
                </div>
                <div className={viewMode === 'grid' ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8" : "flex flex-col border-b border-[#C9C5E6]"}>
                  {modules.map((module) => viewMode === 'grid' ? <ModuleCard key={module.id} module={module} onClick={handleModuleClick} /> : renderListItem(module))}
                </div>
              </section>
            );
          })}
        </div>
      );
    }

    return (
      <div className="max-w-4xl mx-auto py-24 text-center bg-white">
        <h2 className="text-3xl font-bold text-slate-800 tracking-normal mb-2">Em desenvolvimento</h2>
        <p className="text-slate-400 font-medium tracking-normal">Esta funcionalidade será implementada em breve na plataforma Motiva.</p>
      </div>
    );
  };

  if (!isAuthenticated) return <LoginPage onLogin={handleLogin} />;

  return (
    <div className="h-screen bg-white font-sans text-slate-900 flex overflow-hidden">
      <Sidebar 
        activePage={activePage} 
        onNavigate={setActivePage} 
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />
      <div className={`flex-1 ${isSidebarCollapsed ? 'md:ml-[80px]' : 'md:ml-[280px]'} flex flex-col h-full transition-all duration-300`}>
        <Header searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
        <main className={`flex-1 ${activePage === 'icons' || activePage === 'library' || selectedModule ? 'p-0 overflow-hidden flex flex-col' : 'p-6 md:p-10 overflow-y-auto bg-white'}`}>
          {renderContent()}
        </main>
      </div>

      {isExplanationVideoOpen && selectedModule && (
        <ExplanationVideoModal 
          moduleId={selectedModule.id}
          moduleTitle={selectedModule.title}
          onClose={() => setIsExplanationVideoOpen(false)}
        />
      )}
    </div>
  );
};

export default App;
