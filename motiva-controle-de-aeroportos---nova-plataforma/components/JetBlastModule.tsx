
import React, { useState } from 'react';
import { 
  PlusCircle, 
  History, 
  Wind, 
  CheckCircle2, 
  ArrowRight,
  Calendar,
  Clock,
  Plane,
  MapPin,
  AlertTriangle,
  Camera,
  Trash2,
  FileText,
  UploadCloud,
  Filter,
  MoreHorizontal,
  Eye,
  Pencil,
  Building2,
  ChevronDown,
  FileSpreadsheet,
  Zap,
  User,
  ShieldAlert
} from 'lucide-react';
import { AIRPORTS } from './AISComplianceForm';

interface JetBlastRecord {
  id: string;
  airport: string;
  date: string;
  time: string;
  originatorRegistration: string;
  originatorModel: string;
  originatorOperator: string;
  affectedType: 'Aeronave' | 'Veículo' | 'Equipamento' | 'Infraestrutura' | 'Pessoa';
  affectedDetail: string; // Matrícula ou ID do afetado
  location: string;
  position: string;
  description: string;
  status: 'Em Análise' | 'Finalizado';
}

const MOCK_RECORDS: JetBlastRecord[] = [
  {
    id: '1',
    airport: 'Aeroporto de Curitiba',
    date: '2024-05-18',
    time: '11:20',
    originatorRegistration: 'PR-XLA',
    originatorModel: 'B738',
    originatorOperator: 'Gol Linhas Aéreas',
    affectedType: 'Equipamento',
    affectedDetail: 'Escada de Manutenção',
    location: 'Pátio de Estacionamento',
    position: 'Posição 05',
    description: 'Sopro durante acionamento de motores tombou escada de manutenção que não estava travada.',
    status: 'Em Análise'
  },
  {
    id: '2',
    airport: 'Aeroporto de Navegantes',
    date: '2024-05-15',
    time: '16:45',
    originatorRegistration: 'PS-ADU',
    originatorModel: 'A320',
    originatorOperator: 'Azul Linhas Aéreas',
    affectedType: 'Veículo',
    affectedDetail: 'Caminhão de Bagagem (V-12)',
    location: 'Pátio de Estacionamento',
    position: 'Posição 02',
    description: 'Deslocamento de cones e sinalização devido ao jet-blast na saída da posição.',
    status: 'Finalizado'
  }
];

const AFFECTED_TYPES = [
  'Aeronave',
  'Veículo',
  'Equipamento',
  'Infraestrutura',
  'Pessoa'
];

const LOCATIONS = [
  'Pátio de Estacionamento',
  'Pista de Táxi',
  'Pista de Pouso e Decolagem',
  'Via de serviço',
  'Pátio de Hangar',
  'Área de Equipamentos'
];

const INITIAL_FORM_DATA = {
  airport: '',
  date: new Date().toISOString().split('T')[0],
  time: '',
  originatorRegistration: '',
  originatorModel: '',
  originatorOperator: '',
  affectedType: '' as any,
  affectedDetail: '',
  location: '',
  position: '',
  description: ''
};

