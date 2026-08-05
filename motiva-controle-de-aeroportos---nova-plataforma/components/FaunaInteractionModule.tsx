import React, { useState } from 'react';
import { 
  PlusCircle, 
  History, 
  CheckCircle2, 
  ArrowRight,
  Calendar,
  AlertTriangle,
  Camera,
  Trash2,
  UploadCloud,
  MoreHorizontal,
  Eye,
  Pencil,
  Building2,
  FileSpreadsheet,
  ChevronDown,
  Bird,
  Plane
} from 'lucide-react';
import { AIRPORTS } from './AISComplianceForm';

interface FaunaInteractionRecord {
  id: string;
  airport: string;
  date: string;
  time: string;
  eventType: 'Colisão' | 'Quase Colisão' | 'Avistamento';
  aircraftRegistration: string;
  aircraftModel: string;
  aircraftOperator: string;
  flightPhase: string;
  flightEffect: string;
  species: string;
  flockSize: string;
  behavior: string;
  partStruck: string;
  damageAndLoss: 'Sim' | 'Indeterminado' | 'Não' | 'Não informado';
  description: string;
  crewAlerted: string;
  timeOfDay: string;
  skyCondition: string;
  precipitation: string;
  location: string;
  position: string;
  status: 'Em Análise' | 'Finalizado';
}

const MOCK_RECORDS: FaunaInteractionRecord[] = [
  {
    id: '1',
    airport: 'Aeroporto de Curitiba',
    date: '2024-05-25',
    time: '08:15',
    eventType: 'Colisão',
    aircraftRegistration: 'PR-XYZ',
    aircraftModel: 'A320',
    aircraftOperator: 'LATAM',
    flightPhase: 'Aproximação',
    flightEffect: 'Nenhum',
    species: 'Quero-quero (Vanellus chilensis)',
    flockSize: '1',
    behavior: 'Sobrevoando',
    partStruck: 'Trem de Pouso Principal',
    damageAndLoss: 'Não',
    description: 'Tripulação reportou colisão com ave durante a aproximação final. Inspeção de pista realizada e carcaça recolhida. Nenhum dano aparente na aeronave.',
    crewAlerted: 'ATIS',
    timeOfDay: 'Dia',
    skyCondition: 'Claro',
    precipitation: 'Nenhuma',
    location: 'Pista de Pouso e Decolagem',
    position: 'Cabeceira 15',
    status: 'Finalizado'
  },
  {
    id: '2',
    airport: 'Aeroporto de Goiânia',
    date: '2024-05-26',
    time: '17:40',
    eventType: 'Quase Colisão',
    aircraftRegistration: 'PS-AEF',
    aircraftModel: 'B738',
    aircraftOperator: 'Gol Linhas Aéreas',
    flightPhase: 'Decolagem',
    flightEffect: 'Decolagem abortada',
    species: 'Carcará (Caracara plancus)',
    flockSize: '2 a 10',
    behavior: 'Atravessando a via/pista',
    partStruck: 'N/A',
    damageAndLoss: 'Não',
    description: 'Aeronave precisou retardar a rotação devido a um bando de aves cruzando a pista. Não houve colisão.',
    crewAlerted: 'TWR',
    timeOfDay: 'Crepúsculo',
    skyCondition: 'Poucas Nuvens',
    precipitation: 'Nenhuma',
    location: 'Pista de Pouso e Decolagem',
    position: 'Terço médio',
    status: 'Em Análise'
  }
];

const FLIGHT_PHASES = [
  'Táxi',
  'Corrida de Decolagem',
  'Subida',
  'Em Rota',
  'Descida',
  'Aproximação',
  'Pouso',
  'Outra'
];

const FLIGHT_EFFECTS = [
  'Nenhum',
  'Desestabilizado na aproximação',
  'Não reportado',
  'Corte/apagamento de motor',
  'Decolagem abortada',
  'Arremetida',
  'Pouso de precaução',
  'Outros'
];

const CREW_ALERTED_OPTIONS = [
  'Não alertado',
  'ATIS',
  'APP',
  'TWR',
  'NOTAM/ROTAER'
];

const FLOCK_SIZES = [
  '1',
  '2 a 10',
  '11 a 50',
  '51 a 100',
  '100+'
];

const BEHAVIORS = [
  'Sobrevoando',
  'Pousado / Repousando',
  'Alimentando-se',
  'Nidificando (Ninho)',
  'Atravessando a via/pista',
  'Outro'
];

