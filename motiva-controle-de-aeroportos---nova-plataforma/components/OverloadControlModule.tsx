
import React, { useState, useMemo } from 'react';
import { 
  PlusCircle, 
  History, 
  Scale, 
  CheckCircle2, 
  ArrowRight,
  Calendar,
  Clock,
  UploadCloud,
  FileText,
  User,
  Paperclip,
  Trash2,
  MoreHorizontal,
  Pencil,
  CheckCircle,
  XCircle,
  CornerUpLeft,
  Building2,
  FileSpreadsheet,
  Filter,
  ChevronDown,
  Eye
} from 'lucide-react';
import { AIRPORTS } from './AISComplianceForm';

interface OverloadRecord {
  id: string;
  airport: string;
  date: string;
  time: string;
  prefix: string;
  aircraftType: string;
  operator: string;
  landingWeight: string;
  attachmentName?: string;
  aisoPesoAttachmentName?: string;
  status: 'Em Análise' | 'Aprovado' | 'Devolvido' | 'Recusado';
  justification?: string;
  returnReason?: string;
}

const MOCK_RECORDS: OverloadRecord[] = [
  {
    id: '1',
    airport: 'Aeroporto de Navegantes',
    date: '2024-05-18',
    time: '14:30',
    prefix: 'PR-XLA',
    aircraftType: 'B738',
    operator: 'Gol Linhas Aéreas',
    landingWeight: '68.500 kg',
    attachmentName: 'manifesto_carga.pdf',
    status: 'Em Análise'
  },
  {
    id: '2',
    airport: 'Aeroporto de Curitiba',
    date: '2024-05-17',
    time: '09:15',
    prefix: 'PT-MNO',
    aircraftType: 'E195',
    operator: 'Azul Linhas Aéreas',
    landingWeight: 'ACN 44',
    status: 'Aprovado'
  }
];

const INITIAL_FORM_DATA = {
  airport: '',
  date: new Date().toISOString().split('T')[0],
  time: '',
  prefix: '',
  aircraftType: '',
  operator: '',
  landingWeight: ''
};

