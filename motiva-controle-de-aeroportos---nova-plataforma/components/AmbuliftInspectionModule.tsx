import React, { useState } from 'react';
import { 
  PlusCircle, 
  RotateCcw, 
  CheckCircle2, 
  ArrowRight,
  Accessibility,
  Upload,
  AlertCircle,
  XCircle,
  ChevronDown,
  Camera,
  UploadCloud,
  MoreHorizontal,
  Eye,
  Pencil,
  Trash2,
  AlertTriangle,
  History
} from 'lucide-react';

interface CheckItem {
  id: string;
  label: string;
  subLabel?: string;
}

const CHECK_ITEMS: CheckItem[] = [
  { id: 'fuel', label: '1. Nível de combustível (acima de ¼) ou carga da bateria (acima de 50%)' },
  { id: 'platform', label: '2. Integridade da estrutura, plataforma e corrimãos.' },
  { id: 'seatbelts', label: '3. Funcionamento dos cintos de segurança.', subLabel: 'Para Ambulifts sem cintos, marque CONFORME.' },
  { id: 'doors', label: '4. Portas e fechaduras' },
  { id: 'signals', label: '5. Sinalização luminosa e sonora' },
  { id: 'leaks', label: '6. Presença de vazamentos (óleo, fluido hidráulico, combustível)' },
  { id: 'cleaning', label: '7. Limpeza interna e externa da cabine' }
];

const AIRPORTS = [
  'Aeroporto de Bagé',
  'Aeroporto de Uruguaiana',
  'Aeroporto de Pelotas',
  'Aeroporto de Navegantes',
  'Aeroporto de Joinville',
  'Aeroporto de Londrina',
  'Aeroporto de Foz do Iguaçu',
  'Aeroporto de Bacacheri',
  'Aeroporto de Curitiba',
  'Aeroporto da Pampulha',
  'Aeroporto de Goiânia',
  'Aeroporto de Palmas',
  'Aeroporto de Imperatriz',
  'Aeroporto de Teresina',
  'Aeroporto de Petrolina',
  'Aeroporto de São Luís'
];

interface InspectionRecord {
  id: string;
  airport: string;
  date: string;
  time: string;
  equipmentPrefix: string;
  status: 'Conforme' | 'Não Conforme';
}

const MOCK_RECORDS: InspectionRecord[] = [
  {
    id: '1',
    airport: 'SBGR',
    date: '2024-05-18',
    time: '08:00',
    equipmentPrefix: 'AMB-01',
    status: 'Conforme'
  },
  {
    id: '2',
    airport: 'SBKP',
    date: '2024-05-17',
    time: '14:30',
    equipmentPrefix: 'AMB-02',
    status: 'Não Conforme'
  }
];

