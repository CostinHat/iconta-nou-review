---
title: Casa de marcat fără transmitere online: cum depui la ANAF fișierele XML cu rapoartele Z?
description: Aparatele de marcat care transmit offline exportă pe un mediu de stocare extern fișierele XML semnate pentru fiecare zi fiscală încheiată și un fișier XML registru. Fișierele se validează și se atașează la un PDF cu aplicația ANAF, apoi se depun prin mijloace electronice de transmitere la distanță (OPANAF 146/2018, anexa 2).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Casa de marcat fără transmitere online: cum depui la ANAF fișierele XML cu rapoartele Z?

Dacă aparatul de marcat nu transmite singur datele către ANAF, firma trebuie să le transmită ea. Procedura este descrisă în OPANAF 146/2018, anexa nr. 2, secțiunea II.13: pentru aparatele care transmit **offline**, fișierele XML semnate de aparat se exportă pe un mediu de stocare extern, se validează, se atașează la un PDF cu aplicația ANAF și se depun prin mijloace electronice de transmitere la distanță.

### Ce fișiere se exportă

Potrivit secțiunii II.13, se exportă:

- **unul sau mai multe fișiere XML semnate cu certificatul digital al aparatului**, care conțin datele aferente fiecărei zile fiscale încheiate, conform secțiunilor II.1-II.7. Pentru aparatele obișnuite, altele decât cele de schimb valutar și taximetrie, structura raportului fiscal de închidere zilnică este cea din secțiunea II.7 (anexa 2, secțiunea I, pct. 5 lit. c));
- **un fișier XML registru**, conform secțiunii II.12, cu numerele de ordine ale rapoartelor de închidere zilnică emise în perioada raportată.

Fișierul registru conține, printre altele:
- identificatorul unic al mesajului, format din numărul unic de identificare al aparatului și data și ora generării;
- codul de identificare fiscală al utilizatorului;
- numărul primului și al ultimului raport Z din perioadă (`nrRapI`, `nrRapF`);
- tipul aparatului: S pentru schimb valutar, T pentru taximetrie, U pentru uzual sau A pentru magazin în aeroport.

### Cum se depun

Secțiunea II.13: fișierele „se validează și se atașează la un PDF folosind aplicația pusă la dispoziție pe portalul Agenției Naționale de Administrare Fiscală și se depune la organul fiscal folosind mijloace de transmitere la distanță”.

Pașii practici:

1. Exportă din aparat, pe stick USB sau card, fișierele XML ale zilelor fiscale încheiate și fișierul registru.
2. Validează fișierele cu aplicația ANAF.
3. Atașează fișierele la PDF-ul generat de aplicație.
4. Depune PDF-ul la organul fiscal prin mijloace electronice de transmitere la distanță.
5. Păstrează recipisa și o copie a fișierelor exportate.

Anexa 2, secțiunea I, pct. 11 trimite la secțiunea II.13 pentru toate transmiterile de fișiere XML.

### De ce contează: blocarea aparatului

Secțiunea II.13 prevede că aparatul care lucrează în profilul 1, cu obligație de transmitere, își **blochează** emiterea și tipărirea bonurilor fiscale dacă este atins sau depășit termenul stabilit prin normele metodologice. Deblocarea se face după transmiterea datelor, prin importul unui fișier XML de răspuns, conform secțiunii II.10. Codul de deblocare este identificatorul ultimului mesaj registru transmis.

Pentru aparatele offline, mesajul cu codul de deblocare și eventualii indicatori modificați ai profilului se primește **după** transmiterea datelor. Cu alte cuvinte, dacă depunerea întârzie, aparatul se poate opri la termen.

### Profilul aparatului

Anexa 1 la ordin definește:
- **profilul 0**: aparatul nu are obligația conectării la sistemul informatic;
- **profilul 1**: aparatul are obligația de conectare și transmitere a datelor.

Trecerea între profiluri se face exclusiv de tehnicianul de service al distribuitorului autorizat sau al unității de service acreditate (secțiunea II.13). Contabilul nu schimbă singur modul de lucru.

Obligația generală de conectare la distanță pentru transmiterea datelor fiscale către ANAF este prevăzută de OUG 28/1999, art. 3^1 alin. (4).

### Pentru contabil

- Cere clientului să confirme modul de lucru al aparatului, online sau offline, direct de la firma de service.
- Pentru aparatele offline, stabilește cine exportă și cine depune fișierele și la ce interval.
- Arhivează fișierele XML semnate. Ele sunt aceleași rapoarte Z folosite la înregistrarea contabilă a vânzărilor.
- Verifică periodic dacă numerele rapoartelor Z din registru corespund cu cele înregistrate în contabilitate.

### De reținut

- Aparatele offline exportă XML-urile zilnice semnate și un XML registru (OPANAF 146/2018, anexa 2, secțiunea II.13).
- Fișierele se validează, se atașează la un PDF cu aplicația ANAF și se depun electronic.
- Fără transmitere la termen, aparatul în profilul 1 își blochează activitatea.
