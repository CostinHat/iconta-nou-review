---
title: "PFA la normă de venit plătește CASS?"
description: "Baza de calcul a contribuției de asigurări sociale de sănătate pentru persoanele fizice autorizate care își determină venitul pe bază de normă de venit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# PFA la normă de venit plătește CASS?

Da — un PFA care își determină venitul anual pe bază de normă de venit datorează CASS, la fel ca oricare alt PFA, indiferent de sistemul de impunere ales (real sau normă). Ce diferă e doar baza de calcul: pentru cei la normă de venit, contribuția se calculează direct pe norma anuală stabilită, nu pe un venit efectiv, real, realizat.

## Temeiul legal

::: ghid-temei
„Persoanele fizice care în anul fiscal pentru care se depune declarația prevăzută la art. 122 au realizat venituri din cele prevăzute la art. 155 alin. (1) lit. b), din una sau mai multe surse, datorează contribuția de asigurări sociale de sănătate la o bază anuală de calcul egală cu suma rezultată prin cumularea venitului net anual realizat/brut sau normei anuale de venit, respectiv a normei anuale de venit ajustate, după caz, stabilite potrivit art. 68, 68^1, 68^3 și 69, după caz, care nu poate fi mai mare decât cea corespunzătoare unei baze anuale de calcul egale cu nivelul de 72 de salarii minime brute pe țară."
— Codul fiscal (Legea 227/2015), art. 170 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Art. 155 alin. (1) lit. b) trimite la „veniturile din activități independente, definite conform art. 67" — categorie în care se încadrează inclusiv PFA-urile care își determină venitul pe bază de normă de venit.
- Baza de calcul CASS pentru această categorie e explicit „venitul net anual realizat/brut **sau norma anuală de venit**" — deci legea tratează norma de venit exact ca pe un venit impozabil în scopul CASS, nu ca pe o excepție de la contribuție.
- Spre deosebire de alte categorii de venituri (cele din chirii, dividende, dobânzi etc., reglementate la art. 155 alin. (1) lit. c)-h)), pentru care CASS se datorează doar dacă suma cumulată depășește pragul de 6 salarii minime brute pe an, **PFA-ul la normă de venit nu are acest prag minim** — contribuția se datorează indiferent de nivelul normei anuale, cu singura limită fiind plafonul superior de 72 de salarii minime brute pe țară.
- Practic, un PFA la normă de venit plătește CASS pe toată norma anuală de venit stabilită pentru activitatea respectivă (eventual ajustată), până la plafonul maxim legal, chiar dacă venitul efectiv realizat a fost mai mic sau mai mare decât norma.

## Ce se greșește în practică

- Se presupune că regula pragului minim de 6 salarii minime brute (valabilă pentru categoriile de venituri de la art. 155 alin. (1) lit. c)-h)) se aplică și PFA-urilor la normă de venit — de fapt, acestea intră la lit. b), fără un asemenea prag minim.
- Se calculează CASS pe venitul efectiv încasat de PFA, în loc de norma anuală de venit stabilită de administrația financiară pentru activitatea și zona respectivă.
- Se omite verificarea plafonului maxim de 72 de salarii minime brute pe țară atunci când PFA-ul cumulează norma de venit cu alte venituri din activități independente.
- Se confundă impozitul pe venit (care, la normă de venit, se calculează tot pe bază de normă, potrivit art. 69) cu CASS, presupunând greșit că cele două ar avea baze de calcul complet independente, când de fapt ambele pornesc de la aceeași normă anuală.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un capitol dedicat normei de venit în modulul de Declarație Unică (D212), alături de veniturile din sistem real — inclusiv câmpurile pentru contribuțiile CAS/CASS aferente (baza de calcul, diferențe, bonificații). Calculul propriu-zis al normei de venit și al bazei CASS asociate se face pe baza valorilor introduse de contabil pentru fiecare capitol, aplicația asamblând și validând structura declarației, nu recalculând independent normele stabilite de autorități.

[iConta.eu](/)
