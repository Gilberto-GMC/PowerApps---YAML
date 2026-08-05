
import React, { useState, useEffect } from 'react';
import { 
  PlusCircle, 
  History, 
  CheckCircle2, 
  ArrowRight,
  Calendar,
  Plane,
  Car,
  MapPin,
  Beaker,
  AlertTriangle,
  Camera,
  Trash2,
  FileText,
  UploadCloud,
  MoreHorizontal,
  Eye,
  Pencil,
  FileSpreadsheet,
  Building2,
  ChevronDown,
  Info,
  X
} from 'lucide-react';
import { AIRPORTS } from './AISComplianceForm';

interface LeakageRecord {
  id: string;
  airport: string;
  date: string;
  time: string;
  fluidType: string;
  spillArea: string; // Área da mancha
  volume: string; // Litros estimate
  location: string;
  position: string;
  status: 'Contido' | 'Em Limpeza' | 'Finalizado';
  aircraftRegistration?: string;
  model?: string;
  operator?: string;
  aircraftLeakSource?: string;
  originatorType?: string;
  originatorIdentification?: string;
  originatorLeakSource?: string;
  absorbentMats?: string;
  maintenanceProtocol?: string;
  fiscalReport?: string;
  driverReport?: string;
  leakSource?: string;
}

const MOCK_RECORDS: LeakageRecord[] = [
  {
    id: '1',
    airport: 'Aeroporto de Navegantes',
    date: '2024-05-18',
    time: '14:30',
    fluidType: 'QAV',
    spillArea: 'Média (2m² a 5m²)',
    volume: '15 Litros',
    location: 'Pátio de Estacionamento',
    position: 'Posição 03',
    aircraftLeakSource: 'Asa Direita',
    status: 'Finalizado',
    aircraftRegistration: 'PR-XLA',
    model: 'B738',
    operator: 'Gol Linhas Aéreas',
    absorbentMats: '4',
    fiscalReport: 'Vazamento identificado durante abastecimento.',
    driverReport: ''
  },
  {
    id: '2',
    airport: 'Aeroporto de Pelotas',
    date: '2024-05-17',
    time: '09:15',
    fluidType: 'Lubrificantes',
    spillArea: 'Pequena (< 2m²)',
    volume: '2 Litros',
    location: 'Via de Serviço',
    position: 'Próximo ao TECA',
    originatorType: 'Veículo',
    originatorIdentification: 'Caminhão de Bagagem',
    originatorLeakSource: 'Mangueira hidráulica',
    status: 'Contido',
    absorbentMats: '1',
    fiscalReport: 'Rompimento de mangueira hidráulica.',
    driverReport: ''
  }
];

const FLUID_TYPES = [
  'Dejetos (QTU)',
  'Diesel',
  'Fluído Hidráulico',
  'Gasolina',
  'Gasolina de Aviação (AVGAS)',
  'Lubrificantes',
  'Querosene de Aviação (QAV)',
  'Outros'
];

const SPILL_AREAS = [
  'Pequena (< 2m²)',
  'Média (2m² a 5m²)',
  'Grande (> 5m²)'
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
  fluidType: '',
  location: '',
  position: '',
  spillArea: '',
  volume: '',
  absorbentMats: '',
  // Aircraft Info
  registration: '',
  model: '',
  operator: '',
  aircraftLeakSource: '',
  // Originator Info
  originatorType: 'Veículo',
  originatorIdentification: '',
  originatorLeakSource: '',
  // Reports
  maintenanceProtocol: '',
  fiscalReport: '',
  driverReport: ''
};

