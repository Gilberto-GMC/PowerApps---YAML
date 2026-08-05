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
  UploadCloud,
  XCircle,
  Mail,
  AlertTriangle,
  Download
} from 'lucide-react';
import { AIRPORTS } from './AISComplianceForm';
import jsPDF from 'jspdf';

interface AvopRecord {
  id: string;
  aeroporto: string;
  dataInicio: string;
  horaInicio: string;
  dataTermino: string;
  horaTermino: string;
  detalhamento: string;
  impacto: string;
  emails?: string[];
  status: 'Ativo' | 'Encerrado';
}

const MOCK_RECORDS: AvopRecord[] = [
  {
    id: '1',
    aeroporto: 'Aeroporto da Pampulha',
    dataInicio: '2026-04-01',
    horaInicio: '10:00',
    dataTermino: '2026-04-02',
    horaTermino: '18:00',
    detalhamento: 'Manutenção programada na pista principal.',
    impacto: 'Pista interditada para pousos e decolagens.',
    emails: [],
    status: 'Ativo'
  }
];

const loadImage = (url: string): Promise<HTMLImageElement> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'Anonymous';
    img.onload = () => resolve(img);
    img.onerror = (e) => reject(e);
    img.src = url;
  });
};

const generatePDF = async (record: AvopRecord) => {
  const doc = new jsPDF();
  
  let yPos = 45;

  const addHeader = async () => {
    try {
      const logoImg = await loadImage('https://aevo.com.br/wp-content/uploads/2026/02/MOTIVA_Logo_VersaoPositiva_Horizontal_Anil_RGB-1024x365.png');
      doc.addImage(logoImg, 'PNG', 20, 15, 42, 15);
    } catch (e) {
      console.error("Could not load logo", e);
      doc.setTextColor(94, 34, 243);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(16);
      doc.text("MOTIVA", 20, 25);
    }

    doc.setTextColor(94, 34, 243);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text("AVISO OPERACIONAL (AVOP)", 190, 22, { align: "right" });
    
    doc.setTextColor(100, 100, 100);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.text("Registro oficial de alteração ou condição específica", 190, 28, { align: "right" });

    doc.setFillColor(94, 34, 243);
    doc.rect(20, 35, 170, 1.5, 'F');
  };

  await addHeader();

  const addFooter = (pageNumber: number) => {
    doc.setFillColor(94, 34, 243);
    doc.rect(20, 285, 170, 0.5, 'F');
    
    doc.setTextColor(150, 150, 150);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);
    const dateStr = new Date().toLocaleString('pt-BR');
    doc.text(`Gerado em: ${dateStr}`, 20, 290);
    doc.text(`Página ${pageNumber}`, 190, 290, { align: "right" });
  };

  let pageNum = 1;

  const checkPageBreak = (neededHeight: number) => {
    if (yPos + neededHeight > 275) {
      addFooter(pageNum);
      doc.addPage();
      pageNum++;
      yPos = 20;
      doc.setFillColor(94, 34, 243);
      doc.rect(20, 15, 170, 1.5, 'F');
      yPos = 25;
      return true;
    }
    return false;
  };

  const drawSectionTitle = (title: string) => {
    checkPageBreak(15);
    doc.setFillColor(94, 34, 243);
    doc.rect(20, yPos, 170, 8, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(10);
    doc.text(title.toUpperCase(), 25, yPos + 5.5);
    yPos += 14;
  };

  const drawFieldRow = (label1: string, value1: string, label2?: string, value2?: string) => {
    checkPageBreak(15);
    doc.setTextColor(100, 100, 100);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);
    doc.text(label1.toUpperCase(), 20, yPos);
    
    doc.setTextColor(0, 0, 0);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(10);
    doc.text(value1, 20, yPos + 5);

    if (label2 && value2) {
      doc.setTextColor(100, 100, 100);
      doc.setFont("helvetica", "normal");
      doc.setFontSize(8);
      doc.text(label2.toUpperCase(), 105, yPos);
      
      doc.setTextColor(0, 0, 0);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(10);
      doc.text(value2, 105, yPos + 5);
    }
    yPos += 12;
  };

  const drawTextField = (label: string, text: string) => {
    checkPageBreak(20);
    doc.setTextColor(0, 0, 0);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(10);
    doc.text(label.toUpperCase(), 20, yPos);
    yPos += 4;

    doc.setTextColor(0, 0, 0);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    
    const lines = doc.splitTextToSize(text, 166);
    const boxHeight = (lines.length * 5) + 6;
    
    if (checkPageBreak(boxHeight + 5)) {
      doc.setTextColor(0, 0, 0);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(10);
      doc.text(label.toUpperCase() + " (Continuação)", 20, yPos);
      yPos += 4;
    }
    
    doc.setFillColor(248, 250, 252);
    doc.setDrawColor(226, 232, 240);
    doc.rect(20, yPos, 170, boxHeight, 'FD');
    
    let textY = yPos + 6;
    for (let i = 0; i < lines.length; i++) {
      doc.text(lines[i], 22, textY);
      textY += 5;
    }
    
    yPos += boxHeight + 8;
  };

  drawSectionTitle("Informações Gerais");
  drawFieldRow("ID do Registro", record.id, "Status", record.status.toUpperCase());
  drawFieldRow("Aeroporto", record.aeroporto);
  
  yPos += 4;
  drawSectionTitle("Período de Vigência");
  drawFieldRow(
    "Início", 
    `${record.dataInicio.split('-').reverse().join('/')} às ${record.horaInicio} UTC`,
    "Término",
    `${record.dataTermino.split('-').reverse().join('/')} às ${record.horaTermino} UTC`
  );

  yPos += 4;
  drawSectionTitle("Detalhamento");
  drawTextField("Descrição da Situação (Evento, Alteração ou Cancelamento)", record.detalhamento);
  drawTextField("Condição Operacional Resultante (Impactos, Restrições ou Liberações)", record.impacto);

  if (record.emails && record.emails.length > 0) {
    const validEmails = record.emails.filter(e => e.trim() !== '');
    if (validEmails.length > 0) {
      yPos += 4;
      drawSectionTitle("Notificações Adicionais");
      drawTextField("E-mails Notificados", validEmails.join(', '));
    }
  }

  addFooter(pageNum);

  doc.save(`AVOP_${record.aeroporto.replace(/\s+/g, '_')}_${record.dataInicio}.pdf`);
};

