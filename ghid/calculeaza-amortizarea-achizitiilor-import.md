---
title: "Cum se calculează amortizarea achizițiilor din import"
description: "Ce elemente intră în baza de amortizare a unui mijloc fix cumpărat din import — prețul de cumpărare, taxele vamale și cheltuielile conexe — conform reglementărilor contabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează amortizarea achizițiilor din import

Amortizarea unui mijloc fix cumpărat din afara UE nu se calculează doar pe prețul facturat de furnizorul extern. Baza de amortizare este costul de achiziție complet — care include taxele vamale plătite la import și toate cheltuielile necesare pentru a aduce bunul la starea de funcționare, nu doar valoarea în valută convertită în lei.

## Temeiul legal

::: ghid-temei
„6. cost de achiziție înseamnă prețul datorat și eventualele cheltuieli conexe minus eventualele reduceri ale costului de achiziție. În acest sens, costul de achiziție al bunurilor cuprinde prețul de cumpărare, taxele de import și alte taxe (cu excepția acelora pe care persoana juridică le poate recupera de la autoritățile fiscale), cheltuielile de transport, manipulare și alte cheltuieli care pot fi atribuibile direct achiziției bunurilor respective."
— OMFP nr. 1.802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate), pct. 8 subpct. 6 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la un mijloc fix din import, baza de amortizare (valoarea fiscală de intrare) se formează astfel:

- **Prețul de cumpărare** convertit în lei la cursul BNR de la data operațiunii (evaluarea inițială a tranzacției în valută), plus
- **Taxele vamale și alte taxe de import nerecuperabile** — sumele plătite la vamă intră direct în costul de achiziție, exact cum prevede textul citat; excepția o constituie taxele pe care firma le poate recupera de la autoritățile fiscale, cum e TVA-ul la import deductibil, care nu majorează costul, ci se înregistrează separat, ca taxă deductibilă.
- **Cheltuielile de transport, manipulare și alte cheltuieli atribuibile direct achiziției** — de exemplu asigurarea transportului internațional, comisioanele agentului vamal, cheltuielile de descărcare — toate se adaugă la costul de achiziție, nu se trec direct pe cheltuieli curente.
- Suma tuturor acestor elemente formează valoarea de la care pornește amortizarea fiscală, potrivit art. 28 din Codul fiscal — nu doar prețul net facturat de furnizorul din afara UE.

## Ce se greșește în practică

- Se amortizează mijlocul fix doar pe baza prețului din factura externă, fără să se includă taxele vamale plătite separat la vamă.
- Se include în costul de achiziție și TVA-ul la import, deși acesta e recuperabil (deductibil) și nu ar trebui să majoreze baza de amortizare.
- Se trec cheltuielile de transport internațional sau comisioanele vamale direct pe cheltuieli curente, în loc să fie capitalizate în costul mijlocului fix, conform pct. 8 subpct. 6.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează amortizarea pe baza valorii de intrare introduse manual de utilizator pentru fiecare mijloc fix (`core/mijloace_fixe_import_api.py`, `core/repo_mijloace_fixe.py`). Aplicația **nu însumează automat** prețul din factura externă cu taxele vamale, cheltuielile de transport sau alte cheltuieli conexe dintr-o declarație vamală de import — determinarea costului de achiziție complet, conform pct. 8 subpct. 6 din OMFP 1802/2014, și introducerea lui ca valoare de intrare a mijlocului fix rămân o operațiune manuală a contabilului, pe baza documentelor vamale și de transport.

[iConta.eu](/)
