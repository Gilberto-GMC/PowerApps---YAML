import React, { useState, useMemo, useEffect } from 'react';
import { 
  PlusCircle, 
  History, 
  CheckCircle2, 
  ArrowRight,
  Fan,
  Calendar,
  Clock,
  Plane,
  MapPin,
  Filter,
  ChevronDown,
  MoreHorizontal,
  Eye,
  Pencil,
  Trash2,
  AlertTriangle
} from 'lucide-react';
import { AIRPORTS } from './AISComplianceForm';

type TestLocation = 'Pátio de Estacionamento' | 'Pista de Táxi' | 'Pista de Pouso e Decolagem' | '';
type TestType = 'Marcha Lenta' | 'Potência Máxima' | 'Outro' | '';

interface EngineTestRecord {
  id: string;
  airport: string;
  startDate: string;
  endDate: string;
  startTime: string;
  endTime: string;
  registration: string;
  aircraftModel: string;
  operator: string;
  location: TestLocation;
  position: string;
  testType: TestType;
  observations: string;
  status: 'Agendado' | 'Concluído';
}

const LOCATIONS = [
  'Pátio de Estacionamento',
  'Pista de Táxi',
  'Pista de Pouso e Decolagem'
];

const MOCK_RECORDS: EngineTestRecord[] = [
  {
    id: '1',
    airport: 'Aeroporto de Curitiba',
    startDate: '2024-05-20',
    endDate: '2024-05-20',
    startTime: '10:00',
    endTime: '10:30',
    registration: 'PR-YRX',
    aircraftModel: 'A320',
    operator: 'Azul',
    location: 'Pista de Táxi',
    position: 'Ponto de Espera A',
    testType: 'Potência Máxima',
    observations: 'Teste realizado sem anormalidades.',
    status: 'Agendado'
  },
  {
    id: '2',
    airport: 'Aeroporto de Navegantes',
    startDate: '2024-05-19',
    endDate: '2024-05-20',
    startTime: '23:15',
    endTime: '00:45',
    registration: 'PR-GUK',
    aircraftModel: 'B738',
    operator: 'Gol',
    location: 'Pátio de Estacionamento',
    position: 'Posição 01',
    testType: 'Marcha Lenta',
    observations: '',
    status: 'Concluído'
  }
];