export const JetBlastModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [records, setRecords] = useState<JetBlastRecord[]>(MOCK_RECORDS);
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  
  const [actionMenuId, setActionMenuId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  const [filterAirport, setFilterAirport] = useState('');
  const [filterAffected, setFilterAffected] = useState('');
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
      const newRecord: JetBlastRecord = {
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

  const handleEdit = (record: JetBlastRecord) => {
    setFormData({
      airport: record.airport,
      date: record.date,
      time: record.time,
      originatorRegistration: record.originatorRegistration,
      originatorModel: record.originatorModel,
      originatorOperator: record.originatorOperator,
      affectedType: record.affectedType,
      affectedDetail: record.affectedDetail,
      location: record.location,
      position: record.position,
      description: record.description
    });
    setEditingId(record.id);
    setActiveTab('form');
    setActionMenuId(null);
  };

  const filteredRecords = records.filter(record => {
    const matchesAirport = filterAirport === '' || record.airport === filterAirport;
    const matchesAffected = filterAffected === '' || record.affectedType === filterAffected;
    const recordDate = new Date(record.date);
    const start = startDate ? new Date(startDate) : null;
    const end = endDate ? new Date(endDate) : null;
    const matchesDate = (!start || recordDate >= start) && (!end || recordDate <= end);
    return matchesAirport && matchesAffected && matchesDate;
  });

  return (
    <div className="flex flex-col gap-[26px] relative h-full w-full">
      <h2 className="text-[26px] font-bold text-slate-900 tracking-tight leading-tight uppercase shrink-0 flex items-center gap-3">
        Jet-blast / Propeller-Wash
      </h2>

      <div className="flex p-1 bg-slate-50 rounded-none w-fit border border-slate-200 shrink-0">
        <button
          onClick={() => { setActiveTab('form'); setEditingId(null); setFormData(INITIAL_FORM_DATA); }}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-none text-[13px] font-bold transition-all ${activeTab === 'form' ? 'bg-white text-[#391694] shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}
        >
          <PlusCircle className="w-4 h-4" />
          {editingId ? 'Editar Registro' : 'Novo Registro'}
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
                <h3 className="text-2xl font-bold text-slate-900 mb-2">{editingId ? 'Atualizando...' : 'Registrando Ocorrência...'}</h3>
                <p className="text-slate-500">A análise do evento está sendo processada.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-[26px]">
                {/* Alerta de Segurança */}
                <div className="bg-amber-50 border border-amber-200 p-6">
                  <div>
                    <h4 className="text-[13px] font-bold text-amber-900 uppercase tracking-wide mb-1">Atenção</h4>
                    <p className="text-[13px] text-amber-800 font-medium leading-relaxed">
                      RBAC 153.111 - Movimentação de aeronaves, veículos, equipamentos e pessoas na área operacional:<br />
                      (h) Quanto à movimentação de aeronaves na área de movimento, o operador de aeródromo deve assegurar que a velocidade de exaustão de gases dos motores das aeronaves posicionadas em direção a edificações, equipamentos, veículos e pessoas, durante operações aéreas, não ultrapasse <strong>56 km/h</strong> quando atingir estes elementos.
                    </p>
                  </div>
                </div>

                {/* Aeroporto em linha única */}
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

                {/* Aeronave Causadora */}
                <div className="border border-slate-100 p-6 bg-slate-50/30">
                  <h3 className="text-[13px] font-bold text-slate-800 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <Plane className="w-4 h-4" /> Aeronave Causadora (Origem do Sopro)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-[26px]">
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Matrícula *</label>
                      <input required type="text" placeholder="Ex: PR-ABC" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium uppercase" value={formData.originatorRegistration} onChange={(e) => setFormData({...formData, originatorRegistration: e.target.value})} />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Modelo *</label>
                      <input required type="text" placeholder="Ex: B738" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium uppercase" value={formData.originatorModel} onChange={(e) => setFormData({...formData, originatorModel: e.target.value})} />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Operador *</label>
                      <input required type="text" placeholder="Ex: Gol Linhas Aéreas" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium" value={formData.originatorOperator} onChange={(e) => setFormData({...formData, originatorOperator: e.target.value})} />
                    </div>
                  </div>
                </div>

                {/* Entidade Afetada */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Entidade Afetada *</label>
                    <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.affectedType} onChange={(e) => setFormData({...formData, affectedType: e.target.value as any})}>
                      <option value="">Selecione o que foi afetado...</option>
                      {AFFECTED_TYPES.map(type => <option key={type} value={type}>{type}</option>)}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Identificação do Afetado *</label>
                    <input required type="text" placeholder="Ex: PT-XYZ, Veículo CCR-002, Hangar Voar..." className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium" value={formData.affectedDetail} onChange={(e) => setFormData({...formData, affectedDetail: e.target.value})} />
                  </div>
                </div>

                {/* Localização */}
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
                    <input required type="text" placeholder="Ex: Posição 05 ou Via de Serviço Bravo" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium" value={formData.position} onChange={(e) => setFormData({...formData, position: e.target.value})} />
                  </div>
                </div>

                {/* Descrição */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Descrição do Evento e Danos Observados *</label>
                  <textarea required rows={4} placeholder="Descreva como ocorreu o sopro e quais os danos resultantes..." className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium resize-none" value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} />
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
                    <label className="flex flex-col items-center justify-center aspect-square border-2 border-dashed border-slate-300 bg-slate-50 hover:bg-purple-50 hover:border-[#c026d3] hover:text-[#c026d3] transition-all cursor-pointer group text-slate-400">
                      <input type="file" multiple accept="image/*" className="hidden" onChange={handleImageChange} />
                      <UploadCloud className="w-8 h-8 mb-2 group-hover:scale-110 transition-transform" />
                      <span className="text-xs font-bold uppercase">Anexar</span>
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
                <div className="relative min-w-[240px]">
                  <ShieldAlert className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <select 
                    value={filterAffected} 
                    onChange={(e) => setFilterAffected(e.target.value)} 
                    className="w-full pl-10 pr-8 h-10 bg-white border border-slate-200 rounded-none text-sm outline-none focus:ring-2 focus:ring-[#391694]/10 focus:border-[#391694] transition-all appearance-none cursor-pointer"
                  >
                    <option value="">Todas as Entidades</option>
                    {AFFECTED_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
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

            <div className="bg-white border border-slate-200 rounded-none shadow-sm relative overflow-x-auto w-full min-h-[320px]">
              <table className="w-full text-center border-separate border-spacing-0">
                <thead>
                  <tr className="bg-slate-50">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Data/Hora</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Acft Causadora</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Afetado</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Local</th>
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
 <span className="text-xs font-bold text-slate-700 uppercase">{record.originatorRegistration}</span>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex flex-col items-center">
 <span className="text-xs font-semibold text-slate-900">{record.affectedType}</span>
 <span className="text-[10px] text-slate-500">{record.affectedDetail}</span>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex items-center gap-2 justify-center">
 <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
 <span className="text-xs font-medium text-slate-700">{record.location}</span>
 </div>
 <span className="text-[11px] text-slate-400 block ">{record.position}</span>
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
 Nenhum registro encontrado.
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
              <p className="text-slate-500 text-sm leading-relaxed mb-6">Esta ação não poderá ser desfeita. O registro será removido permanentemente.</p>
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
