import React, { useState } from 'react';
import { 
  PlusCircle, 
  History, 
  CheckCircle2, 
  ArrowRight,
  User,
  Users,
  Building,
  Key,
  Shield,
  Clock,
  Calendar,
  Search,
  Filter,
  Trash2,
  ChevronDown,
  Car,
  FileText
} from 'lucide-react';
import { AIRPORTS } from './AISComplianceForm';

interface ThirdPartyAccessRecord {
  id: string;
  airport: string;
  visitorName: string;
  visitorDocument: string;
  company: string;
  reason: string;
  area: string;
  date: string;
  startTime: string;
  endTime: string;
  escortingStaff: string;
  escortingStaffId: string;
  vehiclePlate?: string;
  vehicleModel?: string;
  status: 'Ativo' | 'Concluído' | 'Agendado';
}

const MOCK_RECORDS: ThirdPartyAccessRecord[] = [
  {
    id: 'rec-1',
    airport: 'Aeroporto de Goiânia',
    visitorName: 'Marcos Souza',
    visitorDocument: 'MG-12.345.678',
    company: 'Claro Telecom',
    reason: 'Manutenção de Antena de Telecomunicações',
    area: 'Área de Hangares',
    date: '2024-06-11',
    startTime: '09:00',
    endTime: '11:30',
    escortingStaff: 'Ana Clara Silva',
    escortingStaffId: 'OPS-4421',
    vehiclePlate: 'ABC-1234',
    vehicleModel: 'Fiat Uno Branco',
    status: 'Concluído'
  },
  {
    id: 'rec-2',
    airport: 'Aeroporto de Curitiba',
    visitorName: 'Julia Mendes',
    visitorDocument: 'PR-98.765.432',
    company: 'Serralheria MetalForte',
    reason: 'Reparo na Cerca de Segurança Setor Sul',
    area: 'Pátio de Aeronaves / Cerca Perimetral',
    date: '2024-06-12',
    startTime: '08:15',
    endTime: '17:00',
    escortingStaff: 'Carlos Eduardo',
    escortingStaffId: 'OPS-2189',
    status: 'Ativo'
  },
  {
    id: 'rec-3',
    airport: 'Aeroporto de Navegantes',
    visitorName: 'Ricardo Torres',
    visitorDocument: 'SC-33.444.555',
    company: 'Elevadores Otis',
    reason: 'Inspeção Semestral Elevador de Carga',
    area: 'Terminal de Cargas / Leste',
    date: '2024-06-13',
    startTime: '14:00',
    endTime: '16:00',
    escortingStaff: 'Fernanda Costa',
    escortingStaffId: 'OPS-3921',
    status: 'Agendado'
  }
];

const INITIAL_FORM_DATA = {
  airport: '',
  visitorName: '',
  visitorDocument: '',
  company: '',
  reason: '',
  area: '',
  date: new Date().toISOString().split('T')[0],
  startTime: '',
  endTime: '',
  escortingStaff: '',
  escortingStaffId: '',
  vehiclePlate: '',
  vehicleModel: '',
  status: 'Ativo' as 'Ativo' | 'Concluído' | 'Agendado'
};

