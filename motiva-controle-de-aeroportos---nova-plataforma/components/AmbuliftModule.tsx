import React, { useState, useEffect } from 'react';
import { 
  PlusCircle, 
  RotateCcw, 
  ChevronDown, 
  CheckCircle2, 
  ArrowRight,
  Plane,
  Clock,
  Calendar,
  Accessibility,
  Search,
  Filter,
  MoreHorizontal,
  Eye,
  Pencil,
  Trash2,
  XCircle
} from 'lucide-react';

type Airline = 'Gol Linhas Aéreas' | 'Azul Linhas Aéreas' | 'LATAM Linhas Aéreas' | 'Outras' | '';

interface AmbuliftRecord {
  id: string;
  airline: Airline;
  customAirline?: string;
  flightNumber: string;
  date: string;
  startTime: string;
  endTime: string;
  status: 'Concluído' | 'Agendado';
}

const MOCK_RECORDS: AmbuliftRecord[] = [
  {
    id: '1',
    airline: 'Azul Linhas Aéreas',
    flightNumber: 'AD 4055',
    date: '2024-05-18',
    startTime: '14:30',
    endTime: '14:50',
    status: 'Concluído'
  },
  {
    id: '2',
    airline: 'Gol Linhas Aéreas',
    flightNumber: 'G3 1244',
    date: '2024-05-18',
    startTime: '10:15',
    endTime: '10:35',
    status: 'Agendado'
  },
  {
    id: '3',
    airline: 'LATAM Linhas Aéreas',
    flightNumber: 'LA 3302',
    date: '2024-05-17',
    startTime: '18:00',
    endTime: '18:20',
    status: 'Concluído'
  }
];

