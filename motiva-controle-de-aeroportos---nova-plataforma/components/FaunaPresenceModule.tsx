import React, { useState } from 'react';
import { 
  PlusCircle, 
  History, 
  CheckCircle2, 
  ArrowRight, 
  Calendar, 
  UploadCloud, 
  Trash2, 
  MoreHorizontal, 
  Eye, 
  Pencil, 
  Building2, 
  FileSpreadsheet, 
  ChevronDown, 
  Search,
  X
} from 'lucide-react';
import { AIRPORTS } from './AISComplianceForm';

export interface FaunaPresenceRecord {
  id: string;
  airport: string;
  date: string;
  time: string;
  weather: string;
  location: string; // Área Operacional, Área Patrimonial, Área de Segurança Aeroportuária - ASA
  occurrenceType: string; // Afugentamento, Captura, Manejo de Brando, Coleta de Carcaça, Nenhum, Presença, Vestígio
  evidence: string; // Escuta, Ninho, Fezes, Ovos, Presença, Penas, Pegadas
  behavior: string; // Buscando alimento, Se alimentando, Empoleirado, Parado no chão, Dentro do ninho, Outros
  description: string;
  attachments?: string[];
  status: 'Em Análise' | 'Finalizado';
}

const MOCK_RECORDS: FaunaPresenceRecord[] = [
  {
    id: '1',
    airport: 'Aeroporto de Curitiba',
    date: '2026-07-28',
    time: '14:30',
    weather: 'Claro',
    location: 'Área Operacional',
    occurrenceType: 'Afugentamento',
    evidence: 'Presença',
    behavior: 'Buscando alimento',
    description: 'Avistado bando de Quero-queros próximo à taxiway B. Realizado afugentamento sonoro com veículo da fiscalização do pátio sem alterações.',
    status: 'Finalizado'
  },
  {
    id: '2',
    airport: 'Aeroporto de Goiânia',
    date: '2026-07-29',
    time: '09:15',
    weather: 'Poucas Nuvens',
    location: 'Área de Segurança Aeroportuária - ASA',
    occurrenceType: 'Presença',
    evidence: 'Ninho',
    behavior: 'Dentro do ninho',
    description: 'Localizado ninho ativo de Coruja-buraqueira nas proximidades da cabeceira 14. Área sinalizada e monitorada.',
    status: 'Em Análise'
  },
  {
    id: '3',
    airport: 'Aeroporto de Navegantes',
    date: '2026-07-30',
    time: '16:00',
    weather: 'Encoberto',
    location: 'Área Patrimonial',
    occurrenceType: 'Vestígio',
    evidence: 'Fezes',
    behavior: 'Outros',
    description: 'Identificados vestígios de fezes e penas de urubus na estrutura do galpão de manutenção. Equipe acionada para limpeza e colocação de barreiras físicas.',
    status: 'Finalizado'
  }
];

const WEATHER_OPTIONS = [
  'Claro',
  'Poucas Nuvens',
  'Encoberto',
  'Chuva',
  'Nevoeiro',
  'Tempestade'
];

const LOCATION_OPTIONS = [
  'Área Operacional',
  'Área Patrimonial',
  'Área de Segurança Aeroportuária - ASA'
];

// Anexo 1: Foi registrada alguma ocorrência com fauna?
const OCCURRENCE_OPTIONS = [
  'Afugentamento',
  'Captura',
  'Manejo de Brando',
  'Coleta de Carcaça',
  'Nenhum',
  'Presença',
  'Vestígio'
];

// Anexo 2: Há evidências?
const EVIDENCE_OPTIONS = [
  'Escuta',
  'Ninho',
  'Fezes',
  'Ovos',
  'Presença',
  'Penas',
  'Pegadas'
];

// Anexo 3: Comportamento do animal ou bando
const BEHAVIOR_OPTIONS = [
  'Buscando alimento',
  'Se alimentando',
  'Empoleirado',
  'Parado no chão',
  'Dentro do ninho',
  'Outros'
];

