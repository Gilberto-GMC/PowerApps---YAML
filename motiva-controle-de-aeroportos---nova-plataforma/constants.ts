
import { 
  Globe, 
  FileText, 
  AlertTriangle,
  LayoutGrid,
  PlaneLanding,
  ScanLine,
  ShieldCheck,
  Building,
  CloudLightning,
  Fan,
  Truck,
  Flag,
  Megaphone,
  ArrowRightLeft,
  Droplets,
  Trash2,
  Wind,
  AlertOctagon,
  Car,
  UserX,
  HardHat,
  FileQuestion,
  Accessibility,
  Scale,
  Zap,
  ShieldAlert,
  Eye,
  Activity,
  Locate,
  Bird,
  Flame,
  UserCheck
} from "lucide-react";
import { CategoryDefinition, ModuleItem } from "./types";

export const CATEGORIES: CategoryDefinition[] = [
  { 
    id: 'inspections', 
    label: 'Inspeções', 
    description: 'Rotinas de vistoria de infraestrutura e segurança operacional',
    colorClass: 'text-[#9A4222] bg-[#FFAC8B]/20 border-[#FFAC8B]/50',
    themeColor: '#FFAC8B'
  },
  { 
    id: 'operational', 
    label: 'Operacional', 
    description: 'Gestão de atividades de pátio, pista e recursos operacionais',
    colorClass: 'text-[#0E7490] bg-[#C2F6FF]/50 border-[#C2F6FF]',
    themeColor: '#0891b2'
  },
  { 
    id: 'fauna', 
    label: 'Fauna', 
    description: 'Gestão e monitoramento de risco aviário e fauna no sítio aeroportuário',
    colorClass: 'text-[#166534] bg-[#51FF62]/20 border-[#51FF62]/50',
    themeColor: '#51FF62'
  },
  { 
    id: 'safety_events', 
    label: 'Eventos de Segurança Operacional', 
    description: 'Reporte e gestão de ocorrências, perigos e eventos de risco no lado ar',
    colorClass: 'text-[#6b21a8] bg-[#F1C5FF]/30 border-[#F1C5FF]',
    themeColor: '#d946ef'
  },
  { 
    id: 'aeronautical_info', 
    label: 'Informações e Produtos Aeronáuticos', 
    description: 'Gestão de publicações, AISWEB e conformidade de dados aeronáuticos',
    colorClass: 'text-indigo-600 bg-indigo-50 border-indigo-100',
    themeColor: '#4F46E5'
  },
  { 
    id: 'orientation_program', 
    label: 'Programa de Orientação', 
    description: 'Gestão e acompanhamento do programa de orientação',
    colorClass: 'text-[#858316] bg-[#FFFD8A]/50 border-[#FFFD8A]',
    themeColor: '#FFFD8A'
  }
];

