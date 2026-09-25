---
title: "Telefonul mobil cumpărat pe firmă este deductibil?"
description: "Când costul de achiziție al unui telefon mobil cumpărat de firmă e cheltuială deductibilă, conform regulii generale a Codului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Telefonul mobil cumpărat pe firmă este deductibil?

Nu există o regulă specială pentru telefoane mobile în Codul fiscal — deductibilitatea achiziției urmează regula generală aplicabilă oricărei cheltuieli: dacă e făcută în scopul activității economice, e deductibilă.

## Temeiul legal

::: ghid-temei
„Pentru determinarea rezultatului fiscal sunt considerate cheltuieli deductibile cheltuielile efectuate în scopul desfășurării activității economice, inclusiv cele reglementate prin acte normative în vigoare, precum și taxele de înscriere, cotizațiile și contribuțiile datorate către camerele de comerț și industrie, organizațiile patronale și organizațiile sindicale."
— Legea 227/2015 (Codul fiscal), art. 25 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Aplicat la un telefon mobil cumpărat de firmă:

- Costul e deductibil dacă achiziția e făcută **în scopul activității economice** — un telefon folosit de un angajat sau administrator pentru comunicare legată de activitatea firmei îndeplinește această condiție.
- Modul concret de deducere depinde de **valoarea** telefonului: dacă valoarea de intrare atinge pragul legal pentru mijloc fix, costul se recuperează prin amortizare, pe durata normală de utilizare; sub acel prag, costul intră direct pe cheltuială, la darea în folosință (ca obiect de inventar).
- Dacă telefonul e folosit și în scop personal (uz mixt), deductibilitatea integrală poate fi pusă la îndoială de organul fiscal, care poate cere justificarea scopului economic al cheltuielii — nu există însă, verificat la sursă în acest ghid, o normă specifică de limitare procentuală pentru telefoane mobile, așa cum există pentru alte categorii de cheltuieli (de exemplu vehicule).

## Ce se greșește în practică

- Se presupune că orice telefon cumpărat pe firmă e automat 100% deductibil, fără nicio legătură documentată cu activitatea economică.
- Se tratează greșit modul de deducere: se trece integral pe cheltuială un telefon a cărui valoare depășește pragul legal de mijloc fix, în loc să fie amortizat pe durata normală de utilizare.
- Se ignoră TVA-ul: deducerea TVA la achiziție urmează regulile generale de deducere (folosire în scopul operațiunilor taxabile ale firmei), separat de deductibilitatea costului la impozitul pe profit/venit.

## Ce face iConta.eu

Clasificarea și înregistrarea unui activ ca mijloc fix sau ca obiect de inventar, în funcție de valoarea lui de achiziție, e un motor real în aplicație (`core/obiecte_inventar.py`), care aplică pragul legal curent din registrul de cote al firmei și generează notele contabile corespunzătoare — atât pentru achiziție, cât și pentru darea în folosință. Acest motor nu e specific telefoanelor mobile, ci se aplică oricărui activ de valoare mică introdus în evidență; deductibilitatea propriu-zisă la impozitul pe profit/venit rezultă din felul în care cheltuiala e clasificată și înregistrată, nu dintr-un calcul separat, dedicat unei categorii de bunuri.

[iConta.eu](/)
