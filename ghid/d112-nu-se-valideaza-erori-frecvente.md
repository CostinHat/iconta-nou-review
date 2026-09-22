---
title: De ce nu se validează declarația D112?
description: D112 refuză generarea, nu trimite un fișier invalid la ANAF, când lipsesc date obligatorii din XSD — CAEN sau CUI-ul firmei, CNP-ul, numele sau data angajării salariatului, identificatorul certificatului de concediu medical.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# De ce refuză aplicația să genereze D112 și ce trebuie completat?

D112 (Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate) are un fișier XSD publicat de ANAF care marchează anumite câmpuri drept **obligatorii, fără valoare implicită** — nu pot rămâne goale, nu pot fi completate cu o valoare inventată doar ca să treacă validarea. Când unul dintre ele lipsește, regula corectă nu e să se genereze un XML „aproape corect" care ar pica la ANAF, ci să se oprească generarea și să se spună exact ce lipsește și unde se completează.

## Temeiul legal

::: ghid-temei
D112 e reglementată de **titlul V din Codul fiscal** (contribuții sociale obligatorii) și de structura tehnică publicată de ANAF prin schema XSD a declarației. Câmpurile pe care XSD-ul le marchează drept obligatorii (CAEN, CUI, CNP, numele asiguratului, data angajării, identificatorul certificatului de concediu medical) nu au o valoare implicită validă — absența lor face fișierul neconform structurii pe care ANAF o acceptă la depunere.
:::

## Cauzele frecvente ale refuzului

**CAEN-ul firmei lipsă sau invalid.** D112 cere un cod CAEN valid din profilul firmei — fără el, generarea se oprește cu mesajul că CAEN-ul lipsește/e invalid.

**CUI-ul firmei invalid.** Verificat înainte de generare cu algoritmul de cifră de control — dacă CUI-ul din Profil firmă nu trece validarea, D112 nu se emite; altfel eroarea ar ajunge tăcută la ANAF, ca „CUI invalid", fără indicație unde se corectează.

**CNP invalid pe un salariat.** Fiecare CNP e verificat cu checksum-ul oficial înainte de generare. Un CNP greșit în fișa salariatului oprește declarația pentru salariatul respectiv, cu numele lui în mesaj, ca să fie ușor de găsit.

**Numele asiguratului gol.** Câmpul e obligatoriu în structura ANAF („vid nepermis") — un salariat fără nume completat în fișă blochează generarea.

**Data angajării necompletată.** Câmp obligatoriu în XSD — fără ea, salariatul respectiv nu poate intra în D112.

**Certificat de concediu medical fără identificator, sau fără CNP-ul persoanei îngrijite** (la concediile pentru îngrijirea unui copil sau membru de familie) — câmpuri obligatorii la nivel de certificat, nu se completează implicit.

## Ce se greșește în practică

- **Se caută eroarea în D112 în sine**, deși cauza e aproape întotdeauna în altă parte — profilul firmei sau fișa salariatului/certificatului.
- **Se completează un CNP sau un CAEN „provizoriu"** doar ca să treacă validarea — asta produce exact fișierul invalid pe care regula încearcă să-l prevină, doar mutat de la aplicație la ANAF.
- **Nu se verifică certificatele de concediu medical** ca sursă a blocajului — un certificat introdus fără identificator sau fără CNP-ul persoanei îngrijite oprește declararea, chiar dacă restul datelor salariatului sunt corecte.

## Ce face iConta.eu

Fiecare validare rulează înainte de generarea propriu-zisă și oprește procesul cu un mesaj care spune concret ce lipsește, pe cine anume (numele și CNP-ul salariatului, dacă e cazul) și unde se corectează — Profil firmă sau fișa salariatului/certificatului de concediu medical. Regula e deliberată: nu se emite niciodată un D112 despre care se știe dinainte că va fi respins la ANAF, doar ca declarația să „iasă".

[iConta.eu](/)