const SPECIES_OPTIONS = [
  'Ajajá/Colhereiro-americano (Platalea ajaja)',
  'Albatrozes / Família Diomedeidae',
  'Andorinha-de-bando/chaminé/de-pescoço-vermelho (Hirundo rustica)',
  'Andorinha-de-dorso-acanelado (Petrochelidon pyrrhonota)',
  'Andorinha-de-sobre-branco (Tachycineta leucorrhoa)',
  'Andorinha-do-campo (Progne tapera)',
  'Andorinha-do-rio/ribeirinha (Tachycineta albiventer)',
  'Andorinha-doméstica-grande (Progne chalybea)',
  'Andorinha-morena (Alopochelidon fucata)',
  'Andorinha-pequena-de-casa (Pygochelidon cyanoleuca)',
  'Andorinha-serradora (Stelgidopteryx ruficollis)',
  'Andorinhas / Família Hirundinidae',
  'Andorinhão-de-coleira/Taperuçu-de-coleira-branca (Streptoprocne zonaris)',
  'Andorinhão-do-buriti/poruti (Tachornis squamata)',
  'Andorinhão-do-temporal (Chaetura meridionalis)',
  'Andorinhões / taperuçus (Família Apodidae)',
  'Anhuma/ema-preta (Anhima cornuta)',
  'Anu preto/pequeno/coró-coró/ (Crotophaga ani)',
  'Anu-branco (Guira guira)',
  'Aracuã-pintado/araquã-pintada (Ortalis guttata)',
  'Araras/papagaios/periquitos // Família Psittacidae',
  'Asa-branca/marreca-cabocla/marajoara (Dendrocygna autumnalis)',
  'Asa-de-telha (Agelaioides badius)',
  'Atobás / Família Sulidae',
  'Águia-pescadora/gavião-pescador (Pandion haliaetus)',
  'Bacurau-de-asa-fina (Chordeiles acutipennis)',
  'Bacurau-tesoura/curiango-tesoura (Hydropsalis torquata)',
  'Bacurau/curiango-comum (Hydropsalis albicollis)',
  'Bacurau/curiango/ju-jau/caribamba/amanhã-eu-vou/ibijau/mede-léguas (Nyctidromus albicollis)',
  'Bacuraus/Curiangos // Família Caprimulgidae',
  'Bacurauzinho-da-caatinga (Hydropsalis hirundinacea)',
  'Bacurauzinho/bacurau-pequeno/-preto (Chordeiles pusillus)',
  'Batuíra-de-bando/agachada/norte-americana/pinga-pinga (Charadrius semipalmatus)',
  'Batuíra-de-coleira (Charadrius collaris)',
  'Batuiruçu (Pluvialis dominica)',
  'Beija-flor / Família Trochilidae',
  'Bem- te-vis / Família Tyrannidae',
  'Bem-te-vi (Pitangus sulphuratus)',
  'Biguatinga/mergulhão-serpente/calmaria (Anhinga anhinga)',
  'Biguá/mergulhão/miuá/pata-da-água/corvo-marinho (Phalacrocorax brasilianus)',
  'Cabeça-seca (Mycteria americana)',
  'Caminheiro-zumbidor/corredeira (Anthus lutescens)',
  'Canário-da-terra/Canarinho (Sicalis flaveola)',
  'Carão/garça-preta-do-brejo (Aramus guarauna)',
  'Carcará/carancho (Caracara plancus)',
  'Carrapateiro/caracaraí (Milvago chimachima)',
  'Chimango/chima-chima (Milvago chimango)',
  'Codorna-amarela/comum (Nothura maculosa)',
  'Codornas / Perdizes // Família Tinamidae',
  'Corucão/tabaco-bom (Chordeiles nacunda)',
  'Coruja -buraqueira (Athene cunicularia)',
  'Coruja-da-igreja/rasga-mortalha/suindara (Tyto furcata)',
  'Coruja-orelhuda/listrada/gato/mocho-orelhudo (Asio clamator)',
  'Corujas / Família Strigidae',
  'Corujinha-do-mato/caboré-de-orelha (Megascops choliba)',
  'Curicaca-comum (Theristicus caudatus)',
  'Curicacas/Tapicurus // Família Threskiornithidae',
  'Estorninho (Sturnus vulgaris)',
  'Falcão-de-coleira/gavião-pombo/cauré (Falco femoralis)',
  'Falcão-peregrino (Falco peregrinus)',
  'Falcão-quiriquiri (Falco sparverius)',
  'Falcões / Família Falconidae',
  'Fragata/tesourão (Fregata magnificens)',
  'Frango-da-água-comum/galinhola/jaçanã-galo (Gallinula galeata)',
  'Gaivota-de-cabeça-cinza (Chroicocephalus cirrocephalus)',
  'Gaivotas / Família Laridae',
  'Gansos / Família Anatidae',
  'Garça-branca-grande (Ardea alba)',
  'Garça-branca-pequena (Egretta thula)',
  'Garça-cinzenta/socó/savacu (Nycticorax nycticorax)',
  'Garça-moura (Ardea cocoi)',
  'Garça-vaqueira/cunacoi/boiadeira (Bubulcus ibis)',
  'Garças / Família Ardeidae',
  'Gaviao-tesoura (Elanoides forficatus)',
  'Gavião-asa-de-telha (Parabuteo unicinctus)',
  'Gavião-caboclo/fumaça/tinga (Heterospizias meridionalis)',
  'Gavião-carijó (Rupornis magnirostris)',
  'Gavião-de-cauda-curta (Buteo brachyurus)',
  'Gavião-de-rabo-barrado/gavião-urubu (Buteo albonotatus)',
  'Gavião-de-rabo-branco/curucuturi (Geranoaetus albicaudatus)',
  'Gavião-do-banhado/mangue (Circus buffoni)',
  'Gavião-peneira/peneirador (Elanus leucurus)',
  'Gavião-preto/caipira/fumaça/urubutinga (Urubitinga urubitinga)',
  'Gaviões / Família accipitridae',
  'Graúna/chopim/melro/assum-preto/pássaro-preto (Gnorimopsar chopi)',
  'Irerê/paturi/siriri (Dendrocygna viduata)',
  'Jaçanã/narceja (Jacana jacana)',
  'Jacamaraçu (Jacamerops aureus)',
  'Maçarico-do-campo (Bartramia longicauda)',
  'Maçaricos / Família Scolopacidae',
  'Maguari/jaburu-moleque (Ciconia maguari)',
  'Mandriões / Família Stercorariidae',
  'Maracanã-do-buriti/-de-cara-amarela/arararana (Orthopsittaca manilatus)',
  'Maria-faceira (Syrigma sibilatrix)',
  'Marreca-ananai/pé-vermelho (Amazonetta brasiliensis)',
  'Marreca-cricri/pato-argentino/quiri-quiri (Spatula versicolor)',
  'Marreca-parda (Anas georgica)',
  'Marreca-toicinho/queixo-branco/paturi-do-mato (Anas bahamensis)',
  'Marrecas / patos // Família Anatidae',
  'Martim-pescador / Família Alcedinidae',
  'Mergulhão-grande (Podicephorus major)',
  'Mergulhões / Família Podicipedidae',
  'Mutum-cavalo (Pauxi tuberosa)',
  'Mutum-de-penacho (Crax fasciolata)',
  'Mutuns / Família Cracidae',
  'Narceja (Gallinago paraguaiae)',
  'Noivinha-branca (Xolmis velatus)',
  'Papagaio-galego/-de-barriga-amarela/-curraleiro/-curau/-goiaba (Alipiopsitta xanthops)',
  'Papagaio-verdadeiro (Amazona aestiva)',
  'Pardal (Passer domesticus)',
  'Pato-do-mato (Cairina moschata)',
  'Pavão (Pavo cristatus)',
  'Pavãozinho-do-pará/pavão (Eurypyga helias)',
  'Perdiz/perdigão/napopé/inhambupé (Rhynchotus rufescens)',
  'Periquitão-maracanã/aratinga-de-bando (Psittacara leucophthalmus)',
  'Periquito-da-caatinga/jandaia/gangarra (Eupsittula cactorum)',
  'Periquito-de-encontro-amarelo/asa-amarela/estrela (Brotogeris chiriri)',
  'Periquito-rei (Eupsittula aurea)',
  'Pica-paus / Família Picidae',
  'Polícia-inglesa-do-norte (Sturnella militaris)',
  'Polícia-inglesa-do-sul/furacao-do-arroz/papa-arroz (Sturnella superciliaris)',
  'Pomba-de-bando/arribaçã/arribação (Zenaida auriculata)',
  'Pomba-galega/pocaçu (Patagioenas cayennensis)',
  'Pombão/asa-branca/legítima/carijó (Patagioenas picazuro)',
  'Pombinha-escamada/fogo-apagou (Columbina squammata)',
  'Pombo-doméstico (Columba livia)',
  'Pombos / Rolinhas // Família Columbidae',
  'Primavera (Xolmis cinereus)',
  'Quero-quero/tetéu (Vanellus chilensis)',
  'Rolinha-cinzenta (Columbina passerina)',
  'Rolinha-picuí (Columbina picui)',
  'Rolinha-roxa/barreirinha/caldo-de-feijão/grande (Columbina talpacoti)',
  'Saracura-sana/preta/franguinho-dagua (Pardirallus nigricans)',
  'Saracura-três-potes/-do-brejo (Aramides cajaneus)',
  'Savacu (Nycticorax nycticorax)',
  'Savacu-de-coroa',
  'Seriema (Cariama cristata)',
  'Soco-boi (Tigrisoma lineatum)',
  'Socozinho/socó-tripa (Butorides striata)',
  'Suiriri (Tyrannus melancholicus)',
  'Suiriri-cavaleiro/do-campo/monta-cavalo (Machetornis rixosa)',
  'Tachã/chajá (Chauna torquata)',
  'Talha-mar/corta-água (Rynchops niger)',
  'Tapicuru-de-cara-pelada (Phimosus infuscatus)',
  'Téu-téu-da-savana (Burhinus bistriatus)',
  'Tesourinha (Tyrannus savana)',
  'Trinta-réis / Família Sternidae',
  'Trinta-réis-grande (Phaetusa simplex)',
  'Tucanos / Família Ramphastidae',
  'Tuiuiú/jaburu (Jabiru mycteria)',
  'Urubu-da-mata (Cathartes melambrotus)',
  'Urubu-de-cabeça-amarela (Cathartes burrovianus)',
  'Urubu-de-cabeça-preta/corvo/apitã (Coragyps atratus)',
  'Urubu-de-cabeça-vermelha (Cathartes aura)',
  'Urubus / Família Cathartidae',
  'xx Outros (anfíbios)',
  'xx Outros (bovinos)',
  'xx Outros (cachorro doméstico OU selvagem) > 1,5 kg',
  'xx Outros (cachorro doméstico) > 1,5 kg',
  'xx Outros (cachorro selvagem) > 1,5 kg',
  'xx Outros (Capivara - Hydrochoerus hydrochaeris)',
  'xx Outros (Ema - Rhea americana)',
  'xx Outros (equinos)',
  'xx Outros (gato doméstico) > 1,5 kg',
  'xx Outros (Lebre-comum ou Lebre-europeia - Lepus europaeus)',
  'xx Outros (mamíferos > 1,5 kg)',
  'xx Outros (morcegos)',
  'xx Outros (répteis > 1,5 kg)',
  'xx Passeriformes pequenos'
];

