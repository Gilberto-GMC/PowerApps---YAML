
import React, { useState, useMemo } from 'react';
import { 
  PlusCircle, 
  History, 
  FileText, 
  Map, 
  Radio, 
  Fuel, 
  Home, 
  Siren, 
  CloudSun, 
  Globe, 
  Clock, 
  RotateCcw, 
  LayoutGrid, 
  Navigation, 
  Info, 
  MapIcon,
  CheckCircle2,
  Check,
  X,
  ChevronDown,
  InfoIcon,
  ClipboardCheck,
  AlertTriangle,
  Lock,
  MoreHorizontal,
  Pencil,
  LucideIcon,
  Filter,
  Eye,
  FileSpreadsheet
} from 'lucide-react';
import { AIRPORTS } from './AISComplianceForm';

interface ChecklistItem {
  id: string;
  title: string;
  description?: string;
  expandLabel?: string;
  expandContent?: React.ReactNode;
}

interface SectionDefinition {
  id: number;
  label: string;
  title: string;
  description: string;
  icon: LucideIcon;
  items: ChecklistItem[];
}

interface AuditRecord {
  id: string;
  date: string;
  airport: string;
  answers: Record<string, 'ok' | 'fail'>;
  observations: Record<string, string>;
  sdiaCodes: Record<string, string>;
  status: 'Concluído' | 'Em Andamento';
}

