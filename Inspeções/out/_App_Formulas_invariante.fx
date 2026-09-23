// ══════════════════════════════════════════════════════════════════════════════
// App.Formulas — Inspeções. Named formulas são avaliadas sob demanda e memoizadas:
// tiram carga do OnStart e do OnVisible. Tabelas copiadas byte a byte do export.
// ══════════════════════════════════════════════════════════════════════════════

// ── TABELAS FIXAS (saem do OnStart e do OnVisible de frmHomePista)
nfAeros = Table(
    {
            IATA: "",
            ICAO: "",
            Bloco: "CENTRAL",
            Aeroporto: "",
            Cluster: ""
        },
    {
            IATA: "GYN",
            ICAO: "SBGO",
            Bloco: "CENTRAL",
            Aeroporto: "GOIÂNIA",
            Cluster: "GOIÂNIA"
        },
    {
            IATA: "IMP",
            ICAO: "SBIZ",
            Bloco: "CENTRAL",
            Aeroporto: "IMPERATRIZ",
            Cluster: "GOIÂNIA"
        },
    {
            IATA: "PMW",
            ICAO: "SBPJ",
            Bloco: "CENTRAL",
            Aeroporto: "PALMAS",
            Cluster: "GOIÂNIA"
        },
    {
            IATA: "PLU",
            ICAO: "SBBH",
            Bloco: "CENTRAL",
            Aeroporto: "PAMPULHA",
            Cluster: "GOIÂNIA"
        },
    {
            IATA: "PNZ",
            ICAO: "SBPL",
            Bloco: "CENTRAL",
            Aeroporto: "PETROLINA",
            Cluster: "SÃO LUÍS"
        },
    {
            IATA: "SLZ",
            ICAO: "SBSL",
            Bloco: "CENTRAL",
            Aeroporto: "SÃO LUIS",
            Cluster: "SÃO LUÍS"
        },
    {
            IATA: "THE",
            ICAO: "SBTE",
            Bloco: "CENTRAL",
            Aeroporto: "TERESINA",
            Cluster: "SÃO LUÍS"
        },
    {
            IATA: "",
            ICAO: "",
            Bloco: "SUL",
            Aeroporto: "",
            Cluster: ""
        },
    {
            IATA: "BFH",
            ICAO: "SBBI",
            Bloco: "SUL",
            Aeroporto: "BACACHERI",
            Cluster: "CURITIBA"
        },
    {
            IATA: "CWB",
            ICAO: "SBCT",
            Bloco: "SUL",
            Aeroporto: "CURITIBA",
            Cluster: "CURITIBA"
        },
    {
            IATA: "JOI",
            ICAO: "SBJV",
            Bloco: "SUL",
            Aeroporto: "JOINVILLE",
            Cluster: "CURITIBA"
        },
    {
            IATA: "NVT",
            ICAO: "SBNF",
            Bloco: "SUL",
            Aeroporto: "NAVEGANTES",
            Cluster: "CURITIBA"
        },
    {
            IATA: "BGX",
            ICAO: "SBBG",
            Bloco: "SUL",
            Aeroporto: "BAGÉ",
            Cluster: "FOZ DO IGUAÇU"
        },
    {
            IATA: "IGU",
            ICAO: "SBFI",
            Bloco: "SUL",
            Aeroporto: "FOZ DO IGUAÇU",
            Cluster: "FOZ DO IGUAÇU"
        },
    {
            IATA: "LDB",
            ICAO: "SBLO",
            Bloco: "SUL",
            Aeroporto: "LONDRINA",
            Cluster: "FOZ DO IGUAÇU"
        },
    {
            IATA: "PET",
            ICAO: "SBPK",
            Bloco: "SUL",
            Aeroporto: "PELOTAS",
            Cluster: "FOZ DO IGUAÇU"
        },
    {
            IATA: "URG",
            ICAO: "SBUG",
            Bloco: "SUL",
            Aeroporto: "URUGUAIANA",
            Cluster: "FOZ DO IGUAÇU"
        }
);