const AIRCRAFT_PARTS = [
  'Radome / Nariz',
  'Para-brisa',
  'Motor (Esquerdo)',
  'Motor (Direito)',
  'Hélice',
  'Asa / Flap',
  'Fuselagem',
  'Trem de Pouso',
  'Cauda / Leme',
  'Luzes / Antenas',
  'Múltiplas Partes',
  'Desconhecido'
];

const TIME_OF_DAY = [
  'Alvorada',
  'Dia',
  'Crepúsculo',
  'Noite'
];

const SKY_CONDITIONS = [
  'Claro',
  'Poucas Nuvens',
  'Encoberto'
];

const PRECIPITATION = [
  'Nenhuma',
  'Nevoeiro',
  'Chuva',
  'Chuva Recente'
];

const LOCATIONS = [
  'Pátio de Estacionamento',
  'Pista de Táxi',
  'Pista de Pouso e Decolagem',
  'Via de serviço',
  'Pátio de Hangar',
  'Área de Equipamentos',
  'Terminal de Passageiros',
  'Terminal de Cargas',
  'Outro'
];

const INITIAL_FORM_DATA = {
  airport: '',
  date: new Date().toISOString().split('T')[0],
  time: '',
  eventType: 'Colisão' as 'Colisão' | 'Quase Colisão' | 'Avistamento',
  aircraftRegistration: '',
  aircraftModel: '',
  aircraftOperator: '',
  flightPhase: '',
  flightEffect: '',
  species: '',
  flockSize: '1',
  behavior: '',
  partStruck: '',
  damageAndLoss: 'Não' as 'Sim' | 'Indeterminado' | 'Não' | 'Não informado',
  description: '',
  crewAlerted: '',
  timeOfDay: '',
  skyCondition: '',
  precipitation: '',
  location: '',
  position: ''
};

