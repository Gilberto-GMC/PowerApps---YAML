import React, { useState } from 'react';
import { 
  PlusCircle, 
  RotateCcw, 
  History,
  ChevronDown, 
  CheckCircle2, 
  ArrowRight,
  Calendar,
  Clock,
  Search,
  Filter,
  MoreHorizontal,
  Eye,
  Pencil,
  Trash2,
  XCircle,
  UserX,
  MapPin,
  Building2,
  FileSpreadsheet,
  AlertTriangle,
  UploadCloud,
  FileText,
  Paperclip
} from 'lucide-react';
import { AIRPORTS } from './AISComplianceForm';

type InterferenceType = 'Avistamentos ou detecção de drones' | 'Balões' | 'Pipas em voo' | 'Laser' | '';

interface InterferenceRecord {
  id: string;
  aeroporto: string;
  data: string;
  hora: string;
  tipo: InterferenceType;
  quadrante: string;
  quantidade: number;
  descricao?: string;
  attachmentName?: string;
  status: 'Registrado' | 'Em Análise';
}

const MOCK_RECORDS: InterferenceRecord[] = [
  {
    id: '1',
    aeroporto: 'Aeroporto da Pampulha',
    data: '2026-04-01',
    hora: '14:30',
    tipo: 'Avistamentos ou detecção de drones',
    quadrante: 'A4',
    quantidade: 1,
    descricao: 'Drone de pequeno porte avistado sobrevoando a cabeceira 13.',
    status: 'Registrado'
  }
];