export const AmbuliftModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [records, setRecords] = useState<AmbuliftRecord[]>(MOCK_RECORDS);
  const [filterAirline, setFilterAirline] = useState<string>('');
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  
  const [concluirId, setConcluirId] = useState<string | null>(null);
  const [concluirData, setConcluirData] = useState({ startTime: '', endTime: '' });

  const [formData, setFormData] = useState({
    airline: '' as Airline,
    customAirline: '',
    flightNumber: '',
    date: new Date().toISOString().split('T')[0],
    startTime: '',
    endTime: ''
  });

  // Automatically calculate end time (Start + 20min)
  const handleStartTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newStart = e.target.value;
    let newEnd = formData.endTime;

    if (newStart) {
      const [hours, minutes] = newStart.split(':').map(Number);
      const startDate = new Date();
      startDate.setHours(hours);
      startDate.setMinutes(minutes);
      
      // Add 20 minutes
      const endDate = new Date(startDate.getTime() + 20 * 60000);
      const endHours = String(endDate.getHours()).padStart(2, '0');
      const endMinutes = String(endDate.getMinutes()).padStart(2, '0');
      
      newEnd = `${endHours}:${endMinutes}`;
    }

    setFormData({
      ...formData,
      startTime: newStart,
      endTime: newEnd
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate API call
    setTimeout(() => {
      const newRecord: AmbuliftRecord = {
        id: Math.random().toString(36).substr(2, 9),
        ...formData,
        status: 'Agendado'
      };

      setRecords([newRecord, ...records]);
      setIsSubmitting(false);
      setActiveTab('history');
      
      // Reset form
      setFormData({
        airline: '',
        customAirline: '',
        flightNumber: '',
        date: new Date().toISOString().split('T')[0],
        startTime: '',
        endTime: ''
      });
    }, 1500);
  };

  const getAirlineColor = (airline: string) => {
    switch (airline) {
      case 'Gol Linhas Aéreas':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'Azul Linhas Aéreas':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'LATAM Linhas Aéreas':
        return 'bg-indigo-100 text-indigo-900 border-indigo-200';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  const filteredRecords = records.filter(r => 
    filterAirline === '' || r.airline === filterAirline
  );

  return (
    <div className="flex flex-col gap-[26px] relative h-full w-full">
      {/* Header */}
      <h2 className="text-[26px] font-bold text-slate-900 tracking-tight leading-tight uppercase shrink-0 flex items-center gap-3">
        <Accessibility className="w-8 h-8 text-[#0891b2]" strokeWidth={1.5} />
        Ambulift
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
          <RotateCcw className="w-4 h-4" />
          Registros
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
                <h3 className="text-2xl font-bold text-slate-900 mb-2">Registrando Serviço...</h3>
                <p className="text-slate-500">O acionamento do Ambulift está sendo salvo no sistema.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-[26px]">
                <div className="bg-[#F0FDFF] border border-[#C2F6FF] p-6 mb-[26px]">
                  <p className="text-[13px] text-[#0E7490] font-medium leading-relaxed">
                    <strong>Procedimento Padrão:</strong> O tempo padrão de serviço considerado para faturamento é de 20 minutos. Ajuste o horário de término apenas se houver intercorrências operacionais.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  {/* Airline */}
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Companhia Aérea Solicitante *
                    </label>
                    <div className="relative">
                      <select
                        required
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all appearance-none cursor-pointer font-medium"
                        value={formData.airline}
                        onChange={(e) => setFormData({...formData, airline: e.target.value as Airline})}
                      >
                        <option value="">Selecione a companhia</option>
                        <option value="Gol Linhas Aéreas">Gol Linhas Aéreas</option>
                        <option value="Azul Linhas Aéreas">Azul Linhas Aéreas</option>
                        <option value="LATAM Linhas Aéreas">LATAM Linhas Aéreas</option>
                        <option value="Outras">Outras</option>
                      </select>
                      <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>

                  {/* Flight Number */}
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Número do Voo *
                    </label>
                    <div className="relative">
                      <input
                        required
                        type="text"
                        placeholder="Ex: AD 4055"
                        className="w-full px-5 py-4 pl-12 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all font-medium uppercase"
                        value={formData.flightNumber}
                        onChange={(e) => setFormData({...formData, flightNumber: e.target.value})}
                      />
                      <Plane className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>
                </div>

                {/* Custom Airline (Conditional) */}
                {formData.airline === 'Outras' && (
                  <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                    <label className="text-[13px] font-bold text-slate-900 block mb-2">
                      Nome da Companhia Aérea *
                    </label>
                    <input
                      required
                      type="text"
                      placeholder="Digite o nome da companhia"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all font-medium"
                      value={formData.customAirline}
                      onChange={(e) => setFormData({...formData, customAirline: e.target.value})}
                    />
                  </div>
                )}

                {/* Date & Time */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Data do Acionamento *
                    </label>
                    <input
                      required
                      type="date"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all"
                      value={formData.date}
                      onChange={(e) => setFormData({...formData, date: e.target.value})}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Hora Início *
                    </label>
                    <input
                      required
                      type="time"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all"
                      value={formData.startTime}
                      onChange={handleStartTimeChange}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Hora Término (Previsto) *
                    </label>
                    <input
                      required
                      type="time"
                      className="w-full px-5 py-4 bg-slate-50 border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all"
                      value={formData.endTime}
                      onChange={(e) => setFormData({...formData, endTime: e.target.value})}
                    />
                  </div>
                </div>

                <div className="flex justify-end pt-4">
                  <button
                    type="submit"
                    className="flex items-center gap-3 bg-black text-white px-10 py-4 rounded-none font-bold shadow-lg hover:scale-105 transition-all group"
                  >
                    <span>Registrar Atendimento</span>
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              </form>
            )}
          </div>
        ) : (
          <div className="flex flex-col min-h-0 animate-in fade-in duration-500 w-full space-y-6">
            {/* Filters */}
            <div className="flex flex-col md:flex-row gap-4 bg-white p-4 border border-slate-200 rounded-none">
              <div className="flex-1 relative">
                <select 
                  className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all appearance-none cursor-pointer font-medium pl-10"
                  value={filterAirline}
                  onChange={(e) => setFilterAirline(e.target.value)}
                >
                  <option value="">Todas as Companhias</option>
                  <option value="Gol Linhas Aéreas">Gol Linhas Aéreas</option>
                  <option value="Azul Linhas Aéreas">Azul Linhas Aéreas</option>
                  <option value="LATAM Linhas Aéreas">LATAM Linhas Aéreas</option>
                  <option value="Outras">Outras</option>
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

            <div className="bg-white border border-slate-200 rounded-none shadow-sm relative w-full">
              <table className="w-full text-center border-separate border-spacing-0 table-fixed">
                <thead>
                  <tr className="bg-slate-50">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 w-1/5 text-center">Data/Hora</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 w-1/5 text-center">Companhia Aérea</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 w-1/5 text-center">Voo</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 w-1/5 text-center">Status</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 w-1/5 text-center">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredRecords.map((record, index) => (
                    <tr key={record.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 text-center">
 <div className="flex flex-col items-center">
 <div className="text-xs font-semibold text-slate-900 leading-tight">{record.date.split('-').reverse().join('/')}</div>
 <div className="text-[10px] text-slate-500 font-medium">{record.startTime} - {record.endTime}</div>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="text-xs text-slate-700 font-medium whitespace-normal leading-tight max-w-[200px] mx-auto">
 {record.airline === 'Outras' ? record.customAirline : record.airline.replace(' Linhas Aéreas', '')}
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="text-xs font-bold text-slate-700">{record.flightNumber}</div>
 </td>
                      <td className="px-6 py-4 text-center">
 {record.status === 'Concluído' ? (
 <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-sm inline-flex items-center gap-1 justify-center">
 <CheckCircle2 className="w-3 h-3" />
 CONCLUÍDO
 </span>
 ) : (
 <span className="bg-blue-100 text-blue-800 text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-sm inline-flex items-center gap-1 justify-center">
 <Clock className="w-3 h-3" />
 AGENDADO
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
 <div 
 className={`absolute z-50 right-1/2 translate-x-1/2 w-44 bg-white border border-slate-200 rounded-none shadow-2xl overflow-hidden animate-in fade-in duration-200 ${
 index >= filteredRecords.length - 2 && filteredRecords.length > 2 ? 'bottom-full mb-1 slide-in-from-bottom-2' : 'top-full mt-1 slide-in-from-top-2'
 }`}
 >
 {record.status === 'Agendado' && (
 <button 
 onClick={() => {
 setConcluirId(record.id);
 setConcluirData({ startTime: record.startTime, endTime: record.endTime });
 setOpenMenuId(null);
 }}
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-emerald-600 hover:bg-emerald-50 flex items-center gap-3 border-b border-slate-50"
 >
 <CheckCircle2 className="w-3.5 h-3.5" /> Concluir
 </button>
 )}
 <button 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"
 >
 <Eye className="w-3.5 h-3.5" /> Ver Registro
 </button>
 <button 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"
 >
 <Pencil className="w-3.5 h-3.5" /> Editar
 </button>
 <button 
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
                  {filteredRecords.length === 0 && (
                     <tr>
                        <td colSpan={5} className="py-12 text-center text-slate-400">
 Nenhum registro encontrado.
 </td>
                     </tr>
                  )}
                </tbody>
              </table>
              <div className="bg-slate-50 px-6 py-3 border-t border-slate-200">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{filteredRecords.length} REGISTROS ENCONTRADOS</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Concluir Modal */}
      {concluirId && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-none shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-200">
            <div className="p-6 border-b border-slate-100">
              <h3 className="text-lg font-bold text-slate-900 tracking-tight">Confirmar Horário de Uso</h3>
              <p className="text-slate-500 text-xs mt-1">Confirme os horários reais de início e término do atendimento.</p>
            </div>
            <div className="p-6 space-y-4">
              <div className="space-y-2">
                <label className="text-[13px] font-bold text-slate-900 block">Hora Início Real</label>
                <input
                  type="time"
                  className="w-full px-4 py-3 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all"
                  value={concluirData.startTime}
                  onChange={(e) => setConcluirData({...concluirData, startTime: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <label className="text-[13px] font-bold text-slate-900 block">Hora Término Real</label>
                <input
                  type="time"
                  className="w-full px-4 py-3 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all"
                  value={concluirData.endTime}
                  onChange={(e) => setConcluirData({...concluirData, endTime: e.target.value})}
                />
              </div>
            </div>
            <div className="p-4 bg-slate-50/50 border-t border-slate-100 flex gap-3">
              <button
                onClick={() => setConcluirId(null)}
                className="flex-1 px-4 py-3 text-[13px] font-bold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 hover:text-slate-900 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  setRecords(records.map(r => r.id === concluirId ? { ...r, status: 'Concluído', startTime: concluirData.startTime, endTime: concluirData.endTime } : r));
                  setConcluirId(null);
                }}
                className="flex-1 px-4 py-3 text-[13px] font-bold text-white bg-emerald-600 hover:bg-emerald-700 transition-colors shadow-sm"
              >
                Confirmar e Concluir
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};