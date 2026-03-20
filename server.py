#!/usr/bin/env python3
"""
Petits Déjs Virtuels TogeZer - Serveur de prise de rendez-vous
"""

import sqlite3
import json
import os
import uuid
import tornado.ioloop
import tornado.web
import tornado.httpserver

DB_PATH = os.path.join(os.path.dirname(__file__), 'rdv.db')
EVENT_DATE = "2026-03-25"
SLOTS = [
    "09:00", "09:20", "09:40",
    "10:00", "10:20", "10:40",
    "11:00", "11:20", "11:40",
    "12:00", "12:20", "12:40"
]

RECEPTIFS = [
    # Asie / Océanie
    {"nom": "Atypique Lanka", "pays": "Sri Lanka", "continent": "Asie / Océanie", "contact_nom": "Raphaelle Baes", "telephone": "", "email": "raphaelle@atypiquelanka.com", "desc_entreprise": "Atypique Voyages se distingue dans l'art de créer des expériences uniques et personnalisées. Nous croyons que voyager va bien au-delà de la simple visite ; c'est une immersion profonde dans une culture et une exploration de soi.Notre approche repose sur la création de voyages sur-mesure, enrichis par l'expertise de nos travel designers basés sur place. Cette présence locale nous permet de partager une connaissance authentique du territoire et de révéler des pépites méconnues. Chez Atypique Voyages, nous aspirons à transformer votre façon de voyager en vous invitant à vivre intensément chaque destination à travers ses coutumes, sa gastronomie et son histoire.", "desc_expert": "Responsable B2B chez Atypique Lanka. Mon engagement est d'accompagner l'évolution de vos projets vers un tourisme plus durable et éthique, afin de sauvegarder notre destination et ses cultures."},
    {"nom": "Terra Australia", "pays": "Australie", "continent": "Asie / Océanie", "contact_nom": "Josepha Pepin", "telephone": "", "email": "josepha@terra-australia.com.au", "desc_entreprise": "Terra Australia est un réceptif basé à Brisbane depuis 2013, membre du réseau Terra Group. Nous concevons des voyages sur mesure, authentiques et durables pour les professionnels du tourisme. Notre force repose sur une connaissance terrain fondamentale : notre équipe, certifiée « Aussie specialists », réalise régulièrement des voyages de reconnaissance pour proposer des itinéraires 100% personnalisés.Engagés dans une démarche éthique, nous privilégions les acteurs locaux éco-certifiés pour un impact positif. Nous garantissons une réactivité sous 48h et un suivi 7j/7, assurant une communication étroite et une flexibilité totale lors de la conception et du déroulement des séjours.", "desc_expert": "Travel Designer Australie"},
    {"nom": "Archipel Contact", "pays": "Indonésie", "continent": "Asie / Océanie", "contact_nom": "Sylvie Ponte", "telephone": "", "email": "sylvie@archipel-contact.com", "desc_entreprise": "ARCHIPEL CONTACT – Un autre visage de l’IndonésieCréé en 1989, Archipel Contact est un réceptif spécialisé sur l’Indonésie. Notre équipe de 10 personnes basée à Denpasar coordonne chaque étape des circuits sur Java, Lombok, Sulawesi, Sumatra et Flores avec des partenaires historiques.Alliant créativité et efficacité, nous offrons un service sur mesure exclusivement dédié aux professionnels du tourisme (B2B). Nos correspondants francophones assurent une structure réactive avec des réponses sous 24 à 48 heures.Animés par un amour profond pour la culture indonésienne, nous valorisons les communautés locales et proposons des guides francophones expérimentés, capables de s'adapter avec bienveillance aux attentes de chaque voyageur.", "desc_expert": "Fondatrice d'Archipel Contact en 1989. Entourée d'un solide réseau de partenaires de confiance, je tiens à conserver une structure à taille humaine. La proximité et l’écoute sont mes priorités pour vous accompagner dans la création de voyages authentiques et faire découvrir à vos clients un visage intime de l’Indonésie."},
    {"nom": "Mai Globe Travels", "pays": "Sri Lanka", "continent": "Asie / Océanie", "contact_nom": "Catherine Lebouille", "telephone": "", "email": "catherine@maiglobe.com", "desc_entreprise": "Mai Globe Travels est un réceptif francophone spécialiste du sur-mesure en Asie, basé au Sri Lanka et au Vietnam depuis 2012. Forte d’une équipe multiculturelle passionnée, l'agence bénéficie d'une solide réputation sur le marché européen.Nos experts s’appliquent à faire découvrir le meilleur de l'Asie hors des sentiers battus, que ce soit pour des séjours en solo, en famille ou en groupe. Nous sélectionnons rigoureusement nos prestataires pour promouvoir un tourisme durable bénéficiant aux populations locales. De l'aventure avec chauffeur privé au Sri Lanka aux séjours luxueux aux Maldives, Mai Globe Travels concocte des circuits personnalisés et compétitifs répondant à toutes les envies de vos clients.", "desc_expert": "Installée au Sri Lanka depuis plus de 10 ans. Co-créatrice de notre agence locale et d'un hôtel à Colombo, je mets mon expertise du sur-mesure et mon engagement pour un tourisme durable au service de vos projets. Je m'appuie sur une connaissance approfondie du terrain pour concevoir des itinéraires authentiques et responsables, hors des sentiers battus."},
    {"nom": "Shikoku Tours", "pays": "Japon", "continent": "Asie / Océanie", "contact_nom": "Ayaka Sakamoto", "telephone": "", "email": "sakamoto@shikokutours.com", "desc_entreprise": "Le principal réceptif de l’île de Shikoku au Japon travaille en collaboration étroite avec le gouvernement local et les DMO pour développer des contenus touristiques exclusifs. Membre de l’« All Nippon Travel Agents Association » et de l’« Adventure Travel and Trade Association », l'agence s'impose comme l'expert de référence pour découvrir cette région préservée.", "desc_expert": "Manager du marché francophone, Coordinatrice de voyage organisé, Guide"},
    {"nom": "Go Beyond", "pays": "Thaïlande, Vietnam, Cambodge, Laos, Népal", "continent": "Asie / Océanie", "contact_nom": "Marc Ruffet", "telephone": "", "email": "marc@gobeyond.asia", "desc_entreprise": "Go Beyond est un réceptif spécialisé dans les voyages d'aventure à travers l'Asie (Thaïlande, Vietnam, Cambodge, Laos, Sri Lanka, Chine, Inde, Népal). Nous cultivons l'équilibre parfait entre sites incontournables et expériences hors des sentiers battus.Notre force réside dans la création de nos propres produits et activités d'aventure, développés en collaboration directe avec des communautés locales d'entrepreneurs. Que ce soit pour explorer des trésors cachés ou des icônes culturelles, nous proposons des aventures personnalisées qui révèlent la véritable essence de chaque destination.", "desc_expert": "Je suis Marc, Responsable du Développement chez Go Beyond. Mon rôle consiste à établir de nouveaux partenariats stratégiques en France pour faire découvrir nos aventures authentiques en Asie. Je supervise également le développement de produits pour offrir des expériences uniques à vos voyageurs."},
    {"nom": "Odynovo", "pays": "Chine", "continent": "Asie / Océanie", "contact_nom": "Sylvia Ye", "telephone": "", "email": "partnership@odynovotours.com", "desc_entreprise": "Avec plus de 20 ans d'expérience, Odynovo est un réceptif de confiance spécialisé dans les voyages privés et sur mesure à travers toute la Chine. Nous proposons des services terrestres complets, des sites emblématiques aux régions les plus reculées comme le Tibet ou le Yunnan.Notre équipe maîtrise parfaitement le terrain et les attentes du marché francophone, garantissant des itinéraires 100 % personnalisables et une assistance 24h/24. Pourquoi choisir Odynovo : une expertise historique, des tarifs compétitifs, des guides sélectionnés avec soin et une logistique fluide pour des voyages sans souci. Nous sommes votre partenaire privilégié pour ouvrir les portes de l'Empire du Milieu à vos clients.", "desc_expert": "Je suis en charge du développement commercial B2B."},
    {"nom": "Travelart Maestros", "pays": "Bhoutan", "continent": "Asie / Océanie", "contact_nom": "Kiran Joti", "telephone": "", "email": "kiran@travelart-maestros.com", "desc_entreprise": "Travelart Maestros est un réceptif spécialiste du sous-continent Indien, créateur d’expériences et concepteur de voyages grâce à notre équipe de professionnels très expérimentés. Notre connaissance approfondie des attentes de la clientèle des marchés que nous servons, dont la France, nous permet de concevoir de proposer des voyages d’exception adaptés aux aspirations et habitudes des voyageurs. Notre société est basée à New Delhi et nous nous appuyons sur notre réseau de correspondants partenaires répartis à travers toute l’INDE, NEPAL & BHOUTAN.", "desc_expert": "Directrice et fondatrice de Travelart Maestros, agence réceptive sur le sous-continent indien. Ancienne guide francophone, je mets ma connaissance approfondie du terrain et du voyage sur mesure à votre disposition. Je m'appuie sur un réseau solide de partenaires de confiance pour vous garantir des prestations de haute qualité, dans une démarche de tourisme responsable."},
    {"nom": "Evasion Tropicale", "pays": "Philippines", "continent": "Asie / Océanie", "contact_nom": "Kévin Labbé", "telephone": "", "email": "kevin@evasiontropicale.ph", "desc_entreprise": "Evasion Tropicale est un réceptif né de la passion de ses fondateurs pour l'exploration des Philippines. Forts de plusieurs années d'expertise, nous concevons des itinéraires sur mesure qui marient engagement professionnel et soif de découverte.Qu'il s'agisse d'aventure aux Visayas, de détente à Palawan ou d'immersion culturelle dans la Cordillère, nous adaptons chaque projet aux intérêts uniques des voyageurs. Grâce à un vaste réseau de partenaires locaux, nous offrons la flexibilité nécessaire pour accueillir des groupes de toutes tailles. Evasion Tropicale s'impose comme une référence de fiabilité pour transformer les paysages tropicaux de l'archipel en souvenirs inoubliables.", "desc_expert": "Installé aux Philippines depuis 19 ans, j'ai créé notre agence en 2018 après avoir exercé comme guide accompagnateur. Je mets mon expertise terrain à votre service pour accueillir vos voyageurs français et leur faire découvrir les paysages d'un archipel authentique, encore préservé du tourisme de masse."},
    {"nom": "Shanti Travel", "pays": "Inde, Indonésie, Japon, Phillipines, Vietnam, Sri Lanka", "continent": "Asie / Océanie", "contact_nom": "Céline Jasset", "telephone": "", "email": "celine@shantitravel.com", "desc_entreprise": "Shanti Travel, créé en 2005, dispose aujourd'hui de 12 agences locales en Asie. Nos experts vivent et voyagent au cœur des régions qu'ils vous invitent à découvrir, garantissant une connaissance terrain unique et une immersion totale pour vos clients.Opérant une vingtaine de destinations, nous proposons une offre de voyages durables avec un programme zéro carbone et une compensation à 100% des émissions de CO2 via des ONG partenaires. C'est l'engagement d'une proximité humaine, du respect des populations locales et d'une expertise pointue pour des programmes à la carte ou entièrement sur-mesure à travers tout le continent asiatique.", "desc_expert": ""},

    # Europe / Moyen Orient
    {"nom": "Andalucia Aficion", "pays": "Espagne", "continent": "Europe / Moyen Orient", "contact_nom": "Virginie Scamandro", "telephone": "", "email": "andaluciaaficion@gmail.com", "desc_entreprise": "Nous sommes une agence située à Montellano, au cœur des villages blancs de Séville. Depuis 2013, nous sommes spécialistes des séjours sur mesure en Andalousie, ainsi qu'à Madrid et ses alentours. Notre expertise locale nous permet de concevoir des itinéraires personnalisés pour offrir une immersion authentique dans la culture espagnole.", "desc_expert": "Créatrice et gérante de l'agence"},
    {"nom": "Sóprasi", "pays": "Portugal", "continent": "Europe / Moyen Orient", "contact_nom": "Emeline Breant", "telephone": "", "email": "info@soprasi.com", "desc_entreprise": "SóPraSi est un réceptif lancé en 2022, spécialiste du Portugal Continental et des Açores. Notre ambition est de valoriser le patrimoine culturel et humain à travers des voyages privés et sur mesure, des incontournables aux sentiers battus. \n\n\nNous nous entourons de partenaires locaux passionnés pour concevoir des expériences écoresponsables, riches en partage et en émotions. Notre garantie repose sur un engagement rigoureux et un suivi professionnel avant et pendant chaque séjour pour assurer une découverte unique et mémorable.", "desc_expert": "De Paris, j'ai décidé de déménager définitivement vers la région d'Aveiro, au Portugal. Mon objectif est d'offrir à mes clients l'opportunité de profiter et de \"vivre\" des moments uniques et privés lors de leur séjour, à leur propre rythme et en fonction de leurs envies."},
    {"nom": "Alkemia", "pays": "Islande", "continent": "Europe / Moyen Orient", "contact_nom": "Jean-Marc Plessy", "telephone": "", "email": "jmplessy@me.com", "desc_entreprise": "Située dans un fjord au Nord de l'Islande, notre agence est spécialiste des petits groupes et des voyages individuels sur mesure. Fidèles à la philosophie du \"slow travel\", nous prônons un rythme de découverte apaisé. Membre de VVE en France, nous sommes engagés pour un tourisme responsable et une immersion respectueuse de la nature sauvage islandaise.", "desc_expert": "Nous sommes un couple franco-islandais, Harpa et Jean-Marc. Nous avons créé l'agence et la gérons ensemble, et sommes aussi tous les deux guides. Nous avons également un centre de retraite et d'accueil pour nos clients dans le Nord (https://www.helgafell.net)."},
    {"nom": "Dream Jordan", "pays": "Jordanie", "continent": "Europe / Moyen Orient", "contact_nom": "Rafat Zeidan", "telephone": "", "email": "rzidane@dream-jordan.com", "desc_entreprise": "Forte d'une décennie d'expérience, notre équipe de consultants et de guides locaux experts assure une logistique parfaite à travers la Jordanie. Notre objectif est de garantir la meilleure expérience possible dans ce royaume aux trésors anciens. Nous mettons notre savoir-faire au service de voyages remarquables, alliant connaissance approfondie du terrain et maîtrise opérationnelle des transports.", "desc_expert": "Je m’appelle Zeidan, je suis guide touristique en Jordanie avec plus de 20 ans d’expérience, et je serai ravi de mettre mon expertise à votre service afin de créer une collaboration exceptionnelle et durable."},
    {"nom": "Azur Rp", "pays": "Émirats arabes unis", "continent": "Europe / Moyen Orient", "contact_nom": "Firas Koubaydatt", "telephone": "", "email": "firas.k@azur-rp.com", "desc_entreprise": "Azur RP est un bureau de représentation spécialisé dans le conseil et le marketing B2B pour le secteur du tourisme. Nous représentons des réceptifs sélectionnés pour leur solidité financière et leur expertise dans les voyages de loisirs, d'aventure et le secteur MICE.\n\n\nNotre mission est d'accompagner les professionnels du tourisme dans la création de produits innovants et fiables. Grâce à une équipe dynamique et passionnée, nous offrons un support opérationnel et stratégique pour garantir des expériences fluides, créatives et centrées sur l'excellence humaine.", "desc_expert": "Installé entre la France et le Moyen-Orient depuis plusieurs années, j’ai développé Azur RP, un bureau de représentation, afin d’accompagner les professionnels du tourisme dans le développement de produits innovants et adaptés aux attentes du marché. Fort d’une solide expérience terrain et d’un réseau de partenaires locaux fiables, je mets mon expertise au service de vos voyageurs pour leur faire découvrir l’Égypte, la Jordanie, les Émirats Arabes Unis, Oman et le Qatar, à travers des programmes maîtrisés et soigneusement orchestrés."},
    {"nom": "Brightside Travel", "pays": "Royaume-Uni, Irlande", "continent": "Europe / Moyen Orient", "contact_nom": "Loic Acosta", "telephone": "", "email": "loic@brightside-travel.com", "desc_entreprise": "L’équipe de Brightside Travel crée des expériences sur mesure, authentiques et profondément humaines, loin des sentiers battus. Spécialistes du Royaume-Uni, nous révélons des facettes méconnues du territoire à travers des thématiques fortes : nature, culture, histoire ou imaginaire. Notre force réside dans notre capacité à écouter, comprendre et transformer chaque rêve en voyage concret, original et cohérent. Grâce à un réseau de partenaires de confiance et une créativité sans cesse renouvelée, nous concevons des séjours uniques, porteurs de sens et d’émotions durables.", "desc_expert": "Fondateur et directeur de Brightside Travel LTD, spécialiste du Royaume-Uni. Je conçois des itinéraires sur mesure et supervise des expériences de voyage originales. Mon rôle mêle vision stratégique, sélection rigoureuse de partenaires locaux, innovation dans l’offre produit et accompagnement personnalisé des professionnels du tourisme."},
    {"nom": "Viasun", "pays": "Grèce", "continent": "Europe / Moyen Orient", "contact_nom": "Charles Berthault", "telephone": "", "email": "charles_ber@hotmail.com", "desc_entreprise": "Créé en 2013, notre réceptif a su s'imposer par une approche différenciante et authentique de la Grèce. Nous collaborons avec de nombreux acteurs du tourisme pour proposer des séjours ancrés dans la culture locale. Notre développement repose sur une connaissance fine de plusieurs régions grecques, visant à offrir une alternative originale aux circuits classiques.", "desc_expert": "Dans le tourisme depuis 20 ans en tant qu'agent réceptif, spécialiste de la Grèce pour toutes les destinations du pays. Ayant grandi en Grèce, je parle couramment français, grec et anglais."},
    {"nom": "Echappée Nord", "pays": "Norvège, Suède, Finlande", "continent": "Europe / Moyen Orient", "contact_nom": "Emilie Guédo", "telephone": "", "email": "emilie@echappeenord.com", "desc_entreprise": "Au fil des voyages aux quatre coins de la Norvège, l'équipe d'Echappée Nord a acquis une connaissance approfondie du pays. Amoureux de ce pays, nous souhaitons partager notre passion avec vous. Laissez-vous tenter par le charme scandinave. Notre philosophie est simple : vous faire découvrir à vous, voyageurs, la beauté des paysages nordiques selon le friluftsliv (littéralement la 'vie au grand air' en norvégien et désignant la communion avec la nature) tout en préservant cet environnement majestueux avec des voyages plus respectueux de la faune, de la flore et des communautés locales.​​« Rester c'est exister, mais voyager c'est vivre » - Gustave Nadaud -", "desc_expert": "Travel Designer"},
    {"nom": "Terra Gaïa Balka", "pays": "Croatie, Slovénie, Monténégro, Bosnie-Herzégovine", "continent": "Europe / Moyen Orient", "contact_nom": "Hugo Dimoff", "telephone": "", "email": "hugo@terra-balka.com", "desc_entreprise": "Terra Balka, membre du réseau Terra Gaia, est un réceptif basé à Zagreb, né de l'expertise de gérants historiques du groupe en Amérique latine. Nous proposons des itinéraires sur-mesure en Croatie, Slovénie, Monténégro et Bosnie-Herzégovine, avec des extensions vers Venise et l'Autriche.\n\n\nNotre connaissance approfondie du terrain et une sélection rigoureuse de nos prestataires garantissent des expériences authentiques. Notre équipe engagée accompagne les professionnels du tourisme avec réactivité, conseil et une exigence constante de fiabilité.", "desc_expert": "Forte d'un parcours commercial à l'international, je me consacre au développement de relations BtoB solides et sincères. Mon rôle est de vous accompagner avec un conseil sur-mesure pour concevoir des itinéraires uniques et des voyages à forte valeur ajoutée, fidèles à l’esprit authentique des Balkans."},
    {"nom": "Oleaday", "pays": "Corse", "continent": "Europe / Moyen Orient", "contact_nom": "Marie Rabaud", "telephone": "", "email": "info@oleaday.com", "desc_entreprise": "Oleaday est un réceptif événementiel basé à Porto-Vecchio, dédié à la découverte de la Corse toute l'année. Nous défendons un tourisme éco-responsable valorisant les savoir-faire régionaux, les circuits courts et les échanges véritables. \n\n\nPartenaire B2B des agences, CSE et organisateurs de séminaires, nous promettons des expériences immersives et durables sous le signe de l'authenticité méditerranéenne. Notre mission est de faire de la Corse une terre d'expériences intime, vivante et rigoureusement organisée.", "desc_expert": "Fondatrice de l'agence, j'ai d’abord évolué dans de grandes Maisons de Luxe françaises. Mon challenge est de sensibiliser durablement nos clients à notre nature et à notre art de vivre Made in France."},
    {"nom": "Xplore Oman", "pays": "Oman", "continent": "Europe / Moyen Orient", "contact_nom": "Justine Lesage", "telephone": "", "email": "justine@xplore-voyages.com", "desc_entreprise": "Xplore Oman est une agence experte en séjours sur mesure au Sultanat d'Oman, membre du réseau Xplore. De l'autotour en liberté aux circuits privatifs avec guides locaux, nous couvrons les joyaux du pays : Mascate, les wadis, les fjords de Musandam et le désert de Wahiba Sands.Notre concept repose sur une relation directe avec des experts locaux pour garantir des expériences hors des sentiers battus au juste prix. Les voyageurs bénéficient d'un accompagnement francophone complet, incluant la co-création de l'itinéraire et une assistance sur place pour une aventure sereine et authentique.", "desc_expert": "Installée entre la France et le Sultanat d’Oman, je développe la destination au sein de XPLORE avec une approche sur-mesure, basée sur une solide connaissance terrain et un réseau local fiable.\nJ’accompagne vos voyageurs francophones à la découverte d’un Oman authentique, entre désert, wadis, montagnes et hospitalité légendaire.\nChaque itinéraire est pensé avec soin : étapes équilibrées, hébergements choisis, expériences immersives et suivi personnalisé.\nMon objectif : offrir une immersion dans un Sultanat préservé, avec confort, fluidité et sérénité à chaque étape."},

    # Afrique
    {"nom": "Pura Vida Cabo Verde", "pays": "Cap-Vert", "continent": "Afrique", "contact_nom": "Stan Brun", "telephone": "", "email": "stan@puravidacaboverde.com", "desc_entreprise": "Pura Vida Cabo Verde est un réceptif spécialiste du Cap Vert, dirigé par trois associés experts de la destination depuis 1997. Basée sur l’île de Sao Vicente, notre équipe combine une expérience de tour-opérateur en France et une connaissance intime du terrain.Nous mettons à votre service l'expertise de Laurent, l'un des meilleurs guides de l'archipel, et de Pascal, installé sur place depuis plus de 20 ans. Cette double culture franco-capverdienne nous permet de concevoir des voyages d'une authenticité rare, maîtrisant parfaitement les spécificités logistiques et culturelles de chaque île.", "desc_expert": "Expert de la destination Cap Vert depuis 1997, j'organise des voyages vers cet archipel. Au sein du réceptif Pura Vida Cabo Verde depuis 2014, je propose aux agences de voyages et tour-opérateurs une large gamme de prestations de services."},
    {"nom": "Sikiliza", "pays": "Zimbabwe, Botswana, Malawi, Mozambique, Namibie, Ouganda, Zambie", "continent": "Afrique", "contact_nom": "Nathalie Calonne", "telephone": "", "email": "nathalie@sikiliza.net", "desc_entreprise": "Nous sommes un réceptif basé à Harare, Zimbabwe, depuis 1996. Nous proposons des voyages sur mesure en Afrique australe (Zimbabwe, Botswana, Namibie, Zambie, Malawi, Mozambique). Les séjours peuvent être accompagnés de guides professionnels francophones et organisés en lodges ou en camps mobiles de luxe.Passionnés par nos destinations, nous adaptons chaque itinéraire au profil du voyageur, qu’il s’agisse de thématiques spécifiques comme l’ornithologie, l’histoire ou l’astronomie, pour les couples, familles ou groupes d’amis.", "desc_expert": "Dans le secteur du tourisme depuis 1992, je suis fondateur et directeur de Sikiliza, basé à Harare et spécialisé dans l’organisation de safaris sur mesure à travers l’Afrique australe. Je suis également co-fondateur et directeur général de Mawimbi Bushcamp, un camp de brousse exclusif situé dans le parc national de Kafue, en Zambie."},
    {"nom": "Tanganyika Expeditions", "pays": "Tanzanie", "continent": "Afrique", "contact_nom": "Laurent Gavache", "telephone": "", "email": "laurent@tanganyika.com", "desc_entreprise": "Créée en 1989, Tanganyika Expédition est un réceptif spécialisé exclusivement sur la Tanzanie. Nous gérons une collection exclusive de camps et lodges stratégiquement situés dans le Nord, garantissant une maîtrise totale de la chaîne de services. Nos équipes locales et nos bureaux en France assurent un accompagnement réactif pour vos projets individuels, groupes ou incentive. Avec une flotte de 40 véhicules 4x4 parfaitement entretenus et les premiers safaris électriques du pays, nous allions passion du terrain, confort haut de gamme et engagement pionnier pour un tourisme durable.", "desc_expert": ""},
    {"nom": "Enclose Africa Safaris", "pays": "Rwanda, Kenya, Ouganda", "continent": "Afrique", "contact_nom": "Reginal Hakizimana", "telephone": "", "email": "info@encloseafricasafaris.com", "desc_entreprise": "Enclose Africa Safaris est une agence nationale basée à Arusha, spécialisée dans les safaris sur mesure en Afrique de l'Est. Gérée par des professionnels dotés de plus de dix ans d'expérience, nous collaborons avec des guides certifiés et disposons de notre propre flotte de véhicules 4x4 personnalisés.Notre personnel hautement qualifié s'engage à dépasser vos attentes en organisant des vacances de rêve, du tourisme de luxe aux expéditions pour aventuriers. Nous mettons tout en œuvre pour créer la meilleure expérience de safari possible pour chaque profil de voyageur.", "desc_expert": "Directeur Général et fondateur de l'agence. Fort de plus de 15 ans d'expérience et de mon passé de guide, je suis un spécialiste de l'Afrique de l'Est. Je mets mon expertise de terrain à votre service pour concevoir des itinéraires uniques, en privilégiant un tourisme durable et une collaboration étroite avec les communautés locales."},
    {"nom": "Envie De Maghreb", "pays": "Algérie, Maroc, Tunisie, Égypte", "continent": "Afrique", "contact_nom": "Muriel Le Gal", "telephone": "", "email": "contact@enviedemaghreb.com", "desc_entreprise": "Envie de Maghreb est votre réceptif spécialiste pour des expériences sur mesure en Algérie, au Maroc, en Tunisie et en Égypte. Nous concevons des circuits personnalisables axés sur la culture, l'histoire et la gastronomie, adaptés au budget et aux envies de vos clients.Grâce à une connaissance approfondie de nos destinations et des partenaires rigoureusement sélectionnés, nous garantissons des services de haute qualité. Nos experts francophones vous accompagnent pour créer des itinéraires authentiques et durables, assurant un accueil chaleureux et une immersion totale.", "desc_expert": "Fondatrice d'Envie de Maghreb, je suis experte du tourisme avec 30 ans d'expérience sur l'Algérie, le Maroc, la Tunisie et l'Égypte. Spécialisée dans l'organisation de voyages sur mesure, je mets mon écoute et mon approche personnalisée à votre service pour établir une relation durable et créer des expériences authentiques pour vos clients."},
    {"nom": "Soaring Flamingo", "pays": "Tanzanie", "continent": "Afrique", "contact_nom": "Frédérique Duvignacq", "telephone": "", "email": "fred@soaringflamingo.com", "desc_entreprise": "Soaring Flamingo vous invite à découvrir une Tanzanie intime et méconnue. Nous organisons des safaris, trekkings et séjours d'écotourisme culturel dans toutes les régions du pays, y compris les grands parcs du Sud et les sanctuaires de chimpanzés à Mahale.Spécialistes du sur-mesure pour individuels, nos circuits sont réalisés par des chauffeurs-guides francophones en véhicules 4x4 équipés. Notre philosophie repose sur un partage équitable des revenus avec les communautés locales pour protéger la nature et soutenir l'économie des villages tanzaniens.", "desc_expert": "En charge du développement des partenariats BtoB avec les réseaux francophones pour Soaring Flamingo depuis plus de 15 ans. Je m'investis dans la démarche de développement durable de notre agence, dont la gestion est pleinement confiée à une équipe locale tanzanienne, pour vous accompagner dans la vente de nos circuits."},
    {"nom": "Terra Gaïa Africa", "pays": "Afrique du Sud, Lesotho, Mozambique,, Zimbabwe, Botswana", "continent": "Afrique", "contact_nom": "Mathilde Genet", "telephone": "", "email": "gm@terra.africa.com", "desc_entreprise": "Notre agence réceptive basée au Cap est experte de l'Afrique Australe depuis près de 10 ans. Nous sommes spécialisés dans la conception de voyages sur mesure haut de gamme et hors des sentiers battus, couvrant l'Afrique du Sud et sa région.Notre vocation est de parcourir sans cesse le terrain pour proposer les circuits les plus pertinents : safaris animaliers, randonnées ou séjours originaux. Nous avons l'ambition d'offrir le séjour le mieux adapté à chaque voyageur, garantissant des prestations de qualité au meilleur prix et en toute sécurité.", "desc_expert": "Nantaise d’origine, je me suis installée au Cap en 2017 après un stage de fin d’études. Tombée sous le charme de l’Afrique australe, j’ai choisi d’y construire ma vie professionnelle et personnelle.\n\nAujourd’hui spécialiste de l’Afrique australe et de l’Afrique de l’Est, je possède une solide connaissance terrain de destinations comme l’Afrique du Sud, le Botswana, le Mozambique, la Tanzanie et le Kenya. Passionnée de nature et de grands espaces, j’explore régulièrement la région pour tester lodges, expériences et nouveaux itinéraires.\n\nÀ l’écoute des agences et attentive aux attentes des clients, je conçois des voyages sur mesure alliant logistique fluide, hébergements cohérents et expériences authentiques.\n\nPrenez rendez-vous avec moi pour échanger sur vos projets et découvrir comment je peux accompagner vos clients avec une expertise locale et un service personnalisé."},
    {"nom": "Terra Gaïa Morocco", "pays": "Maroc", "continent": "Afrique", "contact_nom": "Laura Mauro", "telephone": "", "email": "laura@terra-morocco.com", "desc_entreprise": "Bienvenue chez Terra Morocco, votre agence locale francophone basée à Marrakech. Spécialistes du voyage à la carte, nous créons des itinéraires originaux plaçant l'immersion locale et le tourisme responsable au cœur de l'expérience marocaine.Membre de Terra Group (19 agences réceptives dans le monde depuis 1998), notre équipe expérimentée façonne des souvenirs inoubliables dans le respect du territoire et des populations. Nous mettons notre passion et notre solidité opérationnelle au service de vos clients pour des voyages d'exception.", "desc_expert": "Fondatrice de Terra Morocco après 8 ans chez Terra Group en Amérique Latine, je suis revenue sur ma terre natale. Mon objectif est de vous transmettre ma passion pour le Maroc et de vous proposer une vision du voyage conscient, porteur de sens et tourné vers la véritable culture du pays."},
    {"nom": "Serengeti Big Cats Safaris", "pays": "Tanzanie", "continent": "Afrique", "contact_nom": "Mathilde Queva", "telephone": "", "email": "mathilde@togezer.travel", "desc_entreprise": "Créée en 2004, Serengeti Big Cats Safaris est une compagnie tanzanienne basée à Arusha. Nous organisons des safaris dans tous les parcs nationaux et des séjours balnéaires à Zanzibar, avec des guides professionnels francophones et une flotte de véhicules 4x4 modernes.Notre connaissance du terrain nous permet de proposer des excursions hors des sentiers battus pour une immersion authentique. Qu'il s'agisse de safaris photos, d'ascensions du Kilimandjaro ou de voyages culturels, nous personnalisons chaque périple pour garantir un service de qualité au meilleur prix.", "desc_expert": "Représentante commerciale de Serengeti Big Cats Safaris depuis bientôt deux ans, j’ai le plaisir d’accompagner une agence engagée, fiable et reconnue pour la qualité de son expertise locale. De retour des magnifiques terres tanzaniennes il y a quelques semaines, je serai ravie de vous partager mon expérience, mes ressentis et mes conseils pour créer vos prochains voyages mémorables sur cette belle terre d’Afrique."},
    {"nom": "Mahay Expédition", "pays": "Madagascar", "continent": "Afrique", "contact_nom": "Stéphane Thamin", "telephone": "", "email": "stephane@mahayexpedition.com", "desc_entreprise": "Mahay Expédition, agence réceptive engagée, conçoit des voyages responsables et durables à Madagascar, reconnus par les Trophées du Voyage Durable en France.Nous créons des séjours sur mesure : exploration de sites emblématiques, voyages solidaires, trekkings dans le Makay, séjours bien-être ou croisières en catamaran. Chaque projet respecte les populations locales et l’environnement, pour des expériences authentiques et mémorables. Confiez-nous vos projets et offrez à vos voyageurs un tourisme engagé et unique.", "desc_expert": "Titulaire du Brevet d’État d’Accompagnateur en Montagne et passionné par Madagascar depuis 2003. Je suis investi dans le tourisme durable (membre de la Confédération du Tourisme de Madagascar et de l'Association Nationale du Tourisme Responsable). J'ai créé notre structure engagée pour vous accompagner dans la création de voyages responsables, en m'appuyant sur un solide réseau local de guides, d'associations et d'hôteliers."},

    # Amérique
    {"nom": "Terra Gaïa Ecuador", "pays": "Équateur", "continent": "Amérique", "contact_nom": "Nicolas Goronflot", "telephone": "", "email": "nicolas@terra-ecuador.com", "desc_entreprise": "Terra Gaïa Ecuador & Galápagos, membre du réseau Terra Gaïa, est un réceptif fondé en 2010 à Quito. Passionnés par l'exploration du \"pays des 5 Mondes\", nous créons des voyages cousus main, des Andes à l’Amazonie jusqu'à l'archipel des Galápagos.Ardents défenseurs du Slow Travel, nous privilégions les rencontres authentiques et l'immersion chez l'habitant. Certifiée Travelife, notre agence s'engage pour un tourisme communautaire et durable, garantissant des expériences 100% sur mesure qui respectent l'environnement et valorisent les populations locales.", "desc_expert": "Installé à Quito depuis 2014, j'ai longuement exploré l'Amérique Latine et ses communautés avant de tomber amoureux de l'Équateur. Profondément attaché à ce \"pays des 5 Mondes\", je suis toujours enthousiaste à l'idée de partager mon expertise locale et ma passion pour mon pays d'adoption avec vos voyageurs."},
    {"nom": "Holaqueya", "pays": "République Dominicaine", "continent": "Amérique", "contact_nom": "Célia Tichadelle", "telephone": "", "email": "celia@holaqueya.com", "desc_entreprise": "Holaqueya réinvente le voyage en République Dominicaine, loin des complexes hôteliers. Notre promesse est celle d'une intimité retrouvée avec le pays : sortir des sentiers battus pour rencontrer ses habitants et découvrir ses paysages les plus époustouflants.Nous proposons des séjours immersifs et sur mesure, basés sur des adresses rigoureusement sélectionnées pour leur excellence. Notre approche privilégie des excursions au plus près des populations locales, garantissant à vos clients une expérience unique, authentique et respectueuse des valeurs culturelles dominicaines.", "desc_expert": "Je suis Célia Tichadelle, fondatrice et directrice de Holaqueya, installée à Santo Domingo depuis 2022. Après avoir géré la communication de la République Dominicaine sur le marché français pendant plus de 5 ans, j'ai créé cette agence réceptive sur-mesure et engagée. Nous travaillons avec des partenaires locaux pour concevoir des itinéraires authentiques et responsables, loin des clichés."},
    {"nom": "Wakiy Tour", "pays": "Équateur", "continent": "Amérique", "contact_nom": "Olivia Baine", "telephone": "", "email": "olivia@wakiytour.com", "desc_entreprise": "Réceptif spécialisé dans le tourisme communautaire et durable en Équateur, Wakiy Tour est le partenaire des agences et CSE pour l'organisation de voyages en groupe ou sur mesure. L’Équateur offre une diversité culturelle exceptionnelle avec ses 14 nations indigènes. Notre mission est de faire vivre aux voyageurs une expérience immersive et authentique à la rencontre de ces communautés. Nous transformons chaque séjour en un véritable échange humain, au cœur des écosystèmes et des traditions cosmologiques uniques du pays.", "desc_expert": "Installée en Équateur depuis 2005, j'ai d'abord géré des projets avec les organisations sociales avant de co-créer notre agence en 2014. Forte des liens très forts tissés avec les communautés locales, j'organise des moments de rencontre et de partage pour faire découvrir notre pays d'adoption à vos voyageurs."},
    {"nom": "Terra Gaïa Brazil", "pays": "Brésil", "continent": "Amérique", "contact_nom": "Alice Prevot", "telephone": "", "email": "alice@terra-brazil.com", "desc_entreprise": "Depuis 2003, Terra Brazil place l'humain et la découverte au cœur de chaque itinéraire. Conçus par des experts locaux qui sillonnent le pays, nos voyages dénichent des perles rares et des adresses confidentielles pour faire résonner l'âme du Brésil.Avec nos bases à Rio, Paraty et Cumbuco, nous créons des parcours faits de rencontres sincères et d'aventures inoubliables. Bien plus que de simples déplacements, nos expériences invitent à mieux voyager, dans une immersion totale et un respect profond du territoire et de ses habitants.", "desc_expert": "Directrice de l’agence Terra Gaïa Brazil, depuis Rio de Janeiro."},
    {"nom": "Terra Gaïa Argentina", "pays": "Argentine", "continent": "Amérique", "contact_nom": "Emilie Pinel", "telephone": "", "email": "gerencia@terra-argentina.com", "desc_entreprise": "Basée à Bariloche en Patagonie, Terra Argentina crée des voyages sur mesure depuis 2006. Nos itinéraires sont 100% personnalisés pour s'adapter aux envies, budgets et rythmes de vos clients. Notre équipe stable et francophone possède une connaissance parfaite du terrain, assurant un suivi complet sur place pour des séjours fiables et mémorables. Entre glaciers majestueux, immensité de la steppe et rencontres locales authentiques, nous transformons chaque voyage en une expérience unique et profondément humaine.", "desc_expert": "Je suis Emilie. Arrivée en Argentine pour un voyage, j'y ai trouvé ma deuxième maison. J’aime imaginer des itinéraires qui vibrent au rythme des routes lointaines et des grands espaces de la Patagonie pour faire découvrir ce pays autrement à vos clients."},
    {"nom": "Terra Gaïa Bolivia", "pays": "Bolivie", "continent": "Amérique", "contact_nom": "Antoine Meyer", "telephone": "", "email": "gerencia@terra-bolivia.com", "desc_entreprise": "Terra Bolivia est un réceptif francophone basé à La Paz depuis 1998, expert du voyage d’aventure et acteur du tourisme responsable. Laborantins du voyage \"low-tech\", nous privilégions les rencontres locales et l'immersion durable chez l'habitant.Nous proposons des épopées extraordinaires : traversées de la Cordillère Royale, odyssées amazoniennes ou itinéraires complets sur l'Altiplano. Chaque circuit est conçu pour faire vivre des émotions profondes, alliant expertise technique et respect rigoureux des territoires et des populations boliviennes.", "desc_expert": "Grand voyageur dans l’âme, j’ai vécu et travaillé dans plusieurs pays avant de m’installer en Bolivie. Issu d’une formation classique en vente et negotiation, j’ai choisi de me reconvertir dans le tourisme pour donner davantage de sens à mon parcours. J’y poursuis une conviction simple : le voyage n’est pas une consommation, mais une rencontre.\n\nJe dirige aujourd’hui Terra Bolivia avec la certitude que ce pays, l’un des plus préservés d’Amérique latine, offre une intensité rare. Tombé amoureux de ses paysages bruts et de sa richesse humaine, je m’y suis ancré avec une ambition claire : que chaque voyageur reparte avec des étoiles dans les yeux, plus de questions que de certitudes et l’envie profonde de revenir."},
    {"nom": "Xplore Mexique", "pays": "Mexique", "continent": "Amérique", "contact_nom": "Benjamin Senoussi", "telephone": "", "email": "benjamin@xplore-voyages.com", "desc_entreprise": "Xplore Mexique est une agence locale experte en séjours sur mesure. Animée par les \"Xplorers\", notre équipe co-crée des itinéraires personnalisés, du roadtrip en liberté dans le Yucatán à l'immersion profonde en communauté Maya ou à Bacalar.Notre concept repose sur la suppression des intermédiaires pour offrir des hébergements de charme et des expériences hors des sentiers battus au meilleur prix. Pour les voyageurs francophones, nous garantissons un accompagnement complet : ligne dédiée, paiements sécurisés et service de conciergerie local disponible tout au long de l'aventure.", "desc_expert": "Directeur des opérations chez Xplore Mexique. Basé sur le terrain, je mets ma connaissance opérationnelle de la destination et mon expertise logistique au service de l'accompagnement et de la réalisation de vos projets de voyage sur l'ensemble du marché mexicain."},
    {"nom": "Phima Voyages", "pays": "Pérou", "continent": "Amérique", "contact_nom": "Martina Capel", "telephone": "", "email": "martina@phimavoyages.com", "desc_entreprise": "Phima Voyages est un réceptif fondé en 2015 à Chachapoyas, spécialisé dans le tourisme rural et communautaire au nord du Pérou. Nous opérons entre la côte, les Andes et l'Amazonie, offrant des séjours chez l'habitant pour une immersion authentique.Certifiée Travelife Partner, notre agence s'engage pour un tourisme durable valorisant le rôle des femmes et l'économie locale. Chaque circuit sur mesure inclut chauffeur privé et guide professionnel, garantissant un service de haute qualité tout en préservant l'environnement et les traditions ancestrales des régions Amazonas et San Martin.", "desc_expert": "Cofondatrice de Phima Voyages, installée dans la région Amazonas au Pérou depuis 2015. Je m'appuie sur 25 ans d'expérience pour faire découvrir les régions méconnues du nord péruvien. Je gère les relations avec nos partenaires locaux et les réservations pour favoriser les points de rencontre et de partage lors des séjours de vos clients."},
    {"nom": "Terra Gaïa Chile", "pays": "Chili", "continent": "Amérique", "contact_nom": "Sarah Morvan", "telephone": "", "email": "sales9@terra-chile.com", "desc_entreprise": "Chez Terra Chile, agence basée à Santiago et experte de la destination depuis plus de 15 ans, nous parcourons inlassablement le pays pour dénicher des expériences authentiques, insolites et durables. Confiez-nous votre projet : avec nos concepteurs francophones, nous construisons un itinéraire 100% personnalisé en moins de 48h. Que ce soit pour le rythme, le budget ou les envies spécifiques de vos clients, nous garantissons une expertise terrain pointue pour une découverte sur mesure du territoire chilien.", "desc_expert": ""},
    {"nom": "Travel Excellence", "pays": "Costa Rica", "continent": "Amérique", "contact_nom": "Laura Rojas", "telephone": "", "email": "laura@travelexcellence.com", "desc_entreprise": "Travel Excellence est un réceptif basé au Costa Rica avec plus de 30 ans d'expertise dans la création de circuits sur mesure. Nous mettons en valeur la biodiversité exceptionnelle du pays, de ses volcans actifs aux forêts tropicales luxuriantes d'Arenal, Monteverde ou Corcovado.Distinguée par de multiples certifications de qualité et de responsabilité sociale, l'agence propose un accompagnement professionnel complet. Notre expertise locale pointue garantit des solutions de voyage haut de gamme, assurant des expériences inoubliables tout en veillant à la préservation de l'environnement unique du Costa Rica.", "desc_expert": "Avec 20 ans d’expérience dans l’industrie du tourisme, et plus particulièrement en agences de voyages, costaricienne de naissance et de cœur, j’aime profondément mon pays et je suis prête à vous partager les meilleures recommandations d’une locale.\n\nJ’ai commencé mes études en tant que guide touristique, puis j’ai découvert ma passion pour l’organisation de voyages, allant du tourisme rural communautaire aux plus beaux hôtels de luxe que ce magnifique pays a à offrir.\n\nSympathique, souriante et bienveillante, je vous ferai découvrir ce que signifie vraiment être Pura Vida !"},
]

