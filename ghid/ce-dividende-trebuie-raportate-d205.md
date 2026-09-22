---
title: Ce dividende trebuie raportate în D205?
description: D205 raportează, pentru fiecare beneficiar, atât dividendul distribuit cât și cel plătit, iar dividendele distribuite dar neplătite până la sfârșitul anului rămân datoare cu impozit, în declarația anului în care s-a aprobat distribuirea.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce dividende trebuie raportate în D205?

D205 nu cere raportarea unei singure sume de dividend per beneficiar, ci distinge clar între dividendul distribuit (aprobat) și cel efectiv plătit — o distincție cu consecințe fiscale directe, mai ales atunci când plata întârzie față de aprobarea distribuirii. Explicăm mai jos ce trebuie raportat exact și de ce contează diferența.

## Temeiul legal

::: ghid-temei
„Cap. V «Date informative privind impozitul pe veniturile din dividende» se completează de către plătitorii de venituri din dividende, pentru fiecare persoană fizică beneficiară." Col.3 = „totalul venitului distribuit din dividende"; Col.4 = „totalul venitului plătit acţionarilor sau asociaţilor din dividendele distribuite"; Col.5 = „baza de calcul al impozitului"; Col.6 = „totalul impozitului pe venit calculat şi reţinut în cursul anului". (OPANAF 179/2022, Secțiunea V dividende, l.381-397)

„Impozitul aferent dividendelor distribuite, dar care nu au fost plătite acţionarilor sau asociaţilor până la sfârşitul anului în care s-a aprobat distribuirea acestora se cuprinde în declaraţia aferentă perioadei în care s-a aprobat distribuirea dividendelor." (OPANAF 179/2022, Cap.V dividende, l.398-400)

„divid_D 7.V. Dividende distribuite N(15) NU divid_D >=0 pt. tip_venit1=08... divid_D nu se completeaza pt. tip_venit1<>08"; „divid_P 8.V. Dividende platite N(15) NU divid_P >=0 pt. tip_venit1=08..." (structura D205, OPANAF 102/2025, rd.39.a-b)

„În cazul dividendelor/câştigurilor... distribuite, dar care nu au fost plătite acţionarilor/asociaţilor/investitorilor până la sfârşitul anului în care s-a aprobat distribuirea acestora, impozitul pe dividende/câştig se plăteşte până la data de 25 ianuarie inclusiv a anului următor distribuirii." (Legea 141/2025, art.II pct.5)
:::

## Distribuit vs. plătit — de ce contează amândouă

D205 are patru coloane relevante pentru fiecare beneficiar de dividende: totalul distribuit, totalul plătit, baza de calcul a impozitului și impozitul reținut. Distribuirea este momentul aprobării (hotărârea AGA/asociaților pe baza situațiilor financiare), plata este momentul transferului efectiv al banilor către asociat. Cele două pot cădea în ani fiscali diferiți.

Regula legală importantă este că dividendele distribuite dar **neplătite până la 31 decembrie** rămân totuși datoare cu impozit — acesta se raportează în declarația aferentă anului în care s-a aprobat distribuirea, cu termen de plată a impozitului până la 25 ianuarie a anului următor. Cu alte cuvinte, faptul că un asociat nu a încasat încă dividendul nu amână raportarea în D205 — o amână doar pe cea a plății efective a impozitului la buget.

## Ce se greșește în practică

- Se raportează doar dividendele efectiv plătite până la 31 decembrie, omițând complet cele aprobate dar neplătite, deși legal acestea trebuie și ele raportate.
- Se presupune că impozitul pe un dividend distribuit dar neplătit nu e deloc datorat, până la plata efectivă — de fapt termenul de virare devine 25 ianuarie anul următor, nu se anulează.
- Se confundă coloana „distribuit" cu coloana „plătit" la completarea manuală a unor poziții, ceea ce produce o declarație inconsistentă.
- Se ignoră diferența dintre dividendele anuale (contul 457) și cele interimare (contul 456, până la regularizare) — vezi ghidul dedicat dividendelor interimare pentru acest caz specific.

## Ce face iConta.eu

Pentru fiecare asociat, aplicația calculează separat suma distribuită și suma plătită din mișcările din contul de dividende. Atenție însă la un caz important: dacă un dividend a fost **distribuit (aprobat) dar nu a fost plătit deloc** până la sfârșitul anului, generatorul automat **nu include acel beneficiar în declarație** — nu apare nici cu suma distribuită, nici cu o bază de calcul parțială, ci lipsește complet, împreună cu impozitul aferent. Aceasta pentru că motorul de generare calculează beneficiarul pornind de la suma efectiv plătită; când suma plătită este zero, nu se generează nicio poziție pentru acel asociat, deși legal impozitul rămâne datorat (cu termen de plată 25 ianuarie anul următor). Pentru orice dividend aprobat dar neplătit integral până la 31 decembrie, verificați manual, înainte de depunere, dacă beneficiarul respectiv apare în declarația generată — dacă lipsește, trebuie adăugat manual, împreună cu impozitul aferent, pentru a evita omiterea unei sume datorate.

[iConta.eu](/)
