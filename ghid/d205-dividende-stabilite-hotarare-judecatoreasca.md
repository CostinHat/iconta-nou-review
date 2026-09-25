---
title: "D205 pentru dividende stabilite prin hotărâre judecătorească"
description: "Când plata unor dividende e impusă unei firme printr-o hotărâre judecătorească, momentul de impozitare pentru D205 rămâne cel al distribuirii aprobate de AGA, nu data hotărârii."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D205 pentru dividende stabilite prin hotărâre judecătorească

Uneori plata unor dividende deja aprobate de adunarea generală, dar neplătite, ajunge să fie impusă firmei printr-o hotărâre judecătorească (de exemplu la cererea unui asociat care se retrage sau într-un litigiu privind executarea unei hotărâri AGA). Întrebarea firească e ce dată contează pentru D205 și pentru cota de impozit aplicabilă: data hotărârii AGA de distribuire, data hotărârii judecătorești, sau data plății efective? Legea răspunde clar: hotărârea judecătorească nu creează un nou moment de impozitare — ea doar obligă la executarea unei obligații de plată deja existentă.

## Temeiul legal

::: ghid-temei
„Veniturile sub formă de dividende [...] se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. [...] Termenul de virare a impozitului este până la data de 25 inclusiv a lunii următoare celei în care se face plata. În cazul dividendelor/câștigurilor obținute ca urmare a deținerii de titluri de participare, distribuite, dar care nu au fost plătite acționarilor/asociaților/investitorilor până la sfârșitul anului în care s-a aprobat distribuirea acestora, impozitul pe dividende/câștig se plătește până la data de 25 ianuarie inclusiv a anului următor distribuirii."
— Legea 227/2015, art. 97 alin. (7) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Consecințele pentru D205:

- Cota de impozit aplicabilă se determină după **data distribuirii** aprobate de AGA (înregistrarea în credit 457), nu după data hotărârii judecătorești care obligă firma să plătească. O distribuire aprobată în 2025, plătită efectiv în 2026 în urma unei hotărâri judecătorești, poate purta cota valabilă la data distribuirii (10% pentru distribuirile din situații interimare 2025), nu cota de la data plății.
- Dacă dividendul distribuit prin hotărâre AGA nu a fost plătit până la sfârșitul anului distribuirii, legea consideră impozitul scadent oricum, „până la data de 25 ianuarie inclusiv a anului următor distribuirii" — indiferent dacă plata efectivă se produce mai târziu, forțată printr-o hotărâre judecătorească ulterioară.
- Hotărârea judecătorească poate stabili și dobânzi penalizatoare pentru întârzierea plății (conform art. 3 din OG 13/2011), dar acestea sunt un venit distinct al asociatului (venit din dobânzi), nu fac parte din baza de impozitare a dividendului raportat în D205.
- În D205, beneficiarul apare cu dividendul brut aprobat prin hotărârea AGA inițială; hotărârea judecătorească e doar titlul executoriu pentru plată, nu o sursă separată de raportare.

## Ce se greșește în practică

- Se recalculează impozitul pe dividend la cota valabilă în anul plății forțate prin instanță, în loc de cota valabilă la data distribuirii aprobate de AGA.
- Se amână declararea D205 până la finalizarea litigiului, deși legea impune termenul de 25 ianuarie a anului următor distribuirii pentru dividendele aprobate și neplătite, indiferent de existența unui litigiu.
- Se include în baza impozabilă a dividendului și dobânda penalizatoare acordată de instanță pentru întârziere — aceasta se tratează separat, ca venit din dobânzi.

## Ce face iConta.eu

iConta.eu generează D205 pe baza mișcărilor contului 457 (distribuiri și plăți), atribuind impozitul pe fiecare tranșă plătită după cota valabilă la **data distribuirii** ei, nu la data plății — exact mecanismul cerut de lege în situațiile cu plată întârziată. Aplicația nu are însă o funcție dedicată pentru „dividende stabilite prin hotărâre judecătorească": nu distinge automat între o plată normală și una executată silit, nu calculează dobânzile penalizatoare aferente și nu importă hotărâri judecătorești. Contabilul introduce distribuirea și plata ca notă contabilă obișnuită pe 457, cu datele reale; restul (dobânda penalizatoare, dacă există) se evidențiază separat, manual.

[iConta.eu](/)