export const LeakageModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [records, setRecords] = useState<LeakageRecord[]>(MOCK_RECORDS);
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);
  
  // State for Action Menu and Delete Modal
  const [actionMenuId, setActionMenuId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [showHazardousWasteAlert, setShowHazardousWasteAlert] = useState(false);
  const [showSpillGuide, setShowSpillGuide] = useState(false);
  const [showSpillExample, setShowSpillExample] = useState(false);

  // Filters
  const [filterAirport, setFilterAirport] = useState('');
  const [filterLocation, setFilterLocation] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const [formData, setFormData] = useState(INITIAL_FORM_DATA);

  // Cleanup object URLs to avoid memory leaks
  useEffect(() => {
    return () => {
      previewUrls.forEach(url => URL.revokeObjectURL(url));
    };
  }, [previewUrls]);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files) as File[];
      const newUrls = newFiles.map(file => URL.createObjectURL(file));
      
      setSelectedImages(prev => [...prev, ...newFiles]);
      setPreviewUrls(prev => [...prev, ...newUrls]);
    }
  };

  const removeImage = (index: number) => {
    URL.revokeObjectURL(previewUrls[index]);
    
    setSelectedImages(prev => prev.filter((_, i) => i !== index));
    setPreviewUrls(prev => prev.filter((_, i) => i !== index));
  };

  const submitForm = () => {
    setIsSubmitting(true);

    setTimeout(() => {
      const newRecord: LeakageRecord = {
        id: editingId || Math.random().toString(36).substr(2, 9),
        airport: formData.airport,
        date: formData.date,
        time: formData.time,
        fluidType: formData.fluidType,
        spillArea: formData.spillArea,
        volume: formData.volume.includes('L') ? formData.volume : `${formData.volume} L`,
        location: formData.location,
        position: formData.position,
        leakSource: formData.leakSource,
        status: 'Contido',
        aircraftRegistration: formData.registration,
        model: formData.model,
        operator: formData.operator,
        absorbentMats: formData.absorbentMats,
        maintenanceProtocol: formData.maintenanceProtocol,
        fiscalReport: formData.fiscalReport,
        driverReport: formData.driverReport
      };

      if (editingId) {
        setRecords(records.map(r => r.id === editingId ? newRecord : r));
      } else {
        setRecords([newRecord, ...records]);
      }

      setIsSubmitting(false);
      setActiveTab('history');
      
      // Reset
      setFormData(INITIAL_FORM_DATA);
      setSelectedImages([]);
      setPreviewUrls([]);
      setEditingId(null);
    }, 1500);
  };

  const handleDelete = () => {
    if (deleteId) {
      setRecords(records.filter(r => r.id !== deleteId));
      setDeleteId(null);
    }
  };

  const handleEdit = (record: LeakageRecord) => {
    setFormData({
      airport: record.airport,
      date: record.date,
      time: record.time,
      fluidType: record.fluidType,
      leakSource: record.leakSource,
      location: record.location,
      position: record.position,
      spillArea: record.spillArea,
      volume: record.volume.replace(' L', ''),
      absorbentMats: record.absorbentMats || '',
      registration: record.aircraftRegistration || '',
      model: record.model || '',
      operator: record.operator || '',
      maintenanceProtocol: record.maintenanceProtocol || '',
      fiscalReport: record.fiscalReport || '',
      driverReport: record.driverReport || ''
    });
    setEditingId(record.id);
    setActiveTab('form');
    setActionMenuId(null);
  };

  const filteredRecords = records.filter(record => {
    const matchesAirport = filterAirport === '' || record.airport === filterAirport;
    const matchesLocation = filterLocation === '' || record.location.includes(filterLocation);
    const recordDate = new Date(record.date);
    const start = startDate ? new Date(startDate) : null;
    const end = endDate ? new Date(endDate) : null;
    const matchesDate = (!start || recordDate >= start) && (!end || recordDate <= end);
    return matchesAirport && matchesLocation && matchesDate;
  });

  return (
    <div className="flex flex-col gap-[26px] relative h-full w-full">
      {/* Header */}
      <h2 className="text-2xl font-bold text-slate-900 tracking-tight leading-tight uppercase shrink-0 flex items-center gap-3">
        Vazamento em Área Operacional
      </h2>

      {/* Tabs */}
      <div className="flex p-1 bg-slate-50 rounded-none w-fit border border-slate-200 shrink-0">
        <button
          onClick={() => { setActiveTab('form'); setEditingId(null); setFormData(INITIAL_FORM_DATA); }}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-none text-[13px] font-bold transition-all ${
            activeTab === 'form' 
              ? 'bg-white text-[#391694] shadow-sm' 
              : 'text-slate-400 hover:text-slate-600'
          }`}
        >
          <PlusCircle className="w-4 h-4" />
          {editingId ? 'Editar Registro' : 'Novo Registro'}
        </button>
        <button
          onClick={() => { setActiveTab('history'); setEditingId(null); setFormData(INITIAL_FORM_DATA); }}
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
                <h3 className="text-2xl font-bold text-slate-900 mb-2">
                  {editingId ? 'Atualizando Registro...' : 'Registrando Ocorrência...'}
                </h3>
                <p className="text-slate-500">Os dados e imagens estão sendo processados.</p>
              </div>
            ) : (
              <form onSubmit={(e) => { e.preventDefault(); setShowHazardousWasteAlert(true); }} className="space-y-[26px]">
                
                {/* Procedimento de Segurança */}
                <div className="bg-[#FFF8E6] border border-[#FFECB3] p-6">
                  <div className="flex gap-4">
                    <AlertTriangle className="w-6 h-6 text-[#856404] shrink-0" />
                    <div>
                      <h4 className="text-[13px] font-bold text-[#856404] uppercase tracking-wide mb-1">Procedimento de Segurança</h4>
                      <p className="text-[13px] text-slate-600 font-medium leading-relaxed">
                        Em caso de vazamento de produtos perigosos (QAV/AVGAS) com área superior a <strong>5m²</strong>, acione imediatamente os Bombeiros de Aeródromo (SCI). 
                      </p>
                    </div>
                  </div>
                </div>

                {/* Seção 0: Aeroporto */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Aeroporto da Ocorrência *</label>
                  <div className="relative">
                    <select
                      required
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium"
                      value={formData.airport}
                      onChange={(e) => setFormData({...formData, airport: e.target.value})}
                    >
                      <option value="">Selecione o aeroporto</option>
                      {AIRPORTS.map(ap => <option key={ap} value={ap}>{ap}</option>)}
                    </select>
                    <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                  </div>
                </div>

                {/* Seção 1: Dados do Evento e Fluído */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Data da Ocorrência *</label>
                    <input
                      required
                      type="date"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-xs text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                      value={formData.date}
                      onChange={(e) => setFormData({...formData, date: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Hora da Ocorrência (UTC)*</label>
                    <input
                      required
                      type="time"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-xs text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                      value={formData.time}
                      onChange={(e) => setFormData({...formData, time: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2 lg:col-span-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Tipo de Fluído *</label>
                    <div className="relative">
                      <select
                        required
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-xs text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium"
                        value={formData.fluidType}
                        onChange={(e) => setFormData({...formData, fluidType: e.target.value})}
                      >
                        <option value="">Selecione o fluído...</option>
                        {FLUID_TYPES.map(type => <option key={type} value={type}>{type}</option>)}
                      </select>
                      <Beaker className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>
                </div>

                {/* Seção 2: Detalhes do Vazamento */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-[26px]">
                  <div className="space-y-2 lg:col-span-1">
                    <div className="flex items-center justify-between">
                      <label className="text-[13px] font-bold text-slate-900 block">Área da Mancha *</label>
                      <button 
                        type="button"
                        onClick={() => setShowSpillExample(true)}
                        className="text-[10px] font-bold text-[#391694] hover:underline flex items-center gap-1"
                      >
                        <Info className="w-3 h-3" />
                        Ver exemplo
                      </button>
                    </div>
                    <div className="relative">
                      <select
                        required
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium"
                        value={formData.spillArea}
                        onChange={(e) => setFormData({...formData, spillArea: e.target.value})}
                      >
                        <option value="">Selecione...</option>
                        {SPILL_AREAS.map(area => <option key={area} value={area}>{area}</option>)}
                      </select>
                      <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>
                  <div className="space-y-2 lg:col-span-1">
                    <label className="text-[13px] font-bold text-slate-900 block">Volume Estimado (L) *</label>
                    <input
                      required
                      type="number"
                      placeholder="Ex: 5"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-[#391694] transition-all font-medium"
                      value={formData.volume}
                      onChange={(e) => setFormData({...formData, volume: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2 lg:col-span-1">
                    <label className="text-[13px] font-bold text-slate-900 block">Mantas Absorventes *</label>
                    <input
                      required
                      type="number"
                      min="0"
                      placeholder="Qtd. utilizada"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-[#391694] transition-all font-medium"
                      value={formData.absorbentMats}
                      onChange={(e) => setFormData({...formData, absorbentMats: e.target.value})}
                    />
                  </div>
                </div>

                {/* Seção 3: Localização */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Local Geral *</label>
                    <div className="relative">
                      <select
                        required
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium"
                        value={formData.location}
                        onChange={(e) => setFormData({...formData, location: e.target.value})}
                      >
                        <option value="">Selecione o local...</option>
                        {LOCATIONS.map(loc => <option key={loc} value={loc}>{loc}</option>)}
                      </select>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Posição / Box / Referência *</label>
                    <input
                      required
                      type="text"
                      placeholder="Ex: Box 05 ou Próximo ao TECA"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-[#391694] transition-all font-medium"
                      value={formData.position}
                      onChange={(e) => setFormData({...formData, position: e.target.value})}
                    />
                  </div>
                </div>

                {/* Seção 4: Aeronave (Opcional se for veículo) */}
                <div className="border border-slate-100 p-6 bg-slate-50/30">
                  <h3 className="text-[13px] font-bold text-slate-800 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <Plane className="w-4 h-4" /> Dados da Aeronave (Se aplicável)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-[26px]">
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Matrícula</label>
                      <input
                        type="text"
                        placeholder="Ex: PR-ABC"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-[#391694] transition-all uppercase font-medium"
                        value={formData.registration}
                        onChange={(e) => setFormData({...formData, registration: e.target.value})}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Modelo</label>
                      <input
                        type="text"
                        placeholder="Ex: B738"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-[#391694] transition-all uppercase font-medium"
                        value={formData.model}
                        onChange={(e) => setFormData({...formData, model: e.target.value})}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Operador Aéreo</label>
                      <div className="relative">
                         <input
                          type="text"
                          placeholder="Gol Linhas Aéreas"
                          className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-[#391694] transition-all font-medium"
                          value={formData.operator}
                          onChange={(e) => setFormData({...formData, operator: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Origem do Vazamento</label>
                      <input
                        type="text"
                        placeholder="Ex: Asa Direita"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-[#391694] transition-all font-medium"
                        value={formData.aircraftLeakSource}
                        onChange={(e) => setFormData({...formData, aircraftLeakSource: e.target.value})}
                      />
                    </div>
                  </div>
                </div>

                {/* Seção 4.1: Veículo / Equipamento */}
                <div className="border border-slate-100 p-6 bg-slate-50/30">
                  <h3 className="text-[13px] font-bold text-slate-800 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <Car className="w-4 h-4" /> Dados do Veículo / Equipamento (se aplicável)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-[26px]">
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Tipo do Originador</label>
                      <div className="relative">
                        <select
                          className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium"
                          value={formData.originatorType}
                          onChange={(e) => setFormData({...formData, originatorType: e.target.value})}
                        >
                          <option value="Veículo">Veículo</option>
                          <option value="Equipamento">Equipamento</option>
                        </select>
                        <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Identificação</label>
                      <input
                        type="text"
                        placeholder="Ex: Trator de Bagagem (TAG-01)"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-[#391694] transition-all font-medium"
                        value={formData.originatorIdentification}
                        onChange={(e) => setFormData({...formData, originatorIdentification: e.target.value})}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Origem do Vazamento</label>
                      <input
                        type="text"
                        placeholder="Ex: Motor, Tanque, Etc."
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-[#391694] transition-all font-medium"
                        value={formData.originatorLeakSource}
                        onChange={(e) => setFormData({...formData, originatorLeakSource: e.target.value})}
                      />
                    </div>
                  </div>
                </div>

                {/* Seção 5: Relatos */}
                <div className="border-t border-slate-100 pt-6 space-y-[26px]">
                  <h3 className="text-sm font-bold text-slate-800 uppercase tracking-widest flex items-center gap-2">
                    <FileText className="w-4 h-4" /> Detalhamento do Evento
                  </h3>
                  
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Protocolo no Portal da Manutenção *</label>
                    <input
                      required
                      type="text"
                      placeholder="Ex: PM-2024-001"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-[#391694] transition-all font-medium uppercase"
                      value={formData.maintenanceProtocol}
                      onChange={(e) => setFormData({...formData, maintenanceProtocol: e.target.value})}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Relato do Fiscal *</label>
                    <textarea
                      required
                      rows={4}
                      placeholder="Descreva como ocorreu o vazamento, ações tomadas e observações relevantes..."
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-[#391694] transition-all resize-none font-medium"
                      value={formData.fiscalReport}
                      onChange={(e) => setFormData({...formData, fiscalReport: e.target.value})}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Relato do Condutor / Envolvido</label>
                    <textarea
                      rows={4}
                      placeholder="Relato da parte envolvida (se houver)..."
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-[#391694] transition-all resize-none font-medium"
                      value={formData.driverReport}
                      onChange={(e) => setFormData({...formData, driverReport: e.target.value})}
                    />
                  </div>
                </div>

                {/* Seção 6: Fotos */}
                <div className="border-t border-slate-100 pt-6">
                  <h3 className="text-sm font-bold text-slate-800 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <Camera className="w-4 h-4" /> Fotos da Ocorrência
                  </h3>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    {previewUrls.map((url, index) => (
                      <div key={index} className="relative aspect-square bg-slate-100 border border-slate-200 group">
                        <img 
                          src={url} 
                          alt={`Preview ${index}`} 
                          className="w-full h-full object-cover" 
                        />
                        <button
                          type="button"
                          onClick={() => removeImage(index)}
                          className="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                          aria-label="Remover imagem"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                    
                    <label className="flex flex-col items-center justify-center aspect-square border-2 border-dashed border-slate-300 bg-slate-50 hover:bg-[#FDF4FF] hover:border-[#391694] hover:text-[#391694] transition-all cursor-pointer group text-slate-400">
                      <input 
                        type="file" 
                        multiple 
                        accept="image/*" 
                        className="hidden" 
                        onChange={handleImageChange}
                      />
                      <UploadCloud className="w-8 h-8 mb-2 group-hover:scale-110 transition-transform" />
                      <span className="text-xs font-bold uppercase">Adicionar</span>
                    </label>
                  </div>
                  <p className="text-[11px] text-slate-400 text-right">{selectedImages.length} fotos na galeria.</p>
                </div>

                <div className="flex justify-end pt-4">
                  <button
                    type="submit"
                    className="flex items-center gap-3 bg-black text-white px-10 py-4 rounded-none font-bold shadow-lg hover:scale-105 transition-all group"
                  >
                    <span>Finalizar Reporte</span>
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </button>
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
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <select 
                    value={filterLocation}
                    onChange={(e) => setFilterLocation(e.target.value)}
                    className="w-full pl-10 pr-8 h-10 bg-white border border-slate-200 rounded-none text-sm outline-none focus:ring-2 focus:ring-[#391694]/10 focus:border-[#391694] transition-all appearance-none cursor-pointer"
                  >
                    <option value="">Todos os Locais</option>
                    {LOCATIONS.map(loc => <option key={loc} value={loc}>{loc}</option>)}
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

            <div className="bg-white border border-slate-200 rounded-none shadow-sm relative overflow-x-auto w-full">
              <table className="w-full text-center border-separate border-spacing-0">
                <thead>
                  <tr className="bg-slate-50">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Data/Hora</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Aeroporto</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Local</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Fluído/Volume</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Área</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-center border-b border-slate-200">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredRecords.map((record) => (
                    <tr key={record.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 text-center">
 <div className="text-xs font-semibold text-slate-900 leading-tight">
 {record.date.split('-').reverse().join('/')}
 </div>
 <div className="text-[10px] text-slate-500 font-medium">{record.time} UTC</div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="text-xs text-slate-700 font-medium whitespace-normal leading-tight max-w-[200px]">
 {record.airport}
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex items-center gap-2 justify-center">
 <MapPin className="w-3 h-3 text-slate-400" />
 <span className="text-xs font-medium text-slate-700">{record.location}</span>
 </div>
 {record.position && <span className="text-[10px] text-slate-400 block">{record.position}</span>}
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex flex-col items-center">
 <span className="text-xs font-bold text-[#c026d3]">{record.fluidType}</span>
 <span className="text-[10px] text-slate-500">{record.volume}</span>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200 justify-center">
 {record.spillArea}
 </span>
 </td>
                      <td className="px-6 py-4 text-center relative">
 <button 
 onClick={(e) => {
 e.stopPropagation();
 setActionMenuId(actionMenuId === record.id ? null : record.id);
 }}
 className={`p-1.5 rounded-none transition-all ${actionMenuId === record.id ? 'bg-[#c026d3] text-white shadow-md' : 'text-slate-400 hover:text-[#c026d3] hover:bg-purple-50 border border-slate-200'}`}
 aria-label="Ações"
 >
 <MoreHorizontal className="w-5 h-5" />
 </button>

 {actionMenuId === record.id && (
 <div 
 className="absolute z-50 right-14 top-1/2 -translate-y-1/2 w-44 bg-white border border-slate-200 rounded-none shadow-2xl overflow-hidden animate-in fade-in slide-in-from-right-2 duration-200"
 >
 <button 
 onClick={() => setActionMenuId(null)} 
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
 onClick={() => { setDeleteId(record.id); setActionMenuId(null); }} 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-red-600 hover:bg-red-50 flex items-center gap-3"
 >
 <Trash2 className="w-3.5 h-3.5" /> Excluir
 </button>
 </div>
 )}
 </td>
                    </tr>
                  ))}
                  {filteredRecords.length === 0 && (
                     <tr>
                        <td colSpan={6} className="py-12 text-center text-slate-400">
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

      {/* Backdrop para fechar menus */}
      {actionMenuId && (
        <div className="fixed inset-0 z-40 bg-transparent" onClick={() => setActionMenuId(null)}></div>
      )}

      {/* Modal de Confirmação de Exclusão */}
      {deleteId && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-white rounded-none w-full max-w-sm shadow-2xl overflow-hidden border border-slate-100">
            <div className="p-8 text-center">
              <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6 border border-red-100">
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
                className="flex-1 py-3 bg-white border border-slate-200 rounded-none text-xs font-bold text-slate-600 hover:bg-slate-100 transition-all"
              >
                Cancelar
              </button>
              <button 
                onClick={handleDelete} 
                className="flex-1 py-3 bg-red-600 rounded-none text-xs font-bold text-white hover:bg-red-700 transition-all shadow-lg shadow-red-900/20"
              >
                Confirmar Exclusão
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Alerta de Resíduos Perigosos */}
      {showHazardousWasteAlert && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-white rounded-none w-full max-w-sm shadow-2xl overflow-hidden border border-slate-100">
            <div className="p-8 text-center">
              <div className="w-16 h-16 bg-amber-50 rounded-full flex items-center justify-center mx-auto mb-6 border border-amber-100">
                <AlertTriangle className="w-8 h-8 text-amber-500" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 tracking-tight mb-2">Atenção: Resíduos Perigosos</h3>
              <p className="text-slate-500 text-sm leading-relaxed mb-6">
                As mantas absorventes utilizadas na contenção do vazamento são classificadas como <strong>resíduos perigosos</strong>. Certifique-se de descartá-las na Central de Resíduos do Aeroporto para tratamento especial. Em caso de dúvidas, consulte a equipe de SGI.
              </p>
            </div>
            <div className="p-4 bg-slate-50/50 border-t border-slate-100 flex gap-3">
              <button 
                onClick={() => setShowHazardousWasteAlert(false)} 
                className="flex-1 py-3 bg-white border border-slate-200 rounded-none text-xs font-bold text-slate-600 hover:bg-slate-100 transition-all"
              >
                Cancelar
              </button>
              <button 
                onClick={() => { setShowHazardousWasteAlert(false); submitForm(); }} 
                className="flex-1 py-3 bg-amber-500 rounded-none text-xs font-bold text-white hover:bg-amber-600 transition-all shadow-lg shadow-amber-900/20"
              >
                Entendido, Finalizar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Exemplo de Mancha */}
      {showSpillExample && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-white rounded-none w-full max-w-4xl shadow-2xl overflow-hidden border border-slate-100 flex flex-col">
            <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
              <h3 className="font-bold text-slate-800 flex items-center gap-2">
                <Info className="w-5 h-5 text-[#391694]" />
                Referência: Classificação da Área da Mancha
              </h3>
              <button onClick={() => setShowSpillExample(false)} className="text-slate-400 hover:text-slate-600 transition-colors">
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="p-6 bg-slate-100/50 overflow-y-auto max-h-[70vh]">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Pequena */}
                <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm flex flex-col">
                  <div className="bg-[#5c8edb] text-white text-center py-3 font-bold text-sm">
                    Pequena (&lt; 2m²)
                  </div>
                  <div className="p-6 flex-1 flex items-center justify-center bg-[#e2e8f0] relative overflow-hidden min-h-[240px]">
                    <div className="absolute inset-0" style={{ backgroundImage: 'linear-gradient(white 2px, transparent 2px), linear-gradient(90deg, white 2px, transparent 2px)', backgroundSize: '3rem 3rem', opacity: 0.6 }}></div>
                    <div className="w-24 h-20 bg-[#1e3a8a] rounded-[40%_60%_70%_30%/40%_50%_60%_50%] relative z-10 shadow-inner opacity-90"></div>
                    {/* Car */}
                    <div className="absolute top-8 right-8 w-16 h-8 bg-amber-400 rounded-sm z-10 shadow-md rotate-[15deg] border-2 border-amber-500 flex items-center justify-center">
                      <div className="w-4 h-2 bg-red-500 rounded-sm absolute -top-1"></div>
                    </div>
                    {/* Person */}
                    <div className="absolute bottom-8 left-8 w-4 h-4 bg-slate-800 rounded-full z-10 shadow-md"></div>
                  </div>
                </div>
                {/* Média */}
                <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm flex flex-col">
                  <div className="bg-[#5c8edb] text-white text-center py-3 font-bold text-sm">
                    Média (2m² a 5m²)
                  </div>
                  <div className="p-6 flex-1 flex items-center justify-center bg-[#e2e8f0] relative overflow-hidden min-h-[240px]">
                    <div className="absolute inset-0" style={{ backgroundImage: 'linear-gradient(white 2px, transparent 2px), linear-gradient(90deg, white 2px, transparent 2px)', backgroundSize: '3rem 3rem', opacity: 0.6 }}></div>
                    <div className="w-40 h-40 bg-[#1e3a8a] rounded-[60%_40%_30%_70%/60%_30%_70%_40%] relative z-10 shadow-inner opacity-90"></div>
                    <div className="absolute bottom-8 right-8 w-16 h-8 bg-amber-400 rounded-sm z-10 shadow-md -rotate-[15deg] border-2 border-amber-500 flex items-center justify-center">
                      <div className="w-4 h-2 bg-red-500 rounded-sm absolute -top-1"></div>
                    </div>
                    <div className="absolute bottom-12 left-8 w-4 h-4 bg-slate-800 rounded-full z-10 shadow-md"></div>
                  </div>
                </div>
                {/* Grande */}
                <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm flex flex-col">
                  <div className="bg-[#5c8edb] text-white text-center py-3 font-bold text-sm">
                    Grande (&gt; 5m²)
                  </div>
                  <div className="p-6 flex-1 flex items-center justify-center bg-[#e2e8f0] relative overflow-hidden min-h-[240px]">
                    <div className="absolute inset-0" style={{ backgroundImage: 'linear-gradient(white 2px, transparent 2px), linear-gradient(90deg, white 2px, transparent 2px)', backgroundSize: '3rem 3rem', opacity: 0.6 }}></div>
                    <div className="w-56 h-56 bg-[#1e3a8a] rounded-[40%_60%_70%_30%/50%_60%_40%_50%] relative z-10 shadow-inner opacity-90"></div>
                    <div className="absolute bottom-6 right-6 w-16 h-8 bg-amber-400 rounded-sm z-10 shadow-md -rotate-[20deg] border-2 border-amber-500 flex items-center justify-center">
                      <div className="w-4 h-2 bg-red-500 rounded-sm absolute -top-1"></div>
                    </div>
                    <div className="absolute bottom-10 left-6 w-4 h-4 bg-slate-800 rounded-full z-10 shadow-md"></div>
                  </div>
                </div>
              </div>
              <p className="text-center text-xs text-slate-500 mt-6 font-medium">
                Utilize a grade e os veículos/pessoas como referência visual para estimar o tamanho da mancha no local.
              </p>
            </div>
            <div className="p-4 bg-white border-t border-slate-100 flex justify-end">
              <button 
                onClick={() => setShowSpillExample(false)} 
                className="px-8 py-3 bg-[#391694] text-white rounded-none text-xs font-bold hover:bg-[#2a106e] transition-colors shadow-sm"
              >
                Entendido
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
