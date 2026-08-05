import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  X, 
  Play, 
  Pause, 
  Volume2, 
  VolumeX, 
  RotateCcw, 
  HelpCircle, 
  Compass, 
  CheckCircle, 
  ListChecks, 
  MessageSquare, 
  Send,
  Sparkles,
  Info,
  Clock,
  PlayCircle
} from 'lucide-react';

interface ExplanationVideoModalProps {
  moduleId: string;
  moduleTitle: string;
  onClose: () => void;
}

interface Chapter {
  time: string;
  percent: number;
  text: string;
  subtitle: string;
  visualType: 'blueprint' | 'form' | 'security' | 'checklist' | 'map';
}

interface ModuleDetails {
  title: string;
  speaker: string;
  duration: string;
  summary: string;
  chapters: Chapter[];
  writtenSteps: string[];
}

const MODULES_TUTORIAL_DATA: Record<string, ModuleDetails> = {
  'insp-1': {
    title: 'Procedimentos de Inspeção de Pátios',
    speaker: 'Comandante Ricardo Souza (Supervisor de Operações)',
    duration: '02:30',
    summary: 'Aprenda os padrões normativos da ANAC (RBAC 139) para mapear e registrar anomalias de pátio, incluindo pavimentação rachada, trincas, vazamentos e falhas de demarcação horizontal.',
    chapters: [
      { time: '00:00', percent: 0, text: 'Introdução e Requisitos RBAC 139', subtitle: 'Olá! Bem-vindo ao treinamento de Inspeção de Pátios. Vamos ver como classificar os desvios de pavimento.', visualType: 'blueprint' },
      { time: '00:30', percent: 20, text: 'Classificação de Trincas no Pavimento', subtitle: 'Ao identificar trincas, meça a espessura e avalie se há potencial de desprendimento do concreto.', visualType: 'map' },
      { time: '01:05', percent: 43, text: 'Mapeamento de Falhas na Pintura', subtitle: 'Verifique se as faixas de pedestres transversais e as linhas guia de aeronave estão apagadas.', visualType: 'form' },
      { time: '01:45', percent: 70, text: 'Registro de Vazamentos e Oleosidades', subtitle: 'Vazamentos persistentes superiores a 1 metro devem ser registrados e contidos imediatamente.', visualType: 'security' },
      { time: '02:15', percent: 90, text: 'Validação e Envio da Vistoria', subtitle: 'Insira as fotos das não-conformidades e clique em "Registrar Inspeção" para notificar a manutenção.', visualType: 'checklist' }
    ],
    writtenSteps: [
      'Selecione a área do Pátio (Pátio 1, Pátio 2, ou Hangares) que está vistoriando.',
      'Analise a integridade do pavimento asfáltico ou placas de concreto.',
      'Compare a visibilidade das faixas de sinalização diurna com os critérios mínimos.',
      'Se houver detritos ou vazamento de óleo, tire o registro fotográfico.',
      'Conclua assinando digitalmente o formulário de conformidade.'
    ]
  },
  'insp-2': {
    title: 'Inspeção de Pista de Pouso e Pistas de Táxi',
    speaker: 'Eng. Marina Alencar (Gerente de Segurança Operacional)',
    duration: '03:00',
    summary: 'Instruções para vistoriar e registrar as condições operacionais da pista de decolagem (PPD) e taxiways, avaliando auxílios visuais e focos de desprendimento (FOD).',
    chapters: [
      { time: '00:00', percent: 0, text: 'Instruções de Escolta & Entrada na Pista', subtitle: 'É essencial garantir a autorização da Torre (TWR) antes de ingressar no eixo de pista física.', visualType: 'blueprint' },
      { time: '00:45', percent: 25, text: 'Verificação da Zona de Toque', subtitle: 'A zona de decolagem e pouso acumula alta borracha. Analise se o coeficiente de atrito está seguro.', visualType: 'map' },
      { time: '01:30', percent: 50, text: 'Sinalização Luminosa de Cabeceira', subtitle: 'Inspecione se há luzes queimadas ou desalinhadas no balizamento de cabeceira de pista.', visualType: 'security' },
      { time: '02:15', percent: 75, text: 'Identificação de Degraus Laterais', subtitle: 'Verifique se há diferença de altura entre a pista asfáltica e o acostamento de terra batida.', visualType: 'form' },
      { time: '02:45', percent: 91, text: 'Assinatura e Feedback de Desbloqueio', subtitle: 'Finalize o reporte para liberar as operações de pouso no balizamento informatizado.', visualType: 'checklist' }
    ],
    writtenSteps: [
      'Confirme o horário de fechamento temporário de decolagem na frequência rádio.',
      'Percorra a pista no sentido do vento anotando deformações ou restos de borracha.',
      'Marque o status operacional de cada cabeceira de pista (THR 12/30).',
      'Registre falhas de luminárias ou fiações aparentes no formulário.',
      'Finalize o checklist para consolidar o relatório consolidado de pista.'
    ]
  },
  'ops-6': {
    title: 'Operação Segura com Ônibus Ambulift',
    speaker: 'Roberto Mendes (Instrutor Técnico de Ground Handling)',
    duration: '02:45',
    summary: 'Procedimento técnico de acionamento, posicionamento e acoplamento seguro do veículo Ambulift junto às aeronaves para embarque/desembarque de passageiros.',
    chapters: [
      { time: '00:00', percent: 0, text: 'Checklist de Pré-Movimentação', subtitle: 'Antes de movimentar o Ambulift, certifique-se de que os estabilizadores hidráulicos estão integrados.', visualType: 'blueprint' },
      { time: '00:40', percent: 24, text: 'Equipe de Balizamento e Auxiliares', subtitle: 'Sempre faça a marcha à ré com pelo menos dois balizadores visíveis em ambos os retrovisores.', visualType: 'security' },
      { time: '01:20', percent: 48, text: 'Acoplamento com a Aeronave', subtitle: 'Aproxima-se lentamente até que o tapete sensor de toque esteja encostado na fuselagem do jato.', visualType: 'form' },
      { time: '02:00', percent: 72, text: 'Elevação da Cabine Principal', subtitle: 'Eleve a cabine observando se há ventanias fortes superiores ao limite técnico de 40 nós.', visualType: 'map' },
      { time: '02:30', percent: 90, text: 'Protocolo de Desembarque do Passageiro', subtitle: 'Garanta que a cadeira de rodas esteja travada e insira os dados de tempo de atendimento.', visualType: 'checklist' }
    ],
    writtenSteps: [
      'Indique a empresa aérea do voo e o prefixo do avião atendido.',
      'Defina as horas exatas de acionamento inicial e recolhimento final para faturamento.',
      'Assinale se houve necessidade de uso dos sapatos de apoio hidráulico adicionais.',
      'Indique o número exato de passageiros PMA de mobilidade reduzida que foram assistidos.',
      'Certifique-se de preencher o tempo de ciclo (startTime e endTime) recomendado.'
    ]
  },
  'ops-7': {
    title: 'Gestão e Controle de Sobrecarga de Aeronaves',
    speaker: 'Alonso Castilho (Líder Comercial de Pátio)',
    duration: '02:15',
    summary: 'Regulamentos para calcular peso de aeronaves (ACN/PCN) e emitir permissões eletrônicas quando aeronaves operam em regime excepcional de sobrecarga.',
    chapters: [
      { time: '00:00', percent: 0, text: 'Parâmetros ACN/PCN Básicos', subtitle: 'Benvindo. O peso e pressão de pneus das aeronaves não deve comprometer a vida útil do asfalto.', visualType: 'blueprint' },
      { time: '00:30', percent: 22, text: 'Cálculo de Fator de Sobrecarga', subtitle: 'Se o ACN exceder o PCN em até 10%, a operação pode ser autorizada como sobrecarga simples.', visualType: 'form' },
      { time: '01:05', percent: 48, text: 'Preenchimento do Tipo de Pavimento', subtitle: 'Especifique se o pavimento é Flexível (F) ou Rígido (R) para determinar a resistência correta.', visualType: 'map' },
      { time: '01:45', percent: 77, text: 'Gerando Termos de Responsabilidade', subtitle: 'A companhia de voo deve assinar digitalmente aceitando possíveis penalidades operacionais.', visualType: 'security' },
      { time: '02:05', percent: 92, text: 'Protocolo de Aprovação no Sistema', subtitle: 'Clique em salvar. O sistema gerará um bilhete eletrônico para o Despachante Operacional.', visualType: 'checklist' }
    ],
    writtenSteps: [
      'Insira a matrícula da aeronave e o peso máximo de decolagem esperado.',
      'Selecione a rampa ou posição de estacionamento atribuída à operação.',
      'Identifique se o pavimento é rígido ou flexível preenchendo o subcampo apropriado.',
      'Adicione a carta de autorização prévia caso já possua aval da diretoria técnica.',
      'Submeta para obter o número do processo de sobrecarga deferido.'
    ]
  },
  'safe-1': {
    title: 'Reporte de Vazamentos em Área Operacional',
    speaker: 'Capitão Franco (Coordenador do Corpo de Bombeiros Civil)',
    duration: '03:10',
    summary: 'Como agir e preencher o formulário em caso de derramamento de lubrificantes ou combustível Querosene de Aviação (QAV) no solo do aeroporto.',
    chapters: [
      { time: '00:00', percent: 0, text: 'Segurança Inicial e Contenção', subtitle: 'O primeiro passo após o vazamento é afastar fontes de ignição e orientar o isolamento.', visualType: 'blueprint' },
      { time: '00:45', percent: 24, text: 'Cálculo da Área do Vazamento (m²)', subtitle: 'Estime a dimensão da mancha cobrindo furos e bueiros para evitar o impacto ambiental.', visualType: 'map' },
      { time: '01:30', percent: 48, text: 'Especificar Tipo de Combustível', subtitle: 'Identifique se o fluido é Querosene de Aviação (QAV), fluido hidráulico ou lubrificante sintético.', visualType: 'form' },
      { time: '02:15', percent: 72, text: 'Acionamento do Corpo de Bombeiros', subtitle: 'Se a área ultrapassar 5 m², o acionamento do SCI e bombeiros aeroportuários é obrigatório.', visualType: 'security' },
      { time: '02:50', percent: 91, text: 'Uso de Absorvente Granulado', subtitle: 'Informe se o material ecológico granulado foi disperso para coletar os poluentes com sucesso.', visualType: 'checklist' }
    ],
    writtenSteps: [
      'Inicie anotando a posição exata (Box ou debaixo de qual asa ocorreu o gotejamento).',
      'Descreva a fonte do vazamento (mangueira de abastecimento, dreno da asa ou motor).',
      'Selecione a gravidade correspondente física medindo a circunferência da mancha.',
      'Envie o reporte contendo fotos e nomes das equipes solicitadas no socorro.',
      'Certifique-se de arquivar o comprovante ambiental de destinação dos resíduos químicos.'
    ]
  },
  'safe-2': {
    title: 'Manejo de Detritos e Objetos Estranhos (FOD)',
    speaker: 'Fernanda Lima (Inspetora de Risco Operacional)',
    duration: '02:00',
    summary: 'Procedimentos para coletar, identificar e classificar resíduos e objetos estranhos (Foreign Object Debris) que coloquem em perigo turbinas de aviões.',
    chapters: [
      { time: '00:00', percent: 0, text: 'Definição e Origem de FOD', subtitle: 'Olá. Objetos na pista podem ser sugados pelas turbinas, causando sérios danos.', visualType: 'blueprint' },
      { time: '00:30', percent: 25, text: 'Origem Física: Metálico, Plástico ou Pedra', subtitle: 'Classifique o objeto. Parafusos ou rebites metálicos geralmente vêm de equipamentos de solo rampa.', visualType: 'form' },
      { time: '01:00', percent: 50, text: 'Localização por Setor Operacional', subtitle: 'Selecione no mapa se o FOD foi recolhido no taxiway de conexão ou no box de embarque.', visualType: 'map' },
      { time: '01:30', percent: 75, text: 'Fotos de Evidência e descarte seguro', subtitle: 'Tire uma foto do objeto ao lado de um marcador visual (como uma caneta) para dar noção de escala.', visualType: 'security' },
      { time: '01:50', percent: 91, text: 'Alerta e Varredura Preventiva', subtitle: 'Submeta o formulário para enviar um alerta de varredura mecânica ao caminhão de aspersão.', visualType: 'checklist' }
    ],
    writtenSteps: [
      'Assinale o tipo de material encontrado (metal, borracha, plástico, pedra, outros).',
      'Indique a coordenada aproximada ou posição de pátio onde o objeto estava deitado.',
      'Insira o peso aproximado (em gramas) do detrito recolhido.',
      'Selecione se houve impacto operacional ou se foi uma coleta preventiva.',
      'Arremate enviando o formulário para alimentar o índice de Risco FOD Mensal.'
    ]
  }
};