# Emoji flags for continents
CONTINENT_EMOJI = {
    "Afrique": "🌍",
    "Asie / Océanie": "🌏",
    "Amérique": "🌎",
    "Europe / Moyen Orient": "🌍",
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS receptifs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        pays TEXT,
        continent TEXT,
        contact_nom TEXT,
        telephone TEXT,
        email TEXT,
        admin_token TEXT UNIQUE,
        desc_entreprise TEXT DEFAULT '',
        desc_expert TEXT DEFAULT ''
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receptif_id INTEGER,
        heure TEXT,
        statut TEXT DEFAULT 'disponible',
        FOREIGN KEY (receptif_id) REFERENCES receptifs(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slot_id INTEGER UNIQUE,
        agence_nom TEXT,
        contact_nom TEXT,
        email TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (slot_id) REFERENCES slots(id)
    )''')
    conn.commit()

    # Seed receptifs if empty
    c.execute('SELECT COUNT(*) FROM receptifs')
    if c.fetchone()[0] == 0:
        print("\n=== INITIALISATION DE LA BASE DE DONNÉES ===")
        print(f"{'RÉCEPTIF':<40} {'PAYS':<35} {'TOKEN ADMIN'}")
        print("-" * 110)
        for r in RECEPTIFS:
            token = uuid.uuid4().hex[:12]
            c.execute('''INSERT INTO receptifs (nom, pays, continent, contact_nom, telephone, email, admin_token, desc_entreprise, desc_expert)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (r['nom'], r['pays'], r['continent'], r['contact_nom'], r['telephone'], r['email'], token,
                      r.get('desc_entreprise', ''), r.get('desc_expert', '')))
            receptif_id = c.lastrowid
            # Create slots
            for heure in SLOTS:
                c.execute('INSERT INTO slots (receptif_id, heure, statut) VALUES (?, ?, ?)',
                         (receptif_id, heure, 'disponible'))
            label = f"{r['nom']} ({r['pays']})"
            print(f"{label:<40} {r['pays']:<35} http://localhost:5001/admin?token={token}")
        conn.commit()
        print("=" * 110)
        print()
    conn.close()


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")

    def options(self, *args):
        self.set_status(204)
        self.finish()

    def get_db(self):
        return get_db()

    def json_response(self, data, status=200):
        self.set_status(status)
        self.write(json.dumps(data, ensure_ascii=False))
        self.finish()

    def error(self, msg, status=400):
        self.json_response({"error": msg}, status)