export const EngineTestModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [records, setRecords] = useState<EngineTestRecord[]>(MOCK_RECORDS);
  const [filterAirport, setFilterAirport] = useState<string>('');
  
  const [actionMenuId, setActionMenuId] = useState<string | null>(null);
  const [actionMenuPosition, setActionMenuPosition] = useState<{ top?: number, bottom?: number, right?: number } | null>(null);

  useEffect(() => {
    const handleScroll = () => {
      if (actionMenuId) setActionMenuId(null);
    };
    window.addEventListener('scroll', handleScroll, true);
    window.addEventListener('resize', handleScroll);
    return () => {
      window.removeEventListener('scroll', handleScroll, true);
      window.removeEventListener('resize', handleScroll);
    };
  }, [actionMenuId]);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [isReadOnly, setIsReadOnly] = useState(false);
  const [completingRecord, setCompletingRecord] = useState<EngineTestRecord | null>(null);
  const [completeStartTime, setCompleteStartTime] = useState('');
  const [completeEndTime, setCompleteEndTime] = useState('');

  const INITIAL_FORM_DATA = {
    airport: '',
    startDate: new Date().toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
    startTime: '',
    endTime: '',
    registration: '',
    aircraftModel: '',
    operator: '',
    location: '' as TestLocation,
    position: '',
    testType: '' as TestType,
    observations: '',
    status: 'Agendado' as 'Agendado' | 'Concluído'
  };

  const [formData, setFormData] = useState(INITIAL_FORM_DATA);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    setTimeout(() => {
      const newRecord: EngineTestRecord = {
        id: editingId || Math.random().toString(36).substr(2, 9),
        ...formData
      };

      if (editingId) {
        setRecords(records.map(r => r.id === editingId ? newRecord : r));
      } else {
        setRecords([newRecord, ...records]);
      }
      
      setIsSubmitting(false);
      setActiveTab('history');
      
      setFormData(INITIAL_FORM_DATA);
      setEditingId(null);
      setIsReadOnly(false);
    }, 1500);
  };

  const handleDelete = () => {
    if (deleteId) {
      setRecords(records.filter(r => r.id !== deleteId));
      setDeleteId(null);
    }
  };

  const handleCompleteClick = (record: EngineTestRecord) => {
    setCompletingRecord(record);
    setCompleteStartTime(record.startTime);
    setCompleteEndTime(record.endTime);
    setActionMenuId(null);
  };

  const handleConfirmComplete = () => {
    if (completingRecord) {
      setRecords(records.map(r => 
        r.id === completingRecord.id 
          ? { ...r, status: 'Concluído', startTime: completeStartTime, endTime: completeEndTime } 
          : r
      ));
      setCompletingRecord(null);
    }
  };

  const handleEdit = (record: EngineTestRecord) => {
    setFormData({
      airport: record.airport,
      startDate: record.startDate,
      endDate: record.endDate,
      startTime: record.startTime,
      endTime: record.endTime,
      registration: record.registration,
      aircraftModel: record.aircraftModel,
      operator: record.operator,
      location: record.location,
      position: record.position,
      testType: record.testType,
      observations: record.observations,
      status: record.status
    });
    setEditingId(record.id);
    setIsReadOnly(false);
    setActiveTab('form');
    setActionMenuId(null);
  };

  const handleView = (record: EngineTestRecord) => {
    setFormData({
      airport: record.airport,
      startDate: record.startDate,
      endDate: record.endDate,
      startTime: record.startTime,
      endTime: record.endTime,
      registration: record.registration,
      aircraftModel: record.aircraftModel,
      operator: record.operator,
      location: record.location,
      position: record.position,
      testType: record.testType,
      observations: record.observations,
      status: record.status
    });
    setEditingId(record.id);
    setIsReadOnly(true);
    setActiveTab('form');
    setActionMenuId(null);
  };

  const filteredRecords = useMemo(() => {
    return records.filter(record => 
      filterAirport === '' || record.airport === filterAirport
    );
  }, [records, filterAirport]);

  return (
    <div className="flex flex-col gap-[26px] relative h-full w-full">
      {/* Header */}
      <h2 className="text-[26px] font-bold text-slate-900 tracking-tight leading-tight uppercase shrink-0">
        Teste de Motores
      </h2>

      {/* Tabs */}
      <div className="flex p-1 bg-slate-50 rounded-none w-fit border border-slate-200 shrink-0">
        <button
          onClick={() => { setActiveTab('form'); setEditingId(null); setIsReadOnly(false); setFormData(INITIAL_FORM_DATA); }}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-none text-[13px] font-bold transition-all ${
            activeTab === 'form' 
              ? 'bg-white text-[#391694] shadow-sm' 
              : 'text-slate-400 hover:text-slate-600'
          }`}
        >
          <PlusCircle className="w-4 h-4" />
          {editingId && !isReadOnly ? 'Editar Registro' : isReadOnly ? 'Ver Registro' : 'Novo Registro'}
        </button>
        <button
          onClick={() => { setActiveTab('history'); setEditingId(null); setIsReadOnly(false); setFormData(INITIAL_FORM_DATA); }}
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
          <div className="max-w-4xl animate-in fade-in duration-500 pb-10">
            {isSubmitting ? (
              <div className="flex flex-col items-center justify-center py-24 text-center animate-in zoom-in duration-300">
                <div className="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mb-6">
                  <CheckCircle2 className="w-10 h-10 text-emerald-600 animate-pulse" />
                </div>
                <h3 className="text-2xl font-bold text-slate-900 mb-2">
                  {editingId ? 'Atualizando Registro...' : 'Registrando Teste...'}
                </h3>
                <p className="text-slate-500">O registro de teste de motores está sendo salvo no sistema.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-[26px]">
                {/* Aeroporto */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">
                    Aeroporto *
                  </label>
                  <div className="relative">
                    <select
                      required
                      disabled={isReadOnly}
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all appearance-none cursor-pointer disabled:bg-slate-50 disabled:text-slate-500"
                      value={formData.airport}
                      onChange={(e) => setFormData({...formData, airport: e.target.value})}
                    >
                      <option value="">Selecione o aeroporto</option>
                      {AIRPORTS.map(ap => <option key={ap} value={ap}>{ap}</option>)}
                    </select>
                    <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                  </div>
                </div>

                {/* Data e Hora */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Data de Início *
                    </label>
                    <input
                      required
                      type="date"
                      disabled={isReadOnly}
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all disabled:bg-slate-50 disabled:text-slate-500"
                      value={formData.startDate}
                      onChange={(e) => setFormData({...formData, startDate: e.target.value})}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Hora Início *
                    </label>
                    <input
                      required
                      type="time"
                      disabled={isReadOnly}
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all disabled:bg-slate-50 disabled:text-slate-500"
                      value={formData.startTime}
                      onChange={(e) => setFormData({...formData, startTime: e.target.value})}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Data de Término *
                    </label>
                    <input
                      required
                      type="date"
                      disabled={isReadOnly}
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all disabled:bg-slate-50 disabled:text-slate-500"
                      value={formData.endDate}
                      onChange={(e) => setFormData({...formData, endDate: e.target.value})}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Hora Término *
                    </label>
                    <input
                      required
                      type="time"
                      disabled={isReadOnly}
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all disabled:bg-slate-50 disabled:text-slate-500"
                      value={formData.endTime}
                      onChange={(e) => setFormData({...formData, endTime: e.target.value})}
                    />
                  </div>
                </div>

                {/* Dados da Aeronave */}
                <div className="border border-slate-100 p-6 bg-slate-50/30">
                  <h3 className="text-[13px] font-bold text-slate-800 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <Plane className="w-4 h-4" /> Dados da Aeronave
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-[26px]">
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">
                        Matrícula
                      </label>
                      <input
                        type="text"
                        placeholder="EX: PR-ABC"
                        disabled={isReadOnly}
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all font-medium uppercase disabled:bg-slate-50 disabled:text-slate-500"
                        value={formData.registration}
                        onChange={(e) => setFormData({...formData, registration: e.target.value})}
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">
                        Modelo
                      </label>
                      <input
                        type="text"
                        placeholder="EX: B738"
                        disabled={isReadOnly}
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all font-medium uppercase disabled:bg-slate-50 disabled:text-slate-500"
                        value={formData.aircraftModel}
                        onChange={(e) => setFormData({...formData, aircraftModel: e.target.value})}
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">
                        Operador Aéreo
                      </label>
                      <input
                        type="text"
                        placeholder="Gol Linhas Aéreas"
                        disabled={isReadOnly}
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all font-medium disabled:bg-slate-50 disabled:text-slate-500"
                        value={formData.operator}
                        onChange={(e) => setFormData({...formData, operator: e.target.value})}
                      />
                    </div>
                  </div>
                </div>

                {/* Detalhes do Teste */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Local Geral *
                    </label>
                    <div className="relative">
                      <select
                        required
                        disabled={isReadOnly}
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all appearance-none cursor-pointer disabled:bg-slate-50 disabled:text-slate-500"
                        value={formData.location}
                        onChange={(e) => setFormData({...formData, location: e.target.value as TestLocation})}
                      >
                        <option value="">Selecione o local...</option>
                        {LOCATIONS.map(loc => <option key={loc} value={loc}>{loc}</option>)}
                      </select>
                      <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Posição / Box / Referência
                    </label>
                    <input
                      type="text"
                      placeholder="Ex: Box 05 ou Próximo ao TECA"
                      disabled={isReadOnly}
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all font-medium disabled:bg-slate-50 disabled:text-slate-500"
                      value={formData.position}
                      onChange={(e) => setFormData({...formData, position: e.target.value})}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">
                      Tipo de Teste *
                    </label>
                    <div className="relative">
                      <select
                        required
                        disabled={isReadOnly}
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all appearance-none cursor-pointer disabled:bg-slate-50 disabled:text-slate-500"
                        value={formData.testType}
                        onChange={(e) => setFormData({...formData, testType: e.target.value as TestType})}
                      >
                        <option value="">Selecione o tipo</option>
                        <option value="Marcha Lenta">Marcha Lenta</option>
                        <option value="Potência Máxima">Potência Máxima</option>
                        <option value="Outro">Outro</option>
                      </select>
                      <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>
                </div>
                
                {/* Status */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">
                    Status *
                  </label>
                  <div className="relative">
                    <select
                      required
                      disabled={isReadOnly}
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all appearance-none cursor-pointer disabled:bg-slate-50 disabled:text-slate-500"
                      value={formData.status}
                      onChange={(e) => setFormData({...formData, status: e.target.value as 'Agendado' | 'Concluído'})}
                    >
                      <option value="Agendado">Agendado</option>
                      <option value="Concluído">Concluído</option>
                    </select>
                    <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                  </div>
                </div>

                {/* Observações */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">
                    Observações Adicionais
                  </label>
                  <textarea
                    rows={4}
                    placeholder="Informações complementares sobre o teste..."
                    disabled={isReadOnly}
                    className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all resize-none font-medium disabled:bg-slate-50 disabled:text-slate-500"
                    value={formData.observations}
                    onChange={(e) => setFormData({...formData, observations: e.target.value})}
                  />
                </div>

                <div className="flex justify-end pt-4 gap-4">
                  {isReadOnly ? (
                    <button
                      type="button"
                      onClick={() => { setActiveTab('history'); setEditingId(null); setIsReadOnly(false); setFormData(INITIAL_FORM_DATA); }}
                      className="flex items-center gap-3 bg-white border border-slate-200 text-slate-700 px-10 py-4 rounded-none font-bold hover:bg-slate-50 transition-all"
                    >
                      Voltar para Registros
                    </button>
                  ) : (
                    <>
                      {editingId && (
                        <button
                          type="button"
                          onClick={() => { setActiveTab('history'); setEditingId(null); setFormData(INITIAL_FORM_DATA); }}
                          className="flex items-center gap-3 bg-white border border-slate-200 text-slate-700 px-10 py-4 rounded-none font-bold hover:bg-slate-50 transition-all"
                        >
                          Cancelar
                        </button>
                      )}
                      <button
                        type="submit"
                        className="flex items-center gap-3 bg-black text-white px-10 py-4 rounded-none font-bold shadow-lg hover:scale-105 transition-all group"
                      >
                        <span>{editingId ? 'Salvar Alterações' : 'Finalizar Registro'}</span>
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                      </button>
                    </>
                  )}
                </div>
              </form>
            )}
          </div>
        ) : (
          <div className="flex flex-col min-h-0 animate-in fade-in duration-500 w-full">
            {/* Filter Bar */}
            <div className="flex items-center gap-4 bg-slate-50 p-4 rounded-none border border-slate-200 mb-[26px] shrink-0 w-full">
               <div className="flex items-center gap-2 text-slate-500">
                  <Filter className="w-4 h-4" />
                  <span className="text-xs font-bold uppercase tracking-widest">Filtrar:</span>
               </div>
               <select 
                  className="bg-white border border-slate-200 text-xs font-bold text-slate-700 py-2 px-4 rounded-none outline-none focus:border-[#391694]"
                  value={filterAirport}
                  onChange={(e) => setFilterAirport(e.target.value)}
               >
                  <option value="">Todos os Aeroportos</option>
                  {AIRPORTS.map(ap => <option key={ap} value={ap}>{ap}</option>)}
               </select>
            </div>

            <div className="bg-white border border-slate-200 rounded-none shadow-sm relative overflow-x-auto w-full min-h-[320px]">
              <table className="w-full text-center border-separate border-spacing-0">
                <thead>
                  <tr className="bg-slate-50">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Status</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Data</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Aeronave</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Local / Aeroporto</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Horário</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-center border-b border-slate-200">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredRecords.map((record, index) => {
                    const isLastRows = index >= filteredRecords.length - 2 && filteredRecords.length > 2;
                    return (
                    <tr key={record.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 text-center">
 <span className={`px-2 py-1 text-[10px] font-black uppercase tracking-wider rounded-sm ${
 record.status === 'Concluído' 
 ? 'bg-emerald-100 text-emerald-700' 
 : 'bg-amber-100 text-amber-700'
 }`}>
 {record.status}
 </span>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex items-center gap-2 justify-center">
 <Calendar className="w-3 h-3 text-slate-400" />
 <span className="text-xs font-semibold text-slate-900">{record.startDate.split('-').reverse().join('/')}</span>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex flex-col items-center">
 <div className="flex items-center gap-2 justify-center">
 <Plane className="w-3 h-3 text-slate-400" />
 <span className="text-xs font-bold text-slate-700">{record.registration}</span>
 </div>
 <span className="text-[10px] text-slate-500 mt-1">{record.operator} - {record.aircraftModel}</span>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex flex-col items-center">
 <div className="flex items-center gap-2 justify-center">
 <MapPin className="w-3 h-3 text-slate-400" />
 <span className="text-xs font-medium text-slate-700">{record.location}</span>
 </div>
 {record.position && <span className="text-[11px] text-slate-400 block">{record.position}</span>}
 <span className="text-[10px] text-slate-500 mt-1">{record.airport}</span>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex items-center gap-2 text-xs font-mono text-slate-600 bg-slate-50 w-fit px-2 py-1 rounded border border-slate-100 justify-center mx-auto">
 <Clock className="w-3 h-3" />
 {record.startTime} - {record.endTime}
 </div>
 </td>
                      <td className="px-6 py-4 text-center relative">
 <button 
 onClick={(e) => {
 e.stopPropagation();
 const rect = e.currentTarget.getBoundingClientRect();
 const spaceBelow = window.innerHeight - rect.bottom;
 const showAbove = spaceBelow < 250;
 
 setActionMenuPosition({
 top: showAbove ? undefined : rect.bottom + 4,
 bottom: showAbove ? window.innerHeight - rect.top + 4 : undefined,
 right: window.innerWidth - rect.right,
 });
 setActionMenuId(actionMenuId === record.id ? null : record.id);
 }}
 className={`p-1.5 rounded-none transition-all ${actionMenuId === record.id ? 'bg-[#0891b2] text-white shadow-md' : 'text-slate-400 hover:text-[#0891b2] hover:bg-cyan-50 border border-slate-200'}`}
 aria-label="Ações"
 >
 <MoreHorizontal className="w-5 h-5" />
 </button>

 {actionMenuId === record.id && actionMenuPosition && (
 <div 
 className="fixed z-50 w-44 bg-white border border-slate-200 rounded-none shadow-2xl overflow-hidden animate-in fade-in duration-200"
 style={{
 top: actionMenuPosition.top,
 bottom: actionMenuPosition.bottom,
 right: actionMenuPosition.right,
 }}
 onClick={(e) => e.stopPropagation()}
 >
 <button 
 onClick={() => handleView(record)} 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"
 >
 <Eye className="w-3.5 h-3.5" /> Ver Registro
 </button>
 {record.status === 'Agendado' && (
 <button 
 onClick={() => handleCompleteClick(record)} 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-emerald-600 hover:bg-emerald-50 flex items-center gap-3 border-b border-slate-50"
 >
 <CheckCircle2 className="w-3.5 h-3.5" /> Concluir
 </button>
 )}
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
                  );
                  })}
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
                Esta ação não poderá ser desfeita. O registro será removido permanentemente do histórico.
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

      {/* Modal de Confirmação de Conclusão */}
      {completingRecord && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-white rounded-none w-full max-w-sm shadow-2xl overflow-hidden border border-slate-100">
            <div className="p-8">
              <div className="w-16 h-16 bg-emerald-50 rounded-full flex items-center justify-center mx-auto mb-6 border border-emerald-100">
                <CheckCircle2 className="w-8 h-8 text-emerald-500" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 tracking-tight mb-2 text-center">Confirmar Conclusão</h3>
              <p className="text-slate-500 text-sm leading-relaxed mb-6 text-center">
                Por favor, confirme os horários reais de início e término do teste.
              </p>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Horário de Início Real
                  </label>
                  <input
                    type="time"
                    value={completeStartTime}
                    onChange={(e) => setCompleteStartTime(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-none text-sm focus:outline-none focus:border-[#0891b2] focus:ring-1 focus:ring-[#0891b2] transition-all"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Horário de Término Real
                  </label>
                  <input
                    type="time"
                    value={completeEndTime}
                    onChange={(e) => setCompleteEndTime(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-none text-sm focus:outline-none focus:border-[#0891b2] focus:ring-1 focus:ring-[#0891b2] transition-all"
                    required
                  />
                </div>
              </div>
            </div>
            <div className="p-4 bg-slate-50/50 border-t border-slate-100 flex gap-3">
              <button 
                onClick={() => setCompletingRecord(null)} 
                className="flex-1 py-3 bg-white border border-slate-200 rounded-none text-xs font-bold text-slate-600 hover:bg-slate-100 transition-all"
              >
                Cancelar
              </button>
              <button 
                onClick={handleConfirmComplete} 
                className="flex-1 py-3 bg-emerald-600 rounded-none text-xs font-bold text-white hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-900/20"
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