const DEFAULT_TUTORIAL: ModuleDetails = {
  title: 'Guia de Preenchimento de Formulários Aeroportuários',
  speaker: 'Equipe de Qualidade e Treinamento Motiva',
  duration: '02:00',
  summary: 'Visualize neste guia interativo as diretrizes gerais de preenchimento, preenchendo todos os dados obrigatórios e anexando fotos em boa qualidade para evitar devoluções de processos operacionais.',
  chapters: [
    { time: '00:00', percent: 0, text: 'Padrão dos Formulários do Sistema', subtitle: 'Olá! Veja o padrão dos nossos formulários. Todos os campos com asterisco são obrigatórios.', visualType: 'blueprint' },
    { time: '00:30', percent: 25, text: 'Mapeamento de Coordenadas e Setor', subtitle: 'A seleção de setores e locais operacionais agiliza a atuação das equipes de infraestrutura.', visualType: 'map' },
    { time: '01:00', percent: 50, text: 'Inserindo Fotos e Evidências Técnicas', subtitle: 'Certifique-se de anexar mídias nítidas, tiradas preferencialmente à luz do dia.', visualType: 'security' },
    { time: '01:30', percent: 75, text: 'Assinaturas de Responsabilidade Técnica', subtitle: 'A assinatura digital fica associada ao seu CPF ou credencial funcional do aeródromo.', visualType: 'form' },
    { time: '01:50', percent: 91, text: 'Envio Seguro e Consultas ao Histórico', subtitle: 'Após o envio, você poderá filtrar, editar ou emitir relatórios PDF com todas as informações.', visualType: 'checklist' }
  ],
  writtenSteps: [
    'Preencha sempre a identificação correta do Aeroporto atendido no cabeçalho.',
    'Certifique-se de que a data e horários inseridos correspondam ao fuso local oficial.',
    'Descreva a não-conformidade de forma direta, sem termos vagos.',
    'Verifique se fotos de evidência estão visíveis e nítidas por dentro do visualizador.',
    'Assine digitalmente e registre para que a gerência técnica seja acionada no ato.'
  ]
};