const VERIFICATION_SECTIONS: SectionDefinition[] = [
  { 
    id: 1, 
    label: '1. Dados Gerais', 
    title: '1. Dados Gerais do Aeródromo',
    description: 'Verifique se os dados cadastrais básicos correspondem à condição vigente.',
    icon: FileText,
    items: [
      { id: '1.1', title: 'Nome oficial do aeroporto', description: 'O nome oficial do aeroporto está correto?' },
      { 
        id: '1.2', 
        title: 'Categoria', 
        description: 'A categoria do aeroporto está correta?',
        expandLabel: 'Ver definições de categoria (Clique para expandir)',
        expandContent: (
          <div className="space-y-3 text-sm text-slate-600 leading-relaxed">
            <p><strong>[Sem código]</strong> – Aeroporto doméstico (apenas voos nacionais).</p>
            <p><strong>INTL</strong> – Internacional: aeródromo usado obrigatoriamente por aeronaves civis nacionais e estrangeiras, como primeira escala por ocasião da entrada e como última por ocasião da saída do território brasileiro.</p>
            <p><strong>INTL/ALTN</strong> – Alternativa Internacional: aeródromo usado por aeronaves civis nacionais e estrangeiras, como primeira escala por ocasião da entrada, ou como última por ocasião da saída do território brasileiro, na impossibilidade eventual de serem utilizados os aeródromos internacionais brasileiros, ou como aeroporto de origem ou destino de Voos "charters" internacionais. Quando o aeródromo não satisfizer uma das condições acima, nada é indicado.</p>
          </div>
        )
      },
      { 
        id: '1.3', 
        title: 'Utilização', 
        description: 'A informação de utilização (Público, Privado ou Militar) está correta?',
        expandLabel: 'Ver definições de utilização (Clique para expandir)',
        expandContent: (
          <div className="space-y-3 text-sm text-slate-600 leading-relaxed">
            <p>A propriedade do aeroporto está correta?</p>
            <p><strong>MIL</strong> – Militar: aeródromo destinado, a princípio, ao uso de aeronaves militares.</p>
            <p><strong>PRIV</strong> – Privado: aeródromo civil, construído em área de propriedade privada, para uso de seu proprietário, cuja exploração comercial é vedada, só podendo ser utilizado com sua permissão.</p>
            <p><strong>PRIV/PUB</strong> – Aeródromo privado aberto ao tráfego público.</p>
            <p><strong>PUB</strong> – Público: aeródromo civil, destinado ao tráfego de aeronaves em geral. <strong>Todos aeroportos da Motiva Aeroportos são públicos.</strong></p>
            <p><strong>PUB/MIL</strong> – Aeródromo público que possui instalações militares do Comando da Aeronáutica.</p>
            <p><strong>PUB/REST</strong> – Público Restrito: aeródromo civil, construído em área de propriedade pública, de uso reservado ao órgão público que o tem sob sua jurisdição, cuja exploração comercial é vedada, só podendo ser utilizado com autorização do respectivo órgão público.</p>
          </div>
        )
      },
      { id: '1.4', title: 'Nome do Operador Aeroportuário responsável', description: 'O nome do Operador Aeroportuário está correto?' },
      { id: '1.5', title: 'Tipo de Operação', description: 'A informação do tipo de operação, ou seja, VFR or VFR/IFR está correta?' },
    ]
  },
  { 
    id: 2, 
    label: '2. Caract. Físicas', 
    title: '2. Características Físicas da Pista de Pouso e Decolagem',
    description: 'Confirme os dados da(s) Pista(s) de Pouso e Decolagem do Aeroporto.',
    icon: Map,
    items: [
      { id: '2.1', title: 'Dados das Pistas', description: 'Verifique dimensões, piso, PCN/PCR, resistência do subleito e pressão máxima admissível dos pneus.' },
      { 
        id: '2.2', 
        title: 'Luzes de Pista e Aproximação', 
        description: 'Todos os auxílios luminosos estão informados por meio dos códigos corretos?',
        expandLabel: 'Ver códigos de luzes (Clique para expandir)',
        expandContent: (
          <div className="space-y-2 text-sm text-slate-600 leading-relaxed font-medium">
            <p><strong>L1</strong> – MALS (Sistema de luzes de aproximação de intensidade média, sem flash).</p>
            <p><strong>L2</strong> – MALSF (Sistema de luzes para aproximação de intensidade média com flash).</p>
            <p><strong>L2A</strong> – MALSR (Sistema de luzes para aproximação de intensidade média com luzes indicadoras de alinhamento de pista.)</p>
            <p><strong>L3</strong> – ALS (Sistema de luzes de aproximação sem flash).</p>
            <p><strong>L4</strong> – ALSF-1 (ALS Categoria I, com flash).</p>
            <p><strong>L5</strong> – ALSF-2 (ALS Categoria II, com flash).</p>
            <p><strong>L6</strong> – VASIS (Sistema indicador de rampa de aproximação visual) de 2 barras e rampa de 3°. Quando diferente de 3°, o ângulo de rampa aparecerá entre parênteses, após a indicação L6.</p>
            <p><strong>L7</strong> – VASIS de 3 barras (duas rampas de aproximação). Os ângulos da 1ª e 2ª rampas aparecerão entre parênteses, após a indicação L7.</p>
            <p><strong>L8</strong> – AVASIS (VASIS de duas barras com nº reduzido de caixas). Quando diferente de 3°, o ângulo de rampa aparecerá entre parênteses, após a indicação L8.</p>
            <p><strong>L9</strong> – PAPI (Sistema indicador de rampa de aproximação de precisão), com rampa normal de 3°. Quando diferente de 3°, o ângulo de rampa aparecerá entre parênteses, após a indicação L9.</p>
            <p><strong>L9A</strong> – APAPI (Sistema indicador de rampa de aproximação de precisão simplificada)</p>
            <p><strong>L10</strong> – REIL (Luzes indicadoras de cabeceira de pista).</p>
            <p><strong>L11</strong> – Luzes de zona de contato.</p>
            <p><strong>L11A</strong> – Luzes de zona de contato de alta intensidade.</p>
            <p><strong>L12</strong> – Luzes de cabeceira (verde no início e vermelha no fim da pista).</p>
            <p><strong>L12A</strong> – Luzes de cabeceira de alta intensidade (verde no início e vermelha no fim da pista).</p>
            <p><strong>L13</strong> – Luzes intermitentes de direção de pista.</p>
            <p><strong>L14</strong> – Luzes ao longo das laterais da pista, de 60 em 60 metros.</p>
            <p><strong>L14A</strong> – Luzes ao longo das laterais da pista de alta intensidade, de 60 em 60 metros.</p>
            <p><strong>L15</strong> – Luzes (azuis) de pista de táxi, indicando sua trajetória.</p>
            <p><strong>L16</strong> – Refletores na cabeceira da pista, indicando sua localização.</p>
            <p><strong>L17</strong> – Placas refletoras instaladas ao lado das luzes laterais e de fim-de-pista, que refletem a luz dos faróis de pouso.</p>
            <p><strong>L18</strong> – Balizamento de emergência (lampiões colocados ao longo das laterais da pista de 60 em 60 metros).</p>
            <p><strong>L19</strong> – Luzes de eixo-de-pista.</p>
            <p><strong>L19A</strong> – Luzes de eixo de pista de alta intensidade.</p>
            <p><strong>L20</strong> – Luzes de eixo-de-pista-de-táxi para saída à grande velocidade.</p>
            <p><strong>L20A</strong> – Luzes de eixo-de-pista-de-táxi para saída à grande velocidade, de alta intensidade.</p>
            <p><strong>L21</strong> – Farol rotativo de aeródromo.</p>
            <p><strong>L22</strong> – Farol de identificação de aeródromo.</p>
            <p><strong>L23</strong> – Luzes de obstáculo.</p>
            <p><strong>L24</strong> – Farol de perigo.</p>
            <p><strong>L25</strong> – Luzes de contorno de área de aeródromo.</p>
            <p><strong>L26</strong> – Indicador de direção de vento iluminado.</p>
            <p><strong>L27</strong> – Luzes de Barra de Parada</p>
            <p><strong>L30</strong> – Luzes de limite de área de pouso de helipontos.</p>
            <p><strong>L31</strong> – Sinal luminoso de identificação de heliponto.</p>
            <p><strong>L32</strong> – Faróis de heliponto.</p>
            <p><strong>L33</strong> – Luzes indicadoras de direção de aproximação de heliponto.</p>
            <p><strong>L34</strong> – Luzes indicadoras de área de toque quadradas de heliponto.</p>
            <p><strong>L35</strong> – Luzes indicadoras do ângulo de direção do heliponto.</p>
          </div>
        )
      }
    ]
  },
  { 
    id: 3, 
    label: '3. Comunicação', 
    title: '3. Comunicação e Rádio Auxílios',
    description: 'Verifique a disponibilidade e frequências.',
    icon: Radio,
    items: [
      { id: '3.1', title: 'Serviços de Tráfego Aéreo Disponíveis', description: 'As informações de Órgãos ATS disponíveis e suas respectivas frequências estão corretas? Verifique na carta ADC ou no AIP as frequências.' },
      { id: '3.2', title: 'Rádio Auxílios', description: 'Os rádio auxílios e suas respectivas frequências estão corretas? Verifique nas cartas ADC, IAC ou no AIP.' }
    ]
  },
  { 
    id: 4, 
    label: '4. Combustível', 
    title: '4. Combustível',
    description: 'Disponibilidade de abastecimento.',
    icon: Fuel,
    items: [
      { id: '4.1', title: 'Tipos de combustível', description: 'Os tipos de combustível estão corretos? AVGAS (PF) / JET-A1 (TF).' },
      { id: '4.2', title: 'Empresas Distribuidoras e Contatos', description: 'As distribuidoras de combustível, seus respectivos telefones e horários de funcionamento estão corretos?' }
    ]
  },
  { 
    id: 5, 
    label: '5. Hangares', 
    title: '5. Hangares', 
    description: 'Serviços de apoio.', 
    icon: Home, 
    items: [
      { 
        id: '5.1', 
        title: 'Hangares e Serviços de Manutenção', 
        description: 'Indica a existência de hangares e oficinas disponíveis para terceiros, de acordo com a codificação abaixo:',
        expandLabel: 'Ver códigos de serviços (Clique para expandir)',
        expandContent: (
          <div className="space-y-2 text-sm text-slate-600 leading-relaxed font-medium">
            <p><strong>S1</strong> – Hangar</p>
            <p><strong>S2</strong> – Hangar e pequenos reparos em aeronaves</p>
            <p><strong>S3</strong> – Hangar e pequenos reparos em aeronaves e motores</p>
            <p><strong>S4</strong> – Hangar e grandes reparos em aeronaves; e pequenos reparos em motores</p>
            <p><strong>S5</strong> – Hangar e grandes reparos em aeronaves e motores.</p>
          </div>
        )
      }
    ] 
  },
  { id: 6, label: '6. Emergência', title: '6. Emergência', description: 'Salvamento e Combate a Incêndio.', icon: Siren, items: [{ id: '6.1', title: 'Categoria Contraincêndio (CAT)', description: 'Confirme se a CAT publicada e o horário de funcionamento condiz com a capacidade atual.' }] },
  { id: 7, label: '7. Meteorologia', title: '7. Meteorologia', description: 'Serviços meteorológicos disponíveis.', icon: CloudSun, items: [{ id: '7.1', title: 'Nível do Centro Meteorológico de Aeródromo', description: 'Confirme com o Órgão ATS Local se as informações referente ao Centro Meteorológico de Aeródromo (CMA) estão corretas.' }] },
  { id: 8, label: '8. AIS', title: '8. Serviço de Informação Aeronáutica (AIS)', description: 'Confirme com o Órgão ATS local.', icon: Globe, items: [{ id: '8.1', title: 'Sala AIS', description: 'O tipo de atendimento, horário de funcionamento e telefone para contato estão atualizados?' }] },
  { id: 9, label: '9. Horário de Func.', title: '9. Horário de Funcionamento', description: 'Janelas operacionais.', icon: Clock, items: [{ id: '9.1', title: 'Horário de funcionamento do aeroporto', description: 'O horário de operação divulgado está correto?' }] },
  { 
    id: 10, 
    label: '10. Retomada Op.', 
    title: '10. Retomada Operacional', 
    description: 'Protocolos de contingência.', 
    icon: RotateCcw, 
    items: [
      { 
        id: '10.1', 
        title: 'Plano de Remoção de Aeronaves Inoperantes (PRAI)', 
        description: 'Texto obrigatório pela ANAC.',
        expandLabel: 'Ver opções de texto padrão (Clique para expandir)',
        expandContent: (
          <div className="space-y-3 text-sm text-slate-600 leading-relaxed">
            <p><strong>Opção 1:</strong> Plano de Remoção de ACFT inoperantes (PRAI): AD não disponibiliza recursos internos para remoção de ACFT.</p>
            <p><strong>Opção 2:</strong> Plano de Remoção de ACFT inoperantes (PRAI): Capacidade para remoção de ACFT [TIPO DA AERONAVE] - Peso XX.XXX kg, acionamento TEL: (XX) XXXXX-XXXX</p>
          </div>
        )
      }
    ] 
  },
  { 
    id: 11, 
    label: '11. Pátios', 
    title: '11. Dados de Pátios e Táxi', 
    description: 'Características operacionais de pátio.', 
    icon: LayoutGrid, 
    items: [
      { 
        id: '11.1', 
        title: 'Informações sobre reserva de pátio', 
        description: 'Consta a informação padronizada de obrigatoriedade para reserva de pátio para os operadores aéreos?',
        expandLabel: 'Ver texto padrão (Clique para expandir)',
        expandContent: (
          <div className="space-y-4 text-sm text-slate-600 leading-relaxed text-justify">
            <p>Compulsória AUTH prévia da concessionária com no mínimo 02 (duas) HR de antecedência à operação, mediante solicitação através do WebApp-MOTIVA AVG pelo link <a href="#" className="text-blue-600 underline">ga.ccraeroportos.com.br</a> quando:</p>
            <ul className="list-none space-y-1 pl-4 border-l-2 border-slate-200">
              <li>01 - ACFT necessitar de reserva de pátio;</li>
              <li>02 - ACFT de matrícula internacional;</li>
              <li>03 - ACFT de matrícula brasileira e mais de um proprietário/operador registrado no Registro Aeronáutico Brasileiro (RAB);</li>
              <li>04 - ACFT de matrícula brasileira, sem cadastro de aeronave/financeiro no WebApp-MOTIVA AVG ou que precise de atualização, mesmo sem intenção de uso do pátio;</li>
              <li>05 - ACFT isenta, em voo de experiência ou de instrução, nos casos de a categoria de registro da aeronave no RAB não constar como PRIVADA, DE INSTRUCAO ou EXPERIMENTAL.</li>
            </ul>
            <p>O Centro de Operações Aeroportuárias analisará a solicitação e retornará com o status por meio do WebApp-MOTIVA AVG. Quando necessário, poderão ser solicitados ajustes na programação, os quais deverão ser regularizados com no mínimo 30 minutos de antecedência à operação. Caso contrário, a solicitação será cancelada.</p>
            <p>Para dúvidas ou auxílio, consulte os canais de comunicação no website <a href="https://aeroportos.motiva.com.br/negocios/aviacao-geral/" target="_blank" rel="noreferrer" className="text-blue-600 underline break-all">https://aeroportos.motiva.com.br/negocios/aviacao-geral/</a></p>
            <p className="font-medium">Em caso de contingência, entre em contato com o aeroporto através do e-mail: apoc.___@motiva.com.br.</p>
          </div>
        )
      }, 
      { id: '11.2', title: 'Pontos de ancoragem', description: 'Existe informação, se aplicável, da indisponibilidade de pontos de arrama? Exemplo: APN PRKG não dispõe de pontos de amarração.' }
    ] 
  },
  { 
    id: 12, 
    label: '12. Reg. Tráfego Local', 
    title: '12. Regulamentos Locais', 
    description: 'Restrições e informações operacionais.', 
    icon: Navigation, 
    items: [
      { 
        id: '12.1', 
        title: 'Restrição de giro 180º na Pista de Pouso e Decolagem', 
        description: 'Verifique se está publicada a restrição que exige que o giro de 180º da aeronave trafegando pela Pista de Pouso e Decolagem ocorra apenas nas cabeceiras. Exemplo: RWY 13/31 Giro de 180 DEG para ACFT com PMD acima de 40T, somente nas THR.' 
      }, 
      { 
        id: '12.2', 
        title: 'Demais Regulamentos e Restrições Locais',
        description: 'Verifique se todas as restrições e informações operacionais publicadas permanecem válidas.',
        expandLabel: 'Ver exemplos de restrições (Clique para expandir)',
        expandContent: (
          <div className="space-y-3 text-sm text-slate-600 leading-relaxed font-medium">
            <p><strong>Aeroporto Certificado:</strong> O aeroporto pode ser utilizado regularmente por ACFT compatíveis com o código de referência 4C ou inferior;</p>
            <p><strong>Serviços Aéreos:</strong> Lançamento de objetos, pulverização, reboque de ACFT, lançamento de paraquedas, voo acrobático.</p>
            <p><strong>Restrições de Pátio:</strong> Pátios não disponíveis para permanência de ACFT vinculadas a instrução.</p>
            <p><strong>Horários (TGL):</strong> Restrições de horários para treinamento e check (Ex: proibido TGL em horários de pico, PPR nos demais).</p>
            <p><strong>Limites de Envergadura:</strong> Restrições em TWY (Ex: TWY Alfa LTD para ACFT envergadura máxima 36m).</p>
            <p><strong>Push-back:</strong> Procedimentos específicos (Ex: Acionamento somente quando o push-back atingir a faixa de rolagem).</p>
            <p><strong>Operações Especiais:</strong> Autorizações específicas (Ex: Operações Boeing 747-8F conforme MOPS aprovado).</p>
          </div>
        )
      }, 
      { 
        id: '12.3', 
        title: 'Operação com Sobrepeso', 
        description: 'Consta a mensagem padronizada: "Operações de aeronaves com ACN/ACR acima do PCN/PCR publicado poderão ser autorizadas mediante avaliação do Operador do Aeródromo, desde que o Operador Aéreo apresente a solicitação com, no mínimo, 2 (dois) dias de antecedência, encaminhando-a para o e-mail apoc.___@motiva.com.br."?' 
      }
    ] 
  },
  { id: 13, label: '13. Info Adicional', title: '13. Informações Adicionais', description: 'Observações não classificadas.', icon: Info, items: [{ id: '13.1', title: 'Instruções Gerais', description: 'As informações adicionais do aeródromo estão válidas?' }, { id: '13.2', title: 'Distâncias Declaradas', description: 'As distâncias declaradas estão corretas?' }] },
  { 
    id: 14, 
    label: '14. Cartas', 
    title: '14. Cartas Publicadas', 
    description: 'Disponibilidade de cartas. Marque como correto quando o aeroporto não dispõe de determinado tipo de carta.', 
    icon: MapIcon, 
    items: [
      { id: '14.1', title: 'Carta VAC (Visual Approach Chart)', description: 'A carta VAC está atualizada?' }, 
      { id: '14.2', title: 'Carta ADC (Aerodrome Chart)', description: 'A carta ADC está atualizada?' },
      { id: '14.3', title: 'Carta PDC (Parking/Docking Chart)', description: 'A carta PDC está atualizada?' },
      { id: '14.4', title: 'Carta AGMC (Aerodrome Ground Movement Chart)', description: 'A carta AGMC está atualizada?' }
    ] 
  },
];

