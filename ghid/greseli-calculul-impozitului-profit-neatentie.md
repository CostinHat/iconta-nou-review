---
title: "Greșeli la calculul impozitului pe profit din neatenție"
description: "Trece în revistă cele mai documentate greșeli de calcul al impozitului pe profit, confirmate în cod și în legislație, plus un bug curent al aplicației."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeli la calculul impozitului pe profit din neatenție

## Temeiul legal

::: ghid-temei
CF art.25 alin.(4) lit.a): cheltuiala cu impozitul pe profit (cont contabil 691) este nedeductibilă și trebuie adăugată înapoi la baza impozabilă.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `core/d101.py`, dosar de cercetare F027.

Art.18^1 alin.(16) CF (introdus prin OUG 89/2025 art.I pct.1, MO 1203/24.12.2025, în vigoare 01.01.2026): "Pentru anul fiscal 2026/anul fiscal modificat care începe în anul 2026, cota de impozit din cadrul formulei prevăzute la alin.(3) este 0,5%."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

CF art.25 alin.(4) lit.i): sponsorizarea e deductibilă în limita a 20% din impozitul pe profit datorat și, suplimentar, în limita a 0,75% din cifra de afaceri.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `core/d101.py`, dosar de cercetare F027.
:::

Din verificarea codului sursă al motorului D101 și a legislației aplicabile, cele mai frecvente greșeli din neatenție la calculul impozitului pe profit sunt: omiterea add-back-ului pentru cheltuiala cu propriul impozit pe profit (cont 691, art.25 alin.(4) lit.a)); reintroducerea manuală uitată a amortizării în D101 după corectarea unui mijloc fix (D101 nu recalculează retroactiv declarația deja generată); nerespectarea dublei limite de deductibilitate a sponsorizării (20% din impozit ȘI 0,75% din cifra de afaceri, art.25 alin.(4) lit.i)); și, pentru anul fiscal 2026, aplicarea cotei greșite de IMCA.

## Ce se greșește în practică

Omiterea add-back-ului pentru cont 691 a redus, măsurat pe portofoliu, impozitul declarat cu 2.432 lei fără niciun semnal anterior introducerii controlului dedicat. Pentru sponsorizare, verificarea manuală a limitei de 0,75% din cifra de afaceri e necesară deoarece motorul oficial DUK verifică singur doar limita de 20%.

## Ce face iConta.eu

iConta.eu emite un avertisment automat când soldul debitor al contului 691 (cheltuiala cu impozitul pe profit) e mai mare decât zero, iar rândul P23 (cheltuieli nedeductibile) e completat cu zero — semn tipic că impozitul pe profit propriu nu a fost adăugat înapoi ca nedeductibil (CF art.25 alin.(4) lit.a)). Măsurată pe un portofoliu de test, omiterea acestei adăugări a scăzut impozitul declarat cu 2.432 lei, fără niciun alt semnal înainte de introducerea acestui gard. Corectarea unui mijloc fix (valoare de intrare, durată normală de funcționare, dată punere în funcțiune) schimbă amortizarea fiscală recalculată de contabil, care intră direct în P11 (deducere) și, unde e cazul, în rollup-ul P28/P34 (add-back contabil) din D101. iConta.eu NU recalculează retroactiv o D101 deja generată la o corecție de mijloc fix — ajustarea trebuie reintrodusă manual în declarație. Motorul de amortizare pe mijloace fixe (`core/d406_active.py`) calculează acum amortizarea pe fiecare metodă din activ — liniară, degresivă, accelerată și superaccelerată (CF art.28 alin.(6)-(8^1)); limitarea anterioară („doar liniar") a fost închisă pe 13.08.2026 (`DECIZII.md`). D101 tratează însă în continuare amortizarea ca intrare manuală, indiferent de metodă — contabilul introduce valorile în P11/P28, aplicația nu le preia automat în declarație. Pentru sponsorizare (P43), iConta.eu aplică dubla limită legală: 20% din impozitul pe profit datorat (verificată de motorul oficial DUK) și, suplimentar, 0,75% din cifra de afaceri — a doua verificare a fost adăugată manual în cod, pentru că motorul DUK verifică singur doar limita de 20% (CF art.25 alin.(4) lit.i)). Atenție: motorul D101 din iConta.eu calculează astăzi IMCA cu formula `impozit_minim_cifra_afaceri`, cablată pe cota fixă de 1% (`core/d101.py`, confirmat de testul `test_imca_formula_1pct_din_vt_vs_i_a`), deși legea prevede explicit 0,5% pentru anul fiscal 2026 (art.18^1 alin.(16) CF, introdus prin OUG 89/2025). Dacă firma dvs. se încadrează la IMCA pentru 2026, impozitul minim generat de aplicație poate fi dublu față de cel legal — verificați manual suma până la corectarea acestui bug. iConta.eu nu generează în prezent o D101 rectificativă din interfață: toate flagurile de stare din structura XML (`d_rec`, `d_reg`, `d_reglem`, `d_anulare`, `d_succ`, `d_prof`, `d_alte`) sunt fixate la `"0"` direct în cod (`build_xml`, `core/d101.py`), fără niciun parametru de intrare care să le poată seta. Modulul de rectificative din aplicație (D710) acoperă doar obligațiile declarate prin D100 (cod 121 micro / cod 103 profit trimestrial), nu și D101. Corectarea unei D101 deja depuse trebuie făcută astăzi direct la ANAF, în afara aplicației; nici sursele legale locale nu conțin un act normativ dedicat procedurii de rectificare a D101 (spre deosebire de D710, unde OPANAF 649/2025 e citat explicit), deși structura XML oficială (`opanaf_206_2025_d101.txt`) confirmă existența flagului `d_rec` la nivel de formular.

[iConta.eu](/)
