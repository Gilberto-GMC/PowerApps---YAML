
import React, { useState, useMemo, useEffect } from 'react';
import { AISComplianceForm, AIRPORTS } from './AISComplianceForm';
import { 
  FileSpreadsheet, 
  PlusCircle, 
  History, 
  MoreHorizontal, 
  CheckCircle, 
  Building2, 
  Calendar,
  X,
  AlertTriangle,
  Pencil,
  CheckCircle2,
  Trash2,
  Clock,
  ExternalLink,
  Filter,
  ChevronDown,
  XCircle,
  CornerUpLeft,
  MessageSquare,
  Eye,
  Plane
} from 'lucide-react';

export const AISComplianceModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [airportFilter, setAirportFilter] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [editingRecord, setEditingRecord] = useState<any | null>(null);
  const [viewingRecord, setViewingRecord] = useState<any | null>(null);
  
  const [records, setRecords] = useState<any[]>([
    {
      id: '1',
      airport: 'Aeroporto de Navegantes',
      date: '2024-05-18',
      time: '14:30',
      registration: 'PR-GUO',
      pilotName: 'Carlos Silveira',
      anacCode: '123456',
      nonCompliantItem: 'NESO 02/2024 - Item 5.1',
      status: 'Aguardando envio',
      description: 'Aeronave iniciou táxi sem autorização da sinalização de solo.'
    },
    {
      id: '2',
      airport: 'Aeroporto de Foz do Iguaçu',
      date: '2024-05-17',
      time: '09:15',
      registration: 'PT-LMN',
      pilotName: 'João da Silva',
      anacCode: '987654',
      nonCompliantItem: 'Isenção 04/2023',
      status: 'Enviado à ANAC',
      seiNumber: '00123.456789/2024-01',
      description: 'Estacionamento em posição não homologada para o porte da aeronave.'
    },
    {
      id: '3',
      airport: 'Aeroporto da Pampulha',
      date: '2021-10-09',
      time: '10:38',
      registration: 'PT-XYZ',
      pilotName: '',
      anacCode: '',
      nonCompliantItem: 'NESO 01/2021',
      status: 'Devolvido',
      returnReason: 'Faltou informar o código ANAC do piloto.',
      description: 'Não informado.'
    }
  ]);

  const [isActionMenuId, setIsActionMenuId] = useState<string | null>(null);
  const [actionMenuPosition, setActionMenuPosition] = useState<{ top?: number, bottom?: number, right?: number } | null>(null);

  useEffect(() => {
    const handleScroll = () => {
      if (isActionMenuId) setIsActionMenuId(null);
    };
    window.addEventListener('scroll', handleScroll, true);
    window.addEventListener('resize', handleScroll);
    return () => {
      window.removeEventListener('scroll', handleScroll, true);
      window.removeEventListener('resize', handleScroll);
    };
  }, [isActionMenuId]);
  const [refuseId, setRefuseId] = useState<string | null>(null);
  const [returnId, setReturnId] = useState<string | null>(null);
  const [completeId, setCompleteId] = useState<string | null>(null);
  const [viewReasonRecord, setViewReasonRecord] = useState<any | null>(null);
  
  const [seiValue, setSeiValue] = useState('');
  const [justification, setJustification] = useState('');
  const [returnReason, setReturnReason] = useState('');

  const handleSaveRecord = (record: any) => {
    if (editingRecord) {
      setRecords(records.map(r => r.id === record.id ? { 
        ...record, 
        status: r.status === 'Devolvido' ? 'Aguardando envio' : r.status, // Reset status if it was returned
        seiNumber: r.seiNumber, 
        justification: r.justification,
        returnReason: r.returnReason 
      } : r));
      setEditingRecord(null);
    } else {
      const recordWithStatus = { ...record, status: 'Aguardando envio' };
      setRecords([recordWithStatus, ...records]);
    }
    setActiveTab('history');
  };

  const handleEditClick = (record: any) => {
    if (record.status === 'Enviado à ANAC' || record.status === 'Recusado') return;
    setEditingRecord(record);
    setViewingRecord(null);
    setActiveTab('form');
    setIsActionMenuId(null);
  };

  const handleViewClick = (record: any) => {
    setViewingRecord(record);
    setEditingRecord(null);
    setActiveTab('form');
    setIsActionMenuId(null);
  };

  const handleCancelEdit = () => {
    setEditingRecord(null);
    setViewingRecord(null);
    setActiveTab('history');
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

  const handleComplete = () => {
    if (completeId) {
      setRecords(records.map(r => 
        r.id === completeId 
          ? { ...r, status: 'Enviado à ANAC', seiNumber: seiValue } 
          : r
      ));
      setCompleteId(null);
      setSeiValue('');
    }
  };

  const filteredRecords = useMemo(() => {
    return records.filter(record => {
      const matchesAirport = airportFilter === '' || record.airport === airportFilter;
      const recordDate = new Date(record.date);
      const start = startDate ? new Date(startDate) : null;
      const end = endDate ? new Date(endDate) : null;
      const matchesDate = (!start || recordDate >= start) && (!end || recordDate <= end);
      return matchesAirport && matchesDate;
    });
  }, [records, airportFilter, startDate, endDate]);

  return (
    <div className="flex flex-col gap-[26px] relative h-full w-full">
      {/* 1. Título conforme solicitado */}
      <h2 className="text-2xl font-bold text-slate-900 tracking-tight leading-tight uppercase shrink-0">
        Descumprimento AIS
      </h2>

      {/* 2. Abas de Navegação */}
      <div className="flex p-1 bg-slate-50 rounded-none w-fit border border-slate-200 shrink-0">
        <button
          onClick={() => { setActiveTab('form'); setEditingRecord(null); setViewingRecord(null); }}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-none text-[13px] font-bold transition-all ${
            activeTab === 'form' 
              ? 'bg-white text-[#391694] shadow-sm' 
              : 'text-slate-400 hover:text-slate-600'
          }`}
        >
          <PlusCircle className="w-4 h-4" />
          {editingRecord ? 'Editar Reporte' : (viewingRecord ? 'Visualizar Reporte' : 'Novo Registro')}
        </button>
        <button
          onClick={() => { setActiveTab('history'); setEditingRecord(null); setViewingRecord(null); }}
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

      {/* 3. Aviso de Segurança conforme imagem */}
      <div className="bg-[#FFF8E6] border border-[#FFECB3] p-4 shrink-0 flex items-start gap-4">
        <AlertTriangle className="w-5 h-5 text-[#E6A23C] shrink-0 mt-0.5" />
        <p className="text-[13px] text-[#856404] font-medium leading-relaxed">
          <strong>Aviso de Segurança:</strong> Somente devem ser reportados eventos que envolverem descumprimento de medidas de segurança operacional. 
          A ausência de reservas de pátio não se enquadra neste quesito.
        </p>
      </div>

      {/* 4. Conteúdo Principal */}
      <div className="flex-1 overflow-visible">
        {activeTab === 'form' ? (
          <div className="w-full">
            <AISComplianceForm 
              onSuccess={handleSaveRecord} 
              initialData={editingRecord || viewingRecord} 
              onCancel={handleCancelEdit}
              isReadOnly={!!viewingRecord}
              onBack={() => { setViewingRecord(null); setActiveTab('history'); }}
            />
          </div>
        ) : (
          <div className="flex flex-col min-h-0 animate-in fade-in duration-500 w-full">
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

            <div className="bg-white border border-slate-200 rounded-none shadow-sm relative overflow-x-auto w-full min-h-[320px]">
              <table className="w-full text-center border-separate border-spacing-0 table-fixed">
                <thead>
                  <tr className="bg-slate-50">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Data/Hora</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Aeronave</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Aeroporto</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-center border-b border-slate-200 whitespace-nowrap">Status</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-center border-b border-slate-200 whitespace-nowrap">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredRecords.map((record, index) => {
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
 <span className="text-xs font-bold text-slate-700 uppercase">{record.registration}</span>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="text-xs text-slate-700 font-medium whitespace-normal leading-tight max-w-[200px] mx-auto">
 {record.airport}
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex flex-col items-center gap-1">
 {record.status === 'Enviado à ANAC' ? (
 <>
 <span className="inline-flex items-center gap-1 px-2 py-1 rounded-sm text-[10px] font-black bg-emerald-100 text-emerald-700 uppercase tracking-wider justify-center">
 <CheckCircle className="w-3 h-3" />
 ENVIADO À ANAC
 </span>
 <span className="text-[9px] text-slate-400 font-mono tracking-tighter">{record.seiNumber}</span>
 </>
 ) : record.status === 'Recusado' ? (
 <>
 <span className="inline-flex items-center gap-1 px-2 py-1 rounded-sm text-[10px] font-black bg-red-100 text-red-700 uppercase tracking-wider justify-center">
 <XCircle className="w-3 h-3" />
 RECUSADO
 </span>
 {record.justification && (
 <button 
 onClick={() => setViewReasonRecord(record)}
 className="text-[9px] font-bold text-slate-400 hover:text-slate-600 underline decoration-slate-300 underline-offset-2 flex items-center gap-1 transition-colors justify-center"
 >
 Ver Motivo
 </button>
 )}
 </>
 ) : record.status === 'Devolvido' ? (
 <>
 <span className="inline-flex items-center gap-1 px-2 py-1 rounded-sm text-[10px] font-black bg-blue-100 text-blue-700 uppercase tracking-wider justify-center">
 <CornerUpLeft className="w-3 h-3" />
 DEVOLVIDO
 </span>
 {record.returnReason && (
 <button 
 onClick={() => setViewReasonRecord(record)}
 className="text-[9px] font-bold text-slate-400 hover:text-slate-600 underline decoration-slate-300 underline-offset-2 flex items-center gap-1 transition-colors justify-center"
 >
 Ver Motivo
 </button>
 )}
 </>
 ) : (
 <span className="inline-flex items-center gap-1 px-2 py-1 rounded-sm text-[10px] font-black bg-amber-100 text-amber-700 uppercase tracking-wider justify-center">
 <Clock className="w-3 h-3" />
 AGUARDANDO ENVIO
 </span>
 )}
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
 setIsActionMenuId(isActionMenuId === record.id ? null : record.id);
 }}
 className={`p-1.5 rounded-none transition-all ${isActionMenuId === record.id ? 'bg-[#391694] text-white shadow-md' : 'text-slate-400 hover:text-[#391694] hover:bg-indigo-50 border border-slate-200'}`}
 >
 <MoreHorizontal className="w-5 h-5" />
 </button>

 {isActionMenuId === record.id && actionMenuPosition && (
 <div 
 className="fixed z-50 w-48 bg-white border border-slate-200 rounded-none shadow-2xl overflow-hidden animate-in fade-in duration-200"
 style={{
 top: actionMenuPosition.top,
 bottom: actionMenuPosition.bottom,
 right: actionMenuPosition.right,
 }}
 onClick={(e) => e.stopPropagation()}
 >
 <button 
 onClick={() => handleViewClick(record)} 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"
 >
 <Eye className="w-3.5 h-3.5" /> Ver Detalhes
 </button>
 <button 
 disabled={record.status === 'Enviado à ANAC'}
 onClick={() => handleEditClick(record)} 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50 disabled:opacity-30 disabled:cursor-not-allowed"
 >
 <Pencil className="w-3.5 h-3.5" /> Editar
 </button>
 <button 
 disabled={record.status === 'Enviado à ANAC'}
 onClick={() => { setCompleteId(record.id); setIsActionMenuId(null); }} 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-emerald-600 hover:bg-emerald-50/50 flex items-center gap-3 border-b border-slate-50 disabled:opacity-30 disabled:cursor-not-allowed"
 >
 <CheckCircle2 className="w-3.5 h-3.5" /> Concluir
 </button>
 <button 
 disabled={record.status === 'Enviado à ANAC'}
 onClick={() => { setRefuseId(record.id); setIsActionMenuId(null); }} 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-red-600 hover:bg-red-50 flex items-center gap-3 border-b border-slate-50 disabled:opacity-30 disabled:cursor-not-allowed"
 >
 <XCircle className="w-3.5 h-3.5" /> Recusar
 </button>
 <button 
 disabled={record.status === 'Enviado à ANAC' || record.status === 'Recusado' || record.status === 'Devolvido'}
 onClick={() => { setReturnId(record.id); setIsActionMenuId(null); }} 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-blue-600 hover:bg-blue-50 flex items-center gap-3 disabled:opacity-30 disabled:cursor-not-allowed"
 >
 <CornerUpLeft className="w-3.5 h-3.5" /> Devolver
 </button>
 </div>
 )}
 </td>
                    </tr>
                  )})}
                </tbody>
              </table>
              <div className="bg-slate-50 px-6 py-3 border-t border-slate-200 text-[10px] text-slate-400 font-bold uppercase tracking-widest">
                {filteredRecords.length} REGISTROS ENCONTRADOS
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modais de Ação */}
      {isActionMenuId && (
        <div className="fixed inset-0 z-40 bg-transparent" onClick={() => setIsActionMenuId(null)}></div>
      )}

      {completeId && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-white rounded-none w-full max-w-sm shadow-2xl overflow-hidden border border-slate-100">
            <div className="p-8">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-emerald-50 rounded-none flex items-center justify-center border border-emerald-100">
                  <CheckCircle2 className="w-6 h-6 text-emerald-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 tracking-tight">Concluir Processo</h3>
              </div>
              
              <p className="text-slate-500 text-sm leading-relaxed mb-6">
                Informe o número do processo gerado no sistema SEI para vincular a este reporte.
              </p>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1">
                  Número SEI! <span className="text-red-500">*</span>
                </label>
                <input 
                  autoFocus
                  type="text" 
                  placeholder="Ex: 00123.456789/2024-00"
                  value={seiValue}
                  onChange={(e) => setSeiValue(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-none outline-none focus:border-[#391694] transition-all text-sm font-mono placeholder:font-sans"
                />
              </div>
            </div>

            <div className="p-4 bg-slate-50/50 border-t border-slate-100 flex gap-3">
              <button onClick={() => { setCompleteId(null); setSeiValue(''); }} className="flex-1 py-3 bg-white border border-slate-200 rounded-none text-xs font-bold text-slate-600 hover:bg-slate-100 transition-all">Cancelar</button>
              <button disabled={!seiValue.trim()} onClick={handleComplete} className="flex-1 py-3 bg-black rounded-none text-xs font-bold text-white hover:opacity-90 transition-all shadow-lg shadow-black/20 disabled:opacity-50">Salvar</button>
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
                <h3 className="text-xl font-bold text-slate-900 tracking-tight">Recusar Reporte</h3>
              </div>
              
              <p className="text-slate-500 text-sm leading-relaxed mb-6">
                O status do reporte será alterado para <strong>RECUSADO</strong>. Por favor, informe o motivo abaixo.
              </p>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1">
                  Justificativa da Recusa <span className="text-red-500">*</span>
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
              <button disabled={!justification.trim()} onClick={handleRefuse} className="flex-1 py-3 bg-black rounded-none text-xs font-bold text-white hover:opacity-90 transition-all shadow-lg shadow-black/20 disabled:opacity-50">Confirmar Recusa</button>
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
                <h3 className="text-xl font-bold text-slate-900 tracking-tight">Devolver Reporte</h3>
              </div>
              
              <p className="text-slate-500 text-sm leading-relaxed mb-6">
                Solicite informações adicionais ou correções para este reporte. O status será alterado para <strong>DEVOLVIDO</strong>.
              </p>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1">
                  Dados Pendentes / Correções <span className="text-red-500">*</span>
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
              <button disabled={!returnReason.trim()} onClick={handleReturn} className="flex-1 py-3 bg-black rounded-none text-xs font-bold text-white hover:opacity-90 transition-all shadow-lg shadow-black/20 disabled:opacity-50">Confirmar Devolução</button>
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