export const ExternalInterferenceModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [records, setRecords] = useState<InterferenceRecord[]>(MOCK_RECORDS);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);

  const [filterAirport, setFilterAirport] = useState('');
  const [filterType, setFilterType] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const [formData, setFormData] = useState({
    aeroporto: '',
    data: new Date().toISOString().split('T')[0],
    hora: '00:00',
    tipo: '' as InterferenceType,
    quadrante: '',
    quantidade: 1,
    descricao: ''
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    setTimeout(() => {
      const newRecord: InterferenceRecord = {
        id: Math.random().toString(36).substr(2, 9),
        ...formData,
        attachmentName: selectedFile?.name,
        status: 'Registrado'
      };

      setRecords([newRecord, ...records]);
      setIsSubmitting(false);
      setActiveTab('history');
      
      // Reset form
      setFormData({
        aeroporto: '',
        data: new Date().toISOString().split('T')[0],
        hora: '00:00',
        tipo: '',
        quadrante: '',
        quantidade: 1,
        descricao: ''
      });
      setSelectedFile(null);
    }, 1500);
  };

  const filteredRecords = records.filter(r => {
    const matchAirport = filterAirport ? r.aeroporto === filterAirport : true;
    const matchType = filterType ? r.tipo === filterType : true;
    const matchStartDate = startDate ? r.data >= startDate : true;
    const matchEndDate = endDate ? r.data <= endDate : true;
    return matchAirport && matchType && matchStartDate && matchEndDate;
  });

  return (
    <div className="flex flex-col gap-[26px] relative h-full w-full">
      {/* Header */}
      <h2 className="text-[26px] font-bold text-slate-900 tracking-tight leading-tight uppercase shrink-0">
        Interferência Externa
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

      {/* Content Area */}
      <div className="flex-1 overflow-visible">
        {activeTab === 'form' ? (
          <div className="max-w-5xl animate-in fade-in duration-500 pb-10">
            {isSubmitting ? (
              <div className="flex flex-col items-center justify-center py-24 text-center animate-in zoom-in duration-300">
                <div className="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mb-6">
                  <CheckCircle2 className="w-10 h-10 text-emerald-600 animate-pulse" />
                </div>
                <h3 className="text-2xl font-bold text-slate-900 mb-2">Salvando Registro...</h3>
                <p className="text-slate-500">O registro está sendo sincronizado com a base de dados.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-[26px]">
                {/* Local e Data */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Aeroporto *</label>
                  <div className="relative">
                    <select 
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 appearance-none outline-none focus:border-[#391694] transition-all font-medium"
                      value={formData.aeroporto}
                      onChange={(e) => setFormData({...formData, aeroporto: e.target.value})}
                      required
                    >
                      <option value="">Selecione o aeroporto</option>
                      {AIRPORTS.map(apt => (
                        <option key={apt} value={apt}>{apt}</option>
                      ))}
                    </select>
                    <Building2 className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Data *</label>
                    <div className="relative">
                      <input 
                        type="date"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                        value={formData.data}
                        onChange={(e) => setFormData({...formData, data: e.target.value})}
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Hora (UTC) *</label>
                    <div className="relative">
                      <input 
                        type="time"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                        value={formData.hora}
                        onChange={(e) => setFormData({...formData, hora: e.target.value})}
                        required
                      />
                    </div>
                  </div>
                </div>

                {/* Detalhes da Interferência */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Tipo de Interferência *</label>
                    <div className="relative">
                      <select 
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 appearance-none outline-none focus:border-[#391694] transition-all font-medium"
                        value={formData.tipo}
                        onChange={(e) => setFormData({...formData, tipo: e.target.value as InterferenceType})}
                        required
                      >
                        <option value="">Selecione o tipo</option>
                        <option value="Avistamentos ou detecção de drones">Avistamentos ou detecção de drones</option>
                        <option value="Balões">Balões</option>
                        <option value="Pipas em voo">Pipas em voo</option>
                        <option value="Laser">Laser</option>
                      </select>
                      <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Quadrante do mapa de grade *</label>
                    <div className="relative">
                      <input 
                        type="text"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-400 placeholder:normal-case outline-none focus:border-[#391694] transition-all font-medium uppercase"
                        placeholder="Ex: A4, B2"
                        value={formData.quadrante}
                        onChange={(e) => setFormData({...formData, quadrante: e.target.value})}
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Quantidade de Objetos *</label>
                    <div className="relative">
                      <input 
                        type="number"
                        min="1"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                        value={formData.quantidade}
                        onChange={(e) => setFormData({...formData, quantidade: parseInt(e.target.value) || 1})}
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Descrição do Evento <span className="text-slate-400 font-normal">(Opcional)</span></label>
                  <textarea 
                    className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-400 placeholder:normal-case outline-none focus:border-[#391694] transition-all font-medium resize-none h-24 uppercase"
                    placeholder="Descreva detalhes adicionais sobre a interferência..."
                    value={formData.descricao}
                    onChange={(e) => setFormData({...formData, descricao: e.target.value})}
                  />
                </div>

                {/* Anexo de Documentos */}
                <div className="border-t border-slate-100 pt-6">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Anexar Documentação (Fotos, Relatórios, etc.)
                    </label>
                    <div className="relative group">
                      <input
                        type="file"
                        id="file-upload"
                        className="hidden"
                        onChange={handleFileChange}
                        accept=".pdf,.jpg,.jpeg,.png"
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
                            <button 
                              type="button"
                              onClick={(e) => { e.preventDefault(); setSelectedFile(null); }}
                              className="ml-4 p-2 hover:bg-red-50 text-red-500 rounded-full transition-colors"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
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
                </div>

                <div className="flex justify-end pt-4">
                  <button
                    type="submit"
                    className="flex items-center gap-3 bg-black text-white px-10 py-4 rounded-none font-bold shadow-lg hover:scale-105 transition-all group"
                    disabled={isSubmitting}
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
                  <AlertTriangle className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <select 
                    value={filterType}
                    onChange={(e) => setFilterType(e.target.value)}
                    className="w-full pl-10 pr-8 h-10 bg-white border border-slate-200 rounded-none text-sm outline-none focus:ring-2 focus:ring-[#391694]/10 focus:border-[#391694] transition-all appearance-none cursor-pointer"
                  >
                    <option value="">Todos os Tipos</option>
                    <option value="Avistamentos ou detecção de drones">Avistamentos ou detecção de drones</option>
                    <option value="Balões">Balões</option>
                    <option value="Pipas em voo">Pipas em voo</option>
                    <option value="Laser">Laser</option>
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

            {/* Table */}
            <div className="bg-white border border-slate-200 rounded-none shadow-sm relative overflow-x-auto w-full">
              <table className="w-full text-center border-separate border-spacing-0">
                <thead>
                  <tr className="bg-slate-50">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Data/Hora</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Aeroporto</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Tipo/Qtd</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Quadrante</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Status</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-center border-b border-slate-200">Anexo</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredRecords.map((record) => (
                    <tr key={record.id} className="hover:bg-slate-50/50 transition-colors group">
                      <td className="px-6 py-4 text-center">
 <div className="text-xs font-semibold text-slate-900 leading-tight">
 {record.data.split('-').reverse().join('/')}
 </div>
 <div className="text-[10px] text-slate-500 font-medium">{record.hora} UTC</div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="text-xs text-slate-700 font-medium whitespace-normal leading-tight max-w-[200px]">
 {record.aeroporto}
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex flex-col items-center">
 <span className="text-xs font-bold text-[#c026d3]">{record.tipo}</span>
 <span className="text-[10px] text-slate-500">{record.quantidade} {record.quantidade === 1 ? 'objeto' : 'objetos'}</span>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <span className="text-[10px] font-mono text-slate-700 bg-slate-100 px-2 py-1 rounded-none">{record.quadrante}</span>
 </td>
                      <td className="px-6 py-4 text-center">
 <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-none text-[10px] font-bold tracking-wide uppercase ${
 record.status === 'Registrado' 
 ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
 : 'bg-amber-100 text-amber-800 border border-amber-200'
 }`}>
 {record.status === 'Registrado' ? <CheckCircle2 className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
 {record.status}
 </span>
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
 <button 
 onClick={() => setOpenMenuId(openMenuId === record.id ? null : record.id)}
 className="p-2 hover:bg-slate-200 rounded-none transition-colors text-slate-400 hover:text-slate-700"
 >
 <MoreHorizontal className="w-5 h-5" />
 </button>

 {openMenuId === record.id && (
 <>
 <div 
 className="fixed inset-0 z-10"
 onClick={() => setOpenMenuId(null)}
 />
 <div className="absolute right-6 top-12 w-48 bg-white border border-slate-200 shadow-xl z-20 py-1 animate-in fade-in slide-in-from-top-2">
 <button className="w-full px-4 py-2 text-left text-[11px] font-medium text-slate-700 hover:bg-slate-50 hover:text-[#391694] flex items-center gap-2 justify-center">
 <Eye className="w-4 h-4" />
 Ver Detalhes
 </button>
 <button className="w-full px-4 py-2 text-left text-[11px] font-medium text-slate-700 hover:bg-slate-50 hover:text-[#391694] flex items-center gap-2 justify-center">
 <Pencil className="w-4 h-4" />
 Editar Registro
 </button>
 <div className="h-px bg-slate-100 my-1"></div>
 <button className="w-full px-4 py-2 text-left text-[11px] font-medium text-red-600 hover:bg-red-50 flex items-center gap-2 justify-center">
 <Trash2 className="w-4 h-4" />
 Excluir
 </button>
 </div>
 </>
 )}
 </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
