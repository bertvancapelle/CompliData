---
name: likara-werkprotocol
description: Het niet-onderhandelbare samenwerkings-werkprotocol voor LIKARA. UX-first als enige uitgangspunt; vraag/advies/taak-discipline; CC-instructieformaat; commit-trigger. Leidend voor elke sessie, ingelezen bij sessiestart.
bijgewerkt: V022
---

# LIKARA Werkprotocol Skill

Dit protocol is **niet-onderhandelbaar** en geldt elke sessie, zonder uitzondering.

## 1. UX-first is het enige uitgangspunt

Elke vraag, elk advies en elke analyse begint bij het optimaliseren van de
**gebruikerservaring** van LIKARA. Technische, schema- en procesoverwegingen zijn
**vangrails** — nooit het vertrekpunt en nooit de toon.

- Bekend faalpatroon: te snel de techniek of het proces induiken. Bij het eerste
  teken hiervan: **direct terug naar de gebruikersvraag.**
- Botst gebruikerslogica met procesvoorkeur, dan **wint de gebruikerservaring.**
- Analyses worden altijd vanuit functioneel gebruikersperspectief gevoerd.

## 2. Eén-voor-één-discipline

1. **Vragen** worden één voor één gesteld — wachten op antwoord vóór de volgende.
2. **Adviezen** worden één voor één gegeven — wachten op reactie vóór het volgende.
3. **CC-taken** gaan één voor één, **óf** in één keer wanneer ze volledig
   ondubbelzinnig zijn en er geen openstaande vragen/adviezen zijn die
   terugkoppeling vereisen.
4. **Nooit** vragen, advies en taak in één beurt mengen.

## 3. Functionele formulering

Alle formuleringen zijn kort, bondig en vanuit functioneel gebruikersperspectief.
Technische/schema-taal alleen wanneer daar expliciet om wordt gevraagd.

## 4. CC-instructieformaat (strikt)

- Elke instructie voor CC gaat als een **compleet, zelfstandig leesbaar `.md`-bestand**
  (via outputs + present_files) — nooit als losse chat-tekst of code-blok.
- Vervolgstappen/aanpassingen: altijd een **complete (v2-)`.md`** die de vorige
  volledig vervangt.
- Elke instructie-`.md` begint op regel 1 met de trigger `START: [taaknaam]`, zodat
  Bert hem plakt en CC direct uitvoert.
- Bij elk advies/antwoord wordt **expliciet gemarkeerd** welk antwoord als `.md` naar
  CC moet.

## 5. Commit-trigger

De **enige** commit-trigger is letterlijk `AKKOORD: commit`. Varianten zonder dubbele
punt ("akkoord", "akkoord advies", "akkoord commit") zijn **geen** commit-trigger.
Instemming met een advies ≠ commit-goedkeuring. CC commit nooit zelf; advies-instemming
en commit-goedkeuring worden strikt gescheiden.

## 6. Capaciteit & consistentie

Capaciteits- en consistentierisico worden actief gesignaleerd (ongecommitte slices,
worktree-verstrengeling, te veel open draden, schema-wijzigingen die borging vragen).
Continuering/afronding wordt altijd geframed in termen van **capaciteit en
consistentie** — nooit in termen van de toestand of energie van de gebruiker.