class ReceptifsHandler(BaseHandler):
    def get(self):
        continent = self.get_argument("continent", None)
        pays = self.get_argument("pays", None)
        conn = self.get_db()
        c = conn.cursor()
        query = "SELECT * FROM receptifs"
        params = []
        conditions = []
        if continent:
            conditions.append("continent = ?")
            params.append(continent)
        if pays:
            conditions.append("pays LIKE ?")
            params.append(f"%{pays}%")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY continent, nom"
        c.execute(query, params)
        rows = [dict(r) for r in c.fetchall()]

        # Add slot counts
        for row in rows:
            c.execute("SELECT COUNT(*) FROM slots WHERE receptif_id=? AND statut='disponible'", (row['id'],))
            row['slots_disponibles'] = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM slots WHERE receptif_id=? AND statut='reserve'", (row['id'],))
            row['slots_reserves'] = c.fetchone()[0]
            row['total_slots'] = len(SLOTS)
            row['emoji'] = CONTINENT_EMOJI.get(row['continent'], '🌐')
        conn.close()
        self.json_response(rows)


class SlotsHandler(BaseHandler):
    def get(self, receptif_id):
        conn = self.get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM receptifs WHERE id=?", (receptif_id,))
        receptif = c.fetchone()
        if not receptif:
            conn.close()
            return self.error("Réceptif introuvable", 404)

        c.execute("""
            SELECT s.*, r.agence_nom, r.contact_nom as resa_contact, r.email as resa_email
            FROM slots s
            LEFT JOIN reservations r ON s.id = r.slot_id
            WHERE s.receptif_id = ?
            ORDER BY s.heure
        """, (receptif_id,))
        slots = [dict(s) for s in c.fetchall()]
        conn.close()
        self.json_response({
            "receptif": dict(receptif),
            "slots": slots,
            "event_date": EVENT_DATE
        })


