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

export interface FaunaAttractionRecord {
  id: string;
  airport: string;
  date: string;
  time: string;
  weather: string;
  location: string; // Área Operacional, Área Patrimonial, Área de Segurança Aeroportuária - ASA
  gridMap: string; // Mapa de grade
  attractiveFocus: string; // Anexo 1
  maintenanceProtocol: string; // Protocolo do chamado da manutenção
  vulnerability: string; // Anexo 2
  mitigationPerformed: string; // Qual foi a mitigação realizada no local?
  observations?: string; // Observações (não obrigatório)
  attachments?: string[];
  status: 'Em Análise' | 'Finalizado';
}

const MOCK_RECORDS: FaunaAttractionRecord[] = [
  {
    id: '1',
    airport: 'Aeroporto de Curitiba',
    date: '2026-07-28',
    time: '11:20',
    weather: 'Claro',
    location: 'Área Operacional',
    gridMap: 'Setor B - Grade 14',
    attractiveFocus: 'Acúmulo de água nas valas de drenagem',
    maintenanceProtocol: 'MNT-2026-0412',
    vulnerability: 'Vulnerabilidade nas entradas/saídas dos sistemas de drenagem',
    mitigationPerformed: 'Desobstrução do canal e drenagem emergencial realizada pela equipe de infraestrutura.',
    observations: 'Necessário reforço na verificação semanal do canal.',
    status: 'Finalizado'
  },
  {
    id: '2',
    airport: 'Aeroporto de Goiânia',
    date: '2026-07-29',
    time: '08:45',
    weather: 'Poucas Nuvens',
    location: 'Área Patrimonial',
    gridMap: 'Setor A - Grade 03',
    attractiveFocus: 'Disposição inadequada de resíduos',
    maintenanceProtocol: 'MNT-2026-0418',
    vulnerability: 'Vulnerabilidade na cerca/muro patrimonial',
    mitigationPerformed: 'Notificação imediata da concessionária de limpeza e substituição das lixeiras com tampa basculante.',
    observations: '',
    status: 'Em Análise'
  },
  {
    id: '3',
    airport: 'Aeroporto de Navegantes',
    date: '2026-07-30',
    time: '15:10',
    weather: 'Encoberto',
    location: 'Área de Segurança Aeroportuária - ASA',
    gridMap: 'Setor C - Grade 22',
    attractiveFocus: 'Vegetação servindo de poleiro',
    maintenanceProtocol: 'MNT-2026-0425',
    vulnerability: 'Nenhum',
    mitigationPerformed: 'Podas de adequação executadas nas árvores da faixa de segurança.',
    observations: 'Acompanhamento previsto para o próximo trimestre.',
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

// Anexo 1: Foi identificados focos atrativos de fauna?
const ATTRACTIVE_FOCUS_OPTIONS = [
  'Acúmulo de água nas valas de drenagem',
  'Acúmulo de materiais e entulhos',
  'Atividade humana (pesqueiro,parques, etc.)',
  'Disposição inadequada de resíduos',
  'Edificações abandonadas',
  'Gramado com apara de vegetação acumulada',
  'Grama com o corte recente',
  'Gramado lateral da pista produzindo sementes',
  'Ponto de acúmulo temporário de água',
  'Ponto de referência para empoleiramento de aves',
  'Presença de carcaças',
  'Presença de colônia de insetos',
  'Vegetação com frutos e sementes',
  'Vegetação servindo de poleiro',
  'Nenhum',
  'Ponto de acumulo permanente de agua',
  'Outros'
];

// Anexo 2: Foi identificada vulnerabilidade
const VULNERABILITY_OPTIONS = [
  'Vulnerabilidade na cerca operacional',
  'Vulnerabilidade na cerca/muro patrimonial',
  'Vulnerabilidade nas entradas/saídas dos sistemas de drenagem',
  'Nenhum'
];

const INITIAL_FORM_STATE = {
  airport: '',
  date: new Date().toISOString().split('T')[0],
  time: '12:00',
  weather: 'Claro',
  location: 'Área Operacional',
  gridMap: '',
  attractiveFocus: '',
  maintenanceProtocol: '',
  vulnerability: '',
  mitigationPerformed: '',
  observations: ''
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

export const FaunaAttractionModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [records, setRecords] = useState<FaunaAttractionRecord[]>(MOCK_RECORDS);
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  
  const [actionMenuId, setActionMenuId] = useState<string | null>(null);
  const [viewRecord, setViewRecord] = useState<FaunaAttractionRecord | null>(null);
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
      const newRecord: FaunaAttractionRecord = {
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

  const handleEdit = (record: FaunaAttractionRecord) => {
    setFormData({
      airport: record.airport,
      date: record.date,
      time: record.time,
      weather: record.weather,
      location: record.location,
      gridMap: record.gridMap,
      attractiveFocus: record.attractiveFocus,
      maintenanceProtocol: record.maintenanceProtocol,
      vulnerability: record.vulnerability,
      mitigationPerformed: record.mitigationPerformed,
      observations: record.observations || ''
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
          Foco de Atração de Fauna
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
          {editingId ? 'Editar Foco de Atração' : 'Novo Registro'}
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
                <h3 className="text-2xl font-bold text-slate-900 mb-2">Processando Foco de Atração de Fauna...</h3>
                <p className="text-slate-500">O registro de foco atrativo está sendo salvo no sistema.</p>
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

                {/* 6. Mapa de grade */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">
                    6. Mapa de grade <span className="text-red-500">*</span>
                  </label>
                  <input
                    required
                    type="text"
                    placeholder="Ex: Setor B - Grade 14, Quadra C..."
                    className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                    value={formData.gridMap}
                    onChange={(e) => setFormData({ ...formData, gridMap: e.target.value })}
                  />
                </div>

                {/* 7. Foi identificados focos atrativos de fauna? (Anexo 1) */}
                <SearchableSelect
                  label="7. Foi identificados focos atrativos de fauna?"
                  required
                  options={ATTRACTIVE_FOCUS_OPTIONS}
                  value={formData.attractiveFocus}
                  onChange={(val) => setFormData({ ...formData, attractiveFocus: val })}
                  placeholder="Localizar itens"
                />

                {/* 8. Protocolo do chamado da manutenção */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">
                    8. Protocolo do chamado da manutenção <span className="text-red-500">*</span>
                  </label>
                  <input
                    required
                    type="text"
                    placeholder="Ex: MNT-2026-0891"
                    className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                    value={formData.maintenanceProtocol}
                    onChange={(e) => setFormData({ ...formData, maintenanceProtocol: e.target.value })}
                  />
                </div>

                {/* 9. Foi identificada vulnerabilidade (Anexo 2) */}
                <SearchableSelect
                  label="9. Foi identificada vulnerabilidade"
                  required
                  options={VULNERABILITY_OPTIONS}
                  value={formData.vulnerability}
                  onChange={(val) => setFormData({ ...formData, vulnerability: val })}
                  placeholder="Localizar itens"
                />

                {/* 10. Qual foi a mitigação realizada no local? */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">
                    10. Qual foi a mitigação realizada no local? <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    required
                    rows={3}
                    placeholder="Descreva as ações imediatas ou corretivas tomadas para sanar ou mitigar o foco atrativo..."
                    className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium resize-none"
                    value={formData.mitigationPerformed}
                    onChange={(e) => setFormData({ ...formData, mitigationPerformed: e.target.value })}
                  />
                </div>

                {/* 11. Observações (campo não obrigatório - SEM ASTERISCO VERMELHO) */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">
                    11. Observações
                  </label>
                  <textarea
                    rows={3}
                    placeholder="Informações adicionais, observações de acompanhamento ou pendências (opcional)..."
                    className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium resize-none"
                    value={formData.observations}
                    onChange={(e) => setFormData({ ...formData, observations: e.target.value })}
                  />
                </div>

                {/* 12. Anexos */}
                <div className="border-t border-slate-100 pt-6">
                  <h3 className="text-sm font-bold text-slate-800 uppercase tracking-widest mb-4">
                    12. Anexos
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
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Mapa de Grade</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Foco Atrativo</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Vulnerabilidade</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Protocolo MNT</th>
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
                            <span className="text-xs font-semibold text-slate-800">
                              {record.gridMap}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span className="text-xs font-bold text-[#166534] bg-emerald-50 px-2.5 py-1 border border-emerald-200 inline-block">
                              {record.attractiveFocus || 'N/A'}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span className="text-xs font-semibold text-slate-800">
                              {record.vulnerability || 'N/A'}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span className="text-xs font-mono font-bold text-slate-700 bg-slate-100 px-2 py-0.5 border border-slate-200">
                              {record.maintenanceProtocol || 'N/A'}
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
                      <td colSpan={7} className="px-6 py-12 text-center text-slate-400 text-sm font-medium">
                        Nenhum registro de foco de atração de fauna encontrado.
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
                Detalhes - Foco de Atração de Fauna
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
                  <span className="text-slate-400 block font-bold uppercase text-[10px]">6. Mapa de grade</span>
                  <span className="font-semibold text-slate-900">{viewRecord.gridMap}</span>
                </div>
                <div>
                  <span className="text-slate-400 block font-bold uppercase text-[10px]">7. Foco Atrativo de Fauna</span>
                  <span className="font-bold text-[#166534] bg-emerald-50 px-2 py-0.5 border border-emerald-200 inline-block mt-0.5">
                    {viewRecord.attractiveFocus}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block font-bold uppercase text-[10px]">8. Protocolo Chamado MNT</span>
                  <span className="font-mono font-bold text-slate-900">{viewRecord.maintenanceProtocol}</span>
                </div>
                <div>
                  <span className="text-slate-400 block font-bold uppercase text-[10px]">9. Vulnerabilidade</span>
                  <span className="font-semibold text-slate-900">{viewRecord.vulnerability}</span>
                </div>
                <div className="col-span-2 bg-slate-50 p-4 border border-slate-100 mt-2">
                  <span className="text-slate-400 block font-bold uppercase text-[10px] mb-1">10. Mitigação Realizada no Local</span>
                  <p className="text-slate-800 leading-relaxed font-normal">{viewRecord.mitigationPerformed}</p>
                </div>
                {viewRecord.observations && (
                  <div className="col-span-2 bg-slate-50 p-4 border border-slate-100">
                    <span className="text-slate-400 block font-bold uppercase text-[10px] mb-1">11. Observações</span>
                    <p className="text-slate-800 leading-relaxed font-normal">{viewRecord.observations}</p>
                  </div>
                )}
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
