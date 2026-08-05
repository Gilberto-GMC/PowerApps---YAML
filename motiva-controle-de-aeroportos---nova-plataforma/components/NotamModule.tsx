
import React, { useState, useMemo } from 'react';
import { 
  PlusCircle, 
  History, 
  CheckCircle2, 
  ArrowRight,
  Trash2,
  FileSpreadsheet,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Lock,
  Building2,
  Calendar
} from 'lucide-react';

const AIRPORTS = [
  "Aeroporto de Bagé",
  "Aeroporto de Uruguaiana",
  "Aeroporto de Pelotas",
  "Aeroporto de Navegantes",
  "Aeroporto de Joinville",
  "Aeroporto de Londrina",
  "Aeroporto de Foz do Iguaçu",
  "Aeroporto de Bacacheri",
  "Aeroporto de Curitiba",
  "Aeroporto da Pampulha",
  "Aeroporto de Goiânia",
  "Aeroporto de Palmas",
  "Aeroporto de Imperatriz",
  "Aeroporto de Teresina",
  "Aeroporto de Petrolina",
  "Aeroporto de São Luís"
];

interface NotamRecord {
  id: string;
  airport: string;
  notamNumber: string;
  startDate: string;
  startTime: string;
  endDate: string;
  endTime: string;
  text: string;
  alertDays: number;
  status: 'Vigente' | 'Vencido' | 'Futuro';
}

const MOCK_RECORDS: NotamRecord[] = [
  {
    id: '1',
    airport: 'Aeroporto de Navegantes',
    notamNumber: 'E1234/24',
    startDate: '2024-05-01',
    startTime: '10:00',
    endDate: '2024-06-01',
    endTime: '23:59',
    text: 'OBST MOVEL (GUINDASTE) ACIONADO AZM 230 DEG DIST 1500M THR 07',
    alertDays: 15,
    status: 'Vigente'
  },
  {
    id: '2',
    airport: 'Aeroporto de Curitiba',
    notamNumber: 'D0987/24',
    startDate: '2024-06-10',
    startTime: '08:00',
    endDate: '2024-06-15',
    endTime: '18:00',
    text: 'PJE EM ANDAMENTO SOBRE O AD',
    alertDays: 5,
    status: 'Futuro'
  }
];