class BookingHandler(BaseHandler):
    def post(self):
        try:
            data = json.loads(self.request.body)
        except:
            return self.error("JSON invalide")

        slot_id = data.get("slot_id")
        agence_nom = data.get("agence_nom", "").strip()
        contact_nom = data.get("contact_nom", "").strip()
        email = data.get("email", "").strip()

        if not all([slot_id, agence_nom, contact_nom, email]):
            return self.error("Tous les champs sont obligatoires")

        conn = self.get_db()
        c = conn.cursor()

        # Check slot exists and is available
        c.execute("SELECT * FROM slots WHERE id=? AND statut='disponible'", (slot_id,))
        slot = c.fetchone()
        if not slot:
            conn.close()
            return self.error("Ce créneau n'est plus disponible", 409)

        # Create booking
        c.execute("UPDATE slots SET statut='reserve' WHERE id=?", (slot_id,))
        c.execute("""INSERT INTO reservations (slot_id, agence_nom, contact_nom, email)
                    VALUES (?, ?, ?, ?)""", (slot_id, agence_nom, contact_nom, email))
        conn.commit()

        # Get receptif info
        c.execute("SELECT r.nom, r.pays, r.contact_nom FROM receptifs r JOIN slots s ON s.receptif_id = r.id WHERE s.id=?", (slot_id,))
        rec = c.fetchone()
        conn.close()

        self.json_response({
            "success": True,
            "message": f"Rendez-vous confirmé avec {rec['nom']} ({rec['pays']}) à {slot['heure']}",
            "details": {
                "receptif": rec['nom'],
                "pays": rec['pays'],
                "interlocuteur": rec['contact_nom'],
                "heure": slot['heure'],
                "date": EVENT_DATE
            }
        })


