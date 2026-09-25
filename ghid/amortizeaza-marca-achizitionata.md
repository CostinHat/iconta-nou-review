---
title: "Cum se amortizează o marcă achiziționată?"
description: "Regula fiscală de amortizare liniară a mărcilor de comerț achiziționate, pe durata contractului sau pe durata de utilizare, conform art. 28 din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se amortizează o marcă achiziționată?

O marcă de comerț achiziționată (cumpărată de la un terț, nu creată intern) e o imobilizare necorporală — Codul fiscal îi rezervă un regim de amortizare distinct de cel al mijloacelor fixe corporale, cu o singură metodă admisă: amortizarea liniară.

## Temeiul legal

::: ghid-temei
„(9) Cheltuielile aferente achiziționării de brevete, drepturi de autor, licențe, mărci de comerț sau fabrică, drepturi de explorare a resurselor naturale și alte imobilizări necorporale recunoscute din punct de vedere contabil, cu excepția cheltuielilor de constituire, a fondului comercial, a imobilizărilor necorporale cu durată de viață utilă nedeterminată, încadrate astfel potrivit reglementărilor contabile aplicabile, precum și cheltuielile de dezvoltare care din punct de vedere contabil reprezintă imobilizări necorporale se recuperează prin intermediul deducerilor de amortizare liniară pe perioada contractului sau pe durata de utilizare, după caz."
— Legea 227/2015 (Codul fiscal), art. 28 alin. (9) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă concret pentru o marcă achiziționată:

- **Metoda e exclusiv liniară** — spre deosebire de mijloacele fixe corporale (unde legea permite, în anumite cazuri, amortizare degresivă sau accelerată), pentru mărci nu există opțiunea altor metode. Textul art. 28 alin. (9) prevede metode alternative doar pentru programe informatice (liniară sau degresivă, pe 3 ani) și pentru brevete de invenție (degresivă sau accelerată) — mărcile rămân la liniară.
- **Durata de amortizare** e „perioada contractului sau durata de utilizare, după caz" — dacă marca a fost achiziționată cu un contract care specifică o durată (de exemplu, o cesiune limitată în timp), se amortizează pe acea durată; dacă achiziția e definitivă, fără termen contractual, se folosește durata de utilizare estimată de firmă.
- **Excepția care blochează amortizarea**: dacă marca e recunoscută contabil ca imobilizare necorporală **cu durată de viață utilă nedeterminată** (o marcă bine consacrată, fără o dată previzibilă de încetare a utilității economice), ea **nu se amortizează** — nici contabil, nici fiscal (art. 28 alin. 4 lit. h, coroborat cu alin. 9).
- Condiția de bază rămâne recunoașterea contabilă a mărcii ca imobilizare necorporală, potrivit reglementărilor contabile aplicabile — dacă achiziția nu îndeplinește criteriile de recunoaștere ca activ (de exemplu, dacă e vorba de o marcă dezvoltată intern, nu achiziționată), regimul poate fi diferit.

## Ce se greșește în practică

- Se aplică o durată de amortizare arbitrară (de exemplu 5 sau 10 ani „din practică"), fără să se verifice dacă marca a fost achiziționată cu sau fără un contract care limitează explicit perioada de utilizare.
- Se amortizează o marcă pe care contabilitatea a clasificat-o drept „durată de viață utilă nedeterminată", ignorând că, în acest caz, legea exclude explicit amortizarea (art. 28 alin. 4 lit. h) — orice cheltuială de amortizare înregistrată ar fi nedeductibilă fiscal.
- Se confundă amortizarea mărcii cu amortizarea programelor informatice, aplicând regimul de 3 ani rezervat exclusiv software-ului — mărcile nu au o perioadă fixă de 3 ani prevăzută de lege.

## Ce face iConta.eu

Modulul de mijloace fixe din iConta.eu (`core/repo_mijloace_fixe.py`) folosește o schemă generică de amortizare (valoare, valoare reziduală, durată normală de funcționare în luni), aplicabilă oricărui activ amortizabil introdus, indiferent dacă e corporal sau necorporal. La data acestui ghid, aplicația **nu diferențiază automat regimul special al imobilizărilor necorporale** (metodă exclusiv liniară, durată legată de contract sau de utilizare, excludere pentru durată de viață nedeterminată) — contabilul e cel care stabilește durata corectă la introducerea mărcii ca activ și confirmă că metoda selectată e liniară, conform art. 28 alin. (9).

[iConta.eu](/)