const MOCK_HISTORY: AuditRecord[] = [
  {
    id: '1',
    date: '2024-05-18',
    airport: 'Aeroporto de Navegantes',
    answers: { 
      '1.1': 'ok', '1.2': 'ok', '1.3': 'ok', '1.4': 'ok', '1.5': 'ok',
      '2.1': 'ok', '2.2': 'ok',
      '3.1': 'fail', '3.2': 'ok'
    },
    observations: { '3.1': 'Frequência do solo desatualizada na carta' },
    sdiaCodes: { '3.1': 'SDIA-2024-885' },
    status: 'Concluído'
  },
  {
    id: '2',
    date: '2024-05-10',
    airport: 'Aeroporto da Pampulha',
    answers: { 
      '1.1': 'ok', '1.2': 'ok',
      '2.1': 'fail', '2.2': 'fail'
    },
    observations: { 
      '2.1': 'Resistência do pavimento incorreta', 
      '2.2': 'Luzes de cabeceira inoperantes' 
    },
    sdiaCodes: { 
      '2.1': 'SDIA-2024-102',
      '2.2': 'SDIA-2024-103'
    },
    status: 'Concluído'
  }
];

export const AISWebModule: React.FC = () => {
  const [selectedAirport, setSelectedAirport] = useState('');
  const [activeSectionId, setActiveSectionId] = useState(1);
  const [isFinalizing, setIsFinalizing] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [viewMode, setViewMode] = useState<'audit' | 'history'>('audit');
  const [historyFilter, setHistoryFilter] = useState('Todos os Aeroportos');
  const [isReadOnlyMode, setIsReadOnlyMode] = useState(false);
  
  const [answers, setAnswers] = useState<Record<string, 'ok' | 'fail'>>({});
  const [observations, setObservations] = useState<Record<string, string>>({});
  const [sdiaCodes, setSdiaCodes] = useState<Record<string, string>>({});
  
  // History State
  const [historyRecords, setHistoryRecords] = useState<AuditRecord[]>(MOCK_HISTORY);
  const [actionMenuId, setActionMenuId] = useState<string | null>(null);

  // State for expanded descriptions
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  const toggleExpand = (itemId: string) => {
    setExpandedItems(prev => 
      prev.includes(itemId) ? prev.filter(id => id !== itemId) : [...prev, itemId]
    );
  };

  const allChecklistItems = useMemo(() => VERIFICATION_SECTIONS.flatMap(s => s.items), []);
  const totalItemsCount = allChecklistItems.length;
  const answeredCount = Object.keys(answers).length;
  const progressPercentage = Math.round((answeredCount / totalItemsCount) * 100) || 0;
  
  const failedItems = useMemo(() => {
    return allChecklistItems.filter(item => answers[item.id] === 'fail');
  }, [answers, allChecklistItems]);

  const conformCount = Object.values(answers).filter(v => v === 'ok').length;
  const nonConformCount = failedItems.length;

  const isAuditComplete = answeredCount === totalItemsCount;

  const areSdiaCodesFilled = useMemo(() => {
    return failedItems.every(item => sdiaCodes[item.id] && sdiaCodes[item.id].trim().length > 0);
  }, [failedItems, sdiaCodes]);

  const areObservationsFilled = useMemo(() => {
    return failedItems.every(item => observations[item.id] && observations[item.id].trim().length > 0);
  }, [failedItems, observations]);

  const handleViewRecord = (record: AuditRecord) => {
    setAnswers(record.answers);
    setObservations(record.observations);
    setSdiaCodes(record.sdiaCodes);
    setSelectedAirport(record.airport);
    setIsReadOnlyMode(true);
    setViewMode('audit');
    setShowSummary(true); // Jump directly to summary for "View"
    setActionMenuId(null);
  };

  const handleEditRecord = (record: AuditRecord) => {
    setAnswers(record.answers);
    setObservations(record.observations);
    setSdiaCodes(record.sdiaCodes);
    setSelectedAirport(record.airport);
    setIsReadOnlyMode(false);
    setViewMode('audit');
    setShowSummary(false); // Start from beginning/sections for "Edit"
    setActiveSectionId(1);
    setActionMenuId(null);
  };

  const handleNewAudit = () => {
    setViewMode('audit'); 
    setAnswers({}); 
    setObservations({}); 
    setSdiaCodes({}); 
    setShowSummary(false); 
    setSelectedAirport('');
    setIsReadOnlyMode(false);
  };

  const handleFinalizeAudit = () => {
    const newRecord: AuditRecord = {
      id: Math.random().toString(36).substr(2, 9),
      date: new Date().toISOString().split('T')[0],
      airport: selectedAirport,
      answers: answers,
      observations: observations,
      sdiaCodes: sdiaCodes,
      status: 'Concluído'
    };

    setHistoryRecords(prev => [newRecord, ...prev]);
    setIsFinalizing(true);
  };

  const renderHistoryContent = () => {
    return (
      <div className="flex-1 flex flex-col overflow-hidden animate-in fade-in duration-500 bg-white" onClick={() => setActionMenuId(null)}>
        <div className="h-14 border-b border-slate-100 px-8 flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-700 uppercase tracking-wide">Histórico de Verificações</h2>
        </div>
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-full space-y-6">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-50 p-4 rounded-none border border-slate-100 shadow-inner">
              <div className="flex items-center gap-4 w-full sm:w-auto">
                <div className="flex items-center gap-2">
                  <Filter className="w-4 h-4 text-slate-400" />
                  <span className="text-xs font-black text-slate-400 uppercase tracking-widest whitespace-nowrap">Filtrar Aeródromo:</span>
                </div>
                <div className="relative flex-1 sm:flex-none">
                  <select 
                    value={historyFilter}
                    onChange={(e) => setHistoryFilter(e.target.value)}
                    className="w-full sm:w-auto h-10 pl-4 pr-10 bg-white border border-slate-200 rounded-none text-xs font-bold text-slate-700 outline-none focus:border-brand-500 transition-all appearance-none cursor-pointer"
                  >
                    <option>Todos os Aeroportos</option>
                    {AIRPORTS.map(ap => <option key={ap}>{ap}</option>)}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                </div>
              </div>
              
              <button className="flex items-center justify-center gap-2 px-6 h-10 bg-[#391694] text-white rounded-none text-xs font-bold hover:bg-[#2a106e] transition-colors shadow-sm w-full sm:w-auto">
                <FileSpreadsheet className="w-4 h-4" />
                Exportar
              </button>
            </div>
            <div className="bg-white rounded-none border border-slate-100 shadow-sm overflow-visible">
              <table className="w-full text-center border-collapse">
                <thead>
                  <tr className="bg-slate-50/50 border-b border-slate-100">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-center border-b border-slate-200">Data</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-center border-b border-slate-200">Aeroporto</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-center border-b border-slate-200">Conformes</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-center border-b border-slate-200">Não Conformes</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-center border-b border-slate-200">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {historyRecords.map((record) => {
                    const conforms = Object.values(record.answers).filter(a => a === 'ok').length;
                    const nonConforms = Object.values(record.answers).filter(a => a === 'fail').length;
                    
                    if (historyFilter !== 'Todos os Aeroportos' && record.airport !== historyFilter) return null;

                    return (
                      <tr key={record.id} className="hover:bg-slate-50/50 transition-colors">
                        <td className="px-6 py-4 text-center">
 <div className="text-xs font-semibold text-slate-900 leading-tight">
 {record.date.split('-').reverse().join('/')}
 </div>
 </td>
                        <td className="px-6 py-4 text-center">
 <div className="text-xs text-slate-700 font-medium whitespace-normal leading-tight max-w-[200px] mx-auto">
 {record.airport}
 </div>
 </td>
                        <td className="px-6 py-4 text-center">
 <span className="inline-flex items-center justify-center px-2 py-1 bg-emerald-100 text-emerald-700 rounded-sm text-[10px] font-black min-w-[30px]">
 {conforms}
 </span>
 </td>
                        <td className="px-6 py-4 text-center">
 <span className={`inline-flex items-center justify-center px-2 py-1 rounded-sm text-[10px] font-black min-w-[30px] ${nonConforms > 0 ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-500'}`}>
 {nonConforms}
 </span>
 </td>
                        <td className="px-6 py-4 text-center relative">
 <button 
 onClick={(e) => {
 e.stopPropagation();
 setActionMenuId(actionMenuId === record.id ? null : record.id);
 }}
 className={`p-1.5 rounded-md transition-all ${actionMenuId === record.id ? 'bg-[#391694] text-white shadow-md' : 'text-slate-400 hover:text-[#391694] hover:bg-indigo-50'}`}
 >
 <MoreHorizontal className="w-5 h-5" />
 </button>

 {actionMenuId === record.id && (
 <div className="absolute z-50 right-8 top-1/2 -translate-y-1/2 w-32 bg-white border border-slate-200 rounded-sm shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200 origin-top-right">
 <button 
 onClick={(e) => { e.stopPropagation(); handleViewRecord(record); }} 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 hover:text-[#391694] flex items-center gap-2 border-b border-slate-50 transition-colors"
 >
 <Eye className="w-3.5 h-3.5" /> Ver
 </button>
 <button 
 onClick={(e) => { e.stopPropagation(); handleEditRecord(record); }} 
 className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 hover:text-[#391694] flex items-center gap-2 transition-colors"
 >
 <Pencil className="w-3.5 h-3.5" /> Editar
 </button>
 </div>
 )}
 </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderSummaryContent = () => {
    return (
      <div className="flex-1 flex flex-col overflow-y-auto bg-slate-50/50 p-6 animate-in fade-in duration-500 pb-10">
        <div className="max-w-5xl w-full space-y-8 pb-10">
          <div className="bg-white p-8 rounded-none border border-slate-100 shadow-sm flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold text-slate-800 mb-2">Conclusão da Auditoria</h2>
              <p className="text-sm text-slate-500">Revise as pendências e informe os códigos SDIA para itens não conformes.</p>
            </div>
            {isReadOnlyMode && (
              <div className="bg-amber-50 px-4 py-2 rounded border border-amber-200 flex items-center gap-2">
                <Eye className="w-4 h-4 text-amber-600" />
                <span className="text-xs font-bold text-amber-700 uppercase tracking-wider">Modo Visualização</span>
              </div>
            )}
          </div>

          <div className="bg-white p-8 rounded-none border border-slate-100 shadow-sm">
            <div className="flex items-center gap-3 mb-8">
              <ClipboardCheck className="w-5 h-5 text-slate-700" />
              <h3 className="font-bold text-slate-800">Resumo da Inspeção</h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-10">
              <div className="p-5 bg-slate-50 rounded-none text-center border border-slate-100">
                <span className="block text-2xl font-black text-slate-700">{totalItemsCount}</span>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Total Itens</span>
              </div>
              <div className="p-5 bg-emerald-50/50 rounded-none text-center border border-emerald-100/50">
                <span className="block text-2xl font-black text-emerald-600">{conformCount}</span>
                <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest">Conformes</span>
              </div>
              <div className="p-5 bg-red-50/50 rounded-none text-center border border-red-100/50">
                <span className="block text-2xl font-black text-red-600">{nonConformCount}</span>
                <span className="text-[10px] font-bold text-red-400 uppercase tracking-widest">Divergências</span>
              </div>
            </div>

            {failedItems.length > 0 && (
              <div className="space-y-6 mb-10">
                <h4 className="text-xs font-black text-red-600 uppercase tracking-widest flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" />
                  Códigos SDIA Necessários
                </h4>
                <div className="divide-y divide-slate-100 border border-slate-100">
                  {failedItems.map((item) => (
                    <div key={item.id} className="p-6 bg-white space-y-3">
                      <div className="flex justify-between items-start">
                        <span className="text-sm font-bold text-slate-900">{item.title}</span>
                        <span className="px-2 py-1 bg-red-50 text-red-600 text-[10px] font-black uppercase">Não Conforme</span>
                      </div>
                      
                      {observations[item.id] ? (
                        <div className="bg-slate-50 p-3 border-l-2 border-slate-300 text-xs text-slate-600 italic">
                          "{observations[item.id]}"
                        </div>
                      ) : (
                        <div className="bg-red-50 p-3 border-l-2 border-red-300 text-xs text-red-600 font-bold">
                          Observação obrigatória não preenchida. Clique em "Revisar" para corrigir.
                        </div>
                      )}

                      <div className="flex flex-col gap-2">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Código da SDIA *</label>
                        <input 
                          disabled={isReadOnlyMode}
                          type="text"
                          placeholder="Ex: SDIA-2025-001"
                          value={sdiaCodes[item.id] || ''}
                          onChange={(e) => setSdiaCodes(prev => ({ ...prev, [item.id]: e.target.value }))}
                          className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-none outline-none focus:border-brand-500 text-sm font-bold disabled:bg-slate-100 disabled:text-slate-500"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!isReadOnlyMode ? (
              <div className="flex flex-col sm:flex-row gap-3">
                <button 
                  onClick={() => setShowSummary(false)}
                  className="flex-1 flex items-center justify-center gap-2 py-4 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-none text-sm font-bold transition-all uppercase"
                >
                  <Pencil className="w-5 h-5" />
                  Revisar
                </button>
                <button 
                  disabled={!isAuditComplete || (failedItems.length > 0 && (!areSdiaCodesFilled || !areObservationsFilled))}
                  onClick={handleFinalizeAudit}
                  className="flex-1 flex items-center justify-center gap-2 py-4 bg-brand-500 hover:bg-brand-600 text-white rounded-none text-sm font-bold transition-all shadow-lg shadow-indigo-900/20 disabled:opacity-50 uppercase"
                >
                  <CheckCircle2 className="w-5 h-5" />
                  Finalizar Auditoria
                </button>
              </div>
            ) : (
              <button 
                onClick={() => { setViewMode('history'); setSelectedAirport(''); }}
                className="w-full flex items-center justify-center gap-2 py-4 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-none text-sm font-bold transition-all uppercase"
              >
                Voltar para Registros
              </button>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderMainContent = () => {
    if (viewMode === 'history') return renderHistoryContent();
    
    if (!selectedAirport) {
      return (
        <div className="flex-1 flex flex-col items-center justify-center p-8 lg:p-12 text-center h-full bg-white animate-in fade-in duration-500">
          <div className="max-w-md w-full">
            <div className="bg-amber-50 border border-amber-200 p-6 mb-8 flex flex-col items-center gap-3 shadow-sm">
              <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
                <Lock className="w-5 h-5 text-amber-700" />
              </div>
              <div>
                <h3 className="text-[13px] font-black text-amber-800 uppercase tracking-widest mb-2">Acesso Restrito</h3>
                <p className="text-[13px] text-amber-800 font-medium leading-relaxed">
                  Este módulo é de preenchimento exclusivo pelos <strong>Analistas de Aeroportos</strong>.
                </p>
              </div>
            </div>

            <div className="relative">
              <select 
                autoFocus
                value={selectedAirport}
                onChange={(e) => setSelectedAirport(e.target.value)}
                className="w-full h-14 pl-5 pr-10 bg-white border border-slate-200 rounded-none text-[13px] font-bold text-slate-700 outline-none focus:border-[#391694] transition-all appearance-none cursor-pointer"
              >
                <option value="">Escolha uma localidade...</option>
                {AIRPORTS.map(ap => <option key={ap} value={ap}>{ap}</option>)}
              </select>
              <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
            </div>
          </div>
        </div>
      );
    }

    if (showSummary) return renderSummaryContent();

    const currentSection = VERIFICATION_SECTIONS.find(s => s.id === activeSectionId);

    return (
      <div className="flex-1 flex flex-col overflow-hidden bg-white">
        <div className="flex-1 overflow-y-auto p-8 lg:p-12">
          <div className="max-w-4xl space-y-6 mx-auto">
            <div className="mb-10">
              <h2 className="text-2xl font-bold text-slate-900 mb-2 leading-tight">{currentSection?.title}</h2>
              <p className="text-[15px] text-slate-500 leading-relaxed font-normal">{currentSection?.description}</p>
            </div>
            
            <div className="space-y-4">
              {currentSection?.items.map((item) => (
                <div key={item.id} className="bg-white border border-slate-100 rounded-none overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                  <div className="px-6 py-5 flex flex-col gap-4">
                    <div className="flex items-center justify-between gap-6">
                      <div className="flex-1">
                        <h4 className="font-bold text-slate-800 text-[15px] leading-tight">{item.title}</h4>
                        <p className="text-[13px] text-slate-500 font-normal leading-relaxed mt-1.5">{item.description}</p>
                        
                        {item.expandContent && (
                          <div className="mt-2">
                            <button 
                              onClick={() => toggleExpand(item.id)}
                              className="flex items-center gap-1 text-[11px] font-bold text-blue-600 hover:text-blue-800 transition-colors uppercase tracking-wide"
                            >
                              <InfoIcon className="w-3.5 h-3.5" />
                              {item.expandLabel || 'Ver mais detalhes (Clique para expandir)'}
                            </button>
                            
                            {expandedItems.includes(item.id) && (
                              <div className="mt-3 p-4 bg-slate-50 border-l-4 border-blue-500 rounded-r-sm animate-in slide-in-from-top-2">
                                {item.expandContent}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                      <div className="flex bg-slate-100 border border-slate-100 rounded-none p-0.5 shrink-0 self-start">
                        <button 
                          onClick={() => setAnswers(prev => ({ ...prev, [item.id]: 'ok' }))} 
                          className={`w-12 h-10 flex items-center justify-center rounded-none transition-all ${answers[item.id] === 'ok' ? 'bg-white text-emerald-600 shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}
                        >
                          <Check className="w-5 h-5" />
                        </button>
                        <button 
                          onClick={() => setAnswers(prev => ({ ...prev, [item.id]: 'fail' }))} 
                          className={`w-12 h-10 flex items-center justify-center rounded-none transition-all ${answers[item.id] === 'fail' ? 'bg-red-500 text-white shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}
                        >
                          <X className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                    
                    {answers[item.id] === 'fail' && (
                      <div className="animate-in slide-in-from-top-2 duration-300">
                        <textarea 
                          placeholder="Descreva a não conformidade encontrada..."
                          value={observations[item.id] || ''}
                          onChange={(e) => setObservations(prev => ({ ...prev, [item.id]: e.target.value }))}
                          className="w-full p-4 bg-red-50/30 border border-red-100 rounded-none text-sm text-slate-700 outline-none focus:border-red-300 resize-none h-24"
                        />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="bg-white border-t border-slate-100 p-6 lg:p-8 flex justify-end gap-3 shrink-0">
          <button 
            onClick={() => { if (activeSectionId < 14) setActiveSectionId(activeSectionId + 1); else setShowSummary(true); }} 
            className="px-10 py-3 bg-[#391694] hover:bg-[#2a106e] text-white font-bold rounded-none text-[13px] uppercase tracking-wider transition-all"
          >
            {activeSectionId === 14 ? 'Concluir' : 'Próximo'}
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col bg-white h-full border border-brand-200">
      <div className="flex flex-1 overflow-hidden h-full">
        {/* Sidebar Especializada */}
        <div className="w-64 bg-white border-r border-slate-100 flex flex-col shrink-0 overflow-y-auto">
          <div className="p-6 flex flex-col gap-4">
            
            {/* 1. Navegação Global - Fonte 12px */}
            <div className="space-y-1">
              <button 
                onClick={handleNewAudit} 
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-none text-[12px] font-bold text-left transition-colors ${viewMode === 'audit' && !showSummary && !isReadOnlyMode ? 'bg-indigo-50 text-brand-500 border-l-2 border-brand-500 pl-3' : 'text-slate-600 hover:bg-slate-50'}`}
              >
                <PlusCircle className="w-4 h-4 shrink-0" />
                Nova Auditoria
              </button>
              <button 
                onClick={() => { setViewMode('history'); setShowSummary(false); setActionMenuId(null); }} 
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-none text-[12px] font-bold text-left transition-colors ${viewMode === 'history' ? 'bg-indigo-50 text-brand-500 border-l-2 border-brand-500 pl-3' : 'text-slate-600 hover:bg-slate-50'}`}
              >
                <History className="w-4 h-4 shrink-0" />
                Registros
              </button>
            </div>

            {/* 2. Divisória Fina */}
            <div className="border-t border-slate-100 my-1" />

            {/* 3. Seção da Auditoria Ativa (Aeroporto -> Progresso -> Itens) */}
            {selectedAirport && viewMode === 'audit' && (
              <div className="space-y-6 animate-in fade-in duration-300">
                {/* Identificação do Aeroporto */}
                <div className="flex justify-center">
                  <div className="px-4 py-2 bg-indigo-50/50 text-brand-500 rounded-none text-[10px] font-black border border-indigo-100 uppercase tracking-widest text-center w-full">
                    {selectedAirport}
                  </div>
                </div>

                {/* Barra de Progresso */}
                {!showSummary && (
                  <div className="space-y-2">
                    <div className="flex justify-between items-end px-1">
                      <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Progresso</span>
                      <span className="text-[10px] font-bold text-brand-500">{answeredCount}/{totalItemsCount}</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-100 rounded-none overflow-hidden">
                      <div 
                        className="h-full bg-brand-500 transition-all duration-500 ease-out"
                        style={{ width: `${progressPercentage}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Lista de Itens 1-14 */}
                {!showSummary && (
                  <div className="pt-2 flex flex-col gap-1">
                    {VERIFICATION_SECTIONS.map((section) => (
                      <button 
                        key={section.id} 
                        onClick={() => setActiveSectionId(section.id)} 
                        className={`w-full text-left px-4 py-2 rounded-none text-[12px] font-semibold transition-all ${activeSectionId === section.id ? 'text-brand-500 bg-slate-50' : 'text-slate-500 hover:text-slate-800'}`}
                      >
                        {section.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden bg-white">
          {renderMainContent()}
        </div>
      </div>

      {isFinalizing && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
           <div className="bg-white rounded-none w-full max-w-sm shadow-2xl border border-slate-100">
              <div className="p-10 text-center">
                <div className="w-20 h-20 bg-emerald-50 rounded-none flex items-center justify-center mx-auto mb-6 border border-emerald-100">
                  <CheckCircle2 className="w-10 h-10 text-emerald-600" />
                </div>
                <h3 className="text-xl font-black text-slate-900 mb-2 tracking-tight uppercase">Auditoria Concluída</h3>
                <p className="text-sm text-slate-500 mb-8">O relatório de verificação AISWEB foi salvo com sucesso.</p>
                <button onClick={() => { setIsFinalizing(false); setViewMode('history'); setSelectedAirport(''); setShowSummary(false); setAnswers({}); setObservations({}); setSdiaCodes({}); }} className="w-full py-3 bg-brand-500 rounded-none text-xs font-black text-white uppercase tracking-widest shadow-lg shadow-indigo-900/20">OK</button>
              </div>
           </div>
        </div>
      )}
    </div>
  );
};
