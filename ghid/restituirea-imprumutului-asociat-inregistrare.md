---
title: Restituirea împrumutului către asociat: înregistrare
description: Când firma restituie asociatului suma împrumutată, se sting datoria propriu-zisă, eventuala dobândă datorată și impozitul de 10% reținut din dobândă, în note contabile distincte.
published: 2026-09-25
modified: 2026-10-13
poarta: v1
---

# Restituirea împrumutului către asociat: înregistrare

Dacă un asociat a lăsat bani la dispoziția firmei sub formă de împrumut, restituirea acelei sume nu e o cheltuială și nu e un venit — e stingerea unei datorii pe care firma o are deja înregistrată față de asociat.

## Temeiul legal

::: ghid-temei
**OMFP 1802/2014, pct. 349**: „Sumele depuse sau lăsate temporar de către acționari/asociați la dispoziția entității, precum și dobânzile aferente [...] se înregistrează în contabilitate în conturi distincte (contul 4551 «Acționari/asociați - conturi curente», respectiv contul 4558 «Acționari/asociați - dobânzi la conturi curente»)."

**Codul fiscal, art. 64 alin. (1) lit. d)** și **art. 91 lit. b)**: dobânda plătită asociatului persoană fizică e venit din investiții, impozitat cu cotă de 10%, reținut la sursă de firma plătitoare.

„(2^4) Societățile care, pe baza situațiilor financiare anuale, aprobate potrivit legii, au o valoare a activului net diminuată la mai puțin de jumătate din valoarea capitalului social subscris nu pot restitui acționarilor sau asociaților, după caz, sau altor persoane afiliate, așa cum sunt definite conform reglementărilor contabile aplicabile, împrumuturile luate de la aceștia."
— Legea 31/1990, art. 67 alin. (2^4), introdus de Legea 239/2025, în vigoare de la 18.12.2025 (sursă: [Legea nr. 31/1990 privind societățile](https://legislatie.just.ro/Public/DetaliiDocument/798))
:::

Restituirea propriu-zisă (capitalul împrumutat) sting datoria din contul curent al asociatului, fără nicio implicație de TVA sau impozit pe profit — nu e o cheltuială deductibilă sau nedeductibilă, ci o mișcare de trezorerie care stinge o datorie. Dacă a fost stabilită dobândă, aceasta se înregistrează separat, ca o cheltuială financiară a firmei, iar impozitul de 10% reținut din dobândă se virează la stat, nu se plătește asociatului.

Notele contabile, pe componente:

- suma principală: **4551 = 5121** (datoria față de asociat se stinge, banca scade);
- dobânda, dacă a fost stabilită: **666 = 4551** (cheltuială financiară);
- impozitul reținut din dobândă: **4551 = 446**, cu cota de 10%;
- suma netă de dobândă rămasă asociatului pleacă tot prin **4551 = 5121**.

Înainte de restituire se verifică activul net al firmei, potrivit ultimelor situații financiare anuale aprobate: dacă e sub jumătate din capitalul social subscris, restituirea împrumutului e interzisă (Legea 31/1990, art. 67 alin. (2^4)), indiferent de vechimea sau valoarea împrumutului.

## Ce se greșește în practică

- Se tratează restituirea sumei principale ca o cheltuială a firmei — greșit, e o mișcare de datorie, nu de cheltuială.
- Se virează asociatului direct suma netă, fără a înregistra separat dobânda brută și impozitul reținut pe ea.
- Se restituie împrumutul fără a verifica activul net din ultimele situații financiare anuale aprobate — sub jumătate din capitalul social subscris, restituirea e interzisă.
- Se plătește asociatului dobânda brută, fără reținerea impozitului de 10%, urmând ca firma să regularizeze ulterior — corect e reținerea impozitului chiar la momentul plății dobânzii.
- Se confundă restituirea împrumutului cu distribuirea de dividende — sunt operațiuni complet diferite din punct de vedere fiscal și contabil, chiar dacă ambele înseamnă „bani ies din firmă către asociat".

## Ce face iConta.eu

La restituirea împrumutului, decontările cu asociații din iConta.eu generează automat trei linii, separate: stingerea datoriei principale către asociat (4551 = 5121), cheltuiala cu dobânda (666 = 4551, dacă a fost introdusă o dobândă diferită de zero) și impozitul de 10% reținut din acea dobândă (4551 = 446). Cota de impozit pe dobândă e implicit 10%, dar poate fi ajustată dacă situația concretă o cere. Aplicația nu verifică automat activul net al firmei înainte de a genera nota — condiția de la art. 67 alin. (2^4) din Legea 31/1990 rămâne o verificare făcută de contabil.

Notă de simplificare: dobânda e înregistrată tot pe contul 4551, alături de principal, nu separat pe 4558 — verifică analiticul dacă ai nevoie de separarea exactă recomandată de nomenclatorul OMFP 1802/2014.

[iConta.eu](/)