export const AmbuliftInspectionModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [records, setRecords] = useState<InspectionRecord[]>(MOCK_RECORDS);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const [isViewing, setIsViewing] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [showConectaAlert, setShowConectaAlert] = useState(false);

  const [formData, setFormData] = useState({
    airport: '',
    date: new Date().toISOString().split('T')[0],
    time: new Date().toTimeString().split(' ')[0].substring(0, 5),
    equipmentPrefix: ''
  });

  const [checks, setChecks] = useState<Record<string, 'Conforme' | 'Não Conforme' | ''>>({});
  const [observations, setObservations] = useState<Record<string, string>>({});
  const [attachments, setAttachments] = useState<File[]>([]);

  const resetForm = () => {
    setFormData({
      airport: '',
      date: new Date().toISOString().split('T')[0],
      time: new Date().toTimeString().split(' ')[0].substring(0, 5),
      equipmentPrefix: ''
    });
    setChecks({});
    setObservations({});
    setAttachments([]);
    setIsViewing(false);
    setEditingId(null);
  };

  const handleView = (record: InspectionRecord) => {
    setFormData({
      airport: record.airport,
      date: record.date,
      time: record.time,
      equipmentPrefix: record.equipmentPrefix
    });
    // For a real app, you would also load checks and observations here
    setIsViewing(true);
    setEditingId(null);
    setActiveTab('form');
    setOpenMenuId(null);
  };

  const handleEdit = (record: InspectionRecord) => {
    setFormData({
      airport: record.airport,
      date: record.date,
      time: record.time,
      equipmentPrefix: record.equipmentPrefix
    });
    // For a real app, you would also load checks and observations here
    setIsViewing(false);
    setEditingId(record.id);
    setActiveTab('form');
    setOpenMenuId(null);
  };

  const handleDelete = () => {
    if (deleteId) {
      setRecords(records.filter(r => r.id !== deleteId));
      setDeleteId(null);
    }
  };

  const handleCheckChange = (id: string, value: 'Conforme' | 'Não Conforme') => {
    setChecks(prev => ({ ...prev, [id]: value }));
    if (value === 'Conforme') {
      setObservations(prev => {
        const newObs = { ...prev };
        delete newObs[id];
        return newObs;
      });
    }
  };

  const handleObservationChange = (id: string, value: string) => {
    setObservations(prev => ({ ...prev, [id]: value }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setAttachments(Array.from(e.target.files));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Check if all items are evaluated
    const allChecked = CHECK_ITEMS.every(item => checks[item.id]);
    if (!allChecked) {
      alert('Por favor, avalie todos os itens do checklist.');
      return;
    }

    // Check if all non-conforming items have observations
    const allNonConformingHaveObs = CHECK_ITEMS.every(item => {
      if (checks[item.id] === 'Não Conforme') {
        return !!observations[item.id]?.trim();
      }
      return true;
    });

    if (!allNonConformingHaveObs) {
      alert('Por favor, preencha as observações para todos os itens não conformes.');
      return;
    }

    const hasNonConformity = Object.values(checks).includes('Não Conforme');
    if (hasNonConformity) {
      setShowConectaAlert(true);
    } else {
      executeSubmit();
    }
  };

  const executeSubmit = () => {
    setShowConectaAlert(false);
    setIsSubmitting(true);

    setTimeout(() => {
      const hasNonConformity = Object.values(checks).includes('Não Conforme');
      
      const newRecord: InspectionRecord = {
        id: editingId || Math.random().toString(36).substr(2, 9),
        ...formData,
        status: hasNonConformity ? 'Não Conforme' : 'Conforme'
      };

      if (editingId) {
        setRecords(records.map(r => r.id === editingId ? newRecord : r));
      } else {
        setRecords([newRecord, ...records]);
      }
      setIsSubmitting(false);
      setActiveTab('history');
      
      resetForm();
    }, 1500);
  };

  return (
    <div className="flex flex-col gap-[26px] relative h-full w-full">
      {/* Header */}
      <h2 className="text-[26px] font-bold text-slate-900 tracking-tight leading-tight uppercase shrink-0 flex items-center gap-3">
        Inspeção do Ambulift
      </h2>

      {/* Tabs */}
      <div className="flex p-1 bg-slate-50 rounded-none w-fit border border-slate-200 shrink-0">
        <button
          onClick={() => { setActiveTab('form'); resetForm(); }}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-none text-[13px] font-bold transition-all ${
            activeTab === 'form' 
              ? 'bg-white text-[#391694] shadow-sm' 
              : 'text-slate-400 hover:text-slate-600'
          }`}
        >
          <PlusCircle className="w-4 h-4" />
          {isViewing ? 'Ver Inspeção' : editingId ? 'Editar Inspeção' : 'Novo Registro'}
        </button>
        <button
          onClick={() => { setActiveTab('history'); resetForm(); }}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-none text-[13px] font-bold transition-all ${
            activeTab === 'history' 
              ? 'bg-white text-[#391694] shadow-sm' 
              : 'text-slate-400 hover:text-slate-600'
          }`}
        >
          <History className="w-4 h-4" />
          Registros
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-visible">
        {activeTab === 'form' ? (
          <div className="max-w-5xl animate-in fade-in duration-500 pb-10">
            {isSubmitting ? (
              <div className="flex flex-col items-center justify-center py-24 text-center animate-in zoom-in duration-300">
                <div className="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mb-6">
                  <CheckCircle2 className="w-10 h-10 text-emerald-600 animate-pulse" />
                </div>
                <h3 className="text-2xl font-bold text-slate-900 mb-2">Registrando Inspeção...</h3>
                <p className="text-slate-500">A inspeção do Ambulift está sendo salva no sistema.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-[26px]">
                
                {/* General Info */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Aeroporto *
                    </label>
                    <div className="relative">
                      <select
                        required
                        disabled={isViewing}
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all appearance-none cursor-pointer font-medium disabled:bg-slate-50 disabled:cursor-not-allowed"
                        value={formData.airport}
                        onChange={(e) => setFormData({...formData, airport: e.target.value})}
                      >
                        <option value="">Selecione a localidade</option>
                        {AIRPORTS.map(airport => (
                          <option key={airport} value={airport}>{airport}</option>
                        ))}
                      </select>
                      <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Prefixo do Equipamento *
                    </label>
                    <input
                      required
                      disabled={isViewing}
                      type="text"
                      placeholder="Ex: AMB-01"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all font-medium uppercase disabled:bg-slate-50 disabled:cursor-not-allowed"
                      value={formData.equipmentPrefix}
                      onChange={(e) => setFormData({...formData, equipmentPrefix: e.target.value})}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Data *
                    </label>
                    <input
                      required
                      disabled={isViewing}
                      type="date"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all disabled:bg-slate-50 disabled:cursor-not-allowed"
                      value={formData.date}
                      onChange={(e) => setFormData({...formData, date: e.target.value})}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Hora do Início da Inspeção(UTC) *
                    </label>
                    <input
                      required
                      disabled={isViewing}
                      type="time"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all disabled:bg-slate-50 disabled:cursor-not-allowed"
                      value={formData.time}
                      onChange={(e) => setFormData({...formData, time: e.target.value})}
                    />
                  </div>
                </div>

                {/* Checklist */}
                <div className="mt-8">
                  <h3 className="text-lg font-bold text-slate-900 mb-4 uppercase tracking-wider">Checklist de Inspeção</h3>
                  <div className="space-y-4">
                    {CHECK_ITEMS.map((item) => (
                      <div key={item.id} className="bg-slate-50 border border-slate-200 p-4 rounded-none flex flex-col gap-4">
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                          <div className="flex flex-col">
                            <span className="text-[13px] font-bold text-slate-800">{item.label}</span>
                            {item.subLabel && (
                              <span className="text-xs font-bold text-slate-600 mt-1">{item.subLabel}</span>
                            )}
                          </div>
                          <div className="flex items-center gap-2 shrink-0">
                            <button
                              type="button"
                              disabled={isViewing}
                              onClick={() => handleCheckChange(item.id, 'Conforme')}
                              className={`px-4 py-2 text-xs font-bold uppercase tracking-widest border transition-all disabled:cursor-not-allowed ${
                                checks[item.id] === 'Conforme'
                                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                                  : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-100'
                              }`}
                            >
                              Conforme
                            </button>
                            <button
                              type="button"
                              disabled={isViewing}
                              onClick={() => handleCheckChange(item.id, 'Não Conforme')}
                              className={`px-4 py-2 text-xs font-bold uppercase tracking-widest border transition-all disabled:cursor-not-allowed ${
                                checks[item.id] === 'Não Conforme'
                                  ? 'bg-red-50 text-red-700 border-red-200'
                                  : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-100'
                              }`}
                            >
                              Não Conforme
                            </button>
                          </div>
                        </div>
                        
                        {checks[item.id] === 'Não Conforme' && (
                          <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                            <textarea
                              required
                              disabled={isViewing}
                              placeholder="Descreva o que está errado..."
                              className="w-full px-4 py-3 bg-white border border-red-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-400 outline-none focus:border-red-400 transition-all min-h-[80px] resize-y disabled:bg-slate-50 disabled:cursor-not-allowed"
                              value={observations[item.id] || ''}
                              onChange={(e) => handleObservationChange(item.id, e.target.value)}
                            />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Divider */}
                <div className="h-px bg-slate-200 my-8 w-full"></div>

                {/* Attachments */}
                <div className="mt-8">
                  <h3 className="text-[13px] font-bold text-slate-900 mb-4 uppercase tracking-wider flex items-center gap-2">
                    <Camera className="w-4 h-4" />
                    Registro Fotográfico
                  </h3>
                  <div className={`border-2 border-dashed border-[#C9C5E6] bg-white w-48 h-48 flex flex-col items-center justify-center text-center relative transition-colors ${isViewing ? 'opacity-50 cursor-not-allowed' : 'hover:bg-slate-50 cursor-pointer'}`}>
                    <input 
                      type="file" 
                      multiple 
                      disabled={isViewing}
                      onChange={handleFileChange}
                      className={`absolute inset-0 w-full h-full opacity-0 ${isViewing ? 'cursor-not-allowed' : 'cursor-pointer'}`}
                    />
                    <UploadCloud className="w-8 h-8 text-[#8B93A7] mb-3" strokeWidth={1.5} />
                    <span className="text-[11px] font-bold text-[#8B93A7] uppercase tracking-widest">Anexar</span>
                    
                    {attachments.length > 0 && (
                      <div className="absolute -bottom-12 left-0 w-max flex flex-wrap gap-2 z-10">
                        {attachments.map((file, idx) => (
                          <span key={idx} className="bg-white border border-slate-200 px-3 py-1 text-xs font-medium text-slate-600 rounded-none flex items-center gap-2 shadow-sm">
                            {file.name}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {!isViewing && (
                  <div className="flex justify-end pt-4">
                    <button
                      type="submit"
                      className="flex items-center gap-3 bg-black text-white px-10 py-4 rounded-none font-bold shadow-lg hover:scale-105 transition-all group"
                    >
                      <span>{editingId ? 'Atualizar Inspeção' : 'Registrar Inspeção'}</span>
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </button>
                  </div>
                )}
              </form>
            )}
          </div>
        ) : (
          <div className="flex flex-col min-h-0 animate-in fade-in duration-500 w-full space-y-6">
            
            {/* Filters */}
            <div className="flex flex-col md:flex-row gap-4 bg-white p-4 border border-slate-200 rounded-none">
              <div className="flex-1 relative">
                <select className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all appearance-none cursor-pointer font-medium pl-10">
                  <option value="">Todos os Aeroportos</option>
                  {AIRPORTS.map(airport => (
                    <option key={airport} value={airport}>{airport}</option>
                  ))}
                </select>
                <div className="absolute left-3 top-1/2 -translate-y-1/2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-slate-400"><path d="M3 21h18"/><path d="M9 8h1"/><path d="M9 12h1"/><path d="M9 16h1"/><path d="M14 8h1"/><path d="M14 12h1"/><path d="M14 16h1"/><path d="M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16"/></svg>
                </div>
              </div>

              <div className="flex-1 flex items-center gap-2">
                <div className="relative flex-1">
                  <input type="date" className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all" />
                </div>
                <span className="text-slate-300">|</span>
                <div className="relative flex-1">
                  <input type="date" className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all" />
                </div>
              </div>

              <button className="bg-[#391694] text-white px-8 py-2.5 rounded-none text-[13px] font-bold flex items-center justify-center gap-2 hover:bg-[#2a0f70] transition-colors">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                Exportar
              </button>
            </div>

            <div className="bg-white border border-slate-200 rounded-none shadow-sm relative overflow-x-auto w-full">
              <table className="w-full text-center border-separate border-spacing-0 table-fixed">
                <thead>
                  <tr className="bg-slate-50">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 w-1/5 text-center">Data/Hora</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 w-1/5 text-center">Aeroporto</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 w-1/5 text-center">Equipamento</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 w-1/5 text-center">Status</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 w-1/5 text-center">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {records.map((record) => (
                    <tr key={record.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 text-center">
 <div className="flex flex-col items-center">
 <div className="text-xs font-semibold text-slate-900 leading-tight">{record.date.split('-').reverse().join('/')}</div>
 <div className="text-[10px] text-slate-500 font-medium">{record.time} UTC</div>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="text-xs text-slate-700 font-medium whitespace-normal leading-tight max-w-[200px] mx-auto">{record.airport}</div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="text-xs font-bold text-slate-700">{record.equipmentPrefix}</div>
 </td>
                      <td className="px-6 py-4 text-center">
 {record.status === 'Conforme' ? (
 <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-sm inline-flex items-center gap-1 justify-center">
 <CheckCircle2 className="w-3 h-3" />
 CONFORME
 </span>
 ) : (
 <span className="bg-red-100 text-red-800 text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-sm inline-flex items-center gap-1 justify-center">
 <XCircle className="w-3 h-3" />
 NÃO CONFORME
 </span>
 )}
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="relative flex justify-center">
 <button 
 onClick={(e) => {
 e.stopPropagation();
 setOpenMenuId(openMenuId === record.id ? null : record.id);
 }}
 onBlur={() => setTimeout(() => setOpenMenuId(null), 200)}
 className={`p-1.5 rounded-none transition-all ${openMenuId === record.id ? 'bg-[#391694] text-white shadow-md' : 'text-slate-400 hover:text-[#391694] hover:bg-purple-50 border border-slate-200'}`}
 aria-label="Ações"
 >
 <MoreHorizontal className="w-5 h-5" />
 </button>
 
 {openMenuId === record.id && (
 <div className="absolute z-50 right-1/2 translate-x-1/2 top-full mt-1 w-44 bg-white border border-slate-200 rounded-none shadow-2xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
 <button 
 onClick={() => handleView(record)}
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"
 >
 <Eye className="w-3.5 h-3.5" /> Ver Registro
 </button>
 <button 
 onClick={() => handleEdit(record)}
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"
 >
 <Pencil className="w-3.5 h-3.5" /> Editar
 </button>
 <button 
 onClick={() => setDeleteId(record.id)}
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-red-600 hover:bg-red-50 flex items-center gap-3"
 >
 <Trash2 className="w-3.5 h-3.5" /> Excluir
 </button>
 </div>
 )}
 </div>
 </td>
                    </tr>
                  ))}
                  {records.length === 0 && (
                     <tr>
                        <td colSpan={5} className="py-12 text-center text-slate-400">
 Nenhum registro encontrado.
 </td>
                     </tr>
                  )}
                </tbody>
              </table>
              <div className="bg-slate-50 px-6 py-3 border-t border-slate-200">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{records.length} REGISTROS ENCONTRADOS</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {deleteId && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-none shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-200">
            <div className="p-8 text-center">
              <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
                <AlertTriangle className="w-8 h-8 text-red-500" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 tracking-tight mb-2">Confirmar Exclusão?</h3>
              <p className="text-slate-500 text-sm leading-relaxed mb-6">
                Esta ação não poderá ser desfeita. O registro será removido permanentemente do sistema.
              </p>
            </div>
            <div className="p-4 bg-slate-50/50 border-t border-slate-100 flex gap-3">
              <button
                onClick={() => setDeleteId(null)}
                className="flex-1 px-4 py-3 text-[13px] font-bold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 hover:text-slate-900 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleDelete}
                className="flex-1 px-4 py-3 text-[13px] font-bold text-white bg-[#dc2626] hover:bg-[#b91c1c] transition-colors shadow-sm"
              >
                Confirmar Exclusão
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Conecta Alert Modal */}
      {showConectaAlert && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-none shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-200">
            <div className="p-8 text-center">
              <div className="w-16 h-16 bg-amber-50 rounded-full flex items-center justify-center mx-auto mb-6">
                <AlertTriangle className="w-8 h-8 text-amber-500" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 tracking-tight mb-2">Atenção: Abertura de Protocolo</h3>
              <p className="text-slate-500 text-sm leading-relaxed mb-6">
                Como há itens marcados como <strong>NÃO CONFORME</strong>, é obrigatório abrir um protocolo na plataforma <strong>CONECTA</strong>, no serviço <strong>Manutenção de Frotas</strong>.
                <br /><br />
                <strong>Exceção:</strong> Nos casos de equipamento sujo, acione a equipe terceirizada local.
              </p>
            </div>
            <div className="p-4 bg-slate-50/50 border-t border-slate-100 flex gap-3">
              <button
                onClick={() => setShowConectaAlert(false)}
                className="flex-1 px-4 py-3 text-[13px] font-bold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 hover:text-slate-900 transition-colors"
              >
                Revisar Inspeção
              </button>
              <button
                onClick={executeSubmit}
                className="flex-1 px-4 py-3 text-[13px] font-bold text-white bg-[#391694] hover:bg-[#2a0f70] transition-colors shadow-sm"
              >
                Estou Ciente e Registrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