export const FaunaInteractionModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'history'>('form');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [records, setRecords] = useState<FaunaInteractionRecord[]>(MOCK_RECORDS);
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  
  const [actionMenuId, setActionMenuId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  const [filterAirport, setFilterAirport] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const [formData, setFormData] = useState(INITIAL_FORM_DATA);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedImages([...selectedImages, ...Array.from(e.target.files)]);
    }
  };

  const removeImage = (index: number) => {
    const newImages = [...selectedImages];
    newImages.splice(index, 1);
    setSelectedImages(newImages);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    setTimeout(() => {
      const newRecord: FaunaInteractionRecord = {
        id: editingId || Math.random().toString(36).substr(2, 9),
        ...formData,
        status: 'Em Análise'
      };

      if (editingId) {
        setRecords(records.map(r => r.id === editingId ? newRecord : r));
      } else {
        setRecords([newRecord, ...records]);
      }

      setIsSubmitting(false);
      setActiveTab('history');
      setFormData(INITIAL_FORM_DATA);
      setSelectedImages([]);
      setEditingId(null);
    }, 1500);
  };

  const handleEdit = (record: FaunaInteractionRecord) => {
    setFormData({
      airport: record.airport,
      date: record.date,
      time: record.time,
      eventType: record.eventType,
      aircraftRegistration: record.aircraftRegistration,
      aircraftModel: record.aircraftModel,
      aircraftOperator: record.aircraftOperator,
      flightPhase: record.flightPhase,
      flightEffect: record.flightEffect || '',
      species: record.species,
      flockSize: record.flockSize,
      behavior: record.behavior || '',
      partStruck: record.partStruck,
      damageAndLoss: record.damageAndLoss || 'Não',
      description: record.description,
      crewAlerted: record.crewAlerted || '',
      timeOfDay: record.timeOfDay || '',
      skyCondition: record.skyCondition || '',
      precipitation: record.precipitation || '',
      location: record.location || '',
      position: record.position || ''
    });
    setEditingId(record.id);
    setActiveTab('form');
    setActionMenuId(null);
  };

  const filteredRecords = records.filter(record => {
    const matchesAirport = filterAirport === '' || record.airport === filterAirport;
    const recordDate = new Date(record.date);
    const start = startDate ? new Date(startDate) : null;
    const end = endDate ? new Date(endDate) : null;
    const matchesDate = (!start || recordDate >= start) && (!end || recordDate <= end);
    return matchesAirport && matchesDate;
  });

  return (
    <div className="flex flex-col gap-[26px] relative h-full w-full">
      <h2 className="text-[26px] font-bold text-slate-900 tracking-tight leading-tight uppercase shrink-0 flex items-center gap-3">
        Reporte Mandatório de Fauna
      </h2>

      <div className="flex p-1 bg-slate-50 rounded-none w-fit border border-slate-200 shrink-0">
        <button
          onClick={() => { setActiveTab('form'); setEditingId(null); setFormData(INITIAL_FORM_DATA); }}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-none text-[13px] font-bold transition-all ${activeTab === 'form' ? 'bg-white text-[#391694] shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}
        >
          <PlusCircle className="w-4 h-4" />
          {editingId ? 'Editar Reporte' : 'Novo Registro'}
        </button>
        <button
          onClick={() => { setActiveTab('history'); setEditingId(null); setFormData(INITIAL_FORM_DATA); }}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-none text-[13px] font-bold transition-all ${activeTab === 'history' ? 'bg-white text-[#391694] shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}
        >
          <History className="w-4 h-4" />
          Registros
        </button>
      </div>

      <div className="flex-1 overflow-visible">
        {activeTab === 'form' ? (
          <div className="max-w-5xl animate-in fade-in duration-500 pb-10">
            {isSubmitting ? (
              <div className="flex flex-col items-center justify-center py-24 text-center animate-in zoom-in duration-300">
                <div className="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mb-6">
                  <CheckCircle2 className="w-10 h-10 text-emerald-600 animate-pulse" />
                </div>
                <h3 className="text-2xl font-bold text-slate-900 mb-2">Processando Registro...</h3>
                <p className="text-slate-500">As informações estão sendo arquivadas para análise técnica.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-[26px]">
                {/* Tipo de Evento */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Tipo de Evento <span className="text-red-500">*</span></label>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-[26px]">
                    {['Colisão', 'Quase Colisão', 'Avistamento'].map((option) => (
                      <button
                        key={option}
                        type="button"
                        onClick={() => setFormData({...formData, eventType: option as any})}
                        className={`w-full py-4 px-4 border rounded-none font-bold text-xs uppercase transition-all ${formData.eventType === option ? 'bg-[#391694] text-white border-[#391694]' : 'bg-white text-slate-400 border-slate-200 hover:bg-slate-50'}`}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Aeroporto e Data/Hora */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Aeroporto <span className="text-red-500">*</span></label>
                    <div className="relative">
                      <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.airport} onChange={(e) => setFormData({...formData, airport: e.target.value})}>
                        <option value="">Selecione...</option>
                        {AIRPORTS.map(ap => <option key={ap} value={ap}>{ap}</option>)}
                      </select>
                      <Building2 className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Data do Evento <span className="text-red-500">*</span></label>
                    <input required type="date" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium" value={formData.date} onChange={(e) => setFormData({...formData, date: e.target.value})} />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Hora do Evento (UTC) <span className="text-red-500">*</span></label>
                    <input required type="time" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium" value={formData.time} onChange={(e) => setFormData({...formData, time: e.target.value})} />
                  </div>
                </div>

                {/* Condições e Local */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Parte do dia <span className="text-red-500">*</span></label>
                    <div className="relative">
                      <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.timeOfDay} onChange={(e) => setFormData({...formData, timeOfDay: e.target.value})}>
                        <option value="">Selecione...</option>
                        {TIME_OF_DAY.map(time => <option key={time} value={time}>{time}</option>)}
                      </select>
                      <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Condições do Céu <span className="text-red-500">*</span></label>
                    <div className="relative">
                      <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.skyCondition} onChange={(e) => setFormData({...formData, skyCondition: e.target.value})}>
                        <option value="">Selecione...</option>
                        {SKY_CONDITIONS.map(cond => <option key={cond} value={cond}>{cond}</option>)}
                      </select>
                      <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Precipitação <span className="text-red-500">*</span></label>
                    <div className="relative">
                      <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.precipitation} onChange={(e) => setFormData({...formData, precipitation: e.target.value})}>
                        <option value="">Selecione...</option>
                        {PRECIPITATION.map(precip => <option key={precip} value={precip}>{precip}</option>)}
                      </select>
                      <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-[26px]">
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Local Geral <span className="text-red-500">*</span></label>
                    <div className="relative">
                      <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.location} onChange={(e) => setFormData({...formData, location: e.target.value})}>
                        <option value="">Selecione o local...</option>
                        {LOCATIONS.map(loc => <option key={loc} value={loc}>{loc}</option>)}
                      </select>
                      <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[13px] font-bold text-slate-900 block">Posição Detalhada <span className="text-red-500">*</span></label>
                    <input required type="text" placeholder="Ex: Cabeceira 15, próximo ao pátio 2..." className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium" value={formData.position} onChange={(e) => setFormData({...formData, position: e.target.value})} />
                  </div>
                </div>

                {/* Aeronave */}
                <div className="border border-slate-100 p-6 bg-slate-50/30">
                  <h3 className="text-[13px] font-bold text-slate-800 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <Plane className="w-4 h-4" /> Aeronave Envolvida
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[26px]">
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Matrícula <span className="text-red-500">*</span></label>
                      <input required type="text" placeholder="Ex: PR-XYZ" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium uppercase" value={formData.aircraftRegistration} onChange={(e) => setFormData({...formData, aircraftRegistration: e.target.value})} />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Modelo <span className="text-red-500">*</span></label>
                      <input required type="text" placeholder="Ex: B738" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium uppercase" value={formData.aircraftModel} onChange={(e) => setFormData({...formData, aircraftModel: e.target.value})} />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Operador <span className="text-red-500">*</span></label>
                      <input required type="text" placeholder="Ex: Gol Linhas Aéreas" className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium" value={formData.aircraftOperator} onChange={(e) => setFormData({...formData, aircraftOperator: e.target.value})} />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Fase do Voo <span className="text-red-500">*</span></label>
                      <div className="relative">
                        <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.flightPhase} onChange={(e) => setFormData({...formData, flightPhase: e.target.value})}>
                          <option value="">Selecione...</option>
                          {FLIGHT_PHASES.map(phase => <option key={phase} value={phase}>{phase}</option>)}
                        </select>
                        <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Efeito no Voo <span className="text-red-500">*</span></label>
                      <div className="relative">
                        <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.flightEffect} onChange={(e) => setFormData({...formData, flightEffect: e.target.value})}>
                          <option value="">Selecione...</option>
                          {FLIGHT_EFFECTS.map(effect => <option key={effect} value={effect}>{effect}</option>)}
                        </select>
                        <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Detalhes da Fauna */}
                <div className="border border-slate-100 p-6 bg-slate-50/30">
                  <h3 className="text-[13px] font-bold text-slate-800 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <Bird className="w-4 h-4" /> Detalhes da Fauna e Colisão
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[26px]">
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Espécie Envolvida/Suspeita <span className="text-red-500">*</span></label>
                      <div className="relative">
                        <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.species} onChange={(e) => setFormData({...formData, species: e.target.value})}>
                          <option value="">Selecione...</option>
                          {SPECIES_OPTIONS.map(species => <option key={species} value={species}>{species}</option>)}
                        </select>
                        <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Tamanho do Bando <span className="text-red-500">*</span></label>
                      <div className="relative">
                        <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.flockSize} onChange={(e) => setFormData({...formData, flockSize: e.target.value})}>
                          {FLOCK_SIZES.map(size => <option key={size} value={size}>{size}</option>)}
                        </select>
                        <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Comportamento Observado <span className="text-red-500">*</span></label>
                      <div className="relative">
                        <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.behavior} onChange={(e) => setFormData({...formData, behavior: e.target.value})}>
                          <option value="">Selecione...</option>
                          {BEHAVIORS.map(behavior => <option key={behavior} value={behavior}>{behavior}</option>)}
                        </select>
                        <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Parte Atingida da Aeronave <span className="text-red-500">*</span></label>
                      <div className="relative">
                        <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.partStruck} onChange={(e) => setFormData({...formData, partStruck: e.target.value})}>
                          <option value="">Selecione...</option>
                          {AIRCRAFT_PARTS.map(part => <option key={part} value={part}>{part}</option>)}
                        </select>
                        <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[13px] font-bold text-slate-900 block">Danos e Prejuízo <span className="text-red-500">*</span></label>
                      <div className="relative">
                        <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.damageAndLoss} onChange={(e) => setFormData({...formData, damageAndLoss: e.target.value as any})}>
                          <option value="">Selecione...</option>
                          {['Sim', 'Indeterminado', 'Não', 'Não informado'].map(opt => <option key={opt} value={opt}>{opt}</option>)}
                        </select>
                        <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Descrição */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Descrição do Evento <span className="text-red-500">*</span></label>
                  <textarea required rows={4} placeholder="Descreva detalhadamente como ocorreu a interação, reportes da tripulação, ações tomadas (ex: inspeção de pista) e danos observados..." className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all font-medium resize-none" value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} />
                </div>

                {/* Tripulação Alertada */}
                <div className="space-y-2">
                  <label className="text-[13px] font-bold text-slate-900 block">Tripulação Alertada para Presença de Fauna? <span className="text-red-500">*</span></label>
                  <div className="relative md:w-1/3">
                    <select required className="w-full px-5 py-4 bg-white border border-slate-200 rounded-none text-[13px] text-slate-700 outline-none focus:border-[#c026d3] transition-all appearance-none cursor-pointer font-medium" value={formData.crewAlerted} onChange={(e) => setFormData({...formData, crewAlerted: e.target.value})}>
                      <option value="">Selecione...</option>
                      {CREW_ALERTED_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                    </select>
                    <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                  </div>
                </div>

                {/* Fotos */}
                <div className="border-t border-slate-100 pt-6">
                  <h3 className="text-sm font-bold text-slate-800 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <Camera className="w-4 h-4" /> Registro Fotográfico e Evidências
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    {selectedImages.map((file, index) => (
                      <div key={index} className="relative aspect-square bg-slate-100 border border-slate-200 group">
                        <img src={URL.createObjectURL(file)} alt="Preview" className="w-full h-full object-cover" />
                        <button type="button" onClick={() => removeImage(index)} className="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"><Trash2 className="w-4 h-4" /></button>
                      </div>
                    ))}
                    <label className="flex flex-col items-center justify-center aspect-square border-2 border-dashed border-slate-300 bg-slate-50 hover:bg-purple-50 hover:border-[#c026d3] hover:text-[#c026d3] transition-all cursor-pointer group text-slate-400">
                      <input type="file" multiple accept="image/*" className="hidden" onChange={handleImageChange} />
                      <UploadCloud className="w-8 h-8 mb-2 group-hover:scale-110 transition-transform" />
                      <span className="text-xs font-bold uppercase text-center px-2">Anexar Evidências</span>
                    </label>
                  </div>
                </div>

                <div className="flex justify-end pt-4">
                  <button type="submit" className="flex items-center gap-3 bg-black text-white px-10 py-4 rounded-none font-bold shadow-lg hover:scale-105 transition-all group">
                    <span>Finalizar Reporte</span>
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              </form>
            )}
          </div>
        ) : (
          <div className="flex flex-col min-h-0 animate-in fade-in duration-500 w-full">
            {/* Filtros */}
            <div className="flex flex-col lg:flex-row gap-4 items-center justify-between bg-slate-50 p-4 rounded-none border border-slate-200 mb-[26px] shrink-0 w-full">
              <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">
                <div className="relative min-w-[240px]">
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
                <div className="flex items-center gap-2 bg-white border border-slate-200 rounded-none px-3 h-10 shadow-sm">
                  <Calendar className="w-4 h-4 text-slate-400 shrink-0" />
                  <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="text-xs font-medium text-slate-700 outline-none cursor-pointer bg-transparent" />
                  <span className="text-slate-300">|</span>
                  <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="text-xs font-medium text-slate-700 outline-none cursor-pointer bg-transparent" />
                </div>
              </div>
              <button className="flex items-center gap-2 px-6 h-10 bg-[#391694] text-white rounded-none text-xs font-bold hover:bg-[#2a106e] transition-colors shadow-sm w-full lg:w-auto">
                <FileSpreadsheet className="w-4 h-4" /> Exportar
              </button>
            </div>

            {/* Tabela */}
            <div className="bg-white border border-slate-200 rounded-none shadow-sm relative overflow-x-auto w-full min-h-[320px]">
              <table className="w-full text-center border-separate border-spacing-0">
                <thead>
                  <tr className="bg-slate-50">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 whitespace-nowrap text-center">Data/Hora</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Aeronave</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center">Fauna / Espécie</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 text-center whitespace-nowrap">Tipo de Evento</th>
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
 <div className="flex flex-col items-center">
 <span className="text-xs font-bold text-slate-900 uppercase">{record.aircraftRegistration}</span>
 <span className="text-[10px] text-slate-500 font-medium">{record.aircraftModel} - {record.flightPhase}</span>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <div className="flex flex-col items-center">
 <span className="text-xs font-semibold text-slate-900">{record.species}</span>
 <span className="text-[10px] text-slate-500 font-medium">Bando: {record.flockSize}</span>
 </div>
 </td>
                      <td className="px-6 py-4 text-center">
 <span className={`text-[10px] font-bold px-2 py-1 uppercase border ${
 record.eventType === 'Colisão' ? 'bg-red-50 text-red-600 border-red-200' : 
 record.eventType === 'Quase Colisão' ? 'bg-orange-50 text-orange-600 border-orange-200' : 
 'bg-blue-50 text-blue-600 border-blue-200'
 }`}>
 {record.eventType}
 </span>
 </td>
                      <td className="px-6 py-4 text-center relative">
 <button onClick={(e) => { e.stopPropagation(); setActionMenuId(actionMenuId === record.id ? null : record.id); }} className={`p-1.5 rounded-none transition-all ${actionMenuId === record.id ? 'bg-[#c026d3] text-white shadow-md' : 'text-slate-400 hover:text-[#c026d3] hover:bg-purple-50 border border-slate-200'}`}><MoreHorizontal className="w-5 h-5" /></button>
 {actionMenuId === record.id && (
 <div className={`absolute z-50 right-14 w-44 bg-white border border-slate-200 rounded-none shadow-2xl overflow-hidden animate-in fade-in slide-in-from-right-2 duration-200 ${
 isLastRows ? 'bottom-0' : 'top-1/2 -translate-y-1/2'
 }`}>
 <button onClick={() => setActionMenuId(null)} className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"><Eye className="w-3.5 h-3.5" /> Ver Detalhes</button>
 <button onClick={() => handleEdit(record)} className="w-full text-left px-4 py-3 text-[11px] font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50"><Pencil className="w-3.5 h-3.5" /> Editar</button>
 <button onClick={() => { setDeleteId(record.id); setActionMenuId(null); }} className="w-full text-left px-4 py-3 text-[11px] font-bold text-red-600 hover:bg-red-50 flex items-center gap-3"><Trash2 className="w-3.5 h-3.5" /> Excluir</button>
 </div>
 )}
 </td>
                    </tr>
                  )})}
                  {filteredRecords.length === 0 && (
                    <tr>
                      <td colSpan={5} className="py-12 text-center text-slate-400">
 Nenhum registro encontrado.
 </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            <div className="bg-slate-50 px-6 py-3 border border-t-0 border-slate-200 text-[10px] text-slate-400 font-bold uppercase tracking-widest">{filteredRecords.length} REGISTROS ENCONTRADOS</div>
          </div>
        )}
      </div>

      {actionMenuId && <div className="fixed inset-0 z-40 bg-transparent" onClick={() => setActionMenuId(null)}></div>}
      
      {deleteId && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-white rounded-none w-full max-w-sm shadow-2xl border border-slate-100 overflow-hidden">
            <div className="p-8 text-center">
              <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6 border border-red-100"><AlertTriangle className="w-8 h-8 text-red-500" /></div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Confirmar Exclusão?</h3>
              <p className="text-slate-500 text-sm leading-relaxed mb-6">Esta ação removerá permanentemente o registro do banco de dados.</p>
            </div>
            <div className="p-4 bg-slate-50 border-t border-slate-100 flex gap-3">
              <button onClick={() => setDeleteId(null)} className="flex-1 py-3 bg-white border border-slate-200 rounded-none text-xs font-bold text-slate-600 hover:bg-slate-100">Cancelar</button>
              <button onClick={() => { setRecords(records.filter(r => r.id !== deleteId)); setDeleteId(null); }} className="flex-1 py-3 bg-red-600 rounded-none text-xs font-bold text-white hover:bg-red-700 shadow-lg shadow-red-900/20">Confirmar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
