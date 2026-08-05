
import React, { useState, useEffect } from 'react';
import { Send, CheckCircle2, XCircle, ChevronDown, ArrowRight, Eye } from 'lucide-react';

interface AISComplianceFormProps {
  onSuccess: (data: any) => void;
  initialData?: any;
  onCancel?: () => void;
  isReadOnly?: boolean;
  onBack?: () => void;
}

export const AIRPORTS = [
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

const DEFAULT_FORM_STATE = {
  airport: '',
  date: '',
  time: '',
  registration: '',
  pilotName: '',
  anacCode: '',
  description: '',
  nonCompliantItem: ''
};

export const AISComplianceForm: React.FC<AISComplianceFormProps> = ({ onSuccess, initialData, onCancel, isReadOnly = false, onBack }) => {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [formData, setFormData] = useState(initialData || DEFAULT_FORM_STATE);

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    } else {
      setFormData(DEFAULT_FORM_STATE);
    }
  }, [initialData]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isReadOnly) return;

    setIsSubmitted(true);
    
    const record = {
      ...formData,
      id: initialData?.id || Math.random().toString(36).substr(2, 9),
      submittedAt: initialData?.submittedAt || new Date().toISOString()
    };

    setTimeout(() => {
      onSuccess(record);
      setIsSubmitted(false);
      if (!initialData) {
        setFormData(DEFAULT_FORM_STATE);
      }
    }, 1000);
  };

  if (isSubmitted) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center animate-in zoom-in duration-300">
        <div className="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mb-6">
          <CheckCircle2 className="w-10 h-10 text-emerald-600" />
        </div>
        <h3 className="text-2xl font-bold text-slate-900 mb-2">{initialData ? 'Salvando Alterações...' : 'Processando...'}</h3>
        <p className="text-slate-500">O reporte de descumprimento AIS está sendo atualizado no sistema.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-5xl space-y-[26px] animate-in fade-in duration-500 pb-10">
      {isReadOnly && (
        <div className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-none px-6 py-4 mb-[26px]">
          <div className="flex items-center gap-3">
            <Eye className="w-4 h-4 text-slate-500" />
            <span className="text-xs font-black text-slate-600 uppercase tracking-widest">Modo de Visualização</span>
          </div>
        </div>
      )}

      {!isReadOnly && initialData && (
        <div className="flex items-center justify-between bg-indigo-50 border border-indigo-100 rounded-none px-6 py-4 mb-[26px]">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></div>
            <span className="text-xs font-black text-indigo-900 uppercase tracking-widest">Modo de Edição Ativo</span>
          </div>
          <button 
            type="button" 
            onClick={onCancel}
            className="text-[10px] font-black text-indigo-600 hover:text-indigo-800 transition-colors flex items-center gap-1.5 uppercase tracking-widest"
          >
            <XCircle className="w-4 h-4" />
            Cancelar Edição
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 gap-[26px]">
        {/* Localidade (Select Estilo Oficial) */}
        <div className="space-y-2">
          <label className="text-[13px] font-bold text-slate-900 block">
            Aeroporto da Ocorrência *
          </label>
          <div className="relative">
            <select
              required
              disabled={isReadOnly}
              className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all appearance-none cursor-pointer disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed"
              value={formData.airport}
              onChange={(e) => setFormData({...formData, airport: e.target.value})}
            >
              <option value="">Selecione a localidade</option>
              {AIRPORTS.map(ap => <option key={ap} value={ap}>{ap}</option>)}
            </select>
            <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
          </div>
        </div>

        {/* Matrícula (Input Estilo Oficial) */}
        <div className="space-y-2">
          <label className="text-[13px] font-bold text-slate-900 block">
            Matrícula da Aeronave *
          </label>
          <input
            required
            disabled={isReadOnly}
            type="text"
            placeholder="Digite a matrícula (ex: PT-ABC)"
            className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all uppercase font-medium placeholder:normal-case disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed"
            value={formData.registration}
            onChange={(e) => setFormData({...formData, registration: e.target.value})}
          />
        </div>

        {/* Data e Hora (Lado a Lado) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
          <div className="space-y-2">
            <label className="text-[13px] font-bold text-slate-900 block">
              Data do Evento *
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
              Hora do Evento (UTC) *
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

        {/* Nome do Piloto */}
        <div className="space-y-2">
          <label className="text-[13px] font-bold text-slate-900 block">
            Nome do Piloto em Comando <span className="text-[11px] italic font-normal text-slate-500">(não obrigatório)</span>
          </label>
          <input
            disabled={isReadOnly}
            type="text"
            placeholder="Digite o nome completo do responsável"
            className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all font-medium disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed"
            value={formData.pilotName}
            onChange={(e) => setFormData({...formData, pilotName: e.target.value})}
          />
        </div>

        {/* Item Descumprido */}
        <div className="space-y-2">
          <label className="text-[13px] font-bold text-slate-900 block">
            Item Descumprido (Normativo/NESO) *
          </label>
          <input
            required
            disabled={isReadOnly}
            type="text"
            placeholder="Digite a norma ou item descumprido"
            className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all font-medium disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed"
            value={formData.nonCompliantItem}
            onChange={(e) => setFormData({...formData, nonCompliantItem: e.target.value})}
          />
        </div>

        {/* Descrição (Textarea) */}
        <div className="space-y-2">
          <label className="text-[13px] font-bold text-slate-900 block">
            Descrição Detalhada do Evento *
          </label>
          <textarea
            required
            disabled={isReadOnly}
            rows={5}
            placeholder="Descreva detalhadamente o ocorrido para análise operacional..."
            className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-300 outline-none focus:border-black transition-all resize-none font-medium disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
          />
        </div>
      </div>

      <div className="flex justify-end items-center gap-6">
        {isReadOnly ? (
          <button
            type="button"
            onClick={onBack}
            className="flex items-center gap-3 bg-slate-200 text-slate-700 px-10 py-4 rounded-none font-bold shadow-sm hover:bg-slate-300 transition-all"
          >
            Voltar
          </button>
        ) : (
          <>
            {initialData && (
              <button
                type="button"
                onClick={onCancel}
                className="text-xs font-black text-slate-400 hover:text-slate-600 uppercase tracking-widest transition-colors"
              >
                Descartar Alterações
              </button>
            )}
            
            <button
              type="submit"
              className="flex items-center gap-3 bg-black text-white px-10 py-4 rounded-none font-bold shadow-lg hover:scale-105 transition-all group"
            >
              <span>{initialData ? 'Salvar Alterações' : 'Finalizar Reporte'}</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </>
        )}
      </div>
    </form>
  );
};