class AdminHandler(BaseHandler):
    def get(self):
        token = self.get_argument("token", None)
        if not token:
            return self.error("Token manquant", 401)
        conn = self.get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM receptifs WHERE admin_token=?", (token,))
        receptif = c.fetchone()
        if not receptif:
            conn.close()
            return self.error("Token invalide", 401)

        c.execute("""
            SELECT s.*, r.agence_nom, r.contact_nom as resa_contact, r.email as resa_email
            FROM slots s
            LEFT JOIN reservations r ON s.id = r.slot_id
            WHERE s.receptif_id = ?
            ORDER BY s.heure
        """, (receptif['id'],))
        slots = [dict(s) for s in c.fetchall()]
        conn.close()
        self.json_response({
            "receptif": dict(receptif),
            "slots": slots,
            "event_date": EVENT_DATE
        })

    def post(self):
        token = self.get_argument("token", None)
        if not token:
            return self.error("Token manquant", 401)
        try:
            data = json.loads(self.request.body)
        except:
            return self.error("JSON invalide")

        slot_id = data.get("slot_id")
        action = data.get("action")  # 'bloquer' or 'debloquer'

        conn = self.get_db()
        c = conn.cursor()
        c.execute("SELECT r.id FROM receptifs r JOIN slots s ON s.receptif_id = r.id WHERE r.admin_token=? AND s.id=?", (token, slot_id))
        if not c.fetchone():
            conn.close()
            return self.error("Non autorisé", 403)

        c.execute("SELECT statut FROM slots WHERE id=?", (slot_id,))
        slot = c.fetchone()
        if not slot:
            conn.close()
            return self.error("Créneau introuvable", 404)

        if action == 'bloquer' and slot['statut'] == 'disponible':
            c.execute("UPDATE slots SET statut='bloque' WHERE id=?", (slot_id,))
            conn.commit()
            conn.close()
            self.json_response({"success": True, "statut": "bloque"})
        elif action == 'debloquer' and slot['statut'] == 'bloque':
            c.execute("UPDATE slots SET statut='disponible' WHERE id=?", (slot_id,))
            conn.commit()
            conn.close()
            self.json_response({"success": True, "statut": "disponible"})
        else:
            conn.close()
            self.error("Action impossible sur ce créneau")


