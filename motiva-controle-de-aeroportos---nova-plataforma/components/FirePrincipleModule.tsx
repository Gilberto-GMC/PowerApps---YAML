import React, { useState } from 'react';
import { 
  PlusCircle, 
  History, 
  CheckCircle2, 
  ArrowRight,
  Calendar,
  Clock,
  MapPin,
  AlertTriangle,
  Camera,
  Trash2,
  FileText,
  UploadCloud,
  MoreHorizontal,
  Eye,
  Pencil,
  Building2,
  FileSpreadsheet,
  ChevronDown,
  Flame,
  User,
  ShieldAlert,
  Info
} from 'lucide-react';
import { AIRPORTS } from './AISComplianceForm';

interface InjuredPerson {
  id: string;
  name: string;
  severity: string;
}

interface FirePrincipleRecord {
  id: string;
  airport: string;
  date: string;
  time: string;
  location: string;
  position: string;
  origin: string;
  extinguishMethod: 'Sim' | 'Não';
  extinguisherType?: string;
  extinguishersQuantity?: string;
  extinguishersLocation?: string;
  seiscResponseTime: string;
  materialDamage: 'Sim' | 'Não' | 'Sob Análise';
  materialDamageDetails?: string;
  hasInjuries: 'Sim' | 'Não';
  injuredPeople: InjuredPerson[];
  description: string;
  status: 'Em Análise' | 'Finalizado';
}

const MOCK_RECORDS: FirePrincipleRecord[] = [
  {
    id: '1',
    airport: 'Aeroporto de Curitiba',
    date: '2024-05-28',
    time: '14:22',
    location: 'Pátio de Estacionamento',
    position: 'Posição 05',
    origin: 'Veículo Terrestre (GSE) - Trator de pushback',
    extinguishMethod: 'Sim',
    extinguisherType: 'Pó Químico Seco (PQS)',
    extinguishersQuantity: '1',
    extinguishersLocation: 'Próprio trator de pushback (GSE)',
    seiscResponseTime: '',
    materialDamage: 'Sim',
    materialDamageDetails: 'Danos parciais no motor de arranque do trator de pushback.',
    hasInjuries: 'Não',
    injuredPeople: [],
    description: 'Durante o procedimento de acoplamento para pushback, houve um princípio de incêndio no compartimento do motor de partida do trator devido a curto-circuito. O operador agiu rapidamente utilizando o extintor portátil de PQS do próprio veículo.',
    status: 'Finalizado'
  },
  {
    id: '2',
    airport: 'Aeroporto de Goiânia',
    date: '2024-05-20',
    time: '09:10',
    location: 'Área de Equipamentos',
    position: 'Setor Bravo - Rampa Nordeste',
    origin: 'Fiação Elétrica / Equipamento Eletrônico',
    extinguishMethod: 'Sim',
    extinguisherType: 'Gás Carbônico (CO2)',
    extinguishersQuantity: '2',
    extinguishersLocation: 'Caixa de extintores do Box 05 - Rampa Nordeste',
    seiscResponseTime: '3',
    materialDamage: 'Não',
    materialDamageDetails: '',
    hasInjuries: 'Não',
    injuredPeople: [],
    description: 'Visualizado princípio de incêndio com fumaça densa saindo de um gerador elétrico móvel (GPU) estacionado na rampa Nordeste. Fiscais de pátio acionaram o SEISC e realizaram o primeiro combate.',
    status: 'Em Análise'
  }
];

const INJURY_SEVERITIES = [
  'Nenhuma / Ileso',
  'Leve (Lesão superficial ou que não requer hospitalização prolongada)',
  'Moderada (Lesão que requer tratamento médico sem risco imediato à vida)',
  'Grave (Lesão que requer hospitalização por mais de 48h ou fraturas/hemorragias)',
  'Fatal (Ocorrência que resulta em óbito)'
];

const EXTINGUISHER_AGENT_TYPES = [
  'Pó Químico Seco (PQS)',
  'Gás Carbônico (CO2)',
  'Água Pressurizada (AP)',
  'Espuma Mecânica (LGE)',
  'Halotron / Agente Limpo',
  'Outro'
];

const LOCATIONS = [
  'Pátio de Estacionamento',
  'Pista de Táxi',
  'Pista de Pouso e Decolagem',
  'Via de serviço',
  'Pátio de Hangar',
  'Área de Equipamentos',
  'Outro'
];

