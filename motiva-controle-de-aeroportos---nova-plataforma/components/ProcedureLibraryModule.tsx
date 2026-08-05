
import React, { useState, useMemo, useEffect } from 'react';
import { 
  Search, 
  BookOpen, 
  Video, 
  Share2, 
  HelpCircle, 
  Paperclip, 
  ChevronRight, 
  FileText, 
  PlayCircle,
  Download,
  Clock,
  Tag,
  ArrowLeft,
  Layout,
  AlertCircle,
  Filter,
  ChevronDown,
  ChevronUp,
  ChevronsDown,
  ChevronsUp,
  LayoutGrid,
  List as ListIcon,
  AlertTriangle,
  ArrowDown,
  ExternalLink,
  ShieldCheck
} from 'lucide-react';

// --- Types ---

type ContentType = 'text' | 'video' | 'flowchart' | 'faq' | 'files';
type ViewMode = 'grid' | 'list';

interface FAQItem {
  question: string;
  answer: string;
}

interface FileItem {
  name: string;
  type: 'PDF' | 'DOCX' | 'XLSX' | 'IMG';
  size: string;
}

interface ProcedureStep {
  id: number;
  text: string;
  isCritical: boolean;
  description?: string;
}

interface Procedure {
  id: string;
  code: string;
  title: string;
  area: string; // e.g., 'Operações', 'Manutenção'
  updatedAt: string;
  version: string;
  description: string;
  content: {
    text: React.ReactNode;
    videoUrl?: string;
    steps: ProcedureStep[];
    faq: FAQItem[];
    files: FileItem[];
  };
}

// --- Helper for Mock Content (Not used for text anymore, but kept for structure if needed) ---
const GenericContent = ({ title, code }: { title: string, code: string }) => (
  <div className="space-y-8 text-slate-700 leading-relaxed max-w-4xl">
    {/* Content replaced by compliance view */}
  </div>
);

// --- Standard Flowchart Steps Generator ---
const getStandardSteps = (title: string): ProcedureStep[] => [
  { id: 1, text: 'Início do Procedimento', isCritical: false },
  { id: 2, text: 'Verificação de EPIs e Equipamentos', isCritical: false },
  { id: 3, text: 'Comunicação com COA/Torre', isCritical: true, description: 'Obter autorização prévia' },
  { id: 4, text: `Execução de: ${title}`, isCritical: false },
  { id: 5, text: 'Verificação Final', isCritical: false },
  { id: 6, text: 'Registro em Log Operacional', isCritical: false },
  { id: 7, text: 'Fim', isCritical: false },
];

// --- Mock Data ---