class ContinentsHandler(BaseHandler):
    def get(self):
        conn = self.get_db()
        c = conn.cursor()
        c.execute("SELECT DISTINCT continent FROM receptifs ORDER BY continent")
        continents = [r[0] for r in c.fetchall()]
        c.execute("SELECT DISTINCT pays FROM receptifs ORDER BY pays")
        pays = [r[0] for r in c.fetchall()]
        conn.close()
        self.json_response({"continents": continents, "pays": pays})


# ── Mots de passe réceptifs (6 chiffres) ──────────────────────────────────────
RECEPTIF_PASSWORDS = {
    "Atypique Lanka": "770487",
    "Terra Australia": "216739",
    "Archipel Contact": "126225",
    "Mai Globe Travels": "877572",
    "Shikoku Tours": "388389",
    "Go Beyond": "356787",
    "Odynovo": "334053",
    "Travelart Maestros": "246316",
    "Evasion Tropicale": "872246",
    "Shanti Travel": "207473",
    "Andalucia Aficion": "809570",
    "Sóprasi": "876646",
    "Alkemia": "671858",
    "Dream Jordan": "191161",
    "Azur Rp": "719176",
    "Brightside Travel": "542417",
    "Viasun": "133326",
    "Echappée Nord": "131244",
    "Terra Gaïa Balka": "198246",
    "Oleaday": "329258",
    "Xplore Oman": "343962",
    "Pura Vida Cabo Verde": "629903",
    "Sikiliza": "731262",
    "Tanganyika Expeditions": "127824",
    "Enclose Africa Safaris": "688508",
    "Envie De Maghreb": "308496",
    "Soaring Flamingo": "850800",
    "Terra Gaïa Africa": "781453",
    "Terra Gaïa Morocco": "835392",
    "Serengeti Big Cats Safaris": "671412",
    "Mahay Expédition": "539898",
    "Terra Gaïa Ecuador": "331148",
    "Holaqueya": "571029",
    "Wakiy Tour": "717889",
    "Terra Gaïa Brazil": "391704",
    "Terra Gaïa Argentina": "948749",
    "Terra Gaïa Bolivia": "106814",
    "Xplore Mexique": "895667",
    "Phima Voyages": "944962",
    "Terra Gaïa Chile": "267414",
    "Travel Excellence": "832052",
}

