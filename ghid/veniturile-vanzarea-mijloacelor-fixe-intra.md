---
title: "Veniturile din vânzarea mijloacelor fixe intră în plafonul micro?"
description: "Cum tratează Codul fiscal veniturile din cesionarea unui mijloc fix, atât la verificarea plafonului de 100.000 euro, cât și la baza impozabilă a microîntreprinderii."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Veniturile din vânzarea mijloacelor fixe intră în plafonul micro?

Legea răspunde clar pentru baza impozabilă a impozitului pe veniturile microîntreprinderilor: veniturile din vânzarea unui mijloc fix nu se numără printre excepțiile permise. Pentru verificarea plafonului de 100.000 euro însă, legea folosește o altă noțiune decât „venituri din orice sursă" — iar art. 54 din Codul fiscal transează explicit ce anume intră în calcul.

## Temeiul legal

::: ghid-temei
„Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie veniturile din orice sursă, din care se scad: a) veniturile aferente costurilor stocurilor de produse; [...] c) veniturile din producția de imobilizări corporale și necorporale; [...]" (urmează o listă închisă de excepții — subvenții, diferențe de curs, dividende primite, despăgubiri, reduceri comerciale acordate ulterior facturării ș.a. — care nu include veniturile din vânzarea mijloacelor fixe deja folosite în activitate).
— Legea nr. 227/2015, art. 53 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„[...] a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile."
— Legea nr. 227/2015, art. 47 alin. (1) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Pentru încadrarea în condițiile privind nivelul veniturilor prevăzute la art. 47 alin. (1) lit. c) și la art. 52 alin. (1) se iau în calcul veniturile care constituie cifra de afaceri definită potrivit reglementărilor contabile aplicabile. Pentru aplicarea prevederilor art. 52 alin. (1), la calculul cifrei de afaceri se adaugă și veniturile din transferul mijloacelor fixe/terenurilor înregistrate cumulat de la începutul anului fiscal, în situația în care microîntreprinderea transferă, în cursul anului fiscal, mai mult de un activ din oricare subgrupă, astfel cum sunt prevăzute în Catalogul privind clasificarea și duratele normale de funcționare a mijloacelor fixe, aprobat prin hotărâre a Guvernului, respectiv mai mult de un teren."
— Legea nr. 227/2015, art. 54 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă, corect de data asta:

- **Baza impozabilă a microîntreprinderii**: venitul din vânzarea unui mijloc fix (de exemplu un utilaj scos din folosință și vândut) intră în baza impozabilă a impozitului pe veniturile microîntreprinderilor, pentru că nu figurează printre excepțiile limitativ enumerate la art. 53 alin. (1) — deci se impozitează, ca orice alt venit.
- **Plafonul de 100.000 euro nu se verifică pe „venituri din orice sursă"**, ci pe **cifra de afaceri definită potrivit reglementărilor contabile** — asta spune explicit art. 54 alin. (1), atât pentru încadrarea de la art. 47 alin. (1) lit. c), cât și pentru verificarea în cursul anului de la art. 52 alin. (1). Veniturile din vânzarea/cedarea unui mijloc fix nu fac parte, ca regulă, din cifra de afaceri (care cuprinde veniturile din vânzarea de produse/mărfuri/prestarea de servicii), spre deosebire de baza impozabilă trimestrială, care pornește de la „venituri din orice sursă".
- **Excepția explicită, îngustă**: pentru verificarea ieșirii din regim în cursul anului (art. 52 alin. (1)), art. 54 alin. (1) adaugă la cifra de afaceri veniturile din transferul mijloacelor fixe/terenurilor cumulate de la începutul anului, dar **doar dacă** firma transferă, în cursul anului fiscal, **mai mult de un activ din aceeași subgrupă** (sau mai mult de un teren). Vânzarea izolată a unui singur mijloc fix nu declanșează această adăugare.
- **Concluzia practică**: contrar unei citiri izolate a art. 47 alin. (1) lit. c), legea nu lasă loc de interpretare aici — art. 54 alin. (1) transează explicit chestiunea. Regula corectă e opusă unei includeri automate „din prudență": venitul din vânzarea unui mijloc fix nu intră, ca regulă, în cifra de afaceri relevantă pentru plafon, cu excepția cazului specific de la art. 54 alin. (1) (mai multe active din aceeași subgrupă transferate în cursul anului, pentru verificarea ieșirii din regim la art. 52 alin. (1)).

## Ce se greșește în practică

- Se include „din prudență" venitul din vânzarea unui mijloc fix la calculul plafonului de micro, confundând baza impozabilă (venituri din orice sursă, art. 53) cu cifra de afaceri relevantă pentru plafon (art. 54 alin. (1)) — legea le tratează diferit, iar includerea nejustificată poate scoate eronat o firmă din regimul micro.
- Se omite acest venit din baza impozabilă trimestrială, deși art. 53 alin. (1) nu îl scutește — omisiunea înseamnă impozit pe veniturile microîntreprinderilor calculat greșit, în minus.
- Se tratează la fel toate veniturile „neobișnuite" (despăgubiri, sponsorizări primite, subvenții), deși fiecare are regim propriu explicit în lege — vânzarea unui mijloc fix nu se regăsește în niciuna dintre excepțiile enumerate.

## Ce face iConta.eu

Calculul impozitului pe veniturile microîntreprinderilor din iConta.eu pornește de la veniturile înregistrate contabil ale firmei, fără o excepție separată, programată, pentru veniturile din vânzarea mijloacelor fixe — acestea intră în baza de calcul ca orice alt venit contabilizat pe conturile de venituri, în linie cu art. 53 alin. (1). Verificarea plafonului de 100.000 euro (distinctă de baza impozabilă, guvernată de cifra de afaceri conform art. 54 alin. (1)) nu este automatizată în aplicație, care nu are o constantă sau un modul dedicat pentru plafonul de încadrare la micro — rămâne o verificare manuală a contabilului.

[iConta.eu](/)
