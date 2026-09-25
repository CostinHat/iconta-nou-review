---
title: "Contabilitate firmă de evenimente: particularități"
description: "Firmele care organizează evenimente încasează de regulă avansuri consistente înainte de eveniment — regula fiscală centrală e momentul exigibilității TVA la avans, nu data evenimentului efectiv."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contabilitate firmă de evenimente: particularități

O firmă de evenimente — organizator de conferințe, agenție de nunți, firmă de catering pentru corporate — are un tipar comun de încasare: un avans (uneori mai multe tranșe) încasat cu mult înainte de data efectivă a evenimentului, urmat de o factură finală după prestarea serviciului. Particularitatea contabilă principală nu ține de industrie în sine, ci de tratamentul avansurilor, care urmează o regulă fiscală strictă, indiferent de tipul evenimentului organizat.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: [...] b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator. Avansurile reprezintă plata parțială sau integrală a contravalorii bunurilor și serviciilor, efectuată înainte de data livrării ori prestării acestora;"
— Codul fiscal (Legea 227/2015), art. 282 alin. (2) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Regula se aplică oricărei firme de evenimente — organizator de conferințe, firmă de catering, agenție de nunți — nu doar unui tip particular de eveniment.
- TVA devine exigibilă la data încasării avansului, nu la data la care are loc efectiv evenimentul — un avans încasat în decembrie pentru un eveniment programat în martie anul următor intră în decontul de TVA din luna încasării, decembrie.
- La factura finală, avansul deja facturat se regularizează (se scade din valoarea totală a prestației), nu se adaugă ca venit separat, nou.

## Ce se greșește în practică

- Se amână înregistrarea avansului până la data evenimentului „ca să fie mai simplu" — greșit: TVA e deja exigibilă la momentul încasării, indiferent cât de departe e evenimentul.
- Se facturează avansul, dar nu se regularizează corect la factura finală, ceea ce dublează valoarea prestației în evidențe sau lasă TVA nereconciliată.
- Se confundă un avans (parte din preț, supus regulii de mai sus) cu o garanție pur returnabilă (de exemplu o garanție de bună execuție pentru echipament sau locație, restituită integral după eveniment) — tratamentul contabil diferă, iar confuzia poate duce la colectarea eronată a TVA pe o sumă care nu e, de fapt, preț al serviciului.
- La evenimente cu mulți subcontractori (locație, catering, sonorizare), se pierde urma cine facturează avansul către cine — fiecare relație contractuală (client final → organizator, organizator → subcontractor) are propriul avans, cu propria exigibilitate.

## Ce face iConta.eu

iConta.eu tratează avansurile prin modulul generic `core/avansuri.py`, cu funcțiile `nota_avans_incasat` (avansul facturat clientului: `4111 = 419 + 4427`) și `nota_avans_platit` (avansul plătit unui furnizor/subcontractor: `409x + 4426 = 401`, pe destinații — stocuri, servicii, imobilizări), plus funcțiile de regularizare la factura finală (`nota_regularizare_avans_incasat`/`nota_regularizare_avans_platit`) — exact mecanica impusă de art. 282 alin. (2) lit. b) de mai sus. Modulul e complet generic, valabil pentru orice tip de avans din orice activitate; nu există în cod o monografie sau un flux dedicat special firmelor de evenimente (subcontractare pe mai multe niveluri, garanții returnabile, facturare eșalonată pe etape ale evenimentului) — contabilul aplică motorul general de avansuri, tranzacție cu tranzacție, cu aceeași disciplină ca la orice altă activitate.

[iConta.eu](/)