const PROCEDURES: Procedure[] = [
  {
    id: 'p1',
    code: 'OPER.P0001',
    title: 'Comunicação: Operação de Rádios, Fraseologia Aeronáutica e Indicativos de Chamada',
    area: 'Operações',
    updatedAt: '10/05/2024',
    version: '1.0',
    description: 'Estabelece os padrões de comunicação via rádio, fraseologia padrão e uso correto de indicativos.',
    content: { 
      text: null, 
      faq: [
        {
          question: "Qual a frequência de contingência em caso de falha do rádio principal?",
          answer: "Em caso de falha do rádio principal, deve-se utilizar o rádio de backup sintonizado na frequência da Torre (TWR) ou Solo (GND) conforme a posição. Se ambos falharem, observar os sinais luminosos da TWR."
        },
        {
          question: "É permitido o uso de gírias ou linguagem informal na frequência?",
          answer: "Não. O uso de fraseologia padrão é obrigatório para garantir a clareza e evitar mal-entendidos que possam comprometer a segurança operacional."
        },
        {
          question: "Como proceder se não houver confirmação (readback) da torre?",
          answer: "Se não houver colação (readback) ou confirmação da instrução por parte do controlador, o operador não deve executar a ação e deve chamar novamente o órgão para confirmar a instrução."
        }
      ], 
      files: [
        { name: 'Formulário', type: 'PDF', size: '450 KB' },
        { name: 'Mapa de Grade', type: 'PDF', size: '1.2 MB' }
      ],
      steps: [
        { id: 1, text: 'Verificar Frequência Livre', isCritical: false, description: 'Escutar antes de falar' },
        { id: 2, text: 'Ajustar Rádio (Volume/Squelch)', isCritical: false },
        { id: 3, text: 'Planejar a Mensagem', isCritical: false },
        { id: 4, text: 'Acionar PTT e Transmitir', isCritical: false },
        { id: 5, text: 'Aguardar Colação (Readback)', isCritical: true, description: 'Confirmação obrigatória de instruções' },
        { id: 6, text: 'Confirmar ou Corrigir', isCritical: false },
      ]
    }
  },
  {
    id: 'p2',
    code: 'OPER.P0002',
    title: 'Divulgação de Informações Aeronáuticas (AIP Brasil, AVOP, NOTAM e ROTAER)',
    area: 'Operações',
    updatedAt: '12/05/2024',
    version: '2.0',
    description: 'Processo de gestão e divulgação de publicações aeronáuticas e avisos operacionais.',
    content: { 
      text: null, 
      faq: [], 
      files: [],
      steps: getStandardSteps('Divulgação AIS')
    }
  },
  {
    id: 'p3',
    code: 'OPER.P0003',
    title: 'Monitoramento e Reporte de Descumprimento de Informações Aeronáuticas',
    area: 'Operações',
    updatedAt: '15/05/2024',
    version: '1.0',
    description: 'Sistemática para identificar e reportar desvios em relação às normas publicadas.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Reporte de Desvio') }
  },
  {
    id: 'p4',
    code: 'OPER.P0004',
    title: 'Análise de Objetos Projetados no Espaço Aéreo (OPEA)',
    area: 'Operações',
    updatedAt: '02/04/2024',
    version: '3.0',
    description: 'Procedimentos para análise e autorização de obstáculos que possam afetar a segurança de voo.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Análise de Obstáculo') }
  },
  {
    id: 'p5',
    code: 'OPER.P0005',
    title: 'Controle de Sobrecarga do Pavimento (PCR-ACR)',
    area: 'Operações',
    updatedAt: '20/05/2024',
    version: '2.0',
    description: 'Monitoramento do ACN/PCN e controle de operações de aeronaves com sobrepeso.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Cálculo ACN/PCN') }
  },
  {
    id: 'p6',
    code: 'OPER.P0006',
    title: 'Aviso de Aeródromo (Meteorologia)',
    area: 'Operações',
    updatedAt: '18/05/2024',
    version: '2.0',
    description: 'Emissão e disseminação de alertas meteorológicos que impactam a operação.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Emissão de Alerta') }
  },
  {
    id: 'p7',
    code: 'OPER.P0007',
    title: 'Teste de motor(es) por aeronaves',
    area: 'Operações',
    updatedAt: '10/03/2024',
    version: '1.0',
    description: 'Regras e locais designados para realização de giros de motor em solo.',
    content: { 
      text: null, 
      faq: [], 
      files: [], 
      steps: [
        { id: 1, text: 'Recebimento da Solicitação', isCritical: false },
        { id: 2, text: 'Verificar Disponibilidade do Box de Teste', isCritical: false },
        { id: 3, text: 'Inspecionar Área (FOD)', isCritical: true, description: 'Risco de ingestão' },
        { id: 4, text: 'Posicionar Aeronave', isCritical: false },
        { id: 5, text: 'Monitorar Teste', isCritical: false },
        { id: 6, text: 'Liberar Área', isCritical: false }
      ]
    }
  },
  {
    id: 'p8',
    code: 'OPER.P0008',
    title: 'Vazamentos em Área Operacional',
    area: 'Operações',
    updatedAt: '22/05/2024',
    version: '4.0',
    description: 'Protocolo de resposta, contenção e limpeza de vazamentos de fluidos em área de manobra.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Contenção de Vazamento') }
  },
  {
    id: 'p9',
    code: 'OPER.P0009',
    title: 'Operação de Ambulift',
    area: 'Operações',
    updatedAt: '05/01/2024',
    version: '1.0',
    description: 'Procedimentos de segurança para operação de veículos de embarque de PMR.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Acoplagem Ambulift') }
  },
  {
    id: 'p10',
    code: 'OPER.P0010',
    title: 'Operação de Pontes de Embarque e Conectores',
    area: 'Operações',
    updatedAt: '14/02/2024',
    version: '2.0',
    description: 'Diretrizes para acoplagem, operação e desacoplagem de pontes de embarque.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Operação de Ponte') }
  },
  {
    id: 'p11',
    code: 'OPER.P0011',
    title: 'Vistoria de Veículos e Equipamentos',
    area: 'Operações',
    updatedAt: '30/04/2024',
    version: '1.0',
    description: 'Checklist e critérios para autorização de veículos na área restrita.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Checklist Veicular') }
  },
  {
    id: 'p12',
    code: 'OPER.P0012',
    title: 'Condução de Veículos, Comboios e “Follow-Me” em Área Operacional',
    area: 'Operações',
    updatedAt: '12/05/2024',
    version: '3.0',
    description: 'Regras de trânsito, limites de velocidade e procedimentos de escolta.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Comboio Follow-me') }
  },
  {
    id: 'p13',
    code: 'OPER.P0013',
    title: 'Sinalização e Orientação de Aeronaves na Área Operacional',
    area: 'Operações',
    updatedAt: '28/02/2024',
    version: '1.0',
    description: 'Procedimentos de balizamento (Marshalling) e orientação de aeronaves nos pátios.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Balizamento') }
  },
  {
    id: 'p14',
    code: 'OPER.P0014',
    title: 'Sistema de Advertência (Pontuação)',
    area: 'Operações',
    updatedAt: '15/01/2024',
    version: '2.0',
    description: 'Regulamento de infrações e sistema de pontuação para condutores e pedestres.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Aplicação de Notificação') }
  },
  {
    id: 'p15',
    code: 'OPER.P0015',
    title: 'Atendimento e Supervisão das Operações nos Pátios',
    area: 'Operações',
    updatedAt: '10/05/2024',
    version: '2.0',
    description: 'Rotinas de fiscalização e acompanhamento do turnaround das aeronaves.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Giro de Pátio') }
  },
  {
    id: 'p16',
    code: 'OPER.P0016',
    title: 'Intervenção Inicial e Combate à Incêndio',
    area: 'Operações',
    updatedAt: '01/03/2024',
    version: '3.0',
    description: 'Ações imediatas em caso de princípio de incêndio antes da chegada do SCI.',
    content: { 
      text: null, 
      faq: [], 
      files: [], 
      steps: [
        { id: 1, text: 'Identificar Fogo/Fumaça', isCritical: false },
        { id: 2, text: 'Acionar Bombeiros (SCI)', isCritical: true, description: 'Prioridade absoluta' },
        { id: 3, text: 'Avaliar Risco Pessoal', isCritical: false },
        { id: 4, text: 'Utilizar Extintor (se seguro)', isCritical: false },
        { id: 5, text: 'Evacuar Área', isCritical: false },
        { id: 6, text: 'Aguardar SCI', isCritical: false }
      ]
    }
  },
  {
    id: 'p17',
    code: 'OPER.P0017',
    title: 'Embarque e Desembarque Híbrido',
    area: 'Operações',
    updatedAt: '20/04/2024',
    version: '1.0',
    description: 'Procedimentos para operações simultâneas de ponte e remota.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Coordenação de Embarque') }
  },
  {
    id: 'p18',
    code: 'OPER.P0018',
    title: 'Centro de Operações Aeroportuárias (APOC)',
    area: 'Operações',
    updatedAt: '15/05/2024',
    version: '3.0',
    description: 'Atribuições, fluxo de informações e tomada de decisão do APOC.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Gestão de Crise') }
  },
  {
    id: 'p19',
    code: 'OPER.P0019',
    title: 'Inspeção do Sistema de Pistas (RWY e TWY)',
    area: 'Operações',
    updatedAt: '25/05/2024',
    version: '4.0',
    description: 'Metodologia para inspeção de pistas, identificação de falhas e reporte.',
    content: { 
      text: null, 
      faq: [], 
      files: [], 
      steps: [
        { id: 1, text: 'Solicitar Acesso à TWR', isCritical: true, description: 'Entrada na Pista' },
        { id: 2, text: 'Ingressar na Pista', isCritical: false },
        { id: 3, text: 'Inspecionar Cabeceira', isCritical: false },
        { id: 4, text: 'Percorrer Faixa Central', isCritical: false },
        { id: 5, text: 'Verificar Luzes e Pintura', isCritical: false },
        { id: 6, text: 'Reportar "Pista Livre"', isCritical: true, description: 'Liberação para pousos' }
      ]
    }
  },
  {
    id: 'p20',
    code: 'OPER.P0020',
    title: 'Inspeção dos Pátios',
    area: 'Operações',
    updatedAt: '25/05/2024',
    version: '3.0',
    description: 'Rotina de verificação de condições operacionais dos pátios de estacionamento.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Varredura de Pátio') }
  },
  {
    id: 'p21',
    code: 'OPER.P0021',
    title: 'Inspeção da Faixa Preparada e Faixa de Pista',
    area: 'Operações',
    updatedAt: '20/02/2024',
    version: '1.0',
    description: 'Verificação das áreas de segurança laterais às pistas de pouso e decolagem.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Inspeção de Faixa') }
  },
  {
    id: 'p22',
    code: 'OPER.P0022',
    title: 'Inspeção da Zona de Proteção do Aeródromo (ZPA) e Identificação de Obstáculos',
    area: 'Operações',
    updatedAt: '10/01/2024',
    version: '2.0',
    description: 'Monitoramento de obstáculos no entorno e violações das superfícies limitadoras.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Monitoramento de Obstáculos') }
  },
  {
    id: 'p23',
    code: 'OPER.P0023',
    title: 'Medição da Lâmina de Água na Pista de Pouso e Decolagem (RwyCC)',
    area: 'Operações',
    updatedAt: '15/04/2024',
    version: '2.0',
    description: 'Procedimentos para reporte de condição de pista (GRF) em dias de chuva.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Medição GRF') }
  },
  {
    id: 'p24',
    code: 'OPER.P0024',
    title: 'Operação em Baixa Visibilidade',
    area: 'Operações',
    updatedAt: '30/03/2024',
    version: '2.0',
    description: 'Procedimentos específicos (LVP) para operação sob condições de neblina ou baixa visibilidade.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Ativação LVP') }
  },
  {
    id: 'p25',
    code: 'OPER.P0025',
    title: 'Monitoramento do Desempenho das Operações',
    area: 'Operações',
    updatedAt: '01/05/2024',
    version: '1.0',
    description: 'Indicadores de performance (KPIs) e análise de eficiência operacional.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Coleta de KPIs') }
  },
  {
    id: 'p26',
    code: 'OPER.P0026',
    title: 'Operações de Aeronaves Internacionais',
    area: 'Operações',
    updatedAt: '10/02/2024',
    version: '1.0',
    description: 'Fluxos específicos para atendimento de voos internacionais.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Recepção Internacional') }
  },
  {
    id: 'p27',
    code: 'OPER.P0027',
    title: 'Operações em Contingência',
    area: 'Operações',
    updatedAt: '15/12/2023',
    version: '3.0',
    description: 'Planos de ação para situações de falha de equipamentos ou sistemas críticos.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Ativação de Contingência') }
  },
  {
    id: 'p28',
    code: 'OPER.P0028',
    title: 'Briefing Operacional Diário',
    area: 'Operações',
    updatedAt: '01/05/2024',
    version: '1.0',
    description: 'Sistemática de passagem de serviço e briefings de turno.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Passagem de Serviço') }
  },
  {
    id: 'p29',
    code: 'OPER.P0029',
    title: 'Solicitação de Obras ou Manutenção',
    area: 'Operações',
    updatedAt: '20/05/2024',
    version: '2.0',
    description: 'Fluxo para abertura de ordens de serviço e intervenções na área operacional.',
    content: { text: null, faq: [], files: [], steps: getStandardSteps('Abertura de OS') }
  }
];

