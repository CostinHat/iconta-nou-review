---
title: "Care este diferența dintre mijloc fix și obiect de inventar?"
description: "Diferența de tratament contabil dintre mijlocul fix (amortizare) și obiectul de inventar (cheltuială integrală + evidență extracontabilă), cu bază legală."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care este diferența dintre mijloc fix și obiect de inventar?

Diferența nu e doar de etichetă contabilă — schimbă complet felul în care valoarea bunului ajunge pe cheltuieli. Un mijloc fix își recuperează costul treptat, prin amortizare, pe durata lui de viață. Un obiect de inventar își trece toată valoarea pe cheltuială dintr-o dată, la momentul în care e dat în folosință, dar rămâne urmărit separat, în afara bilanțului, până când e scos definitiv din uz.

## Temeiul legal

::: ghid-temei
„(2) Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: [...] b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de inflație, prin hotărâre a Guvernului; [...] c) are o durată normală de utilizare mai mare de un an."
— Codul fiscal (Legea 227/2015), art. 28 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

Un bun care nu îndeplinește cumulativ aceste condiții e obiect de inventar, iar tratamentul lui contabil e descris separat, în reglementările OMFP 1802/2014:

::: ghid-temei
„Contul 303 «Materiale de natura obiectelor de inventar» [...] este un cont de activ. [...] În debitul contului 303 [...] se înregistrează: – valoarea la preț de înregistrare a materialelor de natura obiectelor de inventar achiziționate de la terți (401, 408, 446, 323, 542); [...] În creditul contului 303 [...] se înregistrează: – valoarea la preț de înregistrare a materialelor de natura obiectelor de inventar incluse pe cheltuieli, precum și a celor constatate lipsă la inventar sau distruse (603)."
— OMFP 1802/2014, reglementări contabile — funcționarea contului 303 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.html)
:::

Din cele două texte rezultă diferența practică:

- **Mijloc fix**: valoare ≥ prag (5.000 lei din 25.02.2026) **și** durată > 1 an. Costul se recuperează treptat, prin amortizare lunară, pe durata normală de utilizare stabilită.
- **Obiect de inventar**: valoare sub prag **sau** durată ≤ 1 an. La achiziție intră pe contul 303 (activ); la darea în folosință, întreaga valoare trece pe cheltuială (cont 603), iar existența fizică a bunului rămâne urmărită extracontabil, în contul 8035, până la scoaterea lui din uz.
- Un mijloc fix generează, lună de lună, o cheltuială de amortizare proporțională cu valoarea și durata; un obiect de inventar generează o singură cheltuială, integrală, la momentul dării în folosință.

## Ce se greșește în practică

- Se crede că diferența e doar de valoare — de fapt, durata sub un an exclude un bun din categoria mijloc fix indiferent cât de scump e.
- Se amortizează un obiect de inventar sau, invers, se trece integral pe cheltuială un mijloc fix, ceea ce denaturează rezultatul lunii.
- Se ignoră evidența extracontabilă (contul 8035) pentru obiectele de inventar date în folosință — deși valoarea a fost deja trecută pe cheltuială, bunul fizic există în continuare și trebuie urmărit până la scoaterea din uz.
- Se aplică pragul valabil azi unor achiziții mai vechi, în loc de pragul valabil la data intrării în patrimoniu.

## Ce face iConta.eu

iConta.eu tratează cele două categorii prin fluxuri contabile separate. Pentru obiectele de inventar, motorul `core/obiecte_inventar.py` generează automat notele corecte: achiziția (303 = 401, plus TVA dacă e cazul), darea în folosință (603 = 303, cu evidența extracontabilă 8035 = 891) și scoaterea din uz (891 = 8035, care închide evidența). Aceste operații sunt disponibile din formularul „Obiecte de inventar (303)", în ecranul „Operațiuni speciale".

Mijloacele fixe au un flux complet separat, de amortizare, într-o altă zonă a aplicației (registrul de mijloace fixe). Aplicația **nu are** o singură funcție care să „decidă" categoria și să comute automat între cele două fluxuri de la o singură achiziție — contabilul alege ecranul potrivit, iar motorul verifică ulterior, pe baza valorii, dacă achiziția introdusă în ecranul de obiecte de inventar respectă pragul legal.

[iConta.eu](/)