const FIRE_ORIGINS = [
  'Aeronave',
  'Veículo',
  'Equipamento de Rampa',
  'Caminhão Tanque de Abastecimento',
  'Vazamento de Combustível ou Óleo',
  'Fiação / Equipamento Eletrônico',
  'Bagagem',
  'Faísca por Obra / Manutenção',
  'Origem Indeterminada',
  'Outros'
];

const INITIAL_FORM_DATA = {
  airport: '',
  date: new Date().toISOString().split('T')[0],
  time: '',
  location: '',
  position: '',
  origin: '',
  extinguishMethod: 'Não' as 'Sim' | 'Não',
  extinguisherType: '',
  extinguishersQuantity: '',
  extinguishersLocation: '',
  seiscResponseTime: '',
  materialDamage: 'Não' as 'Sim' | 'Não' | 'Sob Análise',
  materialDamageDetails: '',
  hasInjuries: 'Não' as 'Sim' | 'Não',
  injuredPeople: [] as InjuredPerson[],
  description: ''
};

export const FirePrincipleModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [records, setRecords] = useState<FirePrincipleRecord[]>(MOCK_RECORDS);
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  
  const [actionMenuId, setActionMenuId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [detailsRecord, setDetailsRecord] = useState<FirePrincipleRecord | null>(null);

  const [filterAirport, setFilterAirport] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const [formData, setFormData] = useState(INITIAL_FORM_DATA);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedImages([...selectedImages, ...Array.from(e.target.files)]);
    }
  };

  const removeImage = (index: number) => {
    const newImages = [...selectedImages];
    newImages.splice(index, 1);
    setSelectedImages(newImages);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    setTimeout(() => {
      const newRecord: FirePrincipleRecord = {
        id: editingId || Math.random().toString(36).substr(2, 9),
        ...formData,
        status: 'Em Análise'
      };

      if (editingId) {
        setRecords(records.map(r => r.id === editingId ? newRecord : r));
      } else {
        setRecords([newRecord, ...records]);
      }

      setIsSubmitting(false);
      setActiveTab('history');
      setFormData(INITIAL_FORM_DATA);
      setSelectedImages([]);
      setEditingId(null);
    }, 1500);
  };

  const handleEdit = (record: FirePrincipleRecord) => {
    setFormData({
      airport: record.airport,
      date: record.date,
      time: record.time,
      location: record.location,
      position: record.position,
      origin: record.origin,
      extinguishMethod: record.extinguishMethod,
      extinguisherType: record.extinguisherType || '',
      extinguishersQuantity: record.extinguishersQuantity || '',
      extinguishersLocation: record.extinguishersLocation || '',
      seiscResponseTime: record.seiscResponseTime,
      materialDamage: record.materialDamage,
      materialDamageDetails: record.materialDamageDetails || '',
      hasInjuries: record.hasInjuries,
      injuredPeople: record.injuredPeople || [],
      description: record.description
    });
    setEditingId(record.id);
    setActiveTab('form');
    setActionMenuId(null);
  };

  const filteredRecords = records.filter(record => {
    const matchesAirport = filterAirport === '' || record.airport === filterAirport;
    const recordDate = new Date(record.date);
    const start = startDate ? new Date(startDate) : null;
    const end = endDate ? new Date(endDate) : null;
    const matchesDate = (!start || recordDate >= start) && (!end || recordDate <= end);
    return matchesAirport && matchesDate;
  });

  return (
    <div className="flex flex-col gap-[26px] relative h-full w-full">
      <h2 className="text-[26px] font-bold text-slate-900 tracking-tight leading-tight uppercase shrink-0 flex items-center gap-3">
        Princípio de Incêndio
      </h2>

      <div className="flex p-1 bg-slate-50 rounded-none w-fit border border-slate-200 shrink-0">
        <button
          onClick={() => { setActiveTab('form'); setEditingId(null); setFormData(INITIAL_FORM_DATA); }}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-none text-[13px] font-bold transition-all ${activeTab === 'form' ? 'bg-white text-[#391694] shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}
        >
          <PlusCircle className="w-4 h-4" />
          {editingId ? 'Editar Reporte' : 'Novo Registro'}
        </button>
        <button
          onClick={() => { setActiveTab('history'); setEditingId(null); setFormData(INITIAL_FORM_DATA); }}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-none text-[13px] font-bold transition-all ${activeTab === 'history' ? 'bg-white text-[#391694] shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}
        >
          <History className="w-4 h-4" />
          Registros
        </button>
      </div>

      <div className="flex-1 overflow-visible">
        {activeTab === 'form' ? (
          <div className="max-w-5xl animate-in fade-in duration-500 pb-10">
            {isSubmitting ? (
              <div className="flex flex-col items-center justify-center py-24 text-center animate-in zoom-in duration-300">
                <div className="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mb-6">
                  <CheckCircle2 className="w-10 h-10 text-emerald-600 animate-pulse" />
                </div>
                <h3 className="text-2xl font-bold text-slate-900 mb-2">Processando Registro...</h3>
                <p className="text-slate-500">As informações sobre o princípio de incêndio estão sendo cadastradas conforme regulamento da ANAC.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-[26px]">
                {/* Alerta de Regulamento */}
                <div className="bg-amber-50 border border-amber-200 p-6 shadow-sm">
                  <div>
                    <h4 className="text-[13px] font-bold text-amber-900 uppercase tracking-wide mb-1">Atenção</h4>
                    <p className="text-[12px] text-amber-800 font-medium leading-relaxed">
                      Todo princípio de incêndio exige o acionamento da Seção Contra Incêndio (SCI) do aeroporto (apenas aplicável nos aeroportos onde está disponível).
                    </p>
                  </div>
                </div>

                {/* Aeroporto */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Aeroporto *</label>
                  <div className="relative">
                    <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium" value={formData.airport} onChange={(e) => setFormData({...formData, airport: e.target.value})}>
                      <option value="">Selecione o aeroporto</option>
                      {AIRPORTS.map(ap => <option key={ap} value={ap}>{ap}</option>)}
                    </select>
                    <Building2 className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Data do Evento *</label>
                    <input required type="date" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium" value={formData.date} onChange={(e) => setFormData({...formData, date: e.target.value})} />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Hora do Evento (UTC) *</label>
                    <input required type="time" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium" value={formData.time} onChange={(e) => setFormData({...formData, time: e.target.value})} />
                  </div>
                </div>

                {/* Local e Posição */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Local Geral *</label>
                    <div className="relative">
                      <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium" value={formData.location} onChange={(e) => setFormData({...formData, location: e.target.value})}>
                        <option value="">Selecione o local...</option>
                        {LOCATIONS.map(loc => <option key={loc} value={loc}>{loc}</option>)}
                      </select>
                      <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Posição Detalhada *</label>
                    <input required type="text" placeholder="Ex: Box 05, Lixeira Central, Rampa Sul" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium" value={formData.position} onChange={(e) => setFormData({...formData, position: e.target.value})} />
                  </div>
                </div>

                {/* Detalhes de Combustão / Origem e Combate */}
                <div className="border border-slate-100 p-6 bg-slate-50/30 space-y-[26px]">
                  <h3 className="text-[13px] font-bold text-slate-800 uppercase tracking-widest flex items-center gap-2">
                    <Flame className="w-4 h-4 text-red-500" /> Detalhes do Incêndio e Combate
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Origem / Causa Provável *</label>
                      <div className="relative">
                        <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium" value={formData.origin} onChange={(e) => setFormData({...formData, origin: e.target.value})}>
                          <option value="">Selecione a origem...</option>
                          {FIRE_ORIGINS.map(orig => <option key={orig} value={orig}>{orig}</option>)}
                        </select>
                        <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Agente Extintor Utilizado *</label>
                      <div className="flex gap-4">
                        {['Não', 'Sim'].map((option) => (
                          <button
                            key={option}
                            type="button"
                            onClick={() => setFormData({
                              ...formData, 
                              extinguishMethod: option as 'Sim' | 'Não',
                              extinguisherType: option === 'Sim' ? (formData.extinguisherType || '') : '',
                              extinguishersQuantity: option === 'Sim' ? (formData.extinguishersQuantity || '1') : '',
                              extinguishersLocation: option === 'Sim' ? formData.extinguishersLocation : ''
                            })}
                            className={`flex-1 py-4 border rounded-none font-bold text-xs uppercase transition-all ${formData.extinguishMethod === option ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-400 border-slate-200 hover:bg-slate-50'}`}
                          >
                            {option}
                          </button>
                        ))}
                      </div>

                      {formData.extinguishMethod === 'Sim' && (
                        <div className="space-y-3 mt-3 bg-white p-4 border border-slate-200 animate-in fade-in duration-300">
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="space-y-2">
                              <label className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block">
                                Tipo do Agente Extintor *
                              </label>
                              <div className="relative">
                                <select 
                                  required={formData.extinguishMethod === 'Sim'}
                                  className="w-full px-4 py-3 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium"
                                  value={formData.extinguisherType}
                                  onChange={(e) => setFormData({...formData, extinguisherType: e.target.value})}
                                >
                                  <option value="">Selecione o tipo...</option>
                                  {EXTINGUISHER_AGENT_TYPES.map(type => (
                                    <option key={type} value={type}>{type}</option>
                                  ))}
                                </select>
                                <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                              </div>
                            </div>
                            <div className="space-y-2">
                              <label className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block">
                                Quantidade Utilizada *
                              </label>
                              <input 
                                required={formData.extinguishMethod === 'Sim'}
                                type="number"
                                min="1"
                                placeholder="Ex: 1, 2..."
                                className="w-full px-4 py-3 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                                value={formData.extinguishersQuantity}
                                onChange={(e) => setFormData({...formData, extinguishersQuantity: e.target.value})}
                              />
                            </div>
                            <div className="space-y-2">
                              <label className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block">
                                Local de Origem dos Extintores *
                              </label>
                              <input 
                                required={formData.extinguishMethod === 'Sim'}
                                type="text"
                                placeholder="Ex: Próprio veículo GSE, Caixa do Box 05..."
                                className="w-full px-4 py-3 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                                value={formData.extinguishersLocation}
                                onChange={(e) => setFormData({...formData, extinguishersLocation: e.target.value})}
                              />
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                    <div className="space-y-2">
                      <label className="text-[13px] text-slate-900 block"><span className="font-bold">Tempo de Resposta dos Bombeiros</span> <span className="italic">(caso aplicável)</span></label>
                      <div className="relative">
                        <input type="number" placeholder="Em minutos..." className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all" value={formData.seiscResponseTime} onChange={(e) => setFormData({...formData, seiscResponseTime: e.target.value})} />
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Houve Vítimas ou Lesões? *</label>
                      <div className="flex gap-4">
                        {['Não', 'Sim'].map((option) => (
                          <button
                            key={option}
                            type="button"
                            onClick={() => {
                              if (option === 'Sim' && formData.injuredPeople.length === 0) {
                                setFormData({...formData, hasInjuries: 'Sim', injuredPeople: [{ id: Math.random().toString(36).substr(2, 9), name: '', severity: INJURY_SEVERITIES[1] }]});
                              } else if (option === 'Não') {
                                setFormData({...formData, hasInjuries: 'Não', injuredPeople: []});
                              } else {
                                setFormData({...formData, hasInjuries: option as any});
                              }
                            }}
                            className={`flex-1 py-4 border rounded-none font-bold text-xs uppercase transition-all ${formData.hasInjuries === option ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-400 border-slate-200 hover:bg-slate-50'}`}
                          >
                            {option}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Danos e Vítimas */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-[26px] items-start">
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Houve Danos Materiais? *</label>
                      <div className="relative">
                        <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium" value={formData.materialDamage} onChange={(e) => setFormData({...formData, materialDamage: e.target.value as any})}>
                          <option value="Não">Não</option>
                          <option value="Sim">Sim</option>
                          <option value="Sob Análise">Sob Análise</option>
                        </select>
                        <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                      {formData.materialDamage === 'Sim' && (
                        <div className="mt-2 space-y-1.5 animate-in fade-in duration-300">
                          <label className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block">
                            Descrição dos Danos Materiais <span className="text-red-500">*</span>
                          </label>
                          <input 
                            required 
                            type="text" 
                            placeholder="Descreva os danos materiais resultantes..." 
                            className="w-full px-4 py-3 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium" 
                            value={formData.materialDamageDetails} 
                            onChange={(e) => setFormData({...formData, materialDamageDetails: e.target.value})} 
                          />
                        </div>
                      )}
                    </div>

                  {formData.hasInjuries === 'Sim' && (
                    <div className="space-y-4 border border-slate-200 p-6 bg-slate-50/50 animate-in fade-in duration-300">
                      <h4 className="text-xs font-bold text-slate-800 uppercase tracking-widest mb-4">Vítimas</h4>
                      {formData.injuredPeople.map((person, index) => (
                        <div key={person.id} className="flex flex-col md:flex-row gap-4 items-start md:items-end bg-white p-4 border border-slate-200 relative">
                          <div className="w-full md:w-1/2 space-y-2">
                            <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">Nome / Identificação *</label>
                            <input required type="text" placeholder="Ex: João Silva (Frente de rampa)" className="w-full px-4 py-3 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium" value={person.name} onChange={(e) => {
                              const newPeople = [...formData.injuredPeople];
                              newPeople[index].name = e.target.value;
                              setFormData({...formData, injuredPeople: newPeople});
                            }} />
                          </div>
                          <div className="w-full md:w-1/2 space-y-2">
                            <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">Gravidade da Lesão *</label>
                            <div className="relative">
                              <select required className="w-full px-4 py-3 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium" value={person.severity} onChange={(e) => {
                                const newPeople = [...formData.injuredPeople];
                                newPeople[index].severity = e.target.value;
                                setFormData({...formData, injuredPeople: newPeople});
                              }}>
                                {INJURY_SEVERITIES.filter(s => s !== 'Nenhuma / Ileso').map(severity => <option key={severity} value={severity}>{severity}</option>)}
                              </select>
                              <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                            </div>
                          </div>
                          {formData.injuredPeople.length > 1 && (
                            <button type="button" onClick={() => {
                              const newPeople = formData.injuredPeople.filter(p => p.id !== person.id);
                              setFormData({...formData, injuredPeople: newPeople});
                            }} className="p-3 bg-red-50 text-red-600 hover:bg-red-100 transition-colors border border-red-100 self-end mt-4 md:mt-0 shrink-0">
                              <Trash2 className="w-5 h-5" />
                            </button>
                          )}
                        </div>
                      ))}
                      <button type="button" onClick={() => {
                        setFormData({...formData, injuredPeople: [...formData.injuredPeople, { id: Math.random().toString(36).substr(2, 9), name: '', severity: INJURY_SEVERITIES[1] }]});
                      }} className="flex items-center gap-2 text-[13px] font-bold text-[#391694] hover:text-[#2a106e] transition-colors mt-2">
                        <PlusCircle className="w-4 h-4" /> Adicionar outra vítima
                      </button>
                    </div>
                  )}
                  </div>
                </div>

                {/* Dinâmica Narrativa */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Descreva o evento *</label>
                  <textarea required rows={5} placeholder="Descreva os fatos detalhadamente, desde o momento da percepção do fogo/fumaça, as etapas de combate, os envolvidos e a situação final..." className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium resize-none animate-none" value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} />
                </div>

                {/* Fotos */}
                <div className="border-t border-slate-100 pt-6">
                  <h3 className="text-sm font-bold text-slate-800 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <Camera className="w-4 h-4" /> Registro Fotográfico
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    {selectedImages.map((file, index) => (
                      <div key={index} className="relative aspect-square bg-slate-100 border border-slate-200 group">
                        <img src={URL.createObjectURL(file)} alt="Preview" className="w-full h-full object-cover" />
                        <button type="button" onClick={() => removeImage(index)} className="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"><Trash2 className="w-4 h-4" /></button>
                      </div>
                    ))}
                    <label className="flex flex-col items-center justify-center aspect-square border-2 border-dashed border-slate-300 bg-slate-50 hover:bg-red-50 hover:border-red-500 hover:text-red-600 transition-all cursor-pointer group text-slate-400">
                      <input type="file" multiple accept="image/*" className="hidden" onChange={handleImageChange} />
                      <UploadCloud className="w-8 h-8 mb-2 group-hover:scale-110 transition-transform" />
                      <span className="text-xs font-bold uppercase">Anexar</span>
                    </label>
                  </div>
                </div>

                <div className="flex justify-end pt-4">
                  <button type="submit" className="flex items-center gap-3 bg-black text-white px-10 py-4 rounded-none font-bold shadow-lg hover:scale-105 transition-all group">
                    <span>Cadastrar Reporte</span>
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              </form>
            )}
          </div>
        ) : (
          <div className="flex flex-col min-h-0 animate-in fade-in duration-500 w-full">
            {/* Filtros */}
            <div className="flex flex-col lg:flex-row gap-4 items-center justify-between bg-slate-50 p-4 rounded-none border border-slate-200 mb-[26px] shrink-0 w-full">
              <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">
                <div className="relative min-w-[240px]">
                  <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <select 
                    value={filterAirport} 
                    onChange={(e) => setFilterAirport(e.target.value)} 
                    className="w-full pl-10 pr-8 h-10 bg-white border border-slate-200 rounded-none text-sm outline-none focus:ring-2 focus:ring-[#391694]/10 focus:border-[#391694] transition-all appearance-none cursor-pointer"
                  >
                    <option value="">Todos os Aeroportos</option>
                    {AIRPORTS.map(ap => <option key={ap} value={ap}>{ap}</option>)}
                  </select>
                </div>
                <div className="flex items-center gap-2 bg-white border border-slate-200 rounded-none px-3 h-10 shadow-sm">
                  <Calendar className="w-4 h-4 text-slate-400 shrink-0" />
                  <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="text-xs font-medium text-slate-700 outline-none cursor-pointer bg-transparent" />
                  <span className="text-slate-300">|</span>
                  <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="text-xs font-medium text-slate-700 outline-none cursor-pointer bg-transparent" />
                </div>
              </div>
              <button className="flex items-center gap-2 px-6 h-10 bg-[#391694] text-white rounded-none text-xs font-bold hover:bg-[#2a106e] transition-colors shadow-sm w-full lg:w-auto">
                <FileSpreadsheet className="w-4 h-4" /> Exportar Planilha
              </button>
            </div>

            {/* Tabela de Princípios de Incêndio */}
            <div className="bg-white border border-slate-200 rounded-none shadow-sm relative overflow-x-auto w-full min-h-[320px]">
              <table className="w-full text-center border-separate border-spacing-0">
                <thead>
                  <tr className="bg-slate-50">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Data/Hora</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Localização</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Foco / Causa</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center whitespace-nowrap">Agente Extintor</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center whitespace-nowrap">Danos Físicos</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-center border-b border-slate-200 whitespace-nowrap">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredRecords.map((record, index) => {
                    const isLastRows = index >= filteredRecords.length - 2 && filteredRecords.length > 2;
                    return (
                      <tr key={record.id} className="hover:bg-slate-50/50 transition-colors">
                        <td className="px-6 py-4 text-center">
                          <div className="text-xs font-semibold text-slate-900 leading-tight">
                            {record.date.split('-').reverse().join('/')}
                          </div>
                          <div className="text-[10px] text-slate-500 font-medium">{record.time} UTC</div>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <div className="flex flex-col items-center">
                            <span className="text-xs font-semibold text-slate-900">{record.location}</span>
                            <span className="text-[10px] text-slate-500 text-center"><MapPin className="w-2.5 h-2.5 inline mr-1 -mt-0.5" />{record.position}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="text-xs font-semibold text-slate-700">{record.origin}</span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <div className="flex flex-col items-center">
                            <span className={`text-[10px] font-bold px-2 py-1 uppercase rounded-none border ${record.extinguishMethod === 'Sim' ? 'bg-emerald-50 border-emerald-200 text-emerald-600' : 'bg-slate-50 border-slate-200 text-slate-400'}`}>
                              {record.extinguishMethod === 'Sim' ? 'Sim' : 'Não'}
                            </span>
                            {record.extinguishMethod === 'Sim' && (record.extinguisherType || record.extinguishersQuantity || record.extinguishersLocation) && (
                              <span className="text-[9px] text-slate-500 font-semibold mt-1 max-w-[180px] truncate">
                                {record.extinguisherType ? `${record.extinguisherType} ` : ''}
                                {record.extinguishersQuantity ? `(${record.extinguishersQuantity} un.)` : ''} 
                                {record.extinguishersLocation ? ` • ${record.extinguishersLocation}` : ''}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <div className="flex flex-col items-center">
                            <span className={`text-[10px] font-bold uppercase ${record.materialDamage === 'Sim' ? 'text-red-600' : record.materialDamage === 'Sob Análise' ? 'text-amber-600' : 'text-slate-400'}`}>
                              {record.materialDamage === 'Sim' ? 'Com Danos' : record.materialDamage === 'Sob Análise' ? 'Sob Análise' : 'Sem Danos'}
                            </span>
                            {record.hasInjuries === 'Sim' && (
                              <span className="text-[9px] text-red-700 bg-red-50 border border-red-100 font-bold px-1.5 py-0.5 mt-1 uppercase">
                                Com Feridos
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center relative">
                          <button onClick={(e) => { e.stopPropagation(); setActionMenuId(actionMenuId === record.id ? null : record.id); }} className={`p-1.5 rounded-none transition-all ${actionMenuId === record.id ? 'bg-[#c026d3] text-white shadow-md' : 'text-slate-400 hover:text-[#c026d3] hover:bg-purple-50 border border-slate-200'}`}><MoreHorizontal className="w-5 h-5" /></button>
                          {actionMenuId === record.id && (
                            <div className={`absolute z-50 right-14 w-44 bg-white border border-slate-200 rounded-none shadow-2xl overflow-hidden animate-in fade-in slide-in-from-right-2 duration-200 ${
                              isLastRows ? 'bottom-0' : 'top-1/2 -translate-y-1/2'
                            }`}>
                              <button onClick={() => { setDetailsRecord(record); setActionMenuId(null); }} className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"><Eye className="w-3.5 h-3.5" /> Ver Detalhes</button>
                              <button onClick={() => handleEdit(record)} className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"><Pencil className="w-3.5 h-3.5" /> Editar</button>
                              <button onClick={() => { setDeleteId(record.id); setActionMenuId(null); }} className="w-full text-left px-4 py-3 text-[11px] font-bold text-red-600 hover:bg-red-50 flex items-center gap-3"><Trash2 className="w-3.5 h-3.5" /> Excluir</button>
                            </div>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                  {filteredRecords.length === 0 && (
                    <tr>
                      <td colSpan={6} className="py-12 text-center text-slate-400">
                        Nenhum registro de princípio de incêndio encontrado.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            <div className="bg-slate-50 px-6 py-3 border border-t-0 border-slate-200 text-[10px] text-slate-400 font-bold uppercase tracking-widest">{filteredRecords.length} REGISTROS ENCONTRADOS</div>
          </div>
        )}
      </div>

      {actionMenuId && <div className="fixed inset-0 z-40 bg-transparent" onClick={() => setActionMenuId(null)}></div>}
      
      {/* Exclusão do Registro */}
      {deleteId && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-white rounded-none w-full max-w-sm shadow-2xl border border-slate-100 overflow-hidden">
            <div className="p-8 text-center">
              <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6 border border-red-100"><AlertTriangle className="w-8 h-8 text-red-500" /></div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Confirmar Exclusão?</h3>
              <p className="text-slate-500 text-sm leading-relaxed mb-6">Esta ação removerá permanentemente este registro de princípio de incêndio.</p>
            </div>
            <div className="p-4 bg-slate-50 border-t border-slate-100 flex gap-3">
              <button onClick={() => setDeleteId(null)} className="flex-1 py-3 bg-white border border-slate-200 rounded-none text-xs font-bold text-slate-600 hover:bg-slate-100">Cancelar</button>
              <button onClick={() => { setRecords(records.filter(r => r.id !== deleteId)); setDeleteId(null); }} className="flex-1 py-3 bg-red-600 rounded-none text-xs font-bold text-white hover:bg-red-700 shadow-lg shadow-red-900/20">Confirmar</button>
            </div>
          </div>
        </div>
      )}

      {/* Visualização de Detalhes Completa */}
      {detailsRecord && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300 overflow-y-auto">
          <div className="bg-white rounded-none w-full max-w-2xl shadow-2xl border border-slate-100 overflow-hidden my-8">
            <div className="p-6 bg-slate-900 text-white flex items-center justify-between">
              <h3 className="text-lg font-bold uppercase tracking-tight flex items-center gap-2">
                <Flame className="w-5 h-5 text-red-400" />
                Detalhes da Ocorrência • Princípio de Incêndio
              </h3>
              <button onClick={() => setDetailsRecord(null)} className="text-slate-400 hover:text-white font-bold text-sm">Fechar</button>
            </div>
            <div className="p-8 space-y-6 max-h-[70vh] overflow-y-auto">
              {/* Grid 2 cols */}
              <div className="grid grid-cols-2 gap-6 pb-6 border-b border-slate-100">
                <div>
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Aeroporto</h4>
                  <p className="text-[13px] font-bold text-slate-800">{detailsRecord.airport}</p>
                </div>
                <div>
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Data e Hora</h4>
                  <p className="text-[13px] font-bold text-slate-800">{detailsRecord.date.split('-').reverse().join('/')} às {detailsRecord.time} UTC</p>
                </div>
                <div>
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Localização Geral</h4>
                  <p className="text-[13px] font-bold text-slate-800">{detailsRecord.location}</p>
                </div>
                <div>
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Posição Detalhada</h4>
                  <p className="text-[13px] font-bold text-slate-800">{detailsRecord.position}</p>
                </div>
              </div>

              {/* Grid de causa e extinção */}
              <div className="grid grid-cols-2 gap-6 pb-6 border-b border-slate-100">
                <div>
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Origem / Causa Provável</h4>
                  <p className="text-[13px] font-bold text-slate-800">{detailsRecord.origin}</p>
                </div>
                <div>
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Agente Extintor Utilizado</h4>
                  <p className="text-[13px] font-bold text-slate-800">{detailsRecord.extinguishMethod}</p>
                  {detailsRecord.extinguishMethod === 'Sim' && (
                    <div className="text-xs text-slate-600 mt-1 space-y-0.5 font-medium bg-slate-50 p-2 border border-slate-100">
                      {detailsRecord.extinguisherType && <p><strong>Tipo do Agente:</strong> {detailsRecord.extinguisherType}</p>}
                      {detailsRecord.extinguishersQuantity && <p><strong>Qtd Utilizada:</strong> {detailsRecord.extinguishersQuantity} extintor(es)</p>}
                      {detailsRecord.extinguishersLocation && <p><strong>Local de Origem:</strong> {detailsRecord.extinguishersLocation}</p>}
                    </div>
                  )}
                </div>
                <div>
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Tempo de Resposta SEISC</h4>
                  <p className="text-[13px] font-bold text-slate-800">{detailsRecord.seiscResponseTime}</p>
                </div>
              </div>

              {/* Danos e Vítimas */}
              <div className="grid grid-cols-2 gap-6 pb-6 border-b border-slate-100">
                <div>
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Danos Materiais</h4>
                  <p className="text-[13px] font-bold text-slate-800">{detailsRecord.materialDamage}</p>
                  {detailsRecord.materialDamage === 'Sim' && detailsRecord.materialDamageDetails && (
                    <p className="text-xs text-slate-500 mt-1">{detailsRecord.materialDamageDetails}</p>
                  )}
                </div>
                <div>
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Feridos / Vítimas</h4>
                  <p className="text-[13px] font-bold text-slate-800">{detailsRecord.hasInjuries === 'Sim' ? `${detailsRecord.injuredPeople.length} vítima(s)` : 'Não houve feridos'}</p>
                </div>
              </div>

              {/* Listagem de Vítimas */}
              {detailsRecord.hasInjuries === 'Sim' && detailsRecord.injuredPeople.length > 0 && (
                <div className="bg-red-50/50 p-4 border border-red-100 space-y-3">
                  <h4 className="text-[10px] font-black text-[#991b1b] uppercase tracking-widest flex items-center gap-1"><User className="w-3 H-3" /> Lista de Vítimas Registradas</h4>
                  {detailsRecord.injuredPeople.map((person, i) => (
                    <div key={i} className="flex justify-between items-center bg-white p-2 border border-slate-100">
                      <span className="text-xs font-bold text-slate-800">{person.name}</span>
                      <span className="text-[10px] font-bold px-2 py-0.5 bg-red-100 text-red-800 rounded-none uppercase">{person.severity.split(' ')[0]}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Descrição Narrativa */}
              <div className="space-y-2">
                <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Dinâmica da Ocorrência</h4>
                <div className="bg-slate-50 p-4 border border-slate-200 text-slate-700 text-xs leading-relaxed whitespace-pre-line">
                  {detailsRecord.description}
                </div>
              </div>

              {/* Ações imediatas removidas */}
            </div>
            <div className="p-4 bg-slate-50 border-t border-slate-100 flex justify-end">
              <button onClick={() => setDetailsRecord(null)} className="px-6 py-2.5 bg-slate-800 text-white rounded-none text-xs font-bold hover:bg-slate-900 transition-colors shadow-sm">OK, Fechar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
