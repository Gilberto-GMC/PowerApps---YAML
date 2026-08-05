import React, { useState } from 'react';
import { 
  PlusCircle, 
  History, 
  Car, 
  CheckCircle2, 
  ArrowRight,
  Calendar,
  MapPin,
  AlertTriangle,
  Camera,
  Trash2,
  UploadCloud,
  MoreHorizontal,
  Eye,
  Pencil,
  Building2,
  FileSpreadsheet,
  ChevronDown
} from 'lucide-react';
import { AIRPORTS } from './AISComplianceForm';

interface InjuredPerson {
  id: string;
  name: string;
  severity: string;
}

interface VehicleCollisionRecord {
  id: string;
  airport: string;
  date: string;
  time: string;
  originatingType: 'Veículo' | 'Equipamento' | 'Infraestrutura';
  originatingVehicle: string;
  collisionTargetType: 'Veículo' | 'Equipamento' | 'Infraestrutura';
  targetIdentification: string;
  location: string;
  position: string;
  description: string;
  driverReport: string;
  hasInjuries: 'Sim' | 'Não';
  injuredPeople: InjuredPerson[];
  status: 'Em Análise' | 'Finalizado';
}

const MOCK_RECORDS: VehicleCollisionRecord[] = [
  {
    id: '1',
    airport: 'Aeroporto de Curitiba',
    date: '2024-05-20',
    time: '14:30',
    originatingType: 'Veículo',
    originatingVehicle: 'Trator de Bagagem (TAG-01)',
    collisionTargetType: 'Veículo',
    targetIdentification: 'Van de Transporte (VAN-05)',
    location: 'Via de serviço',
    position: 'Próximo ao Portão 3',
    description: 'Colisão traseira entre trator de bagagem e van de transporte de tripulação.',
    driverReport: 'O veículo da frente freou bruscamente e não houve tempo hábil para parar o trator.',
    hasInjuries: 'Não',
    injuredPeople: [],
    status: 'Em Análise'
  },
  {
    id: '2',
    airport: 'Aeroporto de Goiânia',
    date: '2024-05-18',
    time: '09:15',
    originatingType: 'Veículo',
    originatingVehicle: 'Caminhão de Comissaria (CAM-02)',
    collisionTargetType: 'Equipamento',
    targetIdentification: 'Escada de Embarque (ESC-03)',
    location: 'Pátio de Estacionamento',
    position: 'Posição 05',
    description: 'Caminhão de comissaria colidiu levemente com a escada de embarque estacionada.',
    driverReport: 'Ponto cego no retrovisor direito durante a manobra de aproximação.',
    hasInjuries: 'Não',
    injuredPeople: [],
    status: 'Finalizado'
  }
];

