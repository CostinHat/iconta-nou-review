---
title: "Cum se contabilizează un proiect software facturat pe etape?"
description: "Regulile de recunoaștere a veniturilor pentru un proiect de dezvoltare software facturat în tranșe, pe măsura livrării etapelor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează un proiect software facturat pe etape?

Un proiect de dezvoltare software facturat pe etape (analiză, dezvoltare, testare, livrare finală) intră la categoria prestărilor de servicii, iar regula contabilă de bază este simplă: venitul se recunoaște pe măsură ce serviciul e efectiv prestat și acceptat, nu la semnarea contractului și nici doar la facturare.

## Temeiul legal

::: ghid-temei
„Venituri din prestarea de servicii
446. - (1) Veniturile din prestări de servicii se înregistrează în contabilitate pe măsura efectuării acestora. Prestarea de servicii cuprinde inclusiv executarea de lucrări și orice alte operațiuni care nu pot fi considerate livrări de bunuri. (2) Stadiul de execuție al lucrării se determină pe bază de situații de lucrări care însoțesc facturile, procese-verbale de recepție sau alte documente care atestă stadiul realizării și recepția serviciilor prestate. [...] (4) Contravaloarea lucrărilor nerecepționate de beneficiar până la sfârșitul perioadei se evidențiază la cost, în contul 332 «Servicii în curs de execuție», pe seama contului 712 «Venituri aferente costurilor serviciilor în curs de execuție». [...]
447. - În cazul în care prețul de vânzare include o valoare distinctă, specificată contractual, destinată prestării ulterioare de servicii (de exemplu, asistența tehnică și perfecționarea produsului după vânzarea unui program informatic), acea sumă este amânată (contul 472 «Venituri înregistrate în avans») și recunoscută ca venit pe parcursul perioadei în care se prestează serviciile [...]"
— OMFP nr. 1.802/2014, Reglementări contabile privind situațiile financiare anuale individuale, pct. 446-447 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Fiecare etapă facturată și recepționată de client (pe bază de proces-verbal de recepție sau document echivalent) se recunoaște ca venit din prestări de servicii (cont 704 sau 706, după caz) la momentul finalizării etapei respective.
- Dacă la finalul unei perioade de raportare (lună, trimestru, an) există muncă deja efectuată dar încă nerecepționată de client, valoarea la cost a acestei munci se înregistrează în contul 332 „Servicii în curs de execuție", pe seama contului 712 — nu se recunoaște ca venit facturat, ci ca producție neterminată.
- Dacă prețul contractului include o componentă separată pentru servicii ulterioare livrării (de exemplu mentenanță sau suport tehnic post-livrare), acea sumă nu se recunoaște integral la facturare, ci se amână în contul 472 și se eșalonează pe perioada în care serviciile respective se prestează efectiv.
- Facturarea pe etape este un mecanism de decontare cu clientul, dar nu înlocuiește principiul contabil de bază: venitul urmează stadiul real de execuție, nu doar emiterea facturii.

## Ce se greșește în practică

- Se recunoaște integral venitul la emiterea fiecărei facturi de etapă, chiar dacă etapa respectivă nu a fost efectiv finalizată sau recepționată de client la acel moment.
- Se ignoră contul 332 „Servicii în curs de execuție" pentru munca deja prestată dar nefacturată/nerecepționată la închiderea lunii sau a exercițiului financiar, ceea ce denaturează rezultatul perioadei.
- Se facturează integral serviciile de mentenanță sau suport incluse în preț la livrarea finală a proiectului, în loc să se eșaloneze venitul pe durata efectivă a serviciilor ulterioare (contul 472).
- Se confundă avansurile încasate de la client (care nu sunt venit până la prestarea serviciului) cu veniturile din etapele efectiv finalizate.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un modul dedicat pentru contabilitatea de proiect** (urmărirea stadiului de execuție, gestionarea automată a conturilor 332/472/712 pe fiecare proiect software facturat pe etape). Facturile pe etape și înregistrările contabile aferente se introduc și se contează prin fluxul general de facturare și jurnal al aplicației, iar aplicarea corectă a principiilor de mai sus — recunoașterea pe stadiul real de execuție, distincția între venit recunoscut și servicii în curs de execuție — rămâne în sarcina contabilului.

[iConta.eu](/)