export const OverloadControlModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [records, setRecords] = useState<OverloadRecord[]>(MOCK_RECORDS);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Filters
  const [filterAirport, setFilterAirport] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // State for Actions
  const [actionMenuId, setActionMenuId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [viewingId, setViewingId] = useState<string | null>(null);
  
  // State for Modals (Approve/Refuse/Return)
  const [approveId, setApproveId] = useState<string | null>(null);
  const [approveFile, setApproveFile] = useState<File | null>(null);
  const [refuseId, setRefuseId] = useState<string | null>(null);
  const [returnId, setReturnId] = useState<string | null>(null);
  const [viewReasonRecord, setViewReasonRecord] = useState<OverloadRecord | null>(null);
  
  const [justification, setJustification] = useState('');
  const [returnReason, setReturnReason] = useState('');

  const [formData, setFormData] = useState(INITIAL_FORM_DATA);
  const [weightUnit, setWeightUnit] = useState<'kg' | 'ACN' | 'ACR'>('kg');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    setTimeout(() => {
      // Formatar o peso final baseado na unidade selecionada
      let formattedWeight = formData.landingWeight;
      if (weightUnit === 'kg' && !formData.landingWeight.toLowerCase().includes('kg')) {
        formattedWeight = `${formData.landingWeight} kg`;
      } else if (weightUnit !== 'kg' && !formData.landingWeight.includes(weightUnit)) {
        formattedWeight = `${weightUnit} ${formData.landingWeight}`;
      }

      const newRecord: OverloadRecord = {
        id: editingId || Math.random().toString(36).substr(2, 9),
        ...formData,
        landingWeight: formattedWeight,
        attachmentName: selectedFile?.name,
        status: editingId ? records.find(r => r.id === editingId)?.status || 'Em Análise' : 'Em Análise'
      };

      if (editingId) {
        setRecords(records.map(r => r.id === editingId ? newRecord : r));
      } else {
        setRecords([newRecord, ...records]);
      }
      
      setIsSubmitting(false);
      setActiveTab('history');
      
      setFormData(INITIAL_FORM_DATA);
      setWeightUnit('kg');
      setSelectedFile(null);
      setEditingId(null);
      setViewingId(null);
    }, 1500);
  };

  const handleStatusChange = (id: string, newStatus: OverloadRecord['status']) => {
    setRecords(records.map(r => r.id === id ? { ...r, status: newStatus } : r));
    setActionMenuId(null);
  };

  const handleApprove = () => {
    if (approveId && approveFile) {
      setRecords(records.map(r => 
        r.id === approveId 
          ? { 
              ...r, 
              status: 'Aprovado', 
              aisoPesoAttachmentName: approveFile.name,
              attachmentName: r.attachmentName || approveFile.name
            }
          : r
      ));
      setApproveId(null);
      setApproveFile(null);
    }
  };

  const handleRefuse = () => {
    if (refuseId) {
      setRecords(records.map(r => 
        r.id === refuseId 
          ? { ...r, status: 'Recusado', justification: justification }
          : r
      ));
      setRefuseId(null);
      setJustification('');
    }
  };

  const handleReturn = () => {
    if (returnId) {
      setRecords(records.map(r => 
        r.id === returnId 
          ? { ...r, status: 'Devolvido', returnReason: returnReason }
          : r
      ));
      setReturnId(null);
      setReturnReason('');
    }
  };

  const parseWeight = (weightString: string) => {
    let unit: 'kg' | 'ACN' | 'ACR' = 'kg';
    let value = weightString;

    if (weightString.includes('ACN')) {
      unit = 'ACN';
      value = weightString.replace('ACN ', '');
    } else if (weightString.includes('ACR')) {
      unit = 'ACR';
      value = weightString.replace('ACR ', '');
    } else {
      value = weightString.replace(' kg', '');
    }
    return { unit, value };
  };

  const handleView = (record: OverloadRecord) => {
    const { unit, value } = parseWeight(record.landingWeight);
    setFormData({
      airport: record.airport,
      date: record.date,
      time: record.time,
      prefix: record.prefix,
      aircraftType: record.aircraftType,
      operator: record.operator,
      landingWeight: value
    });
    setWeightUnit(unit);
    setViewingId(record.id);
    setEditingId(null);
    setActiveTab('form');
    setActionMenuId(null);
  };

  const handleEdit = (record: OverloadRecord) => {
    const { unit, value } = parseWeight(record.landingWeight);
    setFormData({
      airport: record.airport,
      date: record.date,
      time: record.time,
      prefix: record.prefix,
      aircraftType: record.aircraftType,
      operator: record.operator,
      landingWeight: value
    });
    setWeightUnit(unit);
    setEditingId(record.id);
    setViewingId(null);
    setActiveTab('form');
    setActionMenuId(null);
  };

  const filteredRecords = useMemo(() => {
    return records.filter(record => {
      const matchesAirport = filterAirport === '' || record.airport === filterAirport;
      const matchesStatus = filterStatus === '' || record.status === filterStatus;
      
      const recordDate = new Date(record.date);
      const start = startDate ? new Date(startDate) : null;
      const end = endDate ? new Date(endDate) : null;
      const matchesDate = (!start || recordDate >= start) && (!end || recordDate <= end);

      return matchesAirport && matchesStatus && matchesDate;
    });
  }, [records, filterAirport, filterStatus, startDate, endDate]);

  const getStatusBadge = (record: OverloadRecord) => {
    switch (record.status) {
      case 'Aprovado':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-sm text-[9px] font-black bg-emerald-50 text-emerald-700 border border-emerald-100 uppercase tracking-wide">
            <CheckCircle className="w-3 h-3" /> Aprovado
          </span>
        );
      case 'Recusado':
        return (
          <div className="flex flex-col items-center gap-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-sm text-[9px] font-black bg-red-50 text-red-700 border border-red-100 uppercase tracking-wide">
              <XCircle className="w-3 h-3" /> Recusado
            </span>
            {record.justification && (
              <button 
                onClick={() => setViewReasonRecord(record)}
                className="text-[9px] font-bold text-slate-400 hover:text-slate-600 underline decoration-slate-300 underline-offset-2 flex items-center gap-1 transition-colors"
              >
                Ver Motivo
              </button>
            )}
          </div>
        );
      case 'Devolvido':
        return (
          <div className="flex flex-col items-center gap-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-sm text-[9px] font-black bg-blue-50 text-blue-700 border border-blue-100 uppercase tracking-wide">
              <CornerUpLeft className="w-3 h-3" /> Devolvido
            </span>
            {record.returnReason && (
              <button 
                onClick={() => setViewReasonRecord(record)}
                className="text-[9px] font-bold text-slate-400 hover:text-slate-600 underline decoration-slate-300 underline-offset-2 flex items-center gap-1 transition-colors"
              >
                Ver Motivo
              </button>
            )}
          </div>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-sm text-[9px] font-black bg-amber-50 text-amber-700 border border-amber-100 uppercase tracking-wide">
            <Clock className="w-3 h-3" /> Em Análise
          </span>
        );
    }
  };

  const isReadOnly = !!viewingId;

  return (
    <div className="flex flex-col gap-[26px] relative h-full w-full">
      {/* Header */}
      <h2 className="text-[26px] font-bold text-slate-900 tracking-tight leading-tight uppercase shrink-0 flex items-center gap-3">
        Controle de Sobrecarga
      </h2>

      {/* Tabs */}
      <div className="flex p-1 bg-slate-50 rounded-none w-fit border border-slate-200 shrink-0">
        <button
          onClick={() => { setActiveTab('form'); setEditingId(null); setViewingId(null); setFormData(INITIAL_FORM_DATA); setWeightUnit('kg'); }}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-none text-[13px] font-bold transition-all ${
            activeTab === 'form' 
              ? 'bg-white text-[#391694] shadow-sm' 
              : 'text-slate-400 hover:text-slate-600'
          }`}
        >
          <PlusCircle className="w-4 h-4" />
          {editingId ? 'Editar Registro' : (viewingId ? 'Visualizar Registro' : 'Novo Registro')}
        </button>
        <button
          onClick={() => { setActiveTab('history'); setEditingId(null); setViewingId(null); setFormData(INITIAL_FORM_DATA); }}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-none text-[13px] font-bold transition-all ${
            activeTab === 'history' 
              ? 'bg-white text-[#391694] shadow-sm' 
              : 'text-slate-400 hover:text-slate-600'
          }`}
        >
          <History className="w-4 h-4" />
          Histórico
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-visible">
        {activeTab === 'form' ? (
          <div className="max-w-4xl animate-in fade-in duration-500 pb-10">
            {isSubmitting ? (
              <div className="flex flex-col items-center justify-center py-24 text-center animate-in zoom-in duration-300">
                <div className="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mb-6">
                  <CheckCircle2 className="w-10 h-10 text-emerald-600 animate-pulse" />
                </div>
                <h3 className="text-2xl font-bold text-slate-900 mb-2">{editingId ? 'Salvando Alterações...' : 'Processando...'}</h3>
                <p className="text-slate-500">O registro de sobrecarga está sendo salvo.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-[26px]">
                {editingId && (
                  <div className="flex items-center justify-between bg-indigo-50 border border-indigo-100 rounded-none px-6 py-4 mb-[26px]">
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></div>
                      <span className="text-xs font-black text-indigo-900 uppercase tracking-widest">Editando Registro #{editingId}</span>
                    </div>
                  </div>
                )}

                {viewingId && (
                  <div className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-none px-6 py-4 mb-[26px]">
                    <div className="flex items-center gap-3">
                      <Eye className="w-4 h-4 text-slate-500" />
                      <span className="text-xs font-black text-slate-600 uppercase tracking-widest">Visualizando Registro #{viewingId}</span>
                    </div>
                  </div>
                )}

                <div className="bg-[#F0FDFF] border border-[#C2F6FF] p-6 mb-[26px]">
                  <p className="text-[13px] text-[#0E7490] font-medium leading-relaxed">
                    <strong>Atenção:</strong> Utilize este formulário para reportar operações que excedam o PCN/PCR declarado. Anexe o manifesto de carga ou documentação técnica pertinente para comprovação.
                  </p>
                </div>

                {/* Aeroporto */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">
                    Aeroporto *
                  </label>
                  <div className="relative">
                    <select
                      required
                      disabled={isReadOnly}
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all appearance-none cursor-pointer font-medium disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed"
                      value={formData.airport}
                      onChange={(e) => setFormData({...formData, airport: e.target.value})}
                    >
                      <option value="">Selecione o aeroporto</option>
                      {AIRPORTS.map(ap => <option key={ap} value={ap}>{ap}</option>)}
                    </select>
                    <Building2 className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                  </div>
                </div>

                {/* Data e Hora */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Data da Operação *
                    </label>
                    <input
                      required
                      disabled={isReadOnly}
                      type="date"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed"
                      value={formData.date}
                      onChange={(e) => setFormData({...formData, date: e.target.value})}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Hora da Operação *
                    </label>
                    <input
                      required
                      disabled={isReadOnly}
                      type="time"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed"
                      value={formData.time}
                      onChange={(e) => setFormData({...formData, time: e.target.value})}
                    />
                  </div>
                </div>

                {/* Dados da Aeronave */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Prefixo da Aeronave *
                    </label>
                    <div className="relative">
                      <input
                        required
                        disabled={isReadOnly}
                        type="text"
                        placeholder="Ex: PR-XYZ"
                        className="w-full px-5 py-4 pl-12 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all font-medium uppercase disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed"
                        value={formData.prefix}
                        onChange={(e) => setFormData({...formData, prefix: e.target.value})}
                      />
                      <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Tipo da Aeronave (ICAO) *
                    </label>
                    <input
                      required
                      disabled={isReadOnly}
                      type="text"
                      placeholder="Ex: B738"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all font-medium uppercase disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed"
                      value={formData.aircraftType}
                      onChange={(e) => setFormData({...formData, aircraftType: e.target.value})}
                    />
                  </div>
                </div>

                {/* Operador e Peso */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Operador da Aeronave *
                    </label>
                    <div className="relative">
                      <input
                        required
                        disabled={isReadOnly}
                        type="text"
                        placeholder="Ex: Latam Airlines"
                        className="w-full px-5 py-4 pl-12 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all font-medium disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed"
                        value={formData.operator}
                        onChange={(e) => setFormData({...formData, operator: e.target.value})}
                      />
                      <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Peso Realizado / ACN / ACR *
                    </label>
                    <div className="flex">
                      <select
                        disabled={isReadOnly}
                        className="w-24 px-3 py-4 bg-slate-100 border border-r-0 border-slate-200 rounded-none text-[13px] font-bold text-slate-700 outline-none focus:border-black transition-all cursor-pointer disabled:opacity-70 disabled:cursor-not-allowed"
                        value={weightUnit}
                        onChange={(e) => setWeightUnit(e.target.value as 'kg' | 'ACN' | 'ACR')}
                      >
                        <option value="kg">KG</option>
                        <option value="ACN">ACN</option>
                        <option value="ACR">ACR</option>
                      </select>
                      <input
                        required
                        disabled={isReadOnly}
                        type="text"
                        placeholder={weightUnit === 'kg' ? "Ex: 70.000" : "Ex: 45"}
                        className="flex-1 px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all font-medium disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed"
                        value={formData.landingWeight}
                        onChange={(e) => setFormData({...formData, landingWeight: e.target.value})}
                      />
                    </div>
                  </div>
                </div>

                {/* Anexo de Documentos */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">
                    Anexar Documentação (AISO/PESO, caso aplicável)
                  </label>
                  <div className={`relative group ${isReadOnly ? 'pointer-events-none opacity-60' : ''}`}>
                    <input
                      type="file"
                      id="file-upload"
                      className="hidden"
                      onChange={handleFileChange}
                      accept=".pdf,.jpg,.jpeg,.png"
                      disabled={isReadOnly}
                    />
                    <label
                      htmlFor="file-upload"
                      className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-300 hover:border-[#391694] bg-slate-50 hover:bg-slate-100 transition-all cursor-pointer rounded-none group"
                    >
                      {selectedFile ? (
                        <div className="flex items-center gap-3 text-[#391694]">
                          <FileText className="w-8 h-8" />
                          <div className="text-left">
                            <p className="text-sm font-bold">{selectedFile.name}</p>
                            <p className="text-xs text-slate-500">{(selectedFile.size / 1024).toFixed(2)} KB</p>
                          </div>
                          {!isReadOnly && (
                            <button 
                              type="button"
                              onClick={(e) => { e.preventDefault(); setSelectedFile(null); }}
                              className="ml-4 p-2 hover:bg-red-50 text-red-500 rounded-full transition-colors"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      ) : (
                        <>
                          <UploadCloud className="w-8 h-8 text-slate-400 group-hover:text-[#391694] mb-2 transition-colors" />
                          <p className="text-sm font-bold text-slate-600 group-hover:text-[#391694] transition-colors">
                            Clique para selecionar um arquivo
                          </p>
                          <p className="text-xs text-slate-400 mt-1">PDF, JPG ou PNG (Máx. 10MB)</p>
                        </>
                      )}
                    </label>
                  </div>
                </div>

                <div className="flex justify-end pt-4">
                  {!isReadOnly ? (
                    <button
                      type="submit"
                      className="flex items-center gap-3 bg-black text-white px-10 py-4 rounded-none font-bold shadow-lg hover:scale-105 transition-all group"
                    >
                      <span>{editingId ? 'Atualizar Registro' : 'Salvar Registro'}</span>
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => { setActiveTab('history'); setViewingId(null); }}
                      className="flex items-center gap-3 bg-slate-200 text-slate-700 px-10 py-4 rounded-none font-bold shadow-sm hover:bg-slate-300 transition-all"
                    >
                      Voltar
                    </button>
                  )}
                </div>
              </form>
            )}
          </div>
        ) : (
          <div className="flex flex-col min-h-0 animate-in fade-in duration-500 w-full">
            {/* Filter Bar */}
            <div className="flex flex-col lg:flex-row gap-4 items-center justify-between bg-slate-50 p-4 rounded-none border border-slate-200 mb-[26px] shrink-0 w-full">
              <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">
                <div className="relative min-w-[200px]">
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

                <div className="relative min-w-[200px]">
                  <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <select 
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="w-full pl-10 pr-8 h-10 bg-white border border-slate-200 rounded-none text-sm outline-none focus:ring-2 focus:ring-[#391694]/10 focus:border-[#391694] transition-all appearance-none cursor-pointer"
                  >
                    <option value="">Todos os Status</option>
                    <option value="Em Análise">Em Análise</option>
                    <option value="Aprovado">Aprovado</option>
                    <option value="Devolvido">Devolvido</option>
                    <option value="Recusado">Recusado</option>
                  </select>
                </div>

                <div className="flex items-center gap-2 bg-white border border-slate-200 rounded-none px-3 h-10 shadow-sm">
                  <Calendar className="w-4 h-4 text-slate-400 shrink-0" />
                  <input 
                    type="date" 
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="text-xs font-medium text-slate-700 outline-none cursor-pointer bg-transparent"
                  />
                  <span className="text-slate-300">|</span>
                  <input 
                    type="date" 
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="text-xs font-medium text-slate-700 outline-none cursor-pointer bg-transparent"
                  />
                </div>
              </div>

              <button className="flex items-center gap-2 px-6 h-10 bg-[#391694] text-white rounded-none text-xs font-bold hover:bg-[#2a106e] transition-colors shadow-sm w-full lg:w-auto">
                <FileSpreadsheet className="w-4 h-4" />
                Exportar
              </button>
            </div>

            <div className="bg-white border border-slate-200 rounded-none shadow-sm relative overflow-visible w-full mb-20">
              <table className="w-full text-center border-separate border-spacing-0">
                <thead>
                  <tr className="bg-slate-50">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Data/Hora</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Aeronave</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Operador</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Peso / ACN</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Status</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-center border-b border-slate-200">Anexo</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-center border-b border-slate-200">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredRecords.map((record) => (
                    <tr key={record.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 text-center">
 <div className="flex items-center gap-2 justify-center">
 <Calendar className="w-3 h-3 text-slate-400" />
 <span className="text-xs font-semibold text-slate-900">{record.date.split('-').reverse().join('/')}</span>
 </div>
 <div className="flex items-center gap-2 mt-1 justify-center">
 <Clock className="w-3 h-3 text-slate-400" />
 <span className="text-[10px] font-medium text-slate-500">{record.time} UTC</span>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex flex-col items-center">
 <span className="text-xs font-bold text-slate-800">{record.prefix}</span>
 <span className="text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 w-fit rounded mt-0.5 mx-auto">{record.aircraftType}</span>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <span className="text-xs font-medium text-slate-700">{record.operator}</span>
 </td>
                      <td className="px-6 py-4 text-center">
 <span className="text-xs font-bold text-slate-900">{record.landingWeight}</span>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex justify-center">
 {getStatusBadge(record)}
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex justify-center">
 {record.attachmentName ? (
 <button className="text-[10px] font-bold text-brand-600 hover:text-brand-800 uppercase tracking-wider flex items-center gap-1 group justify-center">
 <Paperclip className="w-3 h-3 group-hover:scale-110 transition-transform" />
 Baixar
 </button>
 ) : (
 <span className="text-[10px] text-slate-400 font-medium italic">Sem anexo</span>
 )}
 </div>
 </td>
                      <td className="px-6 py-4 text-center relative">
 <div className="flex justify-center">
 <button 
 onClick={(e) => {
 e.stopPropagation();
 setActionMenuId(actionMenuId === record.id ? null : record.id);
 }}
 className={`p-1.5 rounded-none transition-all ${actionMenuId === record.id ? 'bg-[#391694] text-white shadow-md' : 'text-slate-400 hover:text-[#391694] hover:bg-indigo-50 border border-slate-200'}`}
 >
 <MoreHorizontal className="w-5 h-5" />
 </button>
 </div>

 {actionMenuId === record.id && (
 <div 
 className="absolute z-50 right-14 top-1/2 -translate-y-1/2 w-48 bg-white border border-slate-200 rounded-none shadow-2xl overflow-hidden animate-in fade-in slide-in-from-right-2 duration-200 text-left"
 onClick={(e) => e.stopPropagation()}
 >
 <button 
 onClick={() => handleView(record)} 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"
 >
 <Eye className="w-3.5 h-3.5" /> Ver Detalhes
 </button>
 <button 
 disabled={record.status === 'Aprovado'}
 onClick={() => { setApproveId(record.id); setApproveFile(null); setActionMenuId(null); }} 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-emerald-600 hover:bg-emerald-50 flex items-center gap-3 border-b border-slate-50 disabled:opacity-30 disabled:cursor-not-allowed"
 >
 <CheckCircle className="w-3.5 h-3.5" /> Aprovar
 </button>
 <button 
 disabled={record.status === 'Aprovado'}
 onClick={() => { setReturnId(record.id); setActionMenuId(null); }} 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-blue-600 hover:bg-blue-50 flex items-center gap-3 border-b border-slate-50 disabled:opacity-30 disabled:cursor-not-allowed"
 >
 <CornerUpLeft className="w-3.5 h-3.5" /> Devolver
 </button>
 <button 
 disabled={record.status === 'Aprovado'}
 onClick={() => { setRefuseId(record.id); setActionMenuId(null); }} 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-red-600 hover:bg-red-50 flex items-center gap-3 border-b border-slate-50 disabled:opacity-30 disabled:cursor-not-allowed"
 >
 <XCircle className="w-3.5 h-3.5" /> Recusar
 </button>
 <button 
 disabled={record.status === 'Aprovado'}
 onClick={() => handleEdit(record)} 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50 disabled:opacity-30 disabled:cursor-not-allowed"
 >
 <Pencil className="w-3.5 h-3.5" /> Editar
 </button>
 </div>
 )}
 </td>
                    </tr>
                  ))}
                  {filteredRecords.length === 0 && (
                     <tr>
                        <td colSpan={7} className="py-12 text-center text-slate-400">
 Nenhum registro encontrado.
 </td>
                     </tr>
                  )}
                </tbody>
              </table>
            </div>
            <div className="bg-slate-50 px-6 py-3 border border-t-0 border-slate-200 text-[10px] text-slate-400 font-bold uppercase tracking-widest">
                {filteredRecords.length} REGISTROS ENCONTRADOS
            </div>
          </div>
        )}
      </div>

      {/* Backdrop for Menu */}
      {actionMenuId && (
        <div className="fixed inset-0 z-40 bg-transparent" onClick={() => setActionMenuId(null)}></div>
      )}

      {/* Modais de Ação */}
      {approveId && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-white rounded-none w-full max-w-md shadow-2xl overflow-hidden border border-slate-100">
            <div className="p-8">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-emerald-50 rounded-none flex items-center justify-center border border-emerald-100 shrink-0">
                  <CheckCircle className="w-6 h-6 text-emerald-600" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 tracking-tight">Aprovar Registro</h3>
                  <p className="text-xs text-slate-500 font-medium">Anexo de conjunto AISO/PESO obrigatório</p>
                </div>
              </div>
              
              <p className="text-slate-600 text-sm leading-relaxed mb-6">
                Para concluir a aprovação do registro de sobrecarga, você deve obrigatoriamente anexar o conjunto <strong>AISO/PESO</strong>.
              </p>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-1">
                  Anexar Conjunto AISO/PESO <span className="text-red-500">*</span>
                </label>
                
                <div className="relative">
                  <input
                    type="file"
                    id="approve-file-upload"
                    className="hidden"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        setApproveFile(e.target.files[0]);
                      }
                    }}
                    accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                  />
                  
                  {approveFile ? (
                    <div className="flex items-center justify-between p-4 bg-emerald-50/60 border border-emerald-200 rounded-none">
                      <div className="flex items-center gap-3 overflow-hidden">
                        <FileText className="w-6 h-6 text-emerald-600 shrink-0" />
                        <div className="truncate">
                          <p className="text-xs font-bold text-slate-900 truncate">{approveFile.name}</p>
                          <p className="text-[10px] text-slate-500 font-medium">{(approveFile.size / 1024).toFixed(2)} KB</p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => setApproveFile(null)}
                        className="p-1.5 hover:bg-red-50 text-red-500 rounded-full transition-colors shrink-0"
                        title="Remover arquivo"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ) : (
                    <label
                      htmlFor="approve-file-upload"
                      className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-slate-300 hover:border-emerald-500 bg-slate-50 hover:bg-emerald-50/30 transition-all cursor-pointer rounded-none group"
                    >
                      <UploadCloud className="w-8 h-8 text-slate-400 group-hover:text-emerald-600 mb-2 transition-colors" />
                      <p className="text-xs font-bold text-slate-700 group-hover:text-emerald-700 transition-colors">
                        Clique para anexar o conjunto AISO/PESO
                      </p>
                      <p className="text-[10px] text-slate-400 mt-1">PDF, JPG, PNG ou DOCX (Obrigatório)</p>
                    </label>
                  )}
                </div>

                {!approveFile && (
                  <p className="text-[11px] font-bold text-amber-600 flex items-center gap-1.5 mt-2">
                    <XCircle className="w-3.5 h-3.5 shrink-0" />
                    Anexar o documento é obrigatório para prosseguir.
                  </p>
                )}
              </div>
            </div>
            
            <div className="p-4 bg-slate-50/50 border-t border-slate-100 flex gap-3">
              <button 
                onClick={() => { setApproveId(null); setApproveFile(null); }} 
                className="flex-1 py-3 bg-white border border-slate-200 rounded-none text-xs font-bold text-slate-600 hover:bg-slate-100 transition-all"
              >
                Cancelar
              </button>
              <button 
                disabled={!approveFile} 
                onClick={handleApprove} 
                className="flex-1 py-3 bg-emerald-600 rounded-none text-xs font-bold text-white hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-600/20 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Confirmar Aprovação
              </button>
            </div>
          </div>
        </div>
      )}

      {refuseId && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-white rounded-none w-full max-w-sm shadow-2xl overflow-hidden border border-slate-100">
            <div className="p-8">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-red-50 rounded-none flex items-center justify-center border border-red-100">
                  <XCircle className="w-6 h-6 text-red-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 tracking-tight">Recusar Registro</h3>
              </div>
              
              <p className="text-slate-500 text-sm leading-relaxed mb-6">
                O status será alterado para <strong>RECUSADO</strong>. Por favor, informe o motivo.
              </p>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1">
                  Justificativa <span className="text-red-500">*</span>
                </label>
                <textarea 
                  autoFocus
                  rows={4}
                  placeholder="Descreva o motivo da recusa..."
                  value={justification}
                  onChange={(e) => setJustification(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-none outline-none focus:border-red-500 transition-all text-sm resize-none"
                />
              </div>
            </div>
            <div className="p-4 bg-slate-50/50 border-t border-slate-100 flex gap-3">
              <button onClick={() => { setRefuseId(null); setJustification(''); }} className="flex-1 py-3 bg-white border border-slate-200 rounded-none text-xs font-bold text-slate-600 hover:bg-slate-100 transition-all">Cancelar</button>
              <button disabled={!justification.trim()} onClick={handleRefuse} className="flex-1 py-3 bg-black rounded-none text-xs font-bold text-white hover:opacity-90 transition-all shadow-lg shadow-black/20 disabled:opacity-50">Confirmar</button>
            </div>
          </div>
        </div>
      )}

      {returnId && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-white rounded-none w-full max-w-sm shadow-2xl overflow-hidden border border-slate-100">
            <div className="p-8">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-blue-50 rounded-none flex items-center justify-center border border-blue-100">
                  <CornerUpLeft className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 tracking-tight">Devolver Registro</h3>
              </div>
              
              <p className="text-slate-500 text-sm leading-relaxed mb-6">
                Solicite correções. O status será alterado para <strong>DEVOLVIDO</strong>.
              </p>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1">
                  Correções Necessárias <span className="text-red-500">*</span>
                </label>
                <textarea 
                  autoFocus
                  rows={4}
                  placeholder="Descreva o que precisa ser corrigido..."
                  value={returnReason}
                  onChange={(e) => setReturnReason(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-none outline-none focus:border-blue-500 transition-all text-sm resize-none"
                />
              </div>
            </div>
            <div className="p-4 bg-slate-50/50 border-t border-slate-100 flex gap-3">
              <button onClick={() => { setReturnId(null); setReturnReason(''); }} className="flex-1 py-3 bg-white border border-slate-200 rounded-none text-xs font-bold text-slate-600 hover:bg-slate-100 transition-all">Cancelar</button>
              <button disabled={!returnReason.trim()} onClick={handleReturn} className="flex-1 py-3 bg-black rounded-none text-xs font-bold text-white hover:opacity-90 transition-all shadow-lg shadow-black/20 disabled:opacity-50">Confirmar</button>
            </div>
          </div>
        </div>
      )}

      {viewReasonRecord && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
           <div className="bg-white rounded-none w-full max-w-sm shadow-2xl overflow-hidden border border-slate-100">
              <div className="p-8">
                 <div className="flex items-center gap-4 mb-6">
                    <div className={`w-12 h-12 rounded-none flex items-center justify-center border ${viewReasonRecord.status === 'Recusado' ? 'bg-red-50 border-red-100 text-red-600' : 'bg-blue-50 border-blue-100 text-blue-600'}`}>
                       {viewReasonRecord.status === 'Recusado' ? <XCircle className="w-6 h-6" /> : <CornerUpLeft className="w-6 h-6" />}
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 tracking-tight">
                       {viewReasonRecord.status === 'Recusado' ? 'Motivo da Recusa' : 'Motivo da Devolução'}
                    </h3>
                 </div>
                 <div className="bg-slate-50 p-4 border border-slate-100 rounded-none min-h-[100px]">
                    <p className="text-sm text-slate-600 font-medium leading-relaxed whitespace-pre-wrap">
                       {viewReasonRecord.status === 'Recusado' ? viewReasonRecord.justification : viewReasonRecord.returnReason}
                    </p>
                 </div>
              </div>
              <div className="p-4 bg-slate-50/50 border-t border-slate-100">
                 <button onClick={() => setViewReasonRecord(null)} className="w-full py-3 bg-white border border-slate-200 rounded-none text-xs font-bold text-slate-600 hover:bg-slate-100 transition-all">
                    Fechar
                 </button>
              </div>
           </div>
        </div>
      )}
    </div>
  );
};
