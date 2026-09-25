---
title: "Veniturile din dividende intră în plafonul micro?"
description: "Ce curs și ce categorie de venituri contează la verificarea plafonului de 100.000 EUR pentru microîntreprinderi, și dacă dividendele primite de la o altă firmă românească intră în calcul."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Veniturile din dividende intră în plafonul micro?

O firmă plătitoare de impozit pe veniturile microîntreprinderilor care încasează, la rândul ei, dividende de la o altă persoană juridică română (de exemplu dintr-o participație) se întreabă frecvent dacă acea sumă se adaugă la plafonul de 100.000 EUR care decide dacă rămâne micro sau trece la impozit pe profit. Răspunsul depinde de o distincție pe care legea o face din 2026 în mod explicit: nu orice venit contează la plafon, ci doar cifra de afaceri.

## Temeiul legal

::: ghid-temei
„a) realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. [...]
(1^1) În aplicarea prevederilor alin. (1) lit. c) limita privind veniturile realizate se verifică luând în calcul veniturile realizate de persoana juridică română, cumulate cu veniturile întreprinderilor legate cu aceasta, iar veniturile care se iau în calcul sunt cele care constituie cifra de afaceri definită potrivit reglementărilor contabile aplicabile/veniturile menționate la lit. d), după caz."
— Codul fiscal (Legea 227/2015), art. 47 alin. (1) lit. c) și alin. (1^1), în forma aplicabilă de la 25.02.2026 (OUG 8/2026, art. 6 pct. 15-16; conform art. 10 alin. (3) din aceeași ordonanță, se aplică inclusiv pentru încadrarea ca microîntreprindere în anul fiscal 2026) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Pe lângă acest text, mai există un al doilea articol relevant, care privește nu plafonul de intrare/ieșire, ci baza pe care se calculează efectiv impozitul de 1%:

- **Art. 53 alin. (1) lit. n) CF**: la baza impozabilă a impozitului pe veniturile microîntreprinderilor se scad „dividendele primite de la o persoană juridică română".

Din cele două texte rezultă două lucruri diferite, care nu trebuie confundate:

- **Plafonul de 100.000 EUR** (art. 47 alin. (1^1)) se verifică pe **cifra de afaceri**, așa cum e definită de reglementările contabile — adică veniturile din vânzarea de produse, mărfuri și prestarea de servicii (conturile de exploatare 70x), nu veniturile financiare. Dividendele primite se înregistrează contabil în conturi de venituri financiare (761/7613 etc.), nu în cifra de afaceri. Prin urmare, **dividendele primite de la o altă firmă românească nu intră, ca regulă, în calculul plafonului de 100.000 EUR** — pentru că nu fac parte din cifra de afaceri.
- **Baza de calcul a impozitului de 1%** (art. 53) e mai largă decât cifra de afaceri („veniturile din orice sursă"), dar exclude explicit dividendele primite de la o persoană juridică română (lit. n) și, în anumite condiții, cele primite de la o filială dintr-un alt stat UE (lit. o). Deci chiar dacă dividendul ar fi contat ca „venit" în sens larg, legea îl scoate oricum din baza impozabilă.

## Ce se greșește în practică

- Se confundă „veniturile realizate" din art. 47 (plafonul de menținere în micro) cu „veniturile din orice sursă" din art. 53 (baza impozitului de 1%) — sunt două noțiuni distincte, verificate cu reguli diferite.
- Se aplică vechea regulă, dinainte de 25.02.2026, când textul art. 47 alin. (1) lit. c) vorbea generic despre „venituri realizate", fără trimiterea explicită la cifra de afaceri introdusă de OUG 8/2026 — pentru anul fiscal 2026, se aplică deja regula nouă.
- Se scapă din vedere că regula „venituri = cifră de afaceri" din art. 47 alin. (1^1) se aplică și cumulat, cu veniturile întreprinderilor legate (participații încrucișate de peste 25%) — pentru firme cu structură de grup, verificarea plafonului nu se face izolat pe fiecare entitate.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu urmărește și nu calculează automat plafonul de 100.000 EUR** al microîntreprinderii. Verificat direct în cod: nu există nicio constantă sau funcție de plafon micro în motorul fiscal — regimul fiscal al firmei (`regim_fiscal`) e un câmp introdus manual de contabil, iar aplicația nu compară veniturile cumulate ale firmei cu pragul legal pentru a semnala automat o eventuală trecere la impozit pe profit.

Ce face aplicația, prin **F029 (D205 + distribuire dividende)**, este partea complementară: calculează impozitul reținut la sursă pe dividendele pe care firma le **plătește** propriilor asociați (cota 16% de la 01.01.2026, generarea automată a declarației D205 din contul 457). Situația din acest ghid — dividende **primite** de firmă de la o altă societate — e un subiect distinct, pe care aplicația nu îl monitorizează în raport cu plafonul micro. Calculul propriu-zis al plafonului rămâne, azi, în responsabilitatea contabilului.

[iConta.eu](/)