const INITIAL_FORM_STATE = {
  airport: '',
  date: new Date().toISOString().split('T')[0],
  time: '12:00',
  weather: 'Claro',
  location: 'Área Operacional',
  occurrenceType: '',
  evidence: '',
  behavior: '',
  description: ''
};

interface SearchableSelectProps {
  label: string;
  required?: boolean;
  options: string[];
  value: string;
  onChange: (val: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

const SearchableSelect: React.FC<SearchableSelectProps> = ({
  label,
  required,
  options,
  value,
  onChange,
  placeholder = 'Localizar itens',
  disabled
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const filtered = options.filter(opt =>
    opt.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-2 relative">
      <label className="text-[13px] font-bold text-slate-900 block">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      
      <div className="relative">
        <button
          type="button"
          disabled={disabled}
          onClick={() => setIsOpen(!isOpen)}
          className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-left text-slate-700 outline-none focus:border-[#391694] transition-all flex items-center justify-between font-medium disabled:bg-slate-50 disabled:cursor-not-allowed"
        >
          <span className={value ? 'text-slate-900 font-semibold' : 'text-slate-400'}>
            {value || 'Selecione...'}
          </span>
          <ChevronDown className={`w-5 h-5 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </button>

        {isOpen && !disabled && (
          <div className="absolute z-50 left-0 right-0 top-full mt-1 bg-white border border-slate-200 shadow-2xl rounded-none overflow-hidden animate-in fade-in duration-150">
            <div className="p-2 border-b border-slate-100 flex items-center gap-2 bg-slate-50">
              <Search className="w-4 h-4 text-slate-400 ml-2 shrink-0" />
              <input
                type="text"
                autoFocus
                placeholder={placeholder}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full py-1.5 px-2 bg-transparent text-xs text-slate-800 outline-none placeholder:text-slate-400 font-medium"
              />
              {searchTerm && (
                <button 
                  type="button" 
                  onClick={() => setSearchTerm('')} 
                  className="p-1 hover:bg-slate-200 rounded-full text-slate-400"
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>

            <div className="max-h-56 overflow-y-auto divide-y divide-slate-50">
              {filtered.length > 0 ? (
                filtered.map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => {
                      onChange(option);
                      setIsOpen(false);
                      setSearchTerm('');
                    }}
                    className={`w-full text-left px-4 py-3 text-xs font-semibold transition-colors flex items-center justify-between ${
                      value === option
                        ? 'bg-[#F5F3FF] text-[#391694] border-l-4 border-[#391694]'
                        : 'text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <span>{option}</span>
                    {value === option && <CheckCircle2 className="w-4 h-4 text-[#391694]" />}
                  </button>
                ))
              ) : (
                <div className="p-4 text-center text-xs text-slate-400 font-medium">
                  Nenhum item encontrado.
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export const FaunaPresenceModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [records, setRecords] = useState<FaunaPresenceRecord[]>(MOCK_RECORDS);
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  
  const [actionMenuId, setActionMenuId] = useState<string | null>(null);
  const [viewRecord, setViewRecord] = useState<FaunaPresenceRecord | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  const [filterAirport, setFilterAirport] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const [formData, setFormData] = useState(INITIAL_FORM_STATE);

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
      const newRecord: FaunaPresenceRecord = {
        id: editingId || Math.random().toString(36).substr(2, 9),
        ...formData,
        attachments: selectedImages.map(f => f.name),
        status: 'Em Análise'
      };

      if (editingId) {
        setRecords(records.map(r => r.id === editingId ? newRecord : r));
      } else {
        setRecords([newRecord, ...records]);
      }

      setIsSubmitting(false);
      setActiveTab('history');
      setFormData(INITIAL_FORM_STATE);
      setSelectedImages([]);
      setEditingId(null);
    }, 1200);
  };

  const handleEdit = (record: FaunaPresenceRecord) => {
    setFormData({
      airport: record.airport,
      date: record.date,
      time: record.time,
      weather: record.weather,
      location: record.location,
      occurrenceType: record.occurrenceType,
      evidence: record.evidence,
      behavior: record.behavior,
      description: record.description
    });
    setEditingId(record.id);
    setActiveTab('form');
    setActionMenuId(null);
  };

  const handleDelete = (id: string) => {
    if (confirm('Tem certeza que deseja excluir este registro?')) {
      setRecords(records.filter(r => r.id !== id));
      setActionMenuId(null);
    }
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 shrink-0">
        <h2 className="text-[26px] font-bold text-slate-900 tracking-tight leading-tight uppercase">
          Presença de Fauna
        </h2>
      </div>

      <div className="flex p-1 bg-slate-50 rounded-none w-fit border border-slate-200 shrink-0">
        <button
          onClick={() => { 
            setActiveTab('form'); 
            setEditingId(null); 
            setViewRecord(null);
            setFormData(INITIAL_FORM_STATE); 
          }}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-none text-[13px] font-bold transition-all ${
            activeTab === 'form' ? 'bg-white text-[#391694] shadow-sm' : 'text-slate-400 hover:text-slate-600'
          }`}
        >
          <PlusCircle className="w-4 h-4" />
          {editingId ? 'Editar Ocorrência' : 'Novo Registro'}
        </button>
        <button
          onClick={() => { 
            setActiveTab('history'); 
            setEditingId(null); 
            setViewRecord(null);
            setFormData(INITIAL_FORM_STATE); 
          }}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-none text-[13px] font-bold transition-all ${
            activeTab === 'history' ? 'bg-white text-[#391694] shadow-sm' : 'text-slate-400 hover:text-slate-600'
          }`}
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
                <h3 className="text-2xl font-bold text-slate-900 mb-2">Processando Registro de Fauna...</h3>
                <p className="text-slate-500">O reporte de presença de fauna está sendo salvo no sistema.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-[26px]">
                {/* 1. Aeroporto */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">
                    1. Aeroporto <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <select
                      required
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium"
                      value={formData.airport}
                      onChange={(e) => setFormData({ ...formData, airport: e.target.value })}
                    >
                      <option value="">Selecione o aeroporto</option>
                      {AIRPORTS.map(ap => <option key={ap} value={ap}>{ap}</option>)}
                    </select>
                    <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                  </div>
                </div>

                {/* 2 & 3. Data e Hora */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      2. Data do Evento <span className="text-red-500">*</span>
                    </label>
                    <input
                      required
                      type="date"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                      value={formData.date}
                      onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      3. Hora do Evento (UTC) <span className="text-red-500">*</span>
                    </label>
                    <input
                      required
                      type="time"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                      value={formData.time}
                      onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                    />
                  </div>
                </div>

                {/* 4 & 5. Clima e Local */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  {/* 4. Clima */}
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      4. Clima <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <select
                        required
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium"
                        value={formData.weather}
                        onChange={(e) => setFormData({ ...formData, weather: e.target.value })}
                      >
                        <option value="">Selecione o clima</option>
                        {WEATHER_OPTIONS.map(w => <option key={w} value={w}>{w}</option>)}
                      </select>
                      <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>

                  {/* 5. Local */}
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      5. Local <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <select
                        required
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium"
                        value={formData.location}
                        onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                      >
                        <option value="">Selecione o local...</option>
                        {LOCATION_OPTIONS.map(loc => <option key={loc} value={loc}>{loc}</option>)}
                      </select>
                      <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>
                </div>

                {/* 6. Foi registrada alguma ocorrência com fauna? (Anexo 1) */}
                <SearchableSelect
                  label="6. Foi registrada alguma ocorrência com fauna?"
                  required
                  options={OCCURRENCE_OPTIONS}
                  value={formData.occurrenceType}
                  onChange={(val) => setFormData({ ...formData, occurrenceType: val })}
                  placeholder="Localizar itens"
                />

                {/* 7. Há evidências? (Anexo 2) */}
                <SearchableSelect
                  label="7. Há evidências?"
                  required
                  options={EVIDENCE_OPTIONS}
                  value={formData.evidence}
                  onChange={(val) => setFormData({ ...formData, evidence: val })}
                  placeholder="Localizar itens"
                />

                {/* 8. Comportamento do animal ou bando (Anexo 3) */}
                <SearchableSelect
                  label="8. Comportamento do animal ou bando"
                  required
                  options={BEHAVIOR_OPTIONS}
                  value={formData.behavior}
                  onChange={(val) => setFormData({ ...formData, behavior: val })}
                  placeholder="Localizar itens"
                />

                {/* 9. Descrição do evento/observação */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">
                    9. Descrição do evento/observação <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    required
                    rows={4}
                    placeholder="Descreva detalhadamente a presença de fauna, quantidade estimada de animais, ações tomadas e observações adicionais..."
                    className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium resize-none"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  />
                </div>

                {/* 10. Anexos */}
                <div className="border-t border-slate-100 pt-6">
                  <h3 className="text-sm font-bold text-slate-800 uppercase tracking-widest mb-4">
                    10. Anexos
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    {selectedImages.map((file, index) => (
                      <div key={index} className="relative aspect-square bg-slate-100 border border-slate-200 group">
                        <img src={URL.createObjectURL(file)} alt="Preview" className="w-full h-full object-cover" />
                        <button
                          type="button"
                          onClick={() => removeImage(index)}
                          className="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                    <label className="flex flex-col items-center justify-center aspect-square border-2 border-dashed border-slate-300 bg-slate-50 hover:bg-emerald-50 hover:border-[#166534] hover:text-[#166534] transition-all cursor-pointer group text-slate-400">
                      <input type="file" multiple accept="image/*,.pdf,.doc,.docx" className="hidden" onChange={handleImageChange} />
                      <UploadCloud className="w-8 h-8 mb-2 group-hover:scale-110 transition-transform" />
                      <span className="text-xs font-bold uppercase text-center px-2">Anexar Documento / Foto</span>
                    </label>
                  </div>
                </div>

                {/* Submit button */}
                <div className="flex justify-end pt-4">
                  <button
                    type="submit"
                    className="flex items-center gap-3 bg-black text-white px-10 py-4 rounded-none font-bold shadow-lg hover:scale-105 transition-all group"
                  >
                    <span>{editingId ? 'Salvar Alterações' : 'Finalizar Registro'}</span>
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              </form>
            )}
          </div>
        ) : (
          <div className="flex flex-col min-h-0 animate-in fade-in duration-500 w-full">
            {/* Filter bar */}
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

            {/* Table */}
            <div className="bg-white border border-slate-200 rounded-none shadow-sm relative overflow-x-auto w-full min-h-[320px]">
              <table className="w-full text-center border-separate border-spacing-0">
                <thead>
                  <tr className="bg-slate-50">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Data/Hora</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Aeroporto / Local</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Ocorrência com Fauna</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Evidência</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Comportamento</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center whitespace-nowrap">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredRecords.length > 0 ? (
                    filteredRecords.map((record, index) => {
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
                              <span className="text-xs font-bold text-slate-900">{record.airport}</span>
                              <span className="text-[10px] text-slate-500 font-medium">{record.location}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span className="text-xs font-bold text-[#166534] bg-emerald-50 px-2.5 py-1 border border-emerald-200 inline-block">
                              {record.occurrenceType || 'N/A'}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span className="text-xs font-semibold text-slate-800">
                              {record.evidence || 'N/A'}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span className="text-xs text-slate-600 font-medium">
                              {record.behavior || 'N/A'}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center relative">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setActionMenuId(actionMenuId === record.id ? null : record.id);
                              }}
                              className={`p-1.5 rounded-none transition-all ${
                                actionMenuId === record.id
                                  ? 'bg-[#391694] text-white shadow-md'
                                  : 'text-slate-400 hover:text-[#391694] hover:bg-purple-50 border border-slate-200'
                              }`}
                            >
                              <MoreHorizontal className="w-5 h-5" />
                            </button>

                            {actionMenuId === record.id && (
                              <div
                                className={`absolute z-50 right-14 w-44 bg-white border border-slate-200 rounded-none shadow-2xl overflow-hidden animate-in fade-in slide-in-from-right-2 duration-200 ${
                                  isLastRows ? 'bottom-0' : 'top-1/2 -translate-y-1/2'
                                }`}
                              >
                                <button
                                  onClick={() => {
                                    setViewRecord(record);
                                    setActionMenuId(null);
                                  }}
                                  className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"
                                >
                                  <Eye className="w-4 h-4 text-slate-400" /> Visualizar
                                </button>
                                <button
                                  onClick={() => handleEdit(record)}
                                  className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"
                                >
                                  <Pencil className="w-4 h-4 text-slate-400" /> Editar
                                </button>
                                <button
                                  onClick={() => handleDelete(record.id)}
                                  className="w-full text-left px-4 py-3 text-[11px] font-bold text-red-600 hover:bg-red-50 flex items-center gap-3"
                                >
                                  <Trash2 className="w-4 h-4 text-red-500" /> Excluir
                                </button>
                              </div>
                            )}
                          </td>
                        </tr>
                      );
                    })
                  ) : (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center text-slate-400 text-sm font-medium">
                        Nenhum registro de presença de fauna encontrado.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* View Modal */}
        {viewRecord && (
          <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-white border border-slate-200 max-w-2xl w-full p-8 shadow-2xl relative animate-in zoom-in duration-200">
              <button
                onClick={() => setViewRecord(null)}
                className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 rounded-full"
              >
                <X className="w-5 h-5" />
              </button>

              <h3 className="text-xl font-bold text-slate-900 mb-6 border-b border-slate-100 pb-4 uppercase">
                Detalhes - Presença de Fauna
              </h3>

              <div className="grid grid-cols-2 gap-4 text-xs font-medium text-slate-700 mb-6">
                <div>
                  <span className="text-slate-400 block font-bold uppercase text-[10px]">1. Aeroporto</span>
                  <span className="font-semibold text-slate-900">{viewRecord.airport}</span>
                </div>
                <div>
                  <span className="text-slate-400 block font-bold uppercase text-[10px]">2 & 3. Data e Hora</span>
                  <span className="font-semibold text-slate-900">{viewRecord.date} às {viewRecord.time} UTC</span>
                </div>
                <div>
                  <span className="text-slate-400 block font-bold uppercase text-[10px]">4. Clima</span>
                  <span className="font-semibold text-slate-900">{viewRecord.weather}</span>
                </div>
                <div>
                  <span className="text-slate-400 block font-bold uppercase text-[10px]">5. Local</span>
                  <span className="font-semibold text-slate-900">{viewRecord.location}</span>
                </div>
                <div>
                  <span className="text-slate-400 block font-bold uppercase text-[10px]">6. Ocorrência com Fauna</span>
                  <span className="font-bold text-[#166534] bg-emerald-50 px-2 py-0.5 border border-emerald-200 inline-block mt-0.5">
                    {viewRecord.occurrenceType}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block font-bold uppercase text-[10px]">7. Evidência</span>
                  <span className="font-semibold text-slate-900">{viewRecord.evidence}</span>
                </div>
                <div className="col-span-2">
                  <span className="text-slate-400 block font-bold uppercase text-[10px]">8. Comportamento do animal ou bando</span>
                  <span className="font-semibold text-slate-900">{viewRecord.behavior}</span>
                </div>
                <div className="col-span-2 bg-slate-50 p-4 border border-slate-100 mt-2">
                  <span className="text-slate-400 block font-bold uppercase text-[10px] mb-1">9. Descrição do evento/observação</span>
                  <p className="text-slate-800 leading-relaxed font-normal">{viewRecord.description}</p>
                </div>
              </div>

              <div className="flex justify-end pt-4 border-t border-slate-100">
                <button
                  onClick={() => setViewRecord(null)}
                  className="px-6 py-2.5 bg-black text-white text-xs font-bold uppercase"
                >
                  Fechar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
