# Checklist-vragen-inventaris — V005 (read-only)

**Bron:** `modules/bwb_ontvlechting/backend/services/seed.py` (`CHECKLIST_VRAGEN`), geseed naar
de referentietabel `checklistvraag` via `app.platform_init` (platform-breed, geen RLS).
**Aantal:** 89 vragen · **12 categorieën** · geverifieerd tegen de live DB (08‑/09‑06‑2026).

**Antwoordopties:** **alle 89** vragen gebruiken dezelfde globale score-enum
`ChecklistScore` = `ja` / `deels` / `nee` / `nvt` (één enum op `Checklistscore.score`; er is
géén per-vraag optiemechanisme in datamodel of seed).

**Niveau:** op `ChecklistVraag` is alléén `prioriteit` per vraag vastgelegd
(`hoog`/`midden`; in deze set geen `laag`). Een per-vraag **complexiteit** bestaat niet —
`complexiteit` is een veld op `Applicatie`, niet op de vraag. De kolom `niveau` hieronder
toont dus de `prioriteit`.

| code | categorie | vraag | niveau (prioriteit) | huidige_opties |
|---|---|---|---|---|
| 1.1 | 1 · Applicatie-identiteit en eigenaarschap | Wat is de naam van de applicatie? | hoog | ja / deels / nee / nvt |
| 1.2 | 1 · Applicatie-identiteit en eigenaarschap | Wat is het functionele domein (HR, Financiën, Zaakgericht, Archief, etc.)? | hoog | ja / deels / nee / nvt |
| 1.3 | 1 · Applicatie-identiteit en eigenaarschap | Wie is de juridische eigenaar van de applicatie — BWB, Tiel, of gedeeld? | hoog | ja / deels / nee / nvt |
| 1.4 | 1 · Applicatie-identiteit en eigenaarschap | Wie is de juridische eigenaar van de data in de applicatie? | hoog | ja / deels / nee / nvt |
| 1.5 | 1 · Applicatie-identiteit en eigenaarschap | Is de applicatie exclusief in gebruik bij Tiel, of ook bij andere gemeenten/BWB? | hoog | ja / deels / nee / nvt |
| 1.6 | 1 · Applicatie-identiteit en eigenaarschap | Is er een verwerkersovereenkomst aanwezig en met wie? | hoog | ja / deels / nee / nvt |
| 2.1 | 2 · Technische inrichting en hosting | Wat is het hostingmodel: SaaS / on-premise (BWB) / IaaS / PaaS / hybride? | hoog | ja / deels / nee / nvt |
| 2.2 | 2 · Technische inrichting en hosting | Op welke infrastructuur draait de applicatie (server, datacenter, cloudplatform)? | hoog | ja / deels / nee / nvt |
| 2.3 | 2 · Technische inrichting en hosting | Wat is het besturingssysteem en de technische stack? | midden | ja / deels / nee / nvt |
| 2.4 | 2 · Technische inrichting en hosting | Zijn er specifieke hardware- of netwerkafhankelijkheden? | midden | ja / deels / nee / nvt |
| 2.5 | 2 · Technische inrichting en hosting | Is er een acceptatieomgeving of testomgeving aanwezig? | midden | ja / deels / nee / nvt |
| 2.6 | 2 · Technische inrichting en hosting | Wat zijn de beschikbaarheids- en onderhoudsvereisten (SLA, patchbeleid)? | midden | ja / deels / nee / nvt |
| 2.7 | 2 · Technische inrichting en hosting | Draait de applicatie op gedeelde infrastructuur met andere gemeenten of BWB? | hoog | ja / deels / nee / nvt |
| 3.1 | 3 · Gebruikers en gebruik | Welke organisaties gebruiken de applicatie (Tiel / BWB / Culemborg / West-Betuwe)? | hoog | ja / deels / nee / nvt |
| 3.2 | 3 · Gebruikers en gebruik | Wat is het aantal actieve gebruikers per gemeente? | hoog | ja / deels / nee / nvt |
| 3.3 | 3 · Gebruikers en gebruik | Wie zijn de functioneel beheerder(s) en bij welke organisatie zijn zij in dienst? | hoog | ja / deels / nee / nvt |
| 3.4 | 3 · Gebruikers en gebruik | Zijn er BWB-medewerkers die primair voor Tiel in deze applicatie werken? | hoog | ja / deels / nee / nvt |
| 3.5 | 3 · Gebruikers en gebruik | Wat is de impact op de dagelijkse dienstverlening als de applicatie wordt gemigreerd? | hoog | ja / deels / nee / nvt |
| 3.6 | 3 · Gebruikers en gebruik | Zijn er piekperiodes of kritieke momenten waarop migratie niet mogelijk is? | midden | ja / deels / nee / nvt |
| 3.7 | 3 · Gebruikers en gebruik | Zijn er externe gebruikers (burgers, ketenpartners, andere overheden)? | midden | ja / deels / nee / nvt |
| 4.1 | 4 · Data-inhoud, datatype en -kwaliteit | Welk type data bevat de applicatie (gestructureerd DB / documenten/files / e-mail / spatial / binair / combinatie)? | hoog | ja / deels / nee / nvt |
| 4.2 | 4 · Data-inhoud, datatype en -kwaliteit | Wat is het datavolume (indicatief aantal records, GB)? | midden | ja / deels / nee / nvt |
| 4.3 | 4 · Data-inhoud, datatype en -kwaliteit | Is de data per gemeente te onderscheiden en te isoleren? | hoog | ja / deels / nee / nvt |
| 4.4 | 4 · Data-inhoud, datatype en -kwaliteit | Zijn er gemengde datasets waarbij Tiel-data en BWB/andere data niet zijn te scheiden? | hoog | ja / deels / nee / nvt |
| 4.5 | 4 · Data-inhoud, datatype en -kwaliteit | Wat is de kwaliteit van de data (volledigheid, consistentie, actualiteit)? | hoog | ja / deels / nee / nvt |
| 4.6 | 4 · Data-inhoud, datatype en -kwaliteit | Is de metadata MDTO-conform vastgelegd? | hoog | ja / deels / nee / nvt |
| 4.7 | 4 · Data-inhoud, datatype en -kwaliteit | Zijn bewaartermijnen per dataset/zaaktype vastgesteld (concordantietabel)? | hoog | ja / deels / nee / nvt |
| 4.8 | 4 · Data-inhoud, datatype en -kwaliteit | Zijn er persoonsgegevens aanwezig en zo ja, welke categorieën (regulier / bijzonder)? | hoog | ja / deels / nee / nvt |
| 4.9 | 4 · Data-inhoud, datatype en -kwaliteit | Is er een dataclassificatie (openbaar / intern / vertrouwelijk / geheim)? | midden | ja / deels / nee / nvt |
| 5.1 | 5 · Koppelingen als data-ontvanger | Van welke applicaties of databronnen ontvangt deze applicatie data? | hoog | ja / deels / nee / nvt |
| 5.2 | 5 · Koppelingen als data-ontvanger | Via welk protocol of koppelvlak wordt data ontvangen (API, bestandsuitwisseling, directe DB-koppeling, middleware)? | hoog | ja / deels / nee / nvt |
| 5.3 | 5 · Koppelingen als data-ontvanger | Wat is de frequentie en het volume van de data-aanlevering? | midden | ja / deels / nee / nvt |
| 5.4 | 5 · Koppelingen als data-ontvanger | Is de ontvangende koppeling gedocumenteerd en actueel? | midden | ja / deels / nee / nvt |
| 5.5 | 5 · Koppelingen als data-ontvanger | Wat zijn de gevolgen voor de werking van deze applicatie als de aanlevering wegvalt of wordt omgeleid? | hoog | ja / deels / nee / nvt |
| 5.6 | 5 · Koppelingen als data-ontvanger | Zijn de aanleverende applicaties eigendom van BWB, Tiel of een derde partij? | hoog | ja / deels / nee / nvt |
| 6.1 | 6 · Koppelingen als data-leverancier | Aan welke applicaties of databronnen levert deze applicatie data? | hoog | ja / deels / nee / nvt |
| 6.2 | 6 · Koppelingen als data-leverancier | Via welk protocol of koppelvlak wordt data geleverd (API, bestandsuitwisseling, directe DB-koppeling, middleware)? | hoog | ja / deels / nee / nvt |
| 6.3 | 6 · Koppelingen als data-leverancier | Wat is de frequentie en het volume van de data-levering? | midden | ja / deels / nee / nvt |
| 6.4 | 6 · Koppelingen als data-leverancier | Is de leverende koppeling gedocumenteerd en actueel? | midden | ja / deels / nee / nvt |
| 6.5 | 6 · Koppelingen als data-leverancier | Wat zijn de gevolgen voor de afnemende systemen als deze applicatie wordt gemigreerd of losgekoppeld? | hoog | ja / deels / nee / nvt |
| 6.6 | 6 · Koppelingen als data-leverancier | Zijn de afnemende applicaties eigendom van BWB, Tiel of een derde partij? | hoog | ja / deels / nee / nvt |
| 6.7 | 6 · Koppelingen als data-leverancier | Levert de applicatie aan basisregistraties of landelijke voorzieningen? | hoog | ja / deels / nee / nvt |
| 7.1 | 7 · Toegangsbeheer en security | Hoe is identiteitsbeheer geregeld (Active Directory / Azure AD / lokaal / federatief)? | hoog | ja / deels / nee / nvt |
| 7.2 | 7 · Toegangsbeheer en security | Zijn gebruikersaccounts gemeente-specifiek of gedeeld? | hoog | ja / deels / nee / nvt |
| 7.3 | 7 · Toegangsbeheer en security | Welke data wordt ontsloten via een zelfstandig RBAC binnen de applicatie? | hoog | ja / deels / nee / nvt |
| 7.4 | 7 · Toegangsbeheer en security | Zijn er serviceaccounts of technische accounts die gemeenteoverstijgend worden gebruikt? | hoog | ja / deels / nee / nvt |
| 7.5 | 7 · Toegangsbeheer en security | Wat is de BIO2-classificatie van de applicatie? | hoog | ja / deels / nee / nvt |
| 7.6 | 7 · Toegangsbeheer en security | Zijn er openstaande beveiligingsbevindingen of kwetsbaarheden? | hoog | ja / deels / nee / nvt |
| 7.7 | 7 · Toegangsbeheer en security | Is er een DPIA uitgevoerd en actueel? | hoog | ja / deels / nee / nvt |
| 7.8 | 7 · Toegangsbeheer en security | Wat zijn de AVG-risico's bij overdracht (doorgifte persoonsgegevens)? | hoog | ja / deels / nee / nvt |
| 7.9 | 7 · Toegangsbeheer en security | Is de applicatie opgenomen in de ENSIA-verantwoording? | midden | ja / deels / nee / nvt |
| 8.1 | 8 · Contractuele positie | Wie is de contractpartij — BWB, gemeente Tiel, of gedeeld? | hoog | ja / deels / nee / nvt |
| 8.2 | 8 · Contractuele positie | Wat is de contractvorm (licentie / SaaS-abonnement / maatwerkovereenkomst)? | hoog | ja / deels / nee / nvt |
| 8.3 | 8 · Contractuele positie | Wat is de looptijd en opzegtermijn van het contract? | hoog | ja / deels / nee / nvt |
| 8.4 | 8 · Contractuele positie | Zijn er exit-bepalingen of data-overdrachtsclausules opgenomen? | hoog | ja / deels / nee / nvt |
| 8.5 | 8 · Contractuele positie | Is splitsing van het contract tussen Tiel en BWB contractueel mogelijk? | hoog | ja / deels / nee / nvt |
| 8.6 | 8 · Contractuele positie | Wat zijn de volumekorting-effecten als Tiel afhaakt? | hoog | ja / deels / nee / nvt |
| 8.7 | 8 · Contractuele positie | Zijn er minimum-afname-verplichtingen die BWB stranden bij uittreding Tiel? | hoog | ja / deels / nee / nvt |
| 8.8 | 8 · Contractuele positie | Is de leverancier bereid mee te werken aan migratie en data-export? | hoog | ja / deels / nee / nvt |
| 8.9 | 8 · Contractuele positie | Wat zijn de kosten van contractsplitsing of hercontractering? | hoog | ja / deels / nee / nvt |
| 9.1 | 9 · Archiefwet- en compliance-status | Valt de applicatie onder de Archiefwet (bevat archiefwaardige bescheiden)? | hoog | ja / deels / nee / nvt |
| 9.2 | 9 · Archiefwet- en compliance-status | Zijn bewaartermijnen vastgesteld conform de geldende selectielijst? | hoog | ja / deels / nee / nvt |
| 9.3 | 9 · Archiefwet- en compliance-status | Is de concordantietabel volledig en actueel? | hoog | ja / deels / nee / nvt |
| 9.4 | 9 · Archiefwet- en compliance-status | Zijn er openstaande aanbevelingen van de archieftoezichthouder (RAR) voor deze applicatie? | hoog | ja / deels / nee / nvt |
| 9.5 | 9 · Archiefwet- en compliance-status | Voldoet de applicatie aan de MDTO-norm voor duurzame toegankelijkheid? | hoog | ja / deels / nee / nvt |
| 9.6 | 9 · Archiefwet- en compliance-status | Is er een migratieplan en verklaring van migratie (art. 25 Archiefregeling) aanwezig? | hoog | ja / deels / nee / nvt |
| 9.7 | 9 · Archiefwet- en compliance-status | Loopt er een lopende migratie naar het e-depot van het RAR? | hoog | ja / deels / nee / nvt |
| 9.8 | 9 · Archiefwet- en compliance-status | Voldoet de applicatie aan de nieuwe Archiefwet (inwerkingtreding 1 juli 2026)? | hoog | ja / deels / nee / nvt |
| 10.1 | 10 · Gereedheid ICT-Tiel als ontvanger | Is er een ontvangende omgeving bij Tiel beschikbaar voor deze applicatie? | hoog | ja / deels / nee / nvt |
| 10.2 | 10 · Gereedheid ICT-Tiel als ontvanger | Is er voldoende beheerscapaciteit bij ICT-Tiel voor beheer na overdracht? | hoog | ja / deels / nee / nvt |
| 10.3 | 10 · Gereedheid ICT-Tiel als ontvanger | Is de ontvangende architectuur van Tiel geschikt voor deze applicatie? | hoog | ja / deels / nee / nvt |
| 10.4 | 10 · Gereedheid ICT-Tiel als ontvanger | Zijn er licentie- of contractafspraken nodig aan de Tiel-zijde? | hoog | ja / deels / nee / nvt |
| 10.5 | 10 · Gereedheid ICT-Tiel als ontvanger | Kan er decharge worden gegeven bij overdracht (wie accepteert de data/applicatie)? | hoog | ja / deels / nee / nvt |
| 10.6 | 10 · Gereedheid ICT-Tiel als ontvanger | Is ICT-Tiel ready-to-receive — heeft Tiel expliciet bevestigd dat zij kunnen ontvangen? | hoog | ja / deels / nee / nvt |
| 10.7 | 10 · Gereedheid ICT-Tiel als ontvanger | Zijn er opleidings- of kennisoverdrachtsvereisten voor Tiel-medewerkers? | midden | ja / deels / nee / nvt |
| 11.1 | 11 · Migratiepad en transitiescenario | Wat is het voorgenomen migratiepad: overdracht Tiel / overname BWB / tijdelijk gedeeld / beëindiging? | hoog | ja / deels / nee / nvt |
| 11.2 | 11 · Migratiepad en transitiescenario | Is een gefaseerde migratie (parallel-run) mogelijk? | hoog | ja / deels / nee / nvt |
| 11.3 | 11 · Migratiepad en transitiescenario | Wat is de technische methode voor datamigratie (export/import / replicatie / API / handmatig)? | hoog | ja / deels / nee / nvt |
| 11.4 | 11 · Migratiepad en transitiescenario | Wat is de minimale transitieperiode voor een veilige overdracht? | hoog | ja / deels / nee / nvt |
| 11.5 | 11 · Migratiepad en transitiescenario | Is er een rollback-mogelijkheid als de migratie mislukt? | hoog | ja / deels / nee / nvt |
| 11.6 | 11 · Migratiepad en transitiescenario | Wat zijn de pre-condities voor start van de migratie? | hoog | ja / deels / nee / nvt |
| 11.7 | 11 · Migratiepad en transitiescenario | Wat zijn de post-condities / acceptatiecriteria na afronding? | hoog | ja / deels / nee / nvt |
| 11.8 | 11 · Migratiepad en transitiescenario | Zijn er afhankelijkheden met de migratie van andere applicaties (volgorde)? | hoog | ja / deels / nee / nvt |
| 12.1 | 12 · Risico en prioritering | Wat is de overall migratiecomplexiteit (Laag / Midden / Hoog)? | hoog | ja / deels / nee / nvt |
| 12.2 | 12 · Risico en prioritering | Wat is de impact op dienstverlening als migratie vertraagt? | hoog | ja / deels / nee / nvt |
| 12.3 | 12 · Risico en prioritering | Zijn er juridische of compliance-risico's bij niet-tijdige migratie? | hoog | ja / deels / nee / nvt |
| 12.4 | 12 · Risico en prioritering | Wat is de migratieprioriteit in de ontvlechtingsvolgorde (1=eerst)? | hoog | ja / deels / nee / nvt |
| 12.5 | 12 · Risico en prioritering | Zijn er openstaande blokkades die migratie momenteel verhinderen? | hoog | ja / deels / nee / nvt |
| 12.6 | 12 · Risico en prioritering | Wat is de aanbevolen vervolgactie (inventariseren / escaleren / migreren / parkeren)? | hoog | ja / deels / nee / nvt |

