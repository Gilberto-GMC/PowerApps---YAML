import React, { useState } from 'react';
import { 
  Building2, 
  Eye, 
  Activity,
  Trash2,
  Bird,
  PlaneLanding,
  CloudSun,
  CloudRain,
  CloudFog,
  Sun,
  Wind,
  AlertTriangle
} from 'lucide-react';
import { AIRPORTS } from './AISComplianceForm';

interface TacticalOverviewProps {
  onSelectModuleById?: (id: string) => void;
  onNavigateToOperations?: () => void;
}

interface OperationalWeatherInfo {
  airport: string;
  category: 'VFR' | 'MVFR' | 'IFR';
  categoryBg: string;
  tempVal: string;
  conditionText: string;
  windShort: string;
  visibilityShort: string;
  icon: React.FC<{ className?: string }>;
  iconColor: string;
}

export const TacticalOverviewModule: React.FC<TacticalOverviewProps> = ({ 
  onSelectModuleById
}) => {
  const [selectedAirport, setSelectedAirport] = useState<string>('all');

  // Time formatting
  const now = new Date();
  const dateFormatted = now.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  const timeFormattedUTC = `${String(now.getUTCHours()).padStart(2, '0')}:${String(now.getUTCMinutes()).padStart(2, '0')} UTC`;

  // Minimal KPIs for Supervisors & Managers - Clean & Unified Brand Accents
  const kpis = [
    { 
      title: 'Ocorrências Hoje', 
      value: '14', 
      detail: '3 em investigação prioritária', 
      icon: Activity
    },
    { 
      title: 'Condição de Pista', 
      value: 'Operacional', 
      detail: 'Aderência média 0.81 (Seca)', 
      icon: PlaneLanding
    },
    { 
      title: 'Varredura FOD (24h)', 
      value: '28.4 kg', 
      detail: '100% das vistorias executadas', 
      icon: Trash2
    },
    { 
      title: 'Nível de Risco Fauna', 
      value: 'Médio', 
      detail: '2 alertas ativos na aproximação', 
      icon: Bird
    }
  ];

  // Weather data simplified specifically for Airport Ground Operations & Management
  const weatherList: OperationalWeatherInfo[] = [
    {
      airport: 'Aeroporto de Bagé',
      category: 'VFR',
      categoryBg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      tempVal: '19°C',
      conditionText: 'Poucas Nuvens',
      windShort: '120° @ 8 kt',
      visibilityShort: '> 10 km',
      icon: Sun,
      iconColor: 'text-amber-500'
    },
    {
      airport: 'Aeroporto de Uruguaiana',
      category: 'MVFR',
      categoryBg: 'bg-amber-50 text-amber-800 border-amber-200',
      tempVal: '22°C',
      conditionText: 'Nuvens Dispersas',
      windShort: '150° @ 11 kt',
      visibilityShort: '7.000 m',
      icon: CloudSun,
      iconColor: 'text-amber-500'
    },
    {
      airport: 'Aeroporto de Pelotas',
      category: 'IFR',
      categoryBg: 'bg-rose-50 text-rose-800 border-rose-200',
      tempVal: '14°C',
      conditionText: 'Névoa Úmida',
      windShort: '080° @ 6 kt',
      visibilityShort: '2.500 m',
      icon: CloudFog,
      iconColor: 'text-slate-400'
    },
    {
      airport: 'Aeroporto de Navegantes',
      category: 'VFR',
      categoryBg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      tempVal: '21°C',
      conditionText: 'Parcialmente Nublado',
      windShort: '090° @ 10 kt',
      visibilityShort: '> 10 km',
      icon: CloudSun,
      iconColor: 'text-amber-500'
    },
    {
      airport: 'Aeroporto de Joinville',
      category: 'MVFR',
      categoryBg: 'bg-amber-50 text-amber-800 border-amber-200',
      tempVal: '18°C',
      conditionText: 'Chuva Leve',
      windShort: '110° @ 9 kt',
      visibilityShort: '6.000 m',
      icon: CloudRain,
      iconColor: 'text-blue-500'
    },
    {
      airport: 'Aeroporto de Londrina',
      category: 'VFR',
      categoryBg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      tempVal: '24°C',
      conditionText: 'Céu Claro',
      windShort: '070° @ 7 kt',
      visibilityShort: '> 10 km',
      icon: Sun,
      iconColor: 'text-amber-500'
    },
    {
      airport: 'Aeroporto de Foz do Iguaçu',
      category: 'IFR',
      categoryBg: 'bg-rose-50 text-rose-800 border-rose-200',
      tempVal: '15°C',
      conditionText: 'Névoa Úmida',
      windShort: '180° @ 5 kt',
      visibilityShort: '3.000 m',
      icon: CloudFog,
      iconColor: 'text-slate-400'
    },
    {
      airport: 'Aeroporto de Bacacheri',
      category: 'VFR',
      categoryBg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      tempVal: '16°C',
      conditionText: 'Tempo Limpo',
      windShort: '100° @ 6 kt',
      visibilityShort: '> 10 km',
      icon: CloudSun,
      iconColor: 'text-amber-500'
    },
    {
      airport: 'Aeroporto de Curitiba',
      category: 'VFR',
      categoryBg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      tempVal: '17°C',
      conditionText: 'Tempo Limpo',
      windShort: '110° @ 7 kt',
      visibilityShort: '> 10 km',
      icon: CloudSun,
      iconColor: 'text-amber-500'
    },
    {
      airport: 'Aeroporto da Pampulha',
      category: 'MVFR',
      categoryBg: 'bg-amber-50 text-amber-800 border-amber-200',
      tempVal: '25°C',
      conditionText: 'Teto Baixo',
      windShort: '050° @ 10 kt',
      visibilityShort: '5.000 m',
      icon: CloudSun,
      iconColor: 'text-amber-500'
    },
    {
      airport: 'Aeroporto de Goiânia',
      category: 'MVFR',
      categoryBg: 'bg-amber-50 text-amber-800 border-amber-200',
      tempVal: '26°C',
      conditionText: 'Chuva c/ Trovoadas',
      windShort: '240° @ 12 kt (Rajada 22 kt)',
      visibilityShort: '8.000 m',
      icon: CloudRain,
      iconColor: 'text-blue-500'
    },
    {
      airport: 'Aeroporto de Palmas',
      category: 'VFR',
      categoryBg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      tempVal: '32°C',
      conditionText: 'Ensolarado',
      windShort: '040° @ 12 kt',
      visibilityShort: '> 10 km',
      icon: Sun,
      iconColor: 'text-amber-500'
    },
    {
      airport: 'Aeroporto de Imperatriz',
      category: 'IFR',
      categoryBg: 'bg-rose-50 text-rose-800 border-rose-200',
      tempVal: '27°C',
      conditionText: 'Pancadas Intensas',
      windShort: '300° @ 16 kt',
      visibilityShort: '3.500 m',
      icon: CloudRain,
      iconColor: 'text-blue-600'
    },
    {
      airport: 'Aeroporto de Teresina',
      category: 'VFR',
      categoryBg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      tempVal: '31°C',
      conditionText: 'Céu Claro',
      windShort: '070° @ 9 kt',
      visibilityShort: '> 10 km',
      icon: Sun,
      iconColor: 'text-amber-500'
    },
    {
      airport: 'Aeroporto de Petrolina',
      category: 'MVFR',
      categoryBg: 'bg-amber-50 text-amber-800 border-amber-200',
      tempVal: '29°C',
      conditionText: 'Vento Forte & Poeira',
      windShort: '130° @ 18 kt',
      visibilityShort: '6.500 m',
      icon: Wind,
      iconColor: 'text-slate-500'
    },
    {
      airport: 'Aeroporto de São Luís',
      category: 'VFR',
      categoryBg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      tempVal: '30°C',
      conditionText: 'Ensolarado',
      windShort: '060° @ 14 kt',
      visibilityShort: '> 10 km',
      icon: Sun,
      iconColor: 'text-amber-500'
    }
  ];

  // Recent Occurrences Feed
  const recentOccurrences = [
    {
      id: 'occ-1',
      time: '10:14 UTC',
      airport: 'Aeroporto de Curitiba',
      module: 'Dano por Detritos (F.O.Damage)',
      moduleId: 'safe-10',
      description: 'Dano leve na carenagem do motor por parafuso no Pátio 1.',
      status: 'Em Investigação',
      badgeColor: 'bg-amber-50 text-amber-800 border-amber-200'
    },
    {
      id: 'occ-2',
      time: '09:40 UTC',
      airport: 'Aeroporto de Goiânia',
      module: 'Interação com Fauna',
      moduleId: 'fauna-1',
      description: 'Avistamento de Quero-queros na faixa de pista 14 próximo à TWY C.',
      status: 'Afugentamento Executado',
      badgeColor: 'bg-slate-100 text-slate-700 border-slate-200'
    },
    {
      id: 'occ-3',
      time: '08:55 UTC',
      airport: 'Aeroporto de Navegantes',
      module: 'Vazamento de Fluídos',
      moduleId: 'safe-1',
      description: 'Vazamento de 3L de óleo hidráulico na Posição 03. Absorvente aplicado.',
      status: 'Contido & Limpo',
      badgeColor: 'bg-slate-100 text-slate-700 border-slate-200'
    },
    {
      id: 'occ-4',
      time: '07:20 UTC',
      airport: 'Aeroporto de Foz do Iguaçu',
      module: 'Atendimento Ambulift',
      moduleId: 'aero-3',
      description: 'Atendimento PRM concluído sem intercorrências na Posição 02.',
      status: 'Concluído',
      badgeColor: 'bg-slate-100 text-slate-700 border-slate-200'
    }
  ];

  const filteredWeather = selectedAirport === 'all' 
    ? weatherList 
    : weatherList.filter(w => w.airport === selectedAirport || w.airport.includes(selectedAirport) || selectedAirport.includes(w.airport));

  const filteredOccurrences = selectedAirport === 'all' 
    ? recentOccurrences 
    : recentOccurrences.filter(o => o.airport === selectedAirport || o.airport.includes(selectedAirport) || selectedAirport.includes(o.airport));

  return (
    <div className="space-y-6 animate-in fade-in duration-300 pb-10">
      {/* Header com Título, Data e Seletor na Esquerda, e Card Meteorológico no Canto Superior Direito */}
      <div className="flex flex-col lg:flex-row lg:items-stretch justify-between gap-6 pb-6 border-b border-slate-200">
        {/* Esquerda: Data (topo), Título (centro) e Seletor de Aeroporto (base) alinhados com o Card */}
        <div className="flex flex-col justify-between gap-4 min-h-[120px] py-0.5">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500" />
            <span>{dateFormatted} • {timeFormattedUTC}</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight uppercase leading-none py-1">
            Visão Tática
          </h1>

          <div className="relative w-full sm:w-[320px]">
            <Building2 className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            <select
              value={selectedAirport}
              onChange={(e) => setSelectedAirport(e.target.value)}
              className="w-full pl-10 pr-8 py-2.5 bg-white border border-slate-200 text-xs font-bold text-slate-800 outline-none focus:border-[#391694] cursor-pointer appearance-none shadow-sm hover:border-slate-300 transition-colors"
            >
              <option value="all">Rede Toda — Todos os Aeroportos</option>
              {AIRPORTS.map((ap) => (
                <option key={ap} value={ap}>{ap}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Canto Superior Direito: Card Meteorológico exibido APENAS quando um aeroporto específico é selecionado */}
        {selectedAirport !== 'all' && (
          <div className="shrink-0 max-w-full">
            <div className="flex flex-wrap lg:flex-nowrap gap-3 items-stretch justify-start lg:justify-end max-w-full overflow-x-auto pb-1">
              {filteredWeather.map((item) => {
                const WeatherIcon = item.icon;
                return (
                  <div 
                    key={item.airport} 
                    className="bg-white border border-slate-200 p-4 min-w-[280px] sm:min-w-[300px] space-y-3 shadow-sm hover:border-slate-300 transition-all flex flex-col justify-between"
                  >
                    {/* Topo: Temperatura, Condição e Ícone */}
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="text-2xl font-black text-slate-900 tracking-tight">{item.tempVal}</div>
                        <span className="text-xs font-semibold text-slate-700 block mt-0.5">{item.conditionText}</span>
                      </div>
                      <div className="p-2 bg-slate-50 border border-slate-100 rounded flex items-center justify-center shrink-0">
                        <WeatherIcon className={`w-6 h-6 ${item.iconColor}`} />
                      </div>
                    </div>

                    {/* Linha Inferior: Tag + Vento + Visibilidade em Ordem */}
                    <div className="flex items-center justify-between gap-2 text-xs text-slate-600 font-medium pt-2.5 border-t border-slate-100">
                      <span className={`text-[10px] font-black px-1.5 py-0.5 border rounded ${item.categoryBg} shrink-0`}>
                        {item.category}
                      </span>

                      <span className="flex items-center gap-1 text-[11px] sm:text-xs text-slate-600 font-medium shrink-0">
                        <Wind className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span>{item.windShort}</span>
                      </span>

                      <span className="flex items-center gap-1 text-[11px] sm:text-xs text-slate-600 font-medium shrink-0">
                        <Eye className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span>Visib: {item.visibilityShort}</span>
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Cards Principais (KPIs) — Em Uma Única Linha */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div key={idx} className="bg-white p-4 border border-slate-200 space-y-2 hover:border-slate-300 transition-all shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">{kpi.title}</span>
                <div className="p-1.5 bg-slate-50 border border-slate-200 flex items-center justify-center">
                  <Icon className="w-4 h-4 text-[#391694]" />
                </div>
              </div>
              <div className="text-2xl font-black text-slate-900 tracking-tight">
                {kpi.value}
              </div>
              <p className="text-xs text-slate-500 font-medium truncate">{kpi.detail}</p>
            </div>
          );
        })}
      </div>

      {/* Feed de Ocorrências Recentes */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-600 uppercase tracking-wider">
            Últimas Ocorrências Registradas
          </h3>
          <span className="text-[11px] text-slate-400 font-medium">{filteredOccurrences.length} registros</span>
        </div>

        <div className="bg-white border border-slate-200 divide-y divide-slate-100 shadow-sm">
          {filteredOccurrences.map((occ) => (
            <div key={occ.id} className="p-4 hover:bg-slate-50/80 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="space-y-1">
                <div className="flex items-center gap-2.5 flex-wrap">
                  <span className="text-xs font-bold text-slate-900">
                    {occ.time}
                  </span>
                  <span className="text-xs text-slate-300">•</span>
                  <span className="text-xs font-semibold text-slate-700">{occ.airport}</span>
                  <span className="text-xs text-slate-300">•</span>
                  <span className="text-[11px] font-bold text-[#391694] uppercase bg-purple-50 px-2 py-0.5 border border-purple-100">
                    {occ.module}
                  </span>
                </div>
                <p className="text-xs text-slate-600 font-medium">
                  {occ.description}
                </p>
              </div>

              <div className="flex items-center gap-3 shrink-0 self-end sm:self-center">
                <span className={`text-[11px] font-bold px-2.5 py-1 border ${occ.badgeColor}`}>
                  {occ.status}
                </span>
                {onSelectModuleById && (
                  <button
                    onClick={() => onSelectModuleById(occ.moduleId)}
                    className="p-1.5 text-slate-400 hover:text-[#391694] hover:bg-purple-50 transition-colors"
                    title="Abrir Módulo"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};



