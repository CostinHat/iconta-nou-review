---
title: "D104 pentru impozitul pe profit din cedarea drepturilor de proprietate intelectuală"
description: "D104 este declarația prin care asociatul desemnat al unei asocieri fără personalitate juridică raportează distribuirea veniturilor și cheltuielilor — inclusiv din cedarea de drepturi de proprietate intelectuală — între asociați."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D104 pentru impozitul pe profit din cedarea drepturilor de proprietate intelectuală

Când mai multe persoane sau firme desfășoară activitate în comun printr-o asociere fără personalitate juridică — inclusiv atunci când asocierea generează venituri din cedarea unor drepturi de proprietate intelectuală — cineva trebuie să raporteze la ANAF cum se împart între asociați veniturile, cheltuielile și impozitul aferent. Acel „cineva" e asociatul desemnat, iar formularul e D104.

## Temeiul legal

::: ghid-temei
„(1) Într-o asociere fără personalitate juridică între două sau mai multe persoane juridice române, veniturile și cheltuielile înregistrate se atribuie fiecărui asociat, conform prevederilor contractului de asociere.
(2) Veniturile și cheltuielile determinate de operațiunile asocierii, transmise pe bază de decont fiecărui asociat, potrivit reglementărilor contabile aplicabile, se iau în calcul pentru determinarea profitului impozabil al fiecărui asociat. Documentele justificative aferente operațiunilor asocierii sunt cele care au stat la baza înregistrării în evidența contabilă de către persoana desemnată de asociați, conform prevederilor contractului de asociere."
— Codul fiscal (Legea 227/2015), art. 34 alin. (1)-(2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce presupune, în esență, D104:

- Declarația e depusă de asociatul desemnat al asocierii, nu individual de fiecare membru — el centralizează profitul/pierderea asocierii și îl repartizează pe fiecare asociat, cu cota de participare a fiecăruia.
- Veniturile și cheltuielile asocierii se atribuie fiecărui asociat **conform contractului de asociere**, iar decontul transmis fiecărui asociat, pe baza documentelor justificative păstrate de persoana desemnată, intră direct în calculul profitului impozabil al fiecăruia.
- Practic, D104 este vehiculul declarativ prin care asociatul desemnat comunică ANAF această repartizare — inclusiv atunci când asocierea a realizat venituri dintr-o cedare de drepturi de proprietate intelectuală, tratate ca orice alt venit al asocierii, potrivit cotelor din contract.
- Se depune trimestrial cumulat (la lunile 3, 6, 9) și se definitivează anual (luna 12) — la depunerile trimestriale, impozitul de recuperat și diferența plată/recuperare rămân zero, acestea calculându-se doar la definitivare.

## Ce se greșește în practică

- Se depune câte o declarație individuală per asociat pentru veniturile din asociere, în loc de o singură declarație D104 depusă de asociatul desemnat, în numele întregii asocieri.
- Se omite definitivarea anuală (luna 12), rămânând doar la nivelul depunerilor trimestriale cumulate, care nu calculează diferența finală de plată sau recuperare.
- Se confundă regimul unei asocieri fără personalitate juridică cu cel al unei persoane juridice de sine stătătoare — profitul/pierderea asocierii nu se declară separat prin D101, ci se repartizează prin D104 pe fiecare asociat.

## Ce face iConta.eu

D104 are motorul de generare construit în iConta.eu (core/d104.py): calculează totalurile pe asociați, diferențele de plată/recuperare și suma de control, cu structura verificată pe validatorul oficial. La data acestui ghid, funcționalitatea este **amânată** în interfață — motorul de calcul și validarea există, dar declarația nu are încă un ecran dedicat în selectorul de declarații al firmei, ci apare doar în dispecerul intern; identitatea asocierii, precum și profitul/pierderea de repartizat (calculul căruia poate implica ajustări fiscale, inclusiv pentru cedarea de drepturi de proprietate intelectuală) rămân date introduse manual.

[iConta.eu](/)