export const ThirdPartyAccessModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [records, setRecords] = useState<ThirdPartyAccessRecord[]>(MOCK_RECORDS);
  const [formData, setFormData] = useState(INITIAL_FORM_DATA);

  // Filters
  const [filterAirport, setFilterAirport] = useState('');
  const [filterSearch, setFilterSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate submission delay
    setTimeout(() => {
      const newRecord: ThirdPartyAccessRecord = {
        id: `rec-${Math.random().toString(36).substr(2, 9)}`,
        airport: formData.airport,
        visitorName: formData.visitorName,
        visitorDocument: formData.visitorDocument,
        company: formData.company,
        reason: formData.reason,
        area: formData.area,
        date: formData.date,
        startTime: formData.startTime,
        endTime: formData.endTime,
        escortingStaff: formData.escortingStaff,
        escortingStaffId: formData.escortingStaffId,
        vehiclePlate: formData.vehiclePlate || undefined,
        vehicleModel: formData.vehicleModel || undefined,
        status: formData.status
      };

      setRecords([newRecord, ...records]);
      setIsSubmitting(false);
      setFormData(INITIAL_FORM_DATA);
      setActiveTab('history');
    }, 1000);
  };

  const handleDelete = (id: string) => {
    if (confirm('Tem certeza de que deseja remover este registro de acesso?')) {
      setRecords(records.filter(rec => rec.id !== id));
    }
  };

  // Filter logic
  const filteredRecords = records.filter(rec => {
    const matchesAirport = filterAirport === '' || rec.airport === filterAirport;
    const matchesStatus = filterStatus === '' || rec.status === filterStatus;
    const matchesSearch = filterSearch.trim() === '' || 
      rec.visitorName.toLowerCase().includes(filterSearch.toLowerCase()) ||
      rec.company.toLowerCase().includes(filterSearch.toLowerCase()) ||
      rec.reason.toLowerCase().includes(filterSearch.toLowerCase());
    return matchesAirport && matchesStatus && matchesSearch;
  });

  return (
    <div className="flex flex-col gap-[26px] relative h-full w-full">
      {/* Header */}
      <div className="shrink-0">
        <h2 className="text-[26px] font-bold text-slate-900 tracking-tight leading-tight uppercase mb-1">
          Acesso de Terceiros
        </h2>
        <p className="text-[13px] text-slate-500 font-medium">
          Registro para acesso de terceiros que requerem apoio da equipe de Operações Aeroportuárias devido falta de credenciamento.
        </p>
      </div>

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
          Registros ({filteredRecords.length})
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
                <h3 className="text-xl font-bold text-slate-900 mb-2">Registrando Acesso...</h3>
                <p className="text-slate-500 text-sm font-medium">Os dados estão sendo salvos com sucesso no sistema.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-[32px]">
                {/* 1. Identificação Geral */}
                <div className="border border-slate-100 p-6 bg-slate-50/30 space-y-[26px]">
                  <h3 className="text-[13px] font-black text-slate-800 uppercase tracking-widest flex items-center gap-2">
                    <Key className="w-4 h-4 text-[#391694]" /> Dados do Acesso e Localidade
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                    {/* Airport Select */}
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Aeroporto / Localidade *</label>
                      <div className="relative">
                        <select
                          required
                          className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium"
                          value={formData.airport}
                          onChange={(e) => setFormData({...formData, airport: e.target.value})}
                        >
                          <option value="">Selecione a localidade</option>
                          {AIRPORTS.map((ap) => (
                            <option key={ap} value={ap}>{ap}</option>
                          ))}
                        </select>
                        <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                    </div>

                    {/* Status Check */}
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Status Inicial do Acesso *</label>
                      <div className="relative">
                        <select
                          required
                          className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-medium"
                          value={formData.status}
                          onChange={(e) => setFormData({...formData, status: e.target.value as any})}
                        >
                          <option value="Ativo">Ativo (Em Andamento)</option>
                          <option value="Agendado">Agendado (Futuro)</option>
                          <option value="Concluído">Concluído (Finalizado)</option>
                        </select>
                        <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                    </div>
                  </div>
                </div>

                {/* 2. Dados do Terceiro / Visitante */}
                <div className="border border-slate-100 p-6 bg-slate-50/30 space-y-[26px]">
                  <h3 className="text-[13px] font-black text-slate-800 uppercase tracking-widest flex items-center gap-2">
                    <User className="w-4 h-4 text-[#391694]" /> Dados do Terceiro / Visitante
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-[26px]">
                    <div className="space-y-2 md:col-span-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Nome Completo *</label>
                      <input
                        required
                        type="text"
                        placeholder="Ex: João da Silva Santos"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                        value={formData.visitorName}
                        onChange={(e) => setFormData({...formData, visitorName: e.target.value})}
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Documento de Identificação *</label>
                      <input
                        required
                        type="text"
                        placeholder="RG, CPF ou Passaporte"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                        value={formData.visitorDocument}
                        onChange={(e) => setFormData({...formData, visitorDocument: e.target.value})}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Empresa Representada *</label>
                      <div className="relative">
                        <input
                          required
                          type="text"
                          placeholder="Ex: Siemens, Claro, Terceirizada X"
                          className="w-full px-5 py-4 pl-12 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                          value={formData.company}
                          onChange={(e) => setFormData({...formData, company: e.target.value})}
                        />
                        <Building className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Área de Destino Autorizada *</label>
                      <input
                        required
                        type="text"
                        placeholder="Ex: Pátio de Aeronaves, Hangar 2, Cabeceira 15"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                        value={formData.area}
                        onChange={(e) => setFormData({...formData, area: e.target.value})}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Motivo / Descrição da Atividade *</label>
                    <textarea
                      required
                      rows={3}
                      placeholder="Descreva detalhadamente a finalidade do acesso perimetral ou operacional..."
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium resize-none"
                      value={formData.reason}
                      onChange={(e) => setFormData({...formData, reason: e.target.value})}
                    />
                  </div>
                </div>

                {/* 3. Escolta / Equipe de Apoio e Data/Hora */}
                <div className="border border-slate-100 p-6 bg-slate-50/30 space-y-[26px]">
                  <h3 className="text-[13px] font-black text-slate-800 uppercase tracking-widest flex items-center gap-2">
                    <Shield className="w-4 h-4 text-[#391694]" /> Controle de Segurança e Período
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-[26px]">
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Data do Acesso *</label>
                      <div className="relative">
                        <input
                          required
                          type="date"
                          className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                          value={formData.date}
                          onChange={(e) => setFormData({...formData, date: e.target.value})}
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Hora de Entrada *</label>
                      <input
                        required
                        type="time"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                        value={formData.startTime}
                        onChange={(e) => setFormData({...formData, startTime: e.target.value})}
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Hora Limite / Saída *</label>
                      <input
                        required
                        type="time"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                        value={formData.endTime}
                        onChange={(e) => setFormData({...formData, endTime: e.target.value})}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Inspetor de Operações / Responsável pela Escolta *</label>
                      <div className="relative">
                        <input
                          required
                          type="text"
                          placeholder="Nome do inspetor que acompanhará"
                          className="w-full px-5 py-4 pl-12 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                          value={formData.escortingStaff}
                          onChange={(e) => setFormData({...formData, escortingStaff: e.target.value})}
                        />
                        <Users className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Matrícula / Registro do Inspetor *</label>
                      <input
                        required
                        type="text"
                        placeholder="Ex: OPS-1234"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                        value={formData.escortingStaffId}
                        onChange={(e) => setFormData({...formData, escortingStaffId: e.target.value})}
                      />
                    </div>
                  </div>
                </div>

                {/* 4. Veículo de Apoio (Opcional) */}
                <div className="border border-slate-100 p-6 bg-slate-50/30 space-y-[26px]">
                  <h3 className="text-[13px] font-black text-slate-800 uppercase tracking-widest flex items-center gap-2">
                    <Car className="w-4 h-4 text-[#391694]" /> Veículo Comercial / Apoio Técnico (Caso Aplicável)
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Placa do Veículo</label>
                      <input
                        type="text"
                        placeholder="Ex: ABC-1234"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium uppercase"
                        value={formData.vehiclePlate}
                        onChange={(e) => setFormData({...formData, vehiclePlate: e.target.value})}
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Modelo e Cor do Veículo</label>
                      <input
                        type="text"
                        placeholder="Ex: Toyota Hilux Prata"
                        className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                        value={formData.vehicleModel}
                        onChange={(e) => setFormData({...formData, vehicleModel: e.target.value})}
                      />
                    </div>
                  </div>
                </div>

                {/* Submit button */}
                <div className="flex justify-end pt-4">
                  <button
                    type="submit"
                    className="px-10 py-4 bg-[#391694] hover:bg-[#2e1279] text-white font-bold text-[13px] uppercase tracking-wider transition-all shadow-md hover:shadow-lg flex items-center gap-2 rounded-none"
                  >
                    Registrar Acesso de Terceiro <ArrowRight className="w-5 h-5" />
                  </button>
                </div>
              </form>
            )}
          </div>
        ) : (
          /* History tab */
          <div className="max-w-6xl animate-in fade-in duration-500 space-y-6 pb-12">
            {/* Filters bar */}
            <div className="bg-slate-50 border border-slate-200 p-6 flex flex-col lg:flex-row items-center gap-4">
              <div className="relative w-full lg:flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Filtrar por nome, empresa ou atividade..."
                  className="w-full pl-11 pr-5 py-3.5 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all font-medium"
                  value={filterSearch}
                  onChange={(e) => setFilterSearch(e.target.value)}
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full lg:w-fit shrink-0">
                <div className="relative min-w-[180px]">
                  <select
                    className="w-full pl-4 pr-10 py-3.5 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-bold"
                    value={filterAirport}
                    onChange={(e) => setFilterAirport(e.target.value)}
                  >
                    <option value="">Todos Aeroportos</option>
                    {AIRPORTS.map((ap) => (
                      <option key={ap} value={ap}>{ap}</option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                </div>

                <div className="relative min-w-[180px]">
                  <select
                    className="w-full pl-4 pr-10 py-3.5 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer font-bold"
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                  >
                    <option value="">Todos Status</option>
                    <option value="Ativo">Ativo</option>
                    <option value="Agendado">Agendado</option>
                    <option value="Concluído">Concluído</option>
                  </select>
                  <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                </div>
              </div>
            </div>

            {/* Table / List */}
            {filteredRecords.length === 0 ? (
              <div className="border border-[#C9C5E6] border-dashed p-16 text-center text-slate-400 font-medium">
                Nenhum registro de acesso encontrado com os filtros selecionados.
              </div>
            ) : (
              <div className="border border-slate-200 overflow-x-auto bg-white">
                <table className="w-full text-left border-collapse min-w-[1000px]">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200">
                      <th className="px-6 py-4 text-slate-500 font-bold text-[11px] uppercase tracking-wider">Período / Localidade</th>
                      <th className="px-6 py-4 text-slate-500 font-bold text-[11px] uppercase tracking-wider">Terceiro / Empresa</th>
                      <th className="px-6 py-4 text-slate-500 font-bold text-[11px] uppercase tracking-wider">Motivo e Destino</th>
                      <th className="px-6 py-4 text-slate-500 font-bold text-[11px] uppercase tracking-wider">Escolta / Acompanhamento</th>
                      <th className="px-6 py-4 text-slate-500 font-bold text-[11px] uppercase tracking-wider text-center">Status</th>
                      <th className="px-6 py-4 text-slate-500 font-bold text-[11px] uppercase tracking-wider text-right">Ações</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {filteredRecords.map((record) => {
                      let statusBadgeClass = "";
                      switch (record.status) {
                        case 'Ativo':
                          statusBadgeClass = "bg-blue-50 text-blue-700 border-blue-200";
                          break;
                        case 'Agendado':
                          statusBadgeClass = "bg-amber-50 text-amber-700 border-amber-200";
                          break;
                        case 'Concluído':
                          statusBadgeClass = "bg-emerald-50 text-emerald-700 border-emerald-200";
                          break;
                      }

                      return (
                        <tr key={record.id} className="hover:bg-slate-50/50 transition-colors">
                          <td className="px-6 py-5">
                            <div className="flex flex-col gap-1.5">
                              <span className="text-[13px] font-bold text-slate-900">{record.airport}</span>
                              <div className="flex items-center gap-1.5 text-slate-400 text-[11px] font-medium">
                                <Calendar className="w-3.5 h-3.5" />
                                <span>{record.date}</span>
                              </div>
                              <div className="flex items-center gap-1.5 text-slate-400 text-[11px] font-medium">
                                <Clock className="w-3.5 h-3.5" />
                                <span>{record.startTime} - {record.endTime}</span>
                              </div>
                            </div>
                          </td>

                          <td className="px-6 py-5">
                            <div className="flex flex-col gap-1">
                              <span className="text-[13px] font-bold text-slate-800">{record.visitorName}</span>
                              <span className="text-[11px] text-slate-400 font-medium">{record.visitorDocument}</span>
                              <span className="text-[12px] font-semibold text-[#391694] mt-1">{record.company}</span>
                            </div>
                          </td>

                          <td className="px-6 py-5 max-w-[280px]">
                            <div className="flex flex-col gap-1">
                              <span className="text-[13px] text-slate-700 font-medium line-clamp-2 leading-relaxed" title={record.reason}>
                                {record.reason}
                              </span>
                              <span className="text-[11px] text-slate-400 font-bold uppercase tracking-wider block mt-1">
                                Área: {record.area}
                              </span>
                              {record.vehiclePlate && (
                                <span className="text-[11.5px] text-amber-800 font-semibold flex items-center gap-1 mt-1">
                                  <Car className="w-3.5 h-3.5 shrink-0" /> {record.vehicleModel} ({record.vehiclePlate})
                                </span>
                              )}
                            </div>
                          </td>

                          <td className="px-6 py-5">
                            <div className="flex flex-col gap-1">
                              <span className="text-[12.5px] text-slate-800 font-semibold">{record.escortingStaff}</span>
                              <span className="text-[11px] text-slate-400 font-medium">{record.escortingStaffId}</span>
                            </div>
                          </td>

                          <td className="px-6 py-5 text-center">
                            <span className={`inline-flex items-center px-2.5 py-1 rounded-none text-[11px] font-bold border uppercase tracking-wider ${statusBadgeClass}`}>
                              {record.status}
                            </span>
                          </td>

                          <td className="px-6 py-5 text-right">
                            <button
                              onClick={() => handleDelete(record.id)}
                              className="p-2 text-slate-300 hover:text-red-600 transition-colors inline-flex"
                              title="Remover Registro"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