export const AvopModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [records, setRecords] = useState<AvopRecord[]>(MOCK_RECORDS);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    aeroporto: '',
    dataInicio: new Date().toISOString().split('T')[0],
    horaInicio: '00:00',
    dataTermino: new Date().toISOString().split('T')[0],
    horaTermino: '00:00',
    detalhamento: '',
    impacto: '',
    emails: ['']
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowConfirmModal(true);
  };

  const handleConfirmSubmit = () => {
    setShowConfirmModal(false);
    setIsSubmitting(true);

    setTimeout(async () => {
      const newRecord: AvopRecord = {
        id: Math.random().toString(36).substr(2, 9),
        ...formData,
        status: 'Ativo'
      };

      setRecords([newRecord, ...records]);
      await generatePDF(newRecord);
      setIsSubmitting(false);
      setActiveTab('history');
      
      // Reset form
      setFormData({
        aeroporto: '',
        dataInicio: new Date().toISOString().split('T')[0],
        horaInicio: '00:00',
        dataTermino: new Date().toISOString().split('T')[0],
        horaTermino: '00:00',
        detalhamento: '',
        impacto: '',
        emails: ['']
      });
    }, 1500);
  };

  return (
    <div className="flex flex-col gap-[26px] relative h-full w-full">
      {/* Header */}
      <h2 className="text-[26px] font-bold text-slate-900 tracking-tight leading-tight uppercase shrink-0 flex items-center gap-3">
        Aviso Operacional (AVOP)
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
                <h3 className="text-2xl font-bold text-slate-900 mb-2">Registrando Aviso...</h3>
                <p className="text-slate-500">O aviso operacional está sendo salvo no sistema.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-[26px]">
                <div className="bg-amber-50 border border-amber-200 p-4 shadow-sm mb-[26px]">
                  <p className="text-[13px] text-amber-800 font-medium leading-relaxed text-justify">
                    O Aviso Operacional (AVOP) é utilizado para comunicar alterações temporárias ou condições específicas que impactam a operação do aeródromo, mas que não requerem publicação formal no AIS. Tem caráter informativo interno e deve ser emitido sempre que houver necessidade de alertar Operadores Aéreos, Órgão ATS Local, ESATAs e outras partes interessadas sobre mudanças relevantes.<br/><br/>
                    <strong>AVOP não cancela NOTAM</strong>
                  </p>
                </div>

                {/* Aeroporto */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Aeroporto *</label>
                  <div className="relative">
                    <select 
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 appearance-none outline-none focus:border-black transition-all font-medium cursor-pointer"
                      value={formData.aeroporto}
                      onChange={(e) => setFormData({...formData, aeroporto: e.target.value})}
                      required
                    >
                      <option value="">Selecione o aeroporto</option>
                      {AIRPORTS.map(ap => <option key={ap} value={ap}>{ap}</option>)}
                    </select>
                    <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                  </div>
                </div>

                {/* Datas e Horas */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Data Inicial *</label>
                    <input 
                      type="date"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all font-medium"
                      value={formData.dataInicio}
                      onChange={(e) => setFormData({...formData, dataInicio: e.target.value})}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Hora Inicial (UTC) *</label>
                    <input 
                      type="time"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all font-medium"
                      value={formData.horaInicio}
                      onChange={(e) => setFormData({...formData, horaInicio: e.target.value})}
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Data Término *</label>
                    <input 
                      type="date"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all font-medium"
                      value={formData.dataTermino}
                      onChange={(e) => setFormData({...formData, dataTermino: e.target.value})}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Hora Término (UTC) *</label>
                    <input 
                      type="time"
                      className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all font-medium"
                      value={formData.horaTermino}
                      onChange={(e) => setFormData({...formData, horaTermino: e.target.value})}
                      required
                    />
                  </div>
                </div>

                {/* Detalhamento */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Descrição da Situação (Evento, Alteração ou Cancelamento) *</label>
                  <textarea 
                    className="w-full p-5 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all min-h-[120px] resize-y font-medium"
                    placeholder="Descreva detalhadamente a situação, evento ou o motivo do cancelamento..."
                    value={formData.detalhamento}
                    onChange={(e) => setFormData({...formData, detalhamento: e.target.value})}
                    required
                  />
                </div>

                {/* Impacto */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Condição Operacional Resultante (Impactos, Restrições ou Liberações) *</label>
                  <textarea 
                    className="w-full p-5 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all min-h-[120px] resize-y font-medium"
                    placeholder="Descreva a condição operacional resultante (ex: pista interditada, operações normalizadas, etc)..."
                    value={formData.impacto}
                    onChange={(e) => setFormData({...formData, impacto: e.target.value})}
                    required
                  />
                </div>

                {/* E-mails para envio */}
                <div className="space-y-3">
                  <label className="text-[13px] font-bold text-slate-900 block">E-mails Adicionais para Notificação</label>
                  <div className="bg-blue-50 border border-blue-200 p-3 mb-3">
                    <p className="text-[12px] text-blue-800 font-medium leading-relaxed">
                      <strong>Nota:</strong> O registro já é enviado automaticamente para o e-mail do <strong>XNG</strong> por padrão. 
                      Insira abaixo apenas os destinatários <strong>adicionais</strong> que possam ser impactados ou que devam receber este AVOP.
                    </p>
                  </div>
                  {formData.emails.map((email, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <div className="relative flex-1">
                        <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                        <input 
                          type="email"
                          className="w-full pl-12 pr-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 placeholder:text-slate-400 outline-none focus:border-[#391694] transition-all font-medium"
                          placeholder="email@exemplo.com"
                          value={email}
                          onChange={(e) => {
                            const newEmails = [...formData.emails];
                            newEmails[index] = e.target.value;
                            setFormData({...formData, emails: newEmails});
                          }}
                        />
                      </div>
                      {formData.emails.length > 1 && (
                        <button
                          type="button"
                          onClick={() => {
                            const newEmails = formData.emails.filter((_, i) => i !== index);
                            setFormData({...formData, emails: newEmails});
                          }}
                          className="p-4 bg-white border border-slate-200 text-red-500 hover:bg-red-50 hover:border-red-200 transition-colors"
                          title="Remover e-mail"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={() => setFormData({...formData, emails: [...formData.emails, '']})}
                    className="flex items-center gap-2 text-[13px] font-bold text-[#391694] hover:text-[#2a106e] transition-colors mt-2"
                  >
                    <PlusCircle className="w-4 h-4" />
                    Adicionar outro e-mail
                  </button>
                </div>

                <div className="h-px bg-slate-200 my-8"></div>

                {/* Anexos */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Anexos</label>
                  <div className="border-2 border-dashed border-slate-300 rounded-none p-8 flex flex-col items-center justify-center bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer group">
                    <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-sm mb-3 group-hover:scale-110 transition-transform">
                      <UploadCloud className="w-6 h-6 text-slate-400 group-hover:text-[#391694] transition-colors" />
                    </div>
                    <p className="text-[13px] font-bold text-slate-700">Clique para anexar ou arraste os arquivos</p>
                    <p className="text-xs text-slate-500 mt-1">PDF, JPG, PNG (Max. 10MB)</p>
                  </div>
                </div>

                <div className="flex justify-end pt-4">
                  <button
                    type="submit"
                    className="flex items-center gap-3 bg-black text-white px-10 py-4 rounded-none font-bold shadow-lg hover:scale-105 transition-all group"
                  >
                    <span>Finalizar AVOP</span>
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              </form>
            )}
          </div>
        ) : (
          <div className="flex flex-col min-h-0 animate-in fade-in duration-500 w-full space-y-6">
            {/* Filter Bar */}
            <div className="flex items-center gap-4 bg-slate-50 p-4 rounded-none border border-slate-200 mb-[26px] shrink-0">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input 
                  type="text" 
                  placeholder="Buscar por aeroporto ou detalhamento..." 
                  className="w-full pl-11 pr-4 py-2.5 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all font-medium"
                />
              </div>
              
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-slate-400" />
                  <input 
                    type="date" 
                    className="px-4 py-2.5 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all font-medium"
                  />
                  <span className="text-slate-400 text-xs font-bold">ATÉ</span>
                  <input 
                    type="date" 
                    className="px-4 py-2.5 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-black transition-all font-medium"
                  />
                </div>

                <button className="bg-[#391694] text-white px-8 py-2.5 rounded-none text-[13px] font-bold flex items-center justify-center gap-2 hover:bg-[#2a0f70] transition-colors">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  Exportar
                </button>
              </div>
            </div>

            {/* Table */}
            <div className="bg-white border border-slate-200 rounded-none shadow-sm relative w-full">
              <table className="w-full text-center border-separate border-spacing-0 table-fixed">
                <thead>
                  <tr className="bg-slate-50">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 w-1/5 text-center">Período</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 w-1/5 text-center">Aeroporto</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 w-2/5 text-center">Situação</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 w-1/5 text-center">Status</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 w-24 text-center">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {records.map((record, index) => (
                    <tr key={record.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 text-center">
 <div className="flex flex-col gap-1 justify-center items-center">
 <div className="flex items-center gap-2 justify-center">
 <span className="text-[10px] font-bold text-emerald-600 w-6 text-right">INI:</span> 
 <span className="text-xs font-semibold text-slate-700">{record.dataInicio.split('-').reverse().join('/')}</span>
 <span className="text-[10px] text-slate-500 font-medium">{record.horaInicio}</span>
 </div>
 <div className="flex items-center gap-2 justify-center">
 <span className="text-[10px] font-bold text-red-600 w-6 text-right">FIM:</span> 
 <span className="text-xs font-semibold text-slate-700">{record.dataTermino.split('-').reverse().join('/')}</span>
 <span className="text-[10px] text-slate-500 font-medium">{record.horaTermino}</span>
 </div>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="text-xs text-slate-700 font-medium">
 {record.aeroporto}
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="text-xs text-slate-700 truncate max-w-[200px] mx-auto">
 {record.detalhamento}
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 {record.status === 'Encerrado' ? (
 <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-sm inline-flex items-center gap-1 justify-center">
 <CheckCircle2 className="w-3 h-3" />
 ENCERRADO
 </span>
 ) : (
 <span className="bg-blue-100 text-blue-800 text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-sm inline-flex items-center gap-1 justify-center">
 <Clock className="w-3 h-3" />
 ATIVO
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
 index >= records.length - 2 && records.length > 2 ? 'bottom-full mb-1 slide-in-from-bottom-2' : 'top-full mt-1 slide-in-from-top-2'
 }`}
 >
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
 onClick={async (e) => {
 e.stopPropagation();
 await generatePDF(record);
 }}
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"
 >
 <Download className="w-3.5 h-3.5" /> Baixar PDF
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
                  {records.length === 0 && (
                     <tr>
                        <td colSpan={5} className="py-12 text-center text-slate-400">
 <div className="flex flex-col items-center justify-center gap-2">
 <Search className="w-8 h-8 opacity-20" />
 <span className="text-sm font-medium">Nenhum registro encontrado</span>
 </div>
 </td>
                     </tr>
                  )}
                </tbody>
              </table>
              <div className="bg-slate-50 px-6 py-3 border-t border-slate-200">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{records.length} REGISTROS ENCONTRADOS</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white max-w-md w-full mx-4 rounded-none shadow-2xl border border-slate-200 animate-in zoom-in-95 duration-200">
            <div className="p-6">
              <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center mb-4">
                <AlertTriangle className="w-6 h-6 text-amber-600" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Confirmação de Recebimento</h3>
              <p className="text-[13px] text-slate-600 leading-relaxed mb-6">
                O Aviso Operacional será enviado automaticamente para o XNG. <strong>É obrigatório confirmar com o XNG se eles receberam este AVOP.</strong>
                <br/><br/>
                Deseja prosseguir com o envio?
              </p>
              <div className="flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowConfirmModal(false)}
                  className="px-5 py-2.5 text-[13px] font-bold text-slate-600 hover:bg-slate-100 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="button"
                  onClick={handleConfirmSubmit}
                  className="px-5 py-2.5 text-[13px] font-bold bg-[#391694] text-white hover:bg-[#2a106e] transition-colors flex items-center gap-2"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  Confirmar e Enviar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