export const ExplanationVideoModal: React.FC<ExplanationVideoModalProps> = ({
  moduleId,
  moduleTitle,
  onClose
}) => {
  const data = MODULES_TUTORIAL_DATA[moduleId] || DEFAULT_TUTORIAL;

  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);
  const [isMuted, setIsMuted] = useState(false);
  const [activeTab, setActiveTab] = useState<'video' | 'checklist'>('video');
  const [questionText, setQuestionText] = useState('');
  const [submittedQuestion, setSubmittedQuestion] = useState(false);
  const [currentCaption, setCurrentCaption] = useState('');
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0);

  const requestRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number | null>(null);

  // Sync current subtitle and active chapter based on play progress
  useEffect(() => {
    let currentChIndex = 0;
    for (let i = 0; i < data.chapters.length; i++) {
      if (progress >= data.chapters[i].percent) {
        currentChIndex = i;
      }
    }
    setCurrentChapterIndex(currentChIndex);
    setCurrentCaption(data.chapters[currentChIndex]?.subtitle || '');
  }, [progress, data.chapters]);

  // Simulated Video Playback engine using requestAnimationFrame for smooth visuals
  const animateVideo = (timestamp: number) => {
    if (!lastTimeRef.current) lastTimeRef.current = timestamp;
    const elapsed = timestamp - lastTimeRef.current;

    // We want the video to play over its duration
    // E.g. progress from 0 to 100
    // If playSpeed is 1, let's step smoothly (approximately 0.5% - 1.5% per second depending on details)
    const rateOfChange = (elapsed / 1000) * 8 * playbackSpeed; // speed constant

    setProgress((prevProgress) => {
      const nextProgress = prevProgress + rateOfChange;
      if (nextProgress >= 100) {
        setIsPlaying(false);
        return 100;
      }
      return nextProgress;
    });

    lastTimeRef.current = timestamp;
    if (isPlaying) {
      requestRef.current = requestAnimationFrame(animateVideo);
    }
  };

  useEffect(() => {
    if (isPlaying) {
      lastTimeRef.current = null;
      requestRef.current = requestAnimationFrame(animateVideo);
    } else {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    }
    return () => {
      if (requestRef.current) cancelAnimationFrame(requestRef.current);
    };
  }, [isPlaying, playbackSpeed]);

  const handlePlayPause = () => {
    if (progress >= 100) {
      setProgress(0);
    }
    setIsPlaying(!isPlaying);
  };

  const handleRestart = () => {
    setProgress(0);
    setIsPlaying(true);
  };

  const handleScrub = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProgress(parseFloat(e.target.value));
  };

  const handleChapterClick = (percent: number) => {
    setProgress(percent);
    setIsPlaying(true);
  };

  const handleToggleMute = () => {
    setIsMuted(!isMuted);
  };

  const handleSpeedChange = () => {
    setPlaybackSpeed((prev) => {
      if (prev === 1) return 1.5;
      if (prev === 1.5) return 2;
      return 1;
    });
  };

  const handleSendQuestion = (e: React.FormEvent) => {
    e.preventDefault();
    if (!questionText.trim()) return;
    setSubmittedQuestion(true);
    setTimeout(() => {
      setQuestionText('');
      setSubmittedQuestion(false);
      alert('Sua dúvida foi encaminhada com sucesso para o instrutor de Operações Aeroportuárias. Você receberá uma notificação na plataforma e no seu e-mail cadastrado em breve!');
    }, 1000);
  };

  // Helper formatting for virtual timer
  const currentVideoSeconds = Math.max(0, Math.floor((progress / 100) * 150)); // Assume 2.5 minutes total (150s)
  const formatTime = (totalSecs: number) => {
    const mins = Math.floor(totalSecs / 60);
    const secs = totalSecs % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  const currentVisualType = data.chapters[currentChapterIndex]?.visualType || 'blueprint';

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-900/80 backdrop-blur-sm">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 15 }}
          transition={{ type: 'spring', damping: 25, stiffness: 220 }}
          className="bg-white border-2 border-[#C9C5E6] rounded-none w-full max-w-5xl shadow-[0_20px_50px_rgba(57,22,148,0.25)] flex flex-col overflow-hidden max-h-[90vh]"
        >
          {/* Modal Header */}
          <div className="bg-[#1a0a45] text-white px-6 py-4 flex items-center justify-between border-b border-[#391694] shrink-0">
            <div className="flex items-center gap-3">
              <span className="p-1 px-2.5 bg-[#391694] text-[10px] uppercase font-black tracking-wider text-[#FFFD8A] border border-[#FFFD8A]/30">
                Curso / Instrução
              </span>
              <div>
                <h3 className="text-lg font-bold text-white tracking-normal leading-snug truncate max-w-md sm:max-w-xl">
                  {data.title}
                </h3>
                <p className="text-xs text-slate-300 flex items-center gap-1">
                  <span className="font-semibold text-[#0E7490]">{data.speaker}</span>
                </p>
              </div>
            </div>
            <button 
              onClick={onClose}
              className="w-9 h-9 flex items-center justify-center bg-[#391694] text-slate-300 hover:text-white transition-all hover:bg-red-600 rounded-none border border-white/10"
              aria-label="Minimizar Guia"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Quick Notice */}
          <div className="bg-[#FFF5F0] border-b border-[#FFAC8B]/40 px-6 py-2.5 flex items-center gap-2.5 sm:gap-4 shrink-0 text-slate-700">
            <div className="flex-1 text-[11px] font-semibold text-[#9A4222] tracking-wide flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#D95D39] shrink-0 animate-pulse" />
              <span>Dúvidas no preenchimento? Acompanhe o fluxo interativo passo-a-passo no player de simulação.</span>
            </div>
            <div className="text-[11px] font-bold text-slate-400 uppercase hidden md:block">
              {moduleTitle}
            </div>
          </div>

          {/* Modal Main Content Container */}
          <div className="flex-1 flex flex-col md:flex-row divide-y md:divide-y-0 md:divide-x divide-slate-200 min-h-0 overflow-y-auto">
            
            {/* LEFT COLUMN: SIMULATED VIDEO PLAYER (or interactive visualizer) */}
            <div className="flex-1 p-6 flex flex-col bg-slate-900 text-white min-h-[340px] md:min-h-0 justify-between relative overflow-hidden">
              
              {/* Top Details HUD */}
              <div className="flex justify-between items-center bg-black/40 p-2.5 px-4 rounded-none backdrop-blur-md border border-white/10 z-10 shrink-0">
                <div className="flex items-center gap-2">
                  <div className={`w-2.5 h-2.5 rounded-full ${isPlaying ? 'bg-red-500 animate-pulse' : 'bg-amber-500'}`} />
                  <span className="text-[10px] font-mono tracking-widest text-[#51FF62] uppercase font-bold">
                    {isPlaying ? 'PLAYING TUTORIAL' : 'PAUSED'}
                  </span>
                </div>
                <div className="text-[11px] font-mono text-slate-300 flex items-center gap-2">
                  <Clock className="w-3.5 h-3.5 text-[#0891b2]" />
                  <span>Duração: {data.duration}</span>
                </div>
              </div>

              {/* VIDEO SCREEN / CENTRAL VISUAL ACCORDING TO STATE */}
              <div className="flex-1 flex flex-col items-center justify-center relative my-4 overflow-hidden rounded-none border border-white/10 p-4 bg-slate-950">
                
                {/* SVG/CSS Animated HUD background simulating Airport System Visual */}
                <div className="absolute inset-0 opacity-20 pointer-events-none">
                  <div className="w-full h-full border border-dashed border-[#391694]/40 flex items-center justify-center">
                    <div className="w-48 h-48 rounded-full border border-dashed border-[#51FF62]/30 animate-spin" style={{ animationDuration: '24s' }} />
                    <div className="w-72 h-72 absolute rounded-full border border-dashed border-[#d946ef]/20 animate-spin" style={{ animationDuration: '60s', animationDirection: 'reverse' }} />
                  </div>
                  {/* Grid Lines */}
                  <div className="absolute top-0 bottom-0 left-1/2 w-px bg-slate-800" />
                  <div className="absolute left-0 right-0 top-1/2 h-px bg-slate-800" />
                </div>

                {/* VISUAL LAYOUT STATE 1: Blueprint Aeródromo */}
                {currentVisualType === 'blueprint' && (
                  <div className="text-center space-y-3 z-10 max-w-sm animate-in fade-in duration-300">
                    <Compass className="w-16 h-16 mx-auto text-[#FFFD8A] animate-spin" style={{ animationDuration: '10s' }} strokeWidth={1} />
                    <h4 className="font-bold text-[#FFFD8A] text-sm uppercase tracking-wider">Mapeamento de Coordenadas do Sítio</h4>
                    <p className="text-xs text-slate-300 leading-normal">
                      Posicionando as anomalias nas cabeceiras físicas de pouso de acordo com os marcos geográficos homologados.
                    </p>
                    <div className="flex justify-center gap-1.5 font-mono text-[9px] text-[#51FF62]">
                      <span className="bg-white/5 px-2 py-0.5 border border-white/10">GEO: -23.435, -46.473</span>
                      <span className="bg-white/5 px-2 py-0.5 border border-white/10">ELEV: 2478 FT</span>
                    </div>
                  </div>
                )}

                {/* VISUAL LAYOUT STATE 2: Mapa Digital do Terminal */}
                {currentVisualType === 'map' && (
                  <div className="w-full h-full max-h-[160px] flex items-center justify-center relative z-10 animate-in zoom-in-95 duration-300">
                    <div className="border border-[#0891b2]/40 bg-black/60 p-4 flex flex-col justify-between h-full w-full max-w-md">
                      <div className="flex justify-between items-center">
                        <span className="text-[10px] font-mono text-[#0891b2] font-black uppercase">VISTA TÁTICA DO PÁTIO</span>
                        <span className="bg-[#0E7490]/20 text-[#51FF62] py-0.5 px-2 text-[8px] font-mono font-bold">ALERTA ATIVO</span>
                      </div>
                      
                      {/* Interactive Visual representation */}
                      <div className="flex justify-around items-center py-2 h-16 w-full relative">
                        <div className="w-full h-1 bg-[#1a0a45] absolute left-0 right-0 top-1/2 -translate-y-1/2" />
                        
                        <div className="p-1 px-1.5 border border-[#c026d3]/60 bg-[#c026d3]/10 text-xs flex flex-col items-center rounded-none z-10">
                          <span className="text-[8px] text-[#c026d3] font-black uppercase">PÁTIO A</span>
                          <span className="font-mono text-[9px] text-white">BOX 11</span>
                        </div>
                        
                        {/* Plane moving simulation */}
                        <motion.div 
                          animate={{ 
                            x: progress ? [-100, 100] : 0 
                          }}
                          transition={{ repeat: Infinity, duration: 12, ease: 'linear' }}
                          className="bg-[#391694] p-1.5 border border-[#FFFD8A]/50 z-20 text-white rounded-none flex items-center gap-1.5"
                        >
                          <span className="text-[9px] font-bold font-mono">AD-403</span>
                        </motion.div>

                        <div className="p-1 px-1.5 border border-[#0891b2]/60 bg-[#0891b2]/10 text-xs flex flex-col items-center rounded-none z-10">
                          <span className="text-[8px] text-[#0891b2] font-black uppercase">TÁXI D</span>
                          <span className="font-mono text-[9px] text-white">THR 12</span>
                        </div>
                      </div>

                      <div className="text-[9px] text-slate-400 flex items-center justify-between font-mono bg-white/5 p-1">
                        <span>LARGURA: 45M</span>
                        <span>DILATAÇÃO TÉRMICA: OK</span>
                        <span>FOD RISCO: MINIMO</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* VISUAL LAYOUT STATE 3: Exemplo Formulário Digital */}
                {currentVisualType === 'form' && (
                  <div className="w-full max-w-sm space-y-2 z-10 animate-in slide-in-from-bottom-2 duration-300 bg-white/5 border border-white/10 p-4 rounded-none">
                    <span className="text-[9px] font-mono text-[#d946ef] font-black uppercase tracking-wider">SIMULADOR DE PREENCHIMENTO</span>
                    <div className="space-y-2">
                      <div className="flex flex-col gap-1">
                        <div className="flex justify-between items-center">
                          <label className="text-[10px] text-slate-300 font-bold">1. Tipo de Ocorrência *</label>
                          <span className="text-[8px] font-mono text-[#51FF62]">SELECIONADO</span>
                        </div>
                        <div className="bg-slate-900 border border-indigo-500/50 p-1.5 text-xs text-[#FFFD8A] flex items-center justify-between font-mono font-bold">
                          <span>{moduleTitle}</span>
                          <span className="text-[9px] text-[#d946ef] animate-pulse">●</span>
                        </div>
                      </div>
                      <div className="flex flex-col gap-1">
                        <label className="text-[10px] text-[#C9C5E6] font-bold">2. Descrição das Circunstâncias *</label>
                        <div className="bg-indigo-950/40 border border-white/10 p-2 text-[11px] text-slate-300 font-sans min-h-[50px] leading-snug">
                          {currentCaption ? `"${currentCaption.slice(0, 50)}..."` : 'Descreva detalhadamente o evento coletado no campo de aviação...'}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* VISUAL LAYOUT STATE 4: Segurança Operacional SGSO */}
                {currentVisualType === 'security' && (
                  <div className="text-center space-y-3 z-10 max-w-xs animate-in zoom-in-95 duration-300">
                    <div className="w-14 h-14 mx-auto rounded-none border border-[#d946ef] bg-[#d946ef]/10 flex items-center justify-center text-[#d946ef] animate-pulse">
                      <Info className="w-8 h-8" strokeWidth={1.5} />
                    </div>
                    <h4 className="font-bold text-[#d946ef] text-sm uppercase tracking-wider">Protocolo de Segurança Ativo</h4>
                    <p className="text-xs text-slate-300 leading-normal">
                      O registro alimenta o banco de dados SGSO. Relatos consistentes apoiam a prevenção de acidentes severos.
                    </p>
                    <span className="inline-block bg-red-600/20 text-[#D95D39] text-[9px] font-mono border border-red-500/40 rounded-none px-3 py-0.5 tracking-wider font-bold">
                      ANEXO 1 do RBAC 139 - MANDATÓRIO
                    </span>
                  </div>
                )}

                {/* VISUAL LAYOUT STATE 5: Checklist visual de Envio */}
                {currentVisualType === 'checklist' && (
                  <div className="w-full max-w-sm border border-[#51FF62]/40 bg-black/60 p-4 rounded-none z-10 animate-in fade-in duration-300 text-left space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="text-[10px] uppercase font-mono tracking-widest text-[#51FF62] font-black">REVISÃO ANTES DO ENVIO</h4>
                      <CheckCircle className="w-4 h-4 text-[#51FF62] shrink-0" />
                    </div>
                    <div className="space-y-1.5 text-[11px] text-slate-300">
                      <div className="flex items-center gap-2">
                        <div className="w-3.5 h-3.5 rounded-none border border-emerald-500 bg-emerald-500/10 flex items-center justify-center text-[#51FF62] font-mono font-bold text-[8px]">✓</div>
                        <span>Coordenadas Geográficas confirmadas</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3.5 h-3.5 rounded-none border border-emerald-500 bg-emerald-500/10 flex items-center justify-center text-[#51FF62] font-mono font-bold text-[8px]">✓</div>
                        <span>Fotos anexadas com nitidez</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3.5 h-3.5 rounded-none border border-emerald-500 bg-emerald-500/10 flex items-center justify-center text-[#51FF62] font-mono font-bold text-[8px]">✓</div>
                        <span>Assinatura digital inserida no rodapé</span>
                      </div>
                    </div>
                    <div className="pt-2 border-t border-white/10 text-[9px] text-slate-400 text-center uppercase tracking-wide">
                      Pronto para envio seguro sem pendências.
                    </div>
                  </div>
                )}

                {/* BIG INITIAL PLAY OVERLAY IF NOT PLAYED YET */}
                {progress === 0 && !isPlaying && (
                  <button 
                    onClick={handlePlayPause}
                    className="absolute inset-0 bg-slate-950/75 hover:bg-slate-950/60 transition-all flex flex-col items-center justify-center gap-3 z-30 group"
                  >
                    <div className="w-16 h-16 bg-[#391694] text-white border-2 border-[#FFFD8A] rounded-full flex items-center justify-center group-hover:scale-110 transition-transform shadow-[0_4px_30px_rgba(57,22,148,0.5)]">
                      <Play className="w-8 h-8 ml-1" fill="currentColor" />
                    </div>
                    <span className="text-xs font-black uppercase text-[#FFFD8A] tracking-widest bg-[#1a0a45] px-3 py-1 border border-white/20">
                      Iniciar Simulação em Vídeo
                    </span>
                  </button>
                )}

                {/* Subtitles Overlay bar */}
                <div className="absolute bottom-2 left-2 right-2 bg-black/80 hover:bg-black/95 transition-all text-slate-100 text-xs p-3 text-center rounded-none font-semibold leading-relaxed border border-white/5 min-h-[50px] flex items-center justify-center z-10">
                  <p className="max-w-md mx-auto">
                    {currentCaption || 'Selecione ou clique em Play para iniciar a simulação guiada.'}
                  </p>
                </div>

              </div>

              {/* VIDEO CONTROLLER BAR */}
              <div className="bg-black/60 p-4 border border-white/10 shrink-0 z-10 space-y-3">
                <div className="flex items-center gap-3">
                  {/* Timer */}
                  <span className="text-[11px] font-mono text-slate-400 shrink-0 select-none">
                    {formatTime(currentVideoSeconds)}
                  </span>
                  
                  {/* Draggable Progress slider */}
                  <input 
                    type="range" 
                    min="0" 
                    max="100" 
                    step="0.1" 
                    value={progress} 
                    onChange={handleScrub}
                    className="flex-1 h-1.5 bg-slate-800 rounded-none appearance-none cursor-pointer accent-[#51FF62]"
                  />

                  {/* End Duration */}
                  <span className="text-[11px] font-mono text-slate-400 shrink-0 select-none">
                    {data.duration}
                  </span>
                </div>

                <div className="flex justify-between items-center gap-4">
                  <div className="flex items-center gap-2">
                    {/* Play / Pause */}
                    <button 
                      onClick={handlePlayPause}
                      className="w-10 h-10 flex items-center justify-center bg-[#391694] hover:bg-[#2a106e] transition-colors border border-indigo-400/40"
                      title={isPlaying ? 'Pausar' : 'Iniciar'}
                    >
                      {isPlaying ? (
                        <Pause className="w-5 h-5 text-white" fill="currentColor" />
                      ) : (
                        <Play className="w-5 h-5 text-[#FFFD8A]" fill="currentColor" />
                      )}
                    </button>

                    {/* Restart */}
                    <button 
                      onClick={handleRestart}
                      className="w-10 h-10 flex items-center justify-center bg-slate-800 hover:bg-slate-755 border border-white/10"
                      title="Reiniciar Vídeo"
                    >
                      <RotateCcw className="w-4 h-4 text-slate-300" />
                    </button>

                    {/* Mute toggle */}
                    <button 
                      onClick={handleToggleMute}
                      className="w-10 h-10 flex items-center justify-center bg-slate-800 hover:bg-slate-755 border border-white/10"
                      title={isMuted ? 'Ativar Áudio' : 'Mutar'}
                    >
                      {isMuted ? (
                        <VolumeX className="w-4 h-4 text-red-400" />
                      ) : (
                        <Volume2 className="w-4 h-4 text-[#51FF62]" />
                      )}
                    </button>
                  </div>

                  {/* Playback speed selector */}
                  <button 
                    onClick={handleSpeedChange}
                    className="px-3.5 py-2 hover:bg-indigo-950 font-mono text-xs font-bold bg-[#391694]/40 border border-indigo-400/30 text-[#FFFD8A]"
                    title="Acelerar Vídeo"
                  >
                    Velocidade: {playbackSpeed}x
                  </button>
                </div>
              </div>

            </div>

            {/* RIGHT COLUMN: REGLAMENTARY STEPS & USER SUPPORTS */}
            <div className="w-full md:w-[360px] bg-slate-50 flex flex-col justify-between divide-y divide-slate-200 min-h-0">
              
              {/* Option Selector (Sub-Tabs) */}
              <div className="flex bg-slate-100 p-2 border-b border-slate-200 shrink-0">
                <button 
                  onClick={() => setActiveTab('video')}
                  className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-bold transition-all border ${activeTab === 'video' ? 'bg-white text-[#391694] border-[#C9C5E6] font-black' : 'text-slate-500 border-transparent hover:text-slate-800'}`}
                >
                  <ListChecks className="w-4 h-4" />
                  Módulos e Etapas
                </button>
                <button 
                  onClick={() => setActiveTab('checklist')}
                  className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-bold transition-all border ${activeTab === 'checklist' ? 'bg-white text-[#391694] border-[#C9C5E6] font-black' : 'text-slate-500 border-transparent hover:text-slate-800'}`}
                >
                  <MessageSquare className="w-4 h-4" />
                  Dúvida / Suporte
                </button>
              </div>

              {/* Dynamic Content Pane */}
              <div className="flex-1 overflow-y-auto p-5">
                {activeTab === 'video' ? (
                  <div className="space-y-6">
                    <div>
                      <h4 className="text-[12px] font-black text-slate-400 uppercase tracking-wider mb-2">Visão Geral do Manual</h4>
                      <p className="text-xs text-slate-600 leading-relaxed font-normal">
                        {data.summary}
                      </p>
                    </div>

                    {/* Interactive Chapters List */}
                    <div>
                      <h4 className="text-[12px] font-black text-slate-400 uppercase tracking-wider mb-3">Tópicos do Vídeo (Clique para Ir)</h4>
                      <div className="space-y-2">
                        {data.chapters.map((chap, idx) => {
                          const isActive = currentChapterIndex === idx;
                          return (
                            <button
                              key={idx}
                              onClick={() => handleChapterClick(chap.percent)}
                              className={`w-full text-left p-3 border transition-all rounded-none flex items-start gap-2.5 ${isActive ? 'bg-indigo-50 border-[#391694] text-[#391694] font-semibold' : 'bg-white hover:bg-slate-50 border-slate-200 text-slate-600'}`}
                            >
                              <PlayCircle className={`w-4 h-4 mt-0.5 shrink-0 ${isActive ? 'text-[#391694]' : 'text-slate-400'}`} />
                              <div className="flex-1 min-w-0">
                                <p className="text-xs truncate leading-snug">{chap.text}</p>
                                <span className="text-[9px] font-mono font-bold text-slate-400 block mt-0.5">Tempo aproximado: {chap.time}</span>
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    </div>

                    {/* Step-by-Step written support list */}
                    <div>
                      <h4 className="text-[12px] font-black text-slate-400 uppercase tracking-wider mb-3">Checklist Rápido de Apoio</h4>
                      <div className="space-y-2.5 bg-[#F5F3FF] border border-[#C9C5E6]/40 p-4 rounded-none">
                        {data.writtenSteps.map((step, idx) => (
                          <div key={idx} className="flex items-start gap-2.5">
                            <div className="w-5 h-5 flex items-center justify-center rounded-none bg-[#391694] text-white text-[9px] font-bold font-mono shrink-0 mt-0.5">
                              {idx + 1}
                            </div>
                            <p className="text-xs text-slate-700 leading-normal font-normal">
                              {step}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>

                  </div>
                ) : (
                  <div className="space-y-5">
                    <div className="bg-amber-50 border border-amber-200/60 p-4 rounded-none text-slate-700">
                      <h5 className="text-xs font-bold text-amber-800 flex items-center gap-1.5 uppercase tracking-wide mb-1">
                        <HelpCircle className="w-4 h-4 text-amber-600 shrink-0" />
                        Esclarecimento Imediato
                      </h5>
                      <p className="text-xs leading-relaxed text-slate-600">
                        O formulário do módulo possui travas automáticas contra dados incorretos ou em desacordo com as instruções da ANAC. Caso encontre problemas ao salvar, revise o checklist ao lado no menu de etapas.
                      </p>
                    </div>

                    {/* Send Doubt Form */}
                    <form onSubmit={handleSendQuestion} className="space-y-4">
                      <div>
                        <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">
                          Qual é a sua dúvida específica no formulário?
                        </label>
                        <textarea
                          value={questionText}
                          onChange={(e) => setQuestionText(e.target.value)}
                          placeholder="Exemplo: Como identificar corretamente se o desvio de asfalto é de grau Leve ou Moderado no Pátio 2?"
                          className="w-full text-xs p-3 bg-white border border-slate-300 focus:outline-none focus:border-[#391694] min-h-[120px] font-normal leading-relaxed rounded-none text-slate-800 shadow-sm"
                          required
                        />
                      </div>
                      
                      <button
                        type="submit"
                        disabled={submittedQuestion}
                        className="w-full bg-[#391694] text-white py-3 px-4 font-bold rounded-none hover:bg-[#2a106e] transition-colors flex items-center justify-center gap-2 text-xs uppercase tracking-widest disabled:opacity-50"
                      >
                        <Send className="w-4 h-4" />
                        {submittedQuestion ? 'Enviando...' : 'Enviar ao Supervisor'}
                      </button>
                    </form>

                    <div className="pt-4 border-t border-slate-200 space-y-3 font-normal text-slate-500 text-[11px] leading-relaxed">
                      <p>● **Suporte Ativo:** Nosso time operacional monitora os canais de dúvida das 07h às 19h no fuso oficial.</p>
                      <p>● **Histórico de Dúvidas:** Suas interações anteriores geram feedbacks rápidos e podem ser consultadas no portal da gerência operacional.</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Bottom Support Callout */}
              <div className="p-4 bg-slate-100 text-center shrink-0">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">
                  MOTIVA AEROPORTOS • CONTROLE DE QUALIDADE
                </span>
              </div>

            </div>

          </div>

          {/* Modal Footer Area */}
          <div className="bg-[#f5f3ff] px-6 py-4 border-t border-slate-200 flex justify-between items-center shrink-0">
            <span className="text-xs text-slate-500 flex items-center gap-2">
              <CheckCircle className="text-emerald-500 w-4 h-4 stroke-2" />
              Treinamento integrado de auxílio ao preenchimento operacional.
            </span>
            <button 
              onClick={onClose}
              className="bg-white border border-[#C9C5E6] hover:bg-slate-55 hover:border-slate-400 text-slate-800 font-bold px-6 py-2.5 text-xs uppercase tracking-wider rounded-none transition-all"
            >
              Compreendi, Voltar ao Formulário
            </button>
          </div>

        </motion.div>
      </div>
    </AnimatePresence>
  );
};