export const MODULES: ModuleItem[] = [
  // Inspeções
  { 
    id: 'insp-1', 
    title: 'Inspeção de Pátios', 
    category: 'inspections', 
    icon: LayoutGrid,
    description: 'Vistoria de condições de pavimento e sinalização dos pátios.'
  },
  { 
    id: 'insp-2', 
    title: 'Inspeção da Pista de Pouso e Decolagem e Pistas de Táxi', 
    category: 'inspections', 
    icon: PlaneLanding,
    description: 'Vistoria do sistema de pistas e auxílios visuais.'
  },
  { 
    id: 'insp-7', 
    title: 'Inspeção Especial (Extraordinária)', 
    category: 'inspections', 
    icon: ShieldAlert,
    description: 'Vistoria extraordinária de infraestrutura acionada por eventos específicos.'
  },
  { 
    id: 'insp-3', 
    title: 'Inspeção da Faixa de Pista', 
    category: 'inspections', 
    icon: ScanLine,
    description: 'Vistoria da área de segurança no entorno da pista.'
  },
  { 
    id: 'insp-4', 
    title: 'Inspeção do Sistema de Proteção', 
    category: 'inspections', 
    icon: ShieldCheck,
    description: 'Vistoria das cercas, muros e pontos de acesso controlado.'
  },
  { 
    id: 'insp-5', 
    title: 'Inspeção das Zonas de Proteção do Aeródromo', 
    category: 'inspections', 
    icon: Building,
    description: 'Monitoramento dos obstáculos no entorno do aeroporto.'
  },
  { 
    id: 'insp-6', 
    title: 'Inspeção do Ambulift', 
    category: 'inspections', 
    icon: Accessibility,
    description: 'Vistoria e checklist de segurança do equipamento Ambulift.'
  },

  // Operacional
  { 
    id: 'ops-1', 
    title: 'Aviso Meteorológico', 
    category: 'operational', 
    icon: CloudLightning,
    description: 'Emissão e consulta de alertas de condições adversas.'
  },
  { 
    id: 'ops-2', 
    title: 'Teste de Motores', 
    category: 'operational', 
    icon: Fan,
    description: 'Registro e autorização de giros de motor em áreas dedicadas.'
  },
  { 
    id: 'ops-3', 
    title: 'Vistoria de Veículos', 
    category: 'operational', 
    icon: Truck,
    description: 'Checklist de segurança para veículos que acessam a área restrita.'
  },
  { 
    id: 'ops-4', 
    title: 'Follow-Me de Aeronaves', 
    category: 'operational', 
    icon: Flag,
    description: 'Registro de balizamento e escolta de aeronaves no pátio.'
  },
  { 
    id: 'ops-5', 
    title: 'Embarque e Desembarque Híbrido', 
    category: 'operational', 
    icon: ArrowRightLeft,
    description: 'Coordenação de fluxo de passageiros em operações mistas.'
  },
  { 
    id: 'ops-6', 
    title: 'Ambulift', 
    category: 'operational', 
    icon: Accessibility,
    description: 'Registro de acionamento do veículo de embarque de passageiros com mobilidade reduzida.'
  },
  { 
    id: 'ops-7', 
    title: 'Controle de Sobrecarga', 
    category: 'operational', 
    icon: Scale,
    description: 'Monitoramento e registro de operações com peso ACN/ACR superior ao PCN/PCR.'
  },
  {
    id: 'ops-8',
    title: 'Acesso de Terceiros',
    category: 'operational',
    icon: UserCheck,
    description: 'Registro para acesso de terceiros que requerem apoio da equipe de Operações Aeroportuárias devido falta de credenciamento.'
  },

  // Fauna (NOVA SEÇÃO)
  { 
    id: 'fauna-1', 
    title: 'Reporte Mandatório de Fauna', 
    category: 'fauna', 
    icon: Zap,
    description: 'Registro de colisões (com ou sem dano) e quase colisões com aeronaves (birdstrike).'
  },
  { 
    id: 'fauna-5', 
    title: 'Presença de Fauna', 
    category: 'fauna', 
    icon: Activity,
    description: 'Monitoramento de rotina e censo de espécies dentro do sítio aeroportuário.'
  },
  { 
    id: 'fauna-6', 
    title: 'Foco de Atração de Fauna', 
    category: 'fauna', 
    icon: Trash2,
    description: 'Identificação e manejo de áreas de alimentação, nidificação ou repouso.'
  },

  // Eventos de Segurança Operacional
  { 
    id: 'safe-1', 
    title: 'Vazamentos em Área Operacional', 
    category: 'safety_events', 
    icon: Droplets,
    description: 'Registro de derramamento de combustível, óleo ou químicos no pátio.'
  },
  { 
    id: 'safe-2', 
    title: 'Detritos (F.O.Debris)', 
    category: 'safety_events', 
    icon: Trash2,
    description: 'Coleta e identificação de objetos estranhos na área de manobra.'
  },
  { 
    id: 'safe-10', 
    title: 'Dano por Detritos (F.O.Damage)', 
    category: 'safety_events', 
    icon: AlertTriangle,
    description: 'Registro de danos causados por detritos ou objetos estranhos (Foreign Object Debris).'
  },
  { 
    id: 'safe-3', 
    title: 'Jet-blast / Propeller-Wash', 
    category: 'safety_events', 
    icon: Wind,
    description: 'Acidentes ou incidentes causados por sopro de reatores ou hélices.'
  },
  { 
    id: 'safe-4', 
    title: 'Ocorrência de Solo', 
    category: 'safety_events', 
    icon: AlertOctagon,
    description: 'Acidentes ou incidentes envolvendo pessoal, equipamentos ou infraestrutura.'
  },
  { 
    id: 'safe-5', 
    title: 'Colisão de Veículos e/ou Equipamentos', 
    category: 'safety_events', 
    icon: Car,
    description: 'Ocorrências de trânsito na área operacional do aeroporto.'
  },
  { 
    id: 'safe-6', 
    title: 'Interferência Externa', 
    category: 'safety_events', 
    icon: UserX,
    description: 'Invasões de perímetro, presença de animais ou pessoas não autorizadas.'
  },
  { 
    id: 'safe-7', 
    title: 'Eventos Envolvendo Obras', 
    category: 'safety_events', 
    icon: HardHat,
    description: 'Incidentes relacionados a áreas em construção ou manutenção.'
  },
  { 
    id: 'safe-9', 
    title: 'Princípio de Incêndio', 
    category: 'safety_events', 
    icon: Flame,
    description: 'Registro de princípios de incêndio ocorridos na área operacional do aeroporto.'
  },
  { 
    id: 'safe-8', 
    title: 'Outras Ocorrências', 
    category: 'safety_events', 
    icon: FileQuestion,
    description: 'Relato de eventos não classificados nas categorias anteriores.'
  },

  // Info Aeronáutica
  { 
    id: 'aero-4', 
    title: 'Aviso Operacional (AVOP)', 
    category: 'aeronautical_info', 
    icon: Megaphone,
    description: 'Comunicados internos e alertas sobre a operação.'
  },
  { 
    id: 'aero-3', 
    title: 'Descumprimento AIS', 
    category: 'aeronautical_info', 
    icon: AlertTriangle,
    description: 'Reporte de desvio(s) praticados por Operadores Aéreos.'
  },
  { 
    id: 'aero-2', 
    title: 'NOTAMs / Suplementos AIP', 
    category: 'aeronautical_info', 
    icon: FileText,
    description: 'Controle de vencimento das informações temporárias.'
  },
  { 
    id: 'aero-1', 
    title: 'Informações Aeronáuticas - AISWEB', 
    category: 'aeronautical_info', 
    icon: Globe,
    description: 'Verificação periódica das informações publicadas.'
  },

  // Programa de Orientação
  { 
    id: 'orient-1', 
    title: 'Registros', 
    category: 'orientation_program', 
    icon: FileText,
    description: 'Registro e acompanhamento de orientações operacionais.'
  }
];