// --- Main Component ---

export const ProcedureLibraryModule: React.FC = () => {
  const [activeProcedureId, setActiveProcedureId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<ContentType>('text');
  const [searchQuery, setSearchQuery] = useState('');
  const [collapsedCategories, setCollapsedCategories] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  
  const categories = ['Operações', 'Segurança (AVSEC)', 'Manutenção', 'SGSO'];

  // Filter Logic
  const filteredProcedures = useMemo(() => {
    return PROCEDURES.filter(proc => 
      proc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      proc.code.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [searchQuery]);

  // Group by Area
  const groupedProcedures = useMemo(() => {
    const groups: Record<string, Procedure[]> = {};
    filteredProcedures.forEach(proc => {
      if (!groups[proc.area]) groups[proc.area] = [];
      groups[proc.area].push(proc);
    });
    return groups;
  }, [filteredProcedures]);

  // Auto-expand categories if searching
  useEffect(() => {
    if (searchQuery) {
      setCollapsedCategories([]);
    }
  }, [searchQuery]);

  const toggleCategory = (category: string) => {
    setCollapsedCategories(prev => 
      prev.includes(category) 
        ? prev.filter(c => c !== category) 
        : [...prev, category]
    );
  };

  const expandAll = () => setCollapsedCategories([]);
  const collapseAll = () => setCollapsedCategories(categories);

  const activeProcedure = PROCEDURES.find(p => p.id === activeProcedureId);

  // --- View: Detail (Active Procedure) ---
  if (activeProcedure) {
    return (
      <div className="flex flex-col h-full bg-white animate-in slide-in-from-right-4 duration-300">
        {/* Detail Header */}
        <div className="bg-white border-b border-slate-200 sticky top-0 z-20 shadow-sm">
          <div className="max-w-7xl mx-auto w-full px-8 py-6">
            <button 
              onClick={() => { setActiveProcedureId(null); setActiveTab('text'); }}
              className="flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-[#391694] mb-4 uppercase tracking-wider transition-colors group"
            >
              <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
              Voltar para Biblioteca
            </button>
            
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
              <div>
                <div className="flex items-center gap-3 mb-3">
                  <span className="px-2 py-1 bg-indigo-50 text-[#391694] text-[10px] font-black uppercase tracking-widest border border-indigo-100">
                    {activeProcedure.area}
                  </span>
                  <span className="text-[11px] font-bold text-white uppercase tracking-widest bg-[#7E17A0] px-2 py-1 border border-[#7E17A0] rounded-sm">
                    {activeProcedure.code}
                  </span>
                </div>
                <h1 className="text-3xl font-bold text-slate-900 leading-tight mb-3">
                  {activeProcedure.title}
                </h1>
                <p className="text-slate-500 text-base max-w-3xl leading-relaxed">
                  {activeProcedure.description}
                </p>
              </div>

              <div className="flex flex-row md:flex-col items-center md:items-end gap-3 shrink-0">
                <div className="text-right">
                  <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">Versão Atual</span>
                  <span className="block text-lg font-bold text-slate-800">{activeProcedure.version}</span>
                </div>
                <div className="w-px h-8 bg-slate-200 md:w-full md:h-px"></div>
                <div className="text-right">
                  <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">Última Revisão</span>
                  <span className="block text-lg font-bold text-slate-800">{activeProcedure.updatedAt}</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Tabs */}
          <div className="bg-slate-50 border-t border-slate-200 w-full">
            <div className="max-w-7xl mx-auto w-full px-8 flex gap-8 overflow-x-auto">
              <TabButton 
                active={activeTab === 'text'} 
                onClick={() => setActiveTab('text')} 
                icon={FileText} 
                label="Procedimento" 
              />
              <TabButton 
                active={activeTab === 'video'} 
                onClick={() => setActiveTab('video')} 
                icon={Video} 
                label="Procedimento em Vídeo" 
              />
              <TabButton 
                active={activeTab === 'flowchart'} 
                onClick={() => setActiveTab('flowchart')} 
                icon={Share2} 
                label="Fluxograma" 
              />
              <TabButton 
                active={activeTab === 'faq'} 
                onClick={() => setActiveTab('faq')} 
                icon={HelpCircle} 
                label="Perguntas Frequentes" 
              />
              <TabButton 
                active={activeTab === 'files'} 
                onClick={() => setActiveTab('files')} 
                icon={Paperclip} 
                label="Arquivos / Anexos" 
              />
            </div>
          </div>
        </div>

        {/* Detail Content */}
        <div className="flex-1 overflow-y-auto bg-slate-50/50">
          <div className="max-w-7xl mx-auto w-full p-8">
            <div className="bg-white border border-slate-200 p-10 shadow-sm min-h-[600px]">
               {/* Text Content (Compliance View) */}
                {activeTab === 'text' && (
                  <div className="animate-in fade-in duration-300 flex flex-col items-center justify-center h-full min-h-[400px]">
                    <div className="bg-slate-50 border border-slate-100 p-10 max-w-2xl text-center">
                      <div className="w-16 h-16 bg-[#391694] rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg shadow-indigo-900/20">
                        <ShieldCheck className="w-8 h-8 text-white" />
                      </div>
                      <h3 className="text-2xl font-bold text-slate-900 mb-3">Conteúdo Protegido</h3>
                      <p className="text-slate-500 leading-relaxed mb-8">
                        Por determinação do Departamento de Qualidade e Compliance, o texto integral deste Procedimento Operacional Padrão (POP) deve ser acessado exclusivamente através do portal oficial de documentação da empresa, garantindo o controle de versão e rastreabilidade de leitura.
                      </p>
                      
                      <button className="flex items-center justify-center gap-2 bg-[#391694] hover:bg-[#2a106e] text-white px-8 py-4 rounded-none font-bold shadow-md transition-all mx-auto group">
                        <span>Acessar Portal da Qualidade</span>
                        <ExternalLink className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                      </button>
                      
                      <p className="text-[10px] text-slate-400 mt-6 uppercase tracking-widest font-bold">
                        Redirecionamento Seguro • DocuShare Enterprise
                      </p>
                    </div>
                  </div>
                )}

                {/* Video Content */}
                {activeTab === 'video' && (
                  <div className="animate-in fade-in duration-300 flex flex-col items-center justify-center h-full min-h-[400px]">
                    {activeProcedure.content.videoUrl ? (
                      <div className="w-full max-w-4xl aspect-video bg-slate-900 flex items-center justify-center text-white shadow-2xl">
                        {/* Placeholder for iframe */}
                        <div className="text-center">
                          <PlayCircle className="w-20 h-20 mx-auto mb-6 opacity-80 hover:scale-110 transition-transform cursor-pointer" />
                          <p className="font-bold text-xl">Vídeo Aula: {activeProcedure.code}</p>
                          <p className="text-sm opacity-60 mt-2">Duração estimada: 15 min</p>
                        </div>
                      </div>
                    ) : (
                      <EmptyState icon={Video} message="Este procedimento não possui vídeo aula disponível." />
                    )}
                  </div>
                )}

                {/* Flowchart Content - DYNAMIC RENDER */}
                {activeTab === 'flowchart' && (
                  <div className="animate-in fade-in duration-300 flex flex-col items-center w-full max-w-3xl mx-auto py-8">
                    {activeProcedure.content.steps.map((step, index) => (
                      <div key={step.id} className="flex flex-col items-center w-full">
                        {/* Box */}
                        <div 
                          className={`
                            relative z-10 w-full md:w-96 p-5 border-2 text-center shadow-sm transition-all duration-300
                            ${step.isCritical 
                              ? 'bg-red-50 border-red-500 shadow-red-100 hover:shadow-md' 
                              : 'bg-white border-slate-200 hover:border-[#391694] hover:shadow-md'
                            }
                          `}
                        >
                          {step.isCritical && (
                            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-red-600 text-white px-3 py-0.5 text-[10px] font-bold uppercase tracking-widest rounded-full flex items-center gap-1 shadow-sm">
                              <AlertTriangle className="w-3 h-3" /> Crítico
                            </div>
                          )}
                          <span className={`block text-xs font-bold uppercase tracking-widest mb-2 ${step.isCritical ? 'text-red-400' : 'text-slate-400'}`}>Etapa {step.id}</span>
                          <h4 className={`text-base font-bold leading-tight ${step.isCritical ? 'text-red-900' : 'text-slate-800'}`}>
                            {step.text}
                          </h4>
                          {step.description && (
                            <p className={`text-xs mt-2 font-medium ${step.isCritical ? 'text-red-700' : 'text-slate-500'}`}>
                              {step.description}
                            </p>
                          )}
                        </div>

                        {/* Connector Line (except for last item) */}
                        {index < activeProcedure.content.steps.length - 1 && (
                          <div className="h-10 w-0.5 bg-slate-300 my-1 relative">
                             <ArrowDown className="w-4 h-4 text-slate-300 absolute -bottom-2.5 -left-[7px]" />
                          </div>
                        )}
                      </div>
                    ))}
                    
                    {/* End Node */}
                    <div className="h-10 w-0.5 bg-slate-300 my-1 relative"></div>
                    <div className="w-4 h-4 bg-slate-300 rounded-full"></div>
                  </div>
                )}

                {/* FAQ Content */}
                {activeTab === 'faq' && (
                  <div className="animate-in fade-in duration-300 space-y-4 max-w-4xl mx-auto">
                    {activeProcedure.content.faq.length > 0 ? (
                      activeProcedure.content.faq.map((item, idx) => (
                        <div key={idx} className="border border-slate-200 bg-slate-50 p-6 hover:border-[#391694] transition-colors group">
                          <h4 className="font-bold text-slate-900 mb-3 flex gap-3 items-start">
                            <HelpCircle className="w-5 h-5 text-[#391694] shrink-0 mt-0.5" />
                            {item.question}
                          </h4>
                          <p className="text-slate-600 pl-8 text-base leading-relaxed">
                            {item.answer}
                          </p>
                        </div>
                      ))
                    ) : (
                      <EmptyState icon={HelpCircle} message="Não há perguntas frequentes cadastradas." />
                    )}
                  </div>
                )}

                {/* Files Content */}
                {activeTab === 'files' && (
                  <div className="animate-in fade-in duration-300">
                    {activeProcedure.content.files.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {activeProcedure.content.files.map((file, idx) => (
                          <div key={idx} className="flex flex-col p-6 border border-slate-200 hover:border-[#391694] hover:shadow-lg transition-all group cursor-pointer bg-slate-50 h-full justify-between">
                            <div className="mb-4">
                              <div className="w-12 h-12 bg-white border border-slate-200 flex items-center justify-center shrink-0 mb-4 shadow-sm">
                                <span className="text-xs font-black uppercase text-slate-500">{file.type}</span>
                              </div>
                              <p className="text-base font-bold text-slate-800 group-hover:text-[#391694] mb-1 leading-tight">{file.name}</p>
                              <p className="text-xs text-slate-400">{file.size}</p>
                            </div>
                            <button className="flex items-center gap-2 text-xs font-bold text-slate-500 group-hover:text-[#391694] uppercase tracking-wider mt-auto pt-4 border-t border-slate-200">
                              <Download className="w-4 h-4" />
                              Baixar Arquivo
                            </button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <EmptyState icon={Paperclip} message="Não há arquivos complementares anexados." />
                    )}
                  </div>
                )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // --- View: List (Dashboard) ---
  return (
    <div className="flex flex-col h-full bg-slate-50/50">
      
      {/* Header Area */}
      <div className="bg-white border-b border-slate-200 px-8 py-10">
        <div className="max-w-7xl mx-auto w-full">
          <div className="flex flex-col md:flex-row justify-between items-end gap-6 mb-8">
            <div>
              <h2 className="text-3xl font-bold text-slate-800 tracking-tight flex items-center gap-3 mb-2">
                <BookOpen className="w-8 h-8 text-[#391694]" />
                Biblioteca de Procedimentos
              </h2>
              <p className="text-slate-500 text-lg max-w-2xl">
                Acesse a base de conhecimento operacional, manuais, procedimentos (POPs) e instruções de trabalho atualizadas.
              </p>
            </div>
             <div className="text-right hidden md:block">
                <p className="text-3xl font-bold text-slate-800">{PROCEDURES.length}</p>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Documentos Totais</p>
             </div>
          </div>

          <div className="flex flex-col gap-4">
            <div className="relative max-w-2xl">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input 
                type="text" 
                placeholder="Pesquisar por título, código ou palavra-chave..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-4 bg-white border-2 border-slate-200 rounded-none text-base outline-none focus:border-[#391694] transition-all shadow-sm placeholder:text-slate-400"
              />
            </div>

            {/* Toolbar: View Toggle & Expand/Collapse */}
            <div className="flex flex-wrap items-center justify-between gap-4 border-t border-slate-100 pt-4">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-none">
                  <button 
                    onClick={() => setViewMode('grid')}
                    className={`p-1.5 transition-all ${viewMode === 'grid' ? 'bg-white shadow-sm text-[#391694]' : 'text-slate-400 hover:text-slate-600'}`}
                    title="Visualização em Grade"
                  >
                    <LayoutGrid className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => setViewMode('list')}
                    className={`p-1.5 transition-all ${viewMode === 'list' ? 'bg-white shadow-sm text-[#391694]' : 'text-slate-400 hover:text-slate-600'}`}
                    title="Visualização em Lista Compacta"
                  >
                    <ListIcon className="w-4 h-4" />
                  </button>
                </div>
                <div className="h-4 w-px bg-slate-200"></div>
                <div className="flex gap-2">
                  <button onClick={expandAll} className="text-[10px] font-bold text-slate-500 hover:text-[#391694] uppercase tracking-wider flex items-center gap-1">
                    <ChevronsDown className="w-3 h-3" /> Expandir Tudo
                  </button>
                  <button onClick={collapseAll} className="text-[10px] font-bold text-slate-500 hover:text-[#391694] uppercase tracking-wider flex items-center gap-1 ml-2">
                    <ChevronsUp className="w-3 h-3" /> Recolher Tudo
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-7xl mx-auto w-full space-y-8">
          
          {categories.map((category) => {
            const categoryProcedures = groupedProcedures[category] || [];
            const isCollapsed = collapsedCategories.includes(category);
            
            // If searching and no results in this category, hide it
            if (searchQuery && categoryProcedures.length === 0) return null;

            return (
              <section key={category} className="animate-in fade-in slide-in-from-bottom-4 duration-500 bg-white border border-slate-200 shadow-sm">
                
                {/* Category Header (Collapsible Trigger) */}
                <button 
                  onClick={() => toggleCategory(category)}
                  className="w-full flex items-center justify-between p-5 bg-slate-50/50 hover:bg-slate-100 transition-colors border-b border-slate-100 text-left group"
                >
                  <div className="flex items-center gap-4">
                     {isCollapsed ? <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-[#391694]" /> : <ChevronDown className="w-5 h-5 text-[#391694]" />}
                     <div>
                       <h3 className="text-lg font-bold text-slate-800 uppercase tracking-wide group-hover:text-[#391694] transition-colors">{category}</h3>
                       {isCollapsed && (
                         <span className="text-xs text-slate-400 font-medium">{categoryProcedures.length} procedimentos ocultos</span>
                       )}
                     </div>
                  </div>
                  {!isCollapsed && (
                    <span className="text-xs font-bold text-slate-400 bg-white px-2 py-1 border border-slate-200 rounded-full">{categoryProcedures.length}</span>
                  )}
                </button>

                {!isCollapsed && (
                  <div className="p-6 bg-white">
                    {categoryProcedures.length > 0 ? (
                      viewMode === 'grid' ? (
                        // Grid View
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                          {categoryProcedures.map(proc => (
                            <div 
                              key={proc.id}
                              onClick={() => setActiveProcedureId(proc.id)}
                              className="group bg-white border border-slate-200 hover:border-[#391694] hover:shadow-xl transition-all cursor-pointer flex flex-col h-full relative overflow-hidden"
                            >
                              <div className="absolute top-0 left-0 w-1 h-full bg-slate-200 group-hover:bg-[#391694] transition-colors"></div>
                              
                              <div className="p-6 flex-1 flex flex-col">
                                  <div className="flex justify-between items-start mb-4">
                                    <span className="text-[10px] font-black uppercase text-white bg-[#7E17A0] px-2 py-1 tracking-wider rounded-sm">
                                        {proc.code}
                                    </span>
                                    <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-[#391694] group-hover:translate-x-1 transition-all" />
                                  </div>
                                  
                                  <h4 className="text-lg font-bold text-slate-800 mb-2 leading-snug group-hover:text-[#391694] transition-colors">
                                    {proc.title}
                                  </h4>
                                  <p className="text-sm text-slate-500 line-clamp-2 mb-4">
                                    {proc.description}
                                  </p>
                              </div>

                              <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400 group-hover:bg-[#F5F3FF] group-hover:text-indigo-900 transition-colors">
                                  <div className="flex items-center gap-1.5 font-bold">
                                    <span>v{proc.version}</span>
                                  </div>
                                  <div className="flex items-center gap-1.5 font-bold">
                                    <Clock className="w-3.5 h-3.5" />
                                    <span>{proc.updatedAt}</span>
                                  </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        // List View (Compact)
                        <div className="flex flex-col border border-slate-200">
                          {categoryProcedures.map((proc, idx) => (
                            <div 
                              key={proc.id}
                              onClick={() => setActiveProcedureId(proc.id)}
                              className={`flex items-center justify-between p-4 hover:bg-slate-50 cursor-pointer group transition-all ${idx !== categoryProcedures.length - 1 ? 'border-b border-slate-100' : ''}`}
                            >
                              <div className="flex items-center gap-6">
                                <span className="w-32 text-[11px] font-black uppercase text-white bg-[#7E17A0] px-2 py-1 text-center tracking-wider rounded-sm shrink-0">
                                  {proc.code}
                                </span>
                                <div>
                                  <h4 className="text-sm font-bold text-slate-800 group-hover:text-[#391694] transition-colors">{proc.title}</h4>
                                  <p className="text-xs text-slate-400 line-clamp-1 max-w-lg mt-0.5">{proc.description}</p>
                                </div>
                              </div>
                              <div className="flex items-center gap-6 text-xs text-slate-400 shrink-0">
                                <span className="flex items-center gap-1.5 w-20 font-bold">v{proc.version}</span>
                                <span className="flex items-center gap-1.5 w-24"><Clock className="w-3 h-3" /> {proc.updatedAt}</span>
                                <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-[#391694]" />
                              </div>
                            </div>
                          ))}
                        </div>
                      )
                    ) : (
                      <div className="p-8 border-2 border-dashed border-slate-200 rounded-none text-center bg-slate-50/50">
                        <p className="text-slate-400 font-medium text-sm">Nenhum procedimento disponível nesta categoria.</p>
                      </div>
                    )}
                  </div>
                )}
              </section>
            );
          })}
          
          {filteredProcedures.length === 0 && (
             <div className="flex flex-col items-center justify-center py-20 text-center">
                <Search className="w-12 h-12 text-slate-200 mb-4" />
                <h3 className="text-lg font-bold text-slate-800 mb-1">Nenhum resultado encontrado</h3>
                <p className="text-slate-500">Tente buscar por outros termos ou códigos.</p>
             </div>
          )}

        </div>
      </div>
    </div>
  );
};

// --- Subcomponents ---

const TabButton: React.FC<{ active: boolean; onClick: () => void; icon: any; label: string }> = ({ active, onClick, icon: Icon, label }) => (
  <button
    onClick={onClick}
    className={`group flex items-center gap-2 py-5 px-1 border-b-[3px] transition-all min-w-fit ${
      active 
        ? 'border-[#391694] text-[#391694]' 
        : 'border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300'
    }`}
  >
    <Icon className={`w-4 h-4 ${active ? 'text-[#391694]' : 'text-slate-400 group-hover:text-slate-600'}`} />
    <span className="text-sm font-bold uppercase tracking-wide">{label}</span>
  </button>
);

const EmptyState: React.FC<{ icon: any; message: string }> = ({ icon: Icon, message }) => (
  <div className="flex flex-col items-center justify-center py-20 text-slate-400">
    <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
      <Icon className="w-8 h-8 opacity-20" />
    </div>
    <p className="text-sm font-medium max-w-xs text-center">{message}</p>
  </div>
);