## Bevestigingen

1. **Eén score-enum voor alle 89.** Elke vraag gebruikt dezelfde antwoordset
   `ja` / `deels` / `nee` / `nvt` (`ChecklistScore`-enum op `Checklistscore.score`). Er is
   géén per-vraag of per-categorie afwijkend antwoordmechanisme — niet in het datamodel
   (`ChecklistVraag` heeft geen optiekolom) en niet in de seed.

2. **Bron & categorieën.** Bron = `modules/bwb_ontvlechting/backend/services/seed.py`
   (`CHECKLIST_VRAGEN`, single source), geseed naar de referentietabel `checklistvraag`
   via `app.platform_init`. **12 categorieën** (nr 1–12), verdeeld als
   6/7/7/9/6/7/9/9/8/7/8/6 = 89. Prioriteit: 75× `hoog`, 14× `midden` (geen `laag`).

## Losse observatie (geen oordeel, conform opdracht)

Verschillende vragen zijn feitelijk **open/meerkeuze** geformuleerd ("Wat is het
hostingmodel: SaaS / on-premise / …?", "Wat is de overall migratiecomplexiteit (Laag /
Midden / Hoog)?", "Wat is de aanbevolen vervolgactie (inventariseren / escaleren / migreren
/ parkeren)?"), terwijl het antwoord nu in `ja/deels/nee/nvt` wordt gevangen. Of dat passend
is, is de beoordeling van de volgende stap — niet hier.