ADMIN_USER = "Togezer"
ADMIN_PASS = "Martin"


class GlobalAdminHandler(BaseHandler):
    """Espace Admin global – voir et modifier tous les RDV"""

    def _check_auth(self):
        user = self.get_argument("user", "")
        pwd = self.get_argument("pwd", "")
        if user != ADMIN_USER or pwd != ADMIN_PASS:
            self.error("Identifiants incorrects", 401)
            return False
        return True

    def get(self):
        if not self._check_auth():
            return
        conn = self.get_db()
        c = conn.cursor()
        c.execute("""
            SELECT res.id as resa_id, res.agence_nom, res.contact_nom as resa_contact,
                   res.email as resa_email, res.created_at,
                   s.heure, s.id as slot_id,
                   rec.id as receptif_id, rec.nom as receptif_nom,
                   rec.pays, rec.continent, rec.contact_nom
            FROM reservations res
            JOIN slots s ON s.id = res.slot_id
            JOIN receptifs rec ON rec.id = s.receptif_id
            ORDER BY rec.continent, rec.nom, s.heure
        """)
        reservations = [dict(r) for r in c.fetchall()]
        # Stats
        c.execute("SELECT COUNT(*) FROM reservations")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM receptifs")
        nb_receptifs = c.fetchone()[0]
        conn.close()
        self.json_response({
            "reservations": reservations,
            "total": total,
            "nb_receptifs": nb_receptifs,
            "event_date": EVENT_DATE
        })

    def post(self):
        """Modifier ou annuler un RDV"""
        if not self._check_auth():
            return
        try:
            data = json.loads(self.request.body)
        except:
            return self.error("JSON invalide")

        action = data.get("action")
        resa_id = data.get("resa_id")

        if not resa_id:
            return self.error("resa_id manquant")

        conn = self.get_db()
        c = conn.cursor()

        if action == "annuler":
            c.execute("SELECT slot_id FROM reservations WHERE id=?", (resa_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                return self.error("Réservation introuvable", 404)
            c.execute("UPDATE slots SET statut='disponible' WHERE id=?", (row['slot_id'],))
            c.execute("DELETE FROM reservations WHERE id=?", (resa_id,))
            conn.commit()
            conn.close()
            self.json_response({"success": True, "message": "Réservation annulée"})

        elif action == "modifier":
            agence_nom = data.get("agence_nom", "").strip()
            contact_nom = data.get("contact_nom", "").strip()
            email = data.get("email", "").strip()
            if not all([agence_nom, contact_nom, email]):
                conn.close()
                return self.error("Champs manquants")
            c.execute("""UPDATE reservations SET agence_nom=?, contact_nom=?, email=?
                         WHERE id=?""", (agence_nom, contact_nom, email, resa_id))
            conn.commit()
            conn.close()
            self.json_response({"success": True, "message": "Réservation modifiée"})
        else:
            conn.close()
            self.error("Action inconnue")


class ReceptifAuthHandler(BaseHandler):
    """Connexion réceptif par nom + mot de passe"""

    def post(self):
        try:
            data = json.loads(self.request.body)
        except:
            return self.error("JSON invalide")

        nom = data.get("nom", "").strip()
        password = data.get("password", "").strip()

        expected = RECEPTIF_PASSWORDS.get(nom)
        if not expected or password != expected:
            return self.error("Identifiants incorrects", 401)

        conn = self.get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM receptifs WHERE nom=?", (nom,))
        receptif = c.fetchone()
        if not receptif:
            conn.close()
            return self.error("Réceptif introuvable", 404)

        c.execute("""
            SELECT s.*, r.agence_nom, r.contact_nom as resa_contact, r.email as resa_email
            FROM slots s
            LEFT JOIN reservations r ON s.id = r.slot_id
            WHERE s.receptif_id = ?
            ORDER BY s.heure
        """, (receptif['id'],))
        slots = [dict(s) for s in c.fetchall()]
        conn.close()
        self.json_response({
            "receptif": dict(receptif),
            "slots": slots,
            "event_date": EVENT_DATE
        })


class PasswordsListHandler(BaseHandler):
    """Liste des mots de passe (admin seulement)"""

    def get(self):
        user = self.get_argument("user", "")
        pwd = self.get_argument("pwd", "")
        if user != ADMIN_USER or pwd != ADMIN_PASS:
            return self.error("Non autorisé", 401)
        result = [{"nom": k, "password": v} for k, v in RECEPTIF_PASSWORDS.items()]
        self.json_response({"passwords": result})




class Fileb64Handler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")

    def get(self):
        import base64
        path = self.get_argument("path", "")
        base_dir = os.path.dirname(__file__)
        if path == "server.py":
            full_path = os.path.join(base_dir, "server.py")
        elif path == "index.html":
            full_path = os.path.join(base_dir, "public", "index.html")
        else:
            self.set_status(400)
            self.write(json.dumps({"error": "invalid path"}))
            self.finish()
            return
        with open(full_path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
        self.write(json.dumps({"content": b64}))
        self.finish()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        public_dir = os.path.join(os.path.dirname(__file__), 'public')
        with open(os.path.join(public_dir, 'index.html'), 'r', encoding='utf-8') as f:
            self.write(f.read())


def make_app():
    public_dir = os.path.join(os.path.dirname(__file__), 'public')
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/admin", MainHandler),
        (r"/api/receptifs", ReceptifsHandler),
        (r"/api/receptifs/(\d+)/slots", SlotsHandler),
        (r"/api/bookings", BookingHandler),
        (r"/api/admin", AdminHandler),
        (r"/api/filters", ContinentsHandler),
        (r"/api/file-b64", Fileb64Handler),
        (r"/api/global-admin", GlobalAdminHandler),
        (r"/api/receptif-auth", ReceptifAuthHandler),
        (r"/api/passwords-list", PasswordsListHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": public_dir}),
    ])


if __name__ == "__main__":
    init_db()
    app = make_app()
    port = int(os.environ.get("PORT", 5001))
    app.listen(port)
    print(f"✅ Serveur démarré sur http://localhost:{port}")
    print(f"📅 Événement : Petits Déjs Virtuels - {EVENT_DATE}")
    print(f"🔗 Ouvrir : http://localhost:{port}")
    tornado.ioloop.IOLoop.current().start()