const INJURY_SEVERITIES = [
  'Nenhuma / Ileso',
  'Leve (Lesão superficial ou que não requer hospitalização prolongada)',
  'Moderada (Lesão que requer tratamento médico sem risco imediato à vida)',
  'Grave (Lesão que requer hospitalização por mais de 48h ou fraturas/hemorragias)',
  'Fatal (Ocorrência que resulta em óbito)'
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

const INITIAL_FORM_DATA = {
  airport: '',
  date: new Date().toISOString().split('T')[0],
  time: '',
  originatingType: 'Veículo' as 'Veículo' | 'Equipamento' | 'Infraestrutura',
  originatingVehicle: '',
  collisionTargetType: 'Veículo' as 'Veículo' | 'Equipamento' | 'Infraestrutura',
  targetIdentification: '',
  location: '',
  position: '',
  description: '',
  driverReport: '',
  hasInjuries: 'Não' as 'Sim' | 'Não',
  injuredPeople: [] as InjuredPerson[]
};

export const VehicleCollisionModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [records, setRecords] = useState<VehicleCollisionRecord[]>(MOCK_RECORDS);
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  
  const [actionMenuId, setActionMenuId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

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
      const newRecord: VehicleCollisionRecord = {
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

  const handleEdit = (record: VehicleCollisionRecord) => {
    setFormData({
      airport: record.airport,
      date: record.date,
      time: record.time,
      originatingType: record.originatingType || 'Veículo',
      originatingVehicle: record.originatingVehicle,
      collisionTargetType: record.collisionTargetType,
      targetIdentification: record.targetIdentification,
      location: record.location,
      position: record.position,
      description: record.description,
      driverReport: record.driverReport,
      hasInjuries: record.hasInjuries,
      injuredPeople: record.injuredPeople || []
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
        Colisão de Veículos e/ou Equipamentos
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
                <p className="text-slate-500">As informações estão sendo arquivadas para análise técnica.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-[26px]">
                <div className="bg-amber-50 border border-amber-200 p-6">
                  <div>
                    <h4 className="text-[13px] font-bold text-amber-900 uppercase tracking-wide mb-1">Atenção</h4>
                    <p className="text-[13px] text-amber-800 font-medium leading-relaxed">
                      Este módulo é exclusivo para o registro de colisões envolvendo veículos e equipamentos na <strong>área operacional</strong>. A colisão pode ocorrer entre veículos/equipamentos ou entre estes e a infraestrutura.
                    </p>
                  </div>
                </div>

                {/* Aeroporto */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Aeroporto *</label>
                  <div className="relative">
                    <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.airport} onChange={(e) => setFormData({...formData, airport: e.target.value})}>
                      <option value="">Selecione o aeroporto</option>
                      {AIRPORTS.map(ap => <option key={ap} value={ap}>{ap}</option>)}
                    </select>
                    <Building2 className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Data do Evento *</label>
                    <input required type="date" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium" value={formData.date} onChange={(e) => setFormData({...formData, date: e.target.value})} />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Hora do Evento (UTC) *</label>
                    <input required type="time" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium" value={formData.time} onChange={(e) => setFormData({...formData, time: e.target.value})} />
                  </div>
                </div>

                {/* Envolvidos na Colisão */}
                <div className="border border-slate-100 p-6 bg-slate-50/30">
                  <h3 className="text-[13px] font-bold text-slate-800 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <Car className="w-4 h-4" /> Envolvidos na Colisão
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Tipo do Originador *</label>
                      <div className="relative">
                        <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.originatingType} onChange={(e) => setFormData({...formData, originatingType: e.target.value as any})}>
                          <option value="Veículo">Veículo</option>
                          <option value="Equipamento">Equipamento</option>
                          <option value="Infraestrutura">Infraestrutura</option>
                        </select>
                        <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Identificação do Originador *</label>
                      <input required type="text" placeholder="Ex: Trator de Bagagem (TAG-01)" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium" value={formData.originatingVehicle} onChange={(e) => setFormData({...formData, originatingVehicle: e.target.value})} />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Tipo do Atingido *</label>
                      <div className="relative">
                        <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.collisionTargetType} onChange={(e) => setFormData({...formData, collisionTargetType: e.target.value as any})}>
                          <option value="Veículo">Veículo</option>
                          <option value="Equipamento">Equipamento</option>
                          <option value="Infraestrutura">Infraestrutura</option>
                        </select>
                        <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Identificação do Atingido *</label>
                      <input required type="text" placeholder="Ex: Escada de Embarque / Poste de Luz" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium" value={formData.targetIdentification} onChange={(e) => setFormData({...formData, targetIdentification: e.target.value})} />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Local Geral *</label>
                    <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.location} onChange={(e) => setFormData({...formData, location: e.target.value})}>
                      <option value="">Selecione o local...</option>
                      {LOCATIONS.map(loc => <option key={loc} value={loc}>{loc}</option>)}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Posição Detalhada *</label>
                    <input required type="text" placeholder="Ex: Próximo ao Portão 3" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium" value={formData.position} onChange={(e) => setFormData({...formData, position: e.target.value})} />
                  </div>
                </div>

                {/* Lesões */}
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Houve Lesão a Pessoa(s)? *</label>
                    <div className="flex gap-4 w-full md:w-1/2">
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

                  {formData.hasInjuries === 'Sim' && (
                    <div className="space-y-4 border border-slate-200 p-6 bg-slate-50/50">
                      <h4 className="text-xs font-bold text-slate-800 uppercase tracking-widest mb-4">Vítimas</h4>
                      {formData.injuredPeople.map((person, index) => (
                        <div key={person.id} className="flex flex-col md:flex-row gap-4 items-start md:items-end bg-white p-4 border border-slate-200 relative">
                          <div className="w-full md:w-1/3 space-y-2">
                            <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">Nome / Identificação *</label>
                            <input required type="text" placeholder="Ex: João Silva (Motorista)" className="w-full px-4 py-3 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium" value={person.name} onChange={(e) => {
                              const newPeople = [...formData.injuredPeople];
                              newPeople[index].name = e.target.value;
                              setFormData({...formData, injuredPeople: newPeople});
                            }} />
                          </div>
                          <div className="w-full md:flex-1 space-y-2">
                            <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">Gravidade da Lesão *</label>
                            <div className="relative">
                              <select required className="w-full px-4 py-3 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={person.severity} onChange={(e) => {
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

                {/* Descrição e Relato */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Dinâmica do Evento e Descrição dos Danos *</label>
                  <textarea required rows={4} placeholder="Descreva como ocorreu a colisão, veículos envolvidos e os danos resultantes..." className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium resize-none" value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} />
                </div>

                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Relato do(s) Condutor(es) *</label>
                  <textarea required rows={4} placeholder="Insira o relato fornecido pelos condutores envolvidos na colisão..." className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium resize-none" value={formData.driverReport} onChange={(e) => setFormData({...formData, driverReport: e.target.value})} />
                </div>

                {/* Fotos */}
                <div className="border-t border-slate-100 pt-6">
                  <h3 className="text-sm font-bold text-slate-800 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <Camera className="w-4 h-4" /> Registro Fotográfico e Evidências
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    {selectedImages.map((file, index) => (
                      <div key={index} className="relative aspect-square bg-slate-100 border border-slate-200 group">
                        <img src={URL.createObjectURL(file)} alt="Preview" className="w-full h-full object-cover" />
                        <button type="button" onClick={() => removeImage(index)} className="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"><Trash2 className="w-4 h-4" /></button>
                      </div>
                    ))}
                    <label className="flex flex-col items-center justify-center aspect-square border-2 border-dashed border-slate-300 bg-slate-50 hover:bg-purple-50 hover:border-[#c026d3] hover:text-[#c026d3] transition-all cursor-pointer group text-slate-400">
                      <input type="file" multiple accept="image/*" className="hidden" onChange={handleImageChange} />
                      <UploadCloud className="w-8 h-8 mb-2 group-hover:scale-110 transition-transform" />
                      <span className="text-xs font-bold uppercase text-center px-2">Anexar Evidências</span>
                    </label>
                  </div>
                </div>

                <div className="flex justify-end pt-4">
                  <button type="submit" className="flex items-center gap-3 bg-black text-white px-10 py-4 rounded-none font-bold shadow-lg hover:scale-105 transition-all group">
                    <span>Finalizar Reporte</span>
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
                <FileSpreadsheet className="w-4 h-4" /> Exportar
              </button>
            </div>

            {/* Tabela */}
            <div className="bg-white border border-slate-200 rounded-none shadow-sm relative overflow-x-auto w-full min-h-[320px]">
              <table className="w-full text-center border-separate border-spacing-0">
                <thead>
                  <tr className="bg-slate-50">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Data/Hora</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Localização</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Envolvidos</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center whitespace-nowrap">Lesão / Gravidade</th>
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
 <span className="text-[10px] text-slate-500 flex items-center gap-1 justify-center"><MapPin className="w-2.5 h-2.5" />{record.position}</span>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex flex-col items-center">
 <span className="text-xs font-bold text-slate-900">{record.originatingType}: {record.originatingVehicle}</span>
 <span className="text-[10px] text-slate-500 font-medium">colidiu com {record.collisionTargetType.toLowerCase()}: {record.targetIdentification}</span>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex flex-col items-center">
 <span className={`text-[10px] font-bold uppercase ${record.hasInjuries === 'Sim' ? 'text-red-600' : 'text-slate-400'}`}>
 {record.hasInjuries === 'Sim' ? 'Com Lesão' : 'Sem Lesão'}
 </span>
 {record.hasInjuries === 'Sim' && (
 <span className="text-[9px] text-slate-500 font-bold bg-slate-50 px-1.5 py-0.5 border border-slate-200 mt-1 uppercase">
 {record.injuredPeople?.length || 1} Vítima(s)
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
 <button onClick={() => setActionMenuId(null)} className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"><Eye className="w-3.5 h-3.5" /> Ver Detalhes</button>
 <button onClick={() => handleEdit(record)} className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"><Pencil className="w-3.5 h-3.5" /> Editar</button>
 <button onClick={() => { setDeleteId(record.id); setActionMenuId(null); }} className="w-full text-left px-4 py-3 text-[11px] font-bold text-red-600 hover:bg-red-50 flex items-center gap-3"><Trash2 className="w-3.5 h-3.5" /> Excluir</button>
 </div>
 )}
 </td>
                    </tr>
                  )})}
                  {filteredRecords.length === 0 && (
                    <tr>
                      <td colSpan={5} className="py-12 text-center text-slate-400">
 Nenhuma colisão encontrada.
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
      
      {deleteId && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-white rounded-none w-full max-w-sm shadow-2xl border border-slate-100 overflow-hidden">
            <div className="p-8 text-center">
              <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6 border border-red-100"><AlertTriangle className="w-8 h-8 text-red-500" /></div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Confirmar Exclusão?</h3>
              <p className="text-slate-500 text-sm leading-relaxed mb-6">Esta ação removerá permanentemente o registro de colisão do banco de dados.</p>
            </div>
            <div className="p-4 bg-slate-50 border-t border-slate-100 flex gap-3">
              <button onClick={() => setDeleteId(null)} className="flex-1 py-3 bg-white border border-slate-200 rounded-none text-xs font-bold text-slate-600 hover:bg-slate-100">Cancelar</button>
              <button onClick={() => { setRecords(records.filter(r => r.id !== deleteId)); setDeleteId(null); }} className="flex-1 py-3 bg-red-600 rounded-none text-xs font-bold text-white hover:bg-red-700 shadow-lg shadow-red-900/20">Confirmar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