nfParametrosAnimais = Table(
    {
                especie: "Andorinhas/Andorinhões (Hirundinidae e Apodidae)",
                tamanho: "MP (<50g)",
                tipo: "Ave"
            },
    {
                especie: "Anhuma ( Anhima cornuta)",
                tamanho: "MG (>1500g)",
                tipo: "Ave"
            },
    {
                especie: "Anu Branco (Guira guira)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Anu Preto (Crotophaga ani)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Ave Tachã (Chauna torquata)",
                tamanho: "MG (>1500g)",
                tipo: "Ave"
            },
    {
                especie: "Bacurau (Hydropsalis albicollis)",
                tamanho: "MP (<50g)",
                tipo: "Ave"
            },
    {
                especie: "Beija-Flor de orelha Violeta (Chlorostilbon lucidus)",
                tamanho: "MP (<50g)",
                tipo: "Ave"
            },
    {
                especie: "Beija-Flor de peito Azul (Amazilia lactea)",
                tamanho: "MP (<50g)",
                tipo: "Ave"
            },
    {
                especie: "Beija-Flor-Tesoura (Eupetomena macroura)",
                tamanho: "MP (<50g)",
                tipo: "Ave"
            },
    {
                especie: "Bem-te-vi (Pitangus sulfuratus)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Biguá (Nannopterum brasilianus)",
                tamanho: "G (751 a 1500g)",
                tipo: "Ave"
            },
    {
                especie: "Cachorro Doméstico (Canis lúpus familiaris)",
                tamanho: "MG (>1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Cachorro-do-Mato (Cerdocyon thous)",
                tamanho: "MG (>1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Cambacica(Coereba flaveola)",
                tamanho: "MP (<50g)",
                tipo: "Ave"
            },
    {
                especie: "Canário (Sicalis flaveola)",
                tamanho: "MP (<50g)",
                tipo: "Ave"
            },
    {
                especie: "Capivara (Hydrochoerus)",
                tamanho: "MG (>1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Carcará (Caracara plancus)",
                tamanho: "G (751 a 1500g)",
                tipo: "Ave"
            },
    {
                especie: "Carrapateiro (Milvago chimachima)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Cavalo Doméstico (Equus ferus caballus)",
                tamanho: "MG (>1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Chupim (Molothrus bonariensis)",
                tamanho: "MP (<50g)",
                tipo: "Ave"
            },
    {
                especie: "Codorna (Coturnix Coturnix)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Coleirinho (Sporophila caerulescens)",
                tamanho: "MP (<50g)",
                tipo: "Ave"
            },
    {
                especie: "Corujas / Família Strigidae",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Curicaca (Theristicus caudatus)",
                tamanho: "MG (>1500g)",
                tipo: "Ave"
            },
    {
                especie: "Curutié (Certhiaxis cinnammomeus)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Cutia (Dasyprocta azarae)",
                tamanho: "MG (>1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Fogo Apagou (Columbina squammata)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Gado, Vaca, Boi (Bovidade)",
                tamanho: "MG (>1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Gaivotas (Laridae)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Galinha d´ água ( Gallinula galeata)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Gambá (Didelphis marsupialis)",
                tamanho: "MG (>1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Garças/Socós (Ardeidade)",
                tamanho: "G (751 a 1500g)",
                tipo: "Ave"
            },
    {
                especie: "Gato-doméstico (Felis catus)",
                tamanho: "MG (>1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Gaviões, Falcões (Accipitridae e Falconidae)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Gralha Azul (Cyanocorax caeruleus)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Guaracava-de-Barriga-Amarela (Elaenia flavogaster)",
                tamanho: "MP (<50g)",
                tipo: "Ave"
            },
    {
                especie: "Irerê (Dendrocygna viduata)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Iguana-verde (Iguana Iguana)",
                tamanho: "G (751 a 1500g)",
                tipo: "Réptil"
            },
    {
                especie: "Jaçanã (Jacana)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Jacaré do papo amarelo (Caiman latirostris)",
                tamanho: "MG (>1500g)",
                tipo: "Réptil"
            },
    {
                especie: "Jacuguaçu (Penelope Obscura)",
                tamanho: "G (751 a 1500g)",
                tipo: "Ave"
            },
    {
                especie: "João Grande (Tillandsia usneoides)",
                tamanho: "MG (>1500g)",
                tipo: "Ave"
            },
    {
                especie: "João-de-Barro (Furnarius rufus)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Lagartos (Lacertilia)",
                tamanho: "G (751 a 1500g)",
                tipo: "Réptil"
            },
    {
                especie: "Lebre Europeia (Lepus europaeus)",
                tamanho: "MG (>1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Macaco-Prego (Sapajus Nigritus)",
                tamanho: "MG (>1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Maitaca (Pionus maximiliani)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Maria Faceira (Syrigma sibilatrix)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Maria-Cavaleira (Myiarchus ferox)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Marrecos, Patos, Gansos e Cines (Anatidae)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Morcego",
                tamanho: "P (51 a 250g)",
                tipo: "Mamífero"
            },
    {
                especie: "Narceja (Gallinago paraguaiae)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Neinei (Megarynchus pitangua)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Noivinha-Branca (Xolmis velatus)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Onça-Parda (Puma concolor)",
                tamanho: "MG (>1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Papagaios, Araras e Periquitos (Psittacidae)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Pardal (Passer domesticus)",
                tamanho: "MP (<50g)",
                tipo: "Ave"
            },
    {
                especie: "Pé -Vermelho (Amazonetta brasiliensis)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Perdiz (Rhynchotus rufescens)",
                tamanho: "G (751 a 1500g)",
                tipo: "Ave"
            },
    {
                especie: "Petrim (Synallaxis frontalis)",
                tamanho: "MP (<50g)",
                tipo: "Ave"
            },
    {
                especie: "Pica-Pau (Celeus flavus)",
                tamanho: "MP (<50g)",
                tipo: "Ave"
            },
    {
                especie: "Policia-Inglesa (Sturnella Superciliaris)",
                tamanho: "MP (<50g)",
                tipo: "Ave"
            },
    {
                especie: "Pombos, Rolinhas, Jurtis, avoantes (Columbidae)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Preá (Cavia aperea)",
                tamanho: "G (751 a 1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Quati (Nasua nasua)",
                tamanho: "G (751 a 1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Quero-Quero (Vanellus Chilensis)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Quiri-Quiri (Falco sparverius)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Sabiá Laranjeira (urdus rufiventris)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Sabiá Poca (Turdus amaurochalinus)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Sabiá-do- Campo (Mimus saturninus)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Sapos, pererecas e rãs (Anura)",
                tamanho: "P (51 a 250g)",
                tipo: "Réptil"
            },
    {
                especie: "Saracura-Três-Potes (Aramides cajaneus)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Savacu (Nycticorax nycticorax)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Seriema (Cariama cristata)",
                tamanho: "G (751 a 1500g)",
                tipo: "Ave"
            },
    {
                especie: "Serpentes",
                tamanho: "M (251 a 750g)",
                tipo: "Réptil"
            },
    {
                especie: "Siriri-Pequeno (Satrapa icterophry)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Sorro (Andropogon bicornis)",
                tamanho: "MG (>1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Taperuçus (Streptoprocne zonaris)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Tapicuru (Phimosus infuscatus)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Tartarugas, cágados e Jabutis (Chelonia)",
                tamanho: "Outros Mamiferos  (> 1,5 Kg)",
                tipo: "Réptil"
            },
    {
                especie: "Tatu (Dasypodidae)",
                tamanho: "MG (>1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Teiú (Salvador Merianae)",
                tamanho: "MG (>1500g)",
                tipo: "Réptil"
            },
    {
                especie: "Tesourinha (Tyrannus savana)",
                tamanho: "MP (<50g)",
                tipo: "Ave"
            },
    {
                especie: "Tucanuçu (Ramphastos toco)",
                tamanho: "M (251 a 750g)",
                tipo: "Ave"
            },
    {
                especie: "Tuim (Forpus xanthopterygius)",
                tamanho: "P (51 a 250g)",
                tipo: "Ave"
            },
    {
                especie: "Urubus (família Cathartidae)",
                tamanho: "MG (>1500g)",
                tipo: "Ave"
            },
    {
                especie: "Veados, cervos e renas (Cervídeos)",
                tamanho: "MG (>1500g)",
                tipo: "Terrestre"
            },
    {
                especie: "Outros",
                tamanho: "Não Identificado",
                tipo: "-"
            },
    {
                especie: "Não Informado",
                tamanho: "",
                tipo: "-"
            }
);

// ── GANCHO OFFLINE: named formulas do motor de sincronização entram abaixo desta linha
