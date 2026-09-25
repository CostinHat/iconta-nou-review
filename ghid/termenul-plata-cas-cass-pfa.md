---
title: "Termenul pentru plata CAS și CASS de către PFA în 2026"
description: "Data limită pentru declararea și plata contribuțiilor sociale datorate de PFA pentru veniturile din activități independente, prin Declarația unică."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Termenul pentru plata CAS și CASS de către PFA în 2026

PFA-urile care realizează venituri peste plafoanele legale datorează contribuția de asigurări sociale (CAS) și contribuția de asigurări sociale de sănătate (CASS). Spre deosebire de salariați, unde angajatorul reține și virează lunar, la PFA obligația e anuală și trece prin Declarația unică — ceea ce schimbă complet logica termenului de plată.

## Temeiul legal

```
::: ghid-temei
„(3) Declarația unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice se completează și se depune la organul fiscal competent, pentru fiecare an fiscal, până la data de 25 mai inclusiv a anului următor celui de realizare a veniturilor."
— Legea nr. 227/2015 privind Codul fiscal, art. 122 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::
```

Ce rezultă concret pentru un PFA, pentru anul fiscal 2026:

- **Termenul de declarare și de plată** a CAS și CASS aferente veniturilor realizate în 2026 este **25 mai 2027** (data de 25 mai inclusiv a anului următor).
- Declarația unică cuprinde atât regularizarea impozitului pe venit, cât și stabilirea CAS/CASS — toate cele trei obligații se declară și se plătesc la același termen, nu separat.
- Baza de calcul pentru CAS nu este venitul net efectiv realizat, ci **venitul ales de contribuabil**, care nu poate fi mai mic decât plafoanele legale (12, respectiv 24 de salarii minime brute pe țară, în funcție de nivelul venitului net realizat cumulat din activități independente).
- Dacă PFA-ul estimează un venit pentru anul curent, poate depune și declarația estimativă la începutul anului — dar obligația de plată efectivă, pe baza venitului definitivat, rămâne legată de termenul de 25 mai al anului următor.

## Ce se greșește în practică

- Se confundă termenul PFA (anual, 25 mai anul următor) cu termenul contribuțiilor salariale, plătite lunar de angajator prin D112 — sunt regimuri complet diferite.
- Se calculează CAS pe venitul net efectiv, ignorând regula venitului ales minim (12/24 salarii minime), ceea ce duce la o contribuție subevaluată și la o diferență de plată constatată ulterior de ANAF.
- Se presupune că, dacă venitul net e sub plafonul de 12 salarii minime, contribuția e automat zero — de fapt, sub acel plafon CAS devine opțională, nu obligatorie, ceea ce e o distincție importantă de verificat înainte de a nu declara nimic.

## Ce face iConta.eu

iConta.eu oferă evidența contabilă a veniturilor și cheltuielilor PFA pe parcursul anului, din care rezultă venitul net, și are un modul dedicat pentru Declarația unică: `core/d212_engine.py` calculează CAS (25%, cu plafonare 12/24 salarii minime) și CASS (10%, cu plafonare 6/60, respectiv 6/72 salarii minime pentru veniturile din 2026, conform Legii 239/2025), iar `core/d212.py` generează formularul D212 (XML), structura fiind confirmată pe validatorul oficial ANAF. Ce **nu automatizează** aplicația: preluarea automată a valorilor calculate în evidența PFA-ului direct în D212 — generatorul primește venitul, cheltuielile deductibile și opțiunile de CAS/CASS ca date furnizate explicit (`manual`), nu le preia singur din registrele contabile — și nici depunerea efectivă a declarației la ANAF, care rămâne, la acest moment, în sarcina contabilului.

[iConta.eu](/)