export const NotamModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [records, setRecords] = useState<NotamRecord[]>(MOCK_RECORDS);

  // Filtros
  const [airportFilter, setAirportFilter] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Ordenação
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);

  const [formData, setFormData] = useState({
    airport: '',
    notamNumber: '',
    startDate: '',
    startTime: '',
    endDate: '',
    endTime: '',
    text: '',
    alertDays: 15
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    setTimeout(() => {
      const newRecord: NotamRecord = {
        id: Math.random().toString(36).substr(2, 9),
        ...formData,
        status: 'Vigente' // Simplificação para demo
      };

      setRecords([newRecord, ...records]);
      setIsSubmitting(false);
      setActiveTab('history');
      
      setFormData({
        airport: '',
        notamNumber: '',
        startDate: '',
        startTime: '',
        endDate: '',
        endTime: '',
        text: '',
        alertDays: 15
      });
    }, 1500);
  };

  const handleSort = (key: string) => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const filteredAndSortedRecords = useMemo(() => {
    // 1. Filtragem
    let result = records.filter(record => {
      const matchesAirport = airportFilter === '' || record.airport === airportFilter;
      
      const recordDate = new Date(record.startDate);
      const start = startDate ? new Date(startDate) : null;
      const end = endDate ? new Date(endDate) : null;
      const matchesDate = (!start || recordDate >= start) && (!end || recordDate <= end);
      
      return matchesAirport && matchesDate;
    });

    // 2. Ordenação
    if (sortConfig) {
      result.sort((a, b) => {
        let aValue: any;
        let bValue: any;

        // Lógica específica para ordenar por "Vencimento" (usa data/hora de término)
        if (sortConfig.key === 'validity') {
          aValue = new Date(`${a.endDate}T${a.endTime}`).getTime();
          bValue = new Date(`${b.endDate}T${b.endTime}`).getTime();
        } else {
          // Ordenação genérica
          aValue = a[sortConfig.key as keyof NotamRecord];
          bValue = b[sortConfig.key as keyof NotamRecord];
        }

        if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return result;
  }, [records, airportFilter, startDate, endDate, sortConfig]);

  const SortIcon = ({ columnKey }: { columnKey: string }) => {
    if (sortConfig?.key !== columnKey) return <ArrowUpDown className="w-3 h-3 text-slate-300 group-hover:text-slate-500" />;
    return sortConfig.direction === 'asc' 
      ? <ArrowUp className="w-3 h-3 text-[#391694]" />
      : <ArrowDown className="w-3 h-3 text-[#391694]" />;
  };

  const renderHeader = (label: string, sortKey: string, align: 'left' | 'center' | 'right' = 'left') => (
    <th 
      className={`px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap cursor-pointer hover:bg-slate-100 transition-colors group select-none ${align === 'center' ? 'text-center' : align === 'right' ? 'text-right' : 'text-left'}`}
      onClick={() => handleSort(sortKey)}
    >
      <div className={`flex items-center gap-2 ${align === 'center' ? 'justify-center' : align === 'right' ? 'justify-end' : 'justify-start'}`}>
        {label}
        <SortIcon columnKey={sortKey} />
      </div>
    </th>
  );

  return (
    <div className="flex flex-col gap-[26px] relative h-full w-full">
      {/* Header */}
      <h2 className="text-[26px] font-bold text-slate-900 tracking-tight leading-tight uppercase shrink-0">
        NOTAMs / Suplementos AIP
      </h2>

      {/* Tabs */}
      <div className="flex p-1 bg-slate-50 rounded-none w-fit border border-slate-200 shrink-0">
        <button
          onClick={() => setActiveTab('form')}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-none text-[13px] font-bold transition-all ${
            activeTab === 'form' 
              ? 'bg-white text-[#391694] shadow-sm' 
              : 'text-slate-400 hover:text-slate-600'
          }`}
        >
          <PlusCircle className="w-4 h-4" />
          Novo Registro
        </button>
        <button
          onClick={() => setActiveTab('history')}
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
                <h3 className="text-2xl font-bold text-slate-900 mb-2">Salvando NOTAM...</h3>
                <p className="text-slate-500">O registro está sendo sincronizado com a base de dados.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-[26px]">
                <div className="bg-amber-50 border border-amber-200 p-4 shadow-sm mb-[26px]">
                  <p className="text-[13px] text-amber-800 font-medium">
                    <strong className="uppercase tracking-wider mr-1">Acesso Restrito:</strong>
                    Este módulo é de preenchimento exclusivo pelos <strong>Analistas de Aeroportos</strong>.
                  </p>
                </div>

                {/* Aeroporto e Número */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Aeroporto *
                    </label>
                    <div className="relative">
                      <select
                        required
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer"
                        value={formData.airport}
                        onChange={(e) => setFormData({...formData, airport: e.target.value})}
                      >
                        <option value="">Selecione o aeroporto</option>
                        {AIRPORTS.map(ap => <option key={ap} value={ap}>{ap}</option>)}
                      </select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Número do NOTAM / Suplemento AIP *
                    </label>
                    <div className="relative">
                      <input
                        required
                        type="text"
                        placeholder="Ex: E1234/24"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-[#391694] transition-all font-medium uppercase"
                        value={formData.notamNumber}
                        onChange={(e) => setFormData({...formData, notamNumber: e.target.value})}
                      />
                    </div>
                  </div>
                </div>

                {/* Início da Vigência */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Data de Início *
                    </label>
                    <input
                      required
                      type="date"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all"
                      value={formData.startDate}
                      onChange={(e) => setFormData({...formData, startDate: e.target.value})}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Hora de Início (UTC) *
                    </label>
                    <input
                      required
                      type="time"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all"
                      value={formData.startTime}
                      onChange={(e) => setFormData({...formData, startTime: e.target.value})}
                    />
                  </div>
                </div>

                {/* Término da Vigência */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Data de Término *
                    </label>
                    <input
                      required
                      type="date"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all"
                      value={formData.endDate}
                      onChange={(e) => setFormData({...formData, endDate: e.target.value})}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Hora de Término (UTC) *
                    </label>
                    <input
                      required
                      type="time"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all"
                      value={formData.endTime}
                      onChange={(e) => setFormData({...formData, endTime: e.target.value})}
                    />
                  </div>
                </div>

                {/* Texto do NOTAM */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">
                    Texto do NOTAM *
                  </label>
                  <div className="relative">
                    <textarea
                      required
                      rows={4}
                      placeholder="Insira o texto completo do NOTAM..."
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-[#391694] transition-all resize-none font-mono uppercase"
                      value={formData.text}
                      onChange={(e) => setFormData({...formData, text: e.target.value})}
                    />
                  </div>
                </div>

                {/* Configuração de Alerta */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">
                    Configuração de Alerta (Dias)
                  </label>
                  <div className="relative max-w-xs">
                    <input
                      type="number"
                      min="1"
                      placeholder="15"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-bold"
                      value={formData.alertDays}
                      onChange={(e) => setFormData({...formData, alertDays: parseInt(e.target.value) || 0})}
                    />
                    <span className="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-slate-400 pointer-events-none font-medium">dias antes</span>
                  </div>
                  <p className="text-[11px] text-slate-400">O sistema alertará o vencimento com a antecedência configurada.</p>
                </div>

                <div className="flex justify-end pt-4">
                  <button
                    type="submit"
                    className="flex items-center gap-3 bg-black text-white px-10 py-4 rounded-none font-bold shadow-lg hover:scale-105 transition-all group"
                  >
                    <span>Salvar NOTAM</span>
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
                <div className="relative min-w-[240px]">
                  <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <select 
                    value={airportFilter}
                    onChange={(e) => setAirportFilter(e.target.value)}
                    className="w-full pl-10 pr-8 h-10 bg-white border border-slate-200 rounded-none text-sm outline-none focus:ring-2 focus:ring-[#391694]/10 focus:border-[#391694] transition-all appearance-none cursor-pointer"
                  >
                    <option value="">Todos os Aeroportos</option>
                    {AIRPORTS.map(ap => <option key={ap} value={ap}>{ap}</option>)}
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
              <table className="w-full text-center border-separate border-spacing-0 table-fixed">
                <thead>
                  <tr className="bg-slate-50">
                    {renderHeader('Status', 'status', 'center')}
                    {renderHeader('NOTAM', 'notamNumber', 'center')}
                    {renderHeader('Aeroporto', 'airport', 'center')}
                    {renderHeader('Vigência', 'validity', 'center')}
                    {renderHeader('Alerta', 'alertDays', 'center')}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredAndSortedRecords.map((record) => (
                    <tr key={record.id} className="hover:bg-slate-50/50 transition-colors group">
                      <td className="px-6 py-4 text-center">
 <span className={`inline-flex items-center px-2 py-1 rounded-sm text-[10px] font-black uppercase tracking-wider ${
 record.status === 'Vigente' 
 ? 'bg-emerald-100 text-emerald-700' 
 : record.status === 'Vencido'
 ? 'bg-red-100 text-red-700'
 : 'bg-indigo-100 text-indigo-700'
 }`}>
 {record.status}
 </span>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex flex-col items-center">
 <span className="text-xs font-bold text-slate-900">{record.notamNumber}</span>
 <span className="text-[10px] text-slate-500 font-medium mt-0.5 line-clamp-1 max-w-[200px]" title={record.text}>{record.text}</span>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="text-xs text-slate-700 font-medium whitespace-normal leading-tight max-w-[200px] mx-auto">
 {record.airport}
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex flex-col gap-1 justify-center items-center">
 <div className="flex items-center gap-2 justify-center">
 <span className="text-[10px] font-bold text-emerald-600 w-6 text-right">INI:</span> 
 <span className="text-xs font-semibold text-slate-700">{record.startDate.split('-').reverse().join('/')}</span>
 <span className="text-[10px] text-slate-500 font-medium">{record.startTime}</span>
 </div>
 <div className="flex items-center gap-2 justify-center">
 <span className="text-[10px] font-bold text-red-600 w-6 text-right">FIM:</span> 
 <span className="text-xs font-semibold text-slate-700">{record.endDate.split('-').reverse().join('/')}</span>
 <span className="text-[10px] text-slate-500 font-medium">{record.endTime}</span>
 </div>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex items-center justify-center gap-2 text-slate-500">
 <span className="text-xs font-medium text-slate-600">{record.alertDays} dias</span>
 </div>
 </td>
                    </tr>
                  ))}
                  {filteredAndSortedRecords.length === 0 && (
                     <tr>
                        <td colSpan={5} className="py-12 text-center text-slate-400">
 Nenhum NOTAM registrado para os filtros selecionados.
 </td>
                     </tr>
                  )}
                </tbody>
              </table>
            </div>
            <div className="bg-slate-50 px-6 py-3 border border-t-0 border-slate-200 text-[10px] text-slate-400 font-bold uppercase tracking-widest">
                {filteredAndSortedRecords.length} REGISTROS ENCONTRADOS
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
