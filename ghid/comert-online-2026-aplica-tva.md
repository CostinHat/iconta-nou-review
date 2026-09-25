---
title: "Comerț online 2026: cum se aplică TVA la vânzările către consumatori din UE"
description: "Regula locului livrării pentru vânzările intracomunitare de bunuri la distanță către consumatori din alte state membre UE și legătura cu regimul special OSS."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Comerț online 2026: cum se aplică TVA la vânzările către consumatori din UE

Pentru un magazin online românesc care vinde către persoane fizice din alte state UE, regula de bază nu mai este locul de unde pleacă marfa, ci locul unde ajunge ea — cu o singură excepție relevantă la volume mici.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (1) lit. a), locul livrării în cazul vânzărilor intracomunitare de bunuri la distanță este considerat a fi locul în care se află bunurile în momentul în care se încheie expedierea sau transportul bunurilor către client."
— Legea nr. 227/2015 (Codul fiscal), art. 275 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Consecințele practice ale acestei reguli:

- TVA-ul datorat pentru o vânzare la distanță către un consumator din, de exemplu, Germania sau Franța, se calculează la **cota din statul de destinație**, nu la cota românească — pentru că locul livrării este, prin excepție, locul unde se încheie transportul.
- Pentru a nu se înregistra în scopuri de TVA în fiecare stat membru în care vinde, firma poate opta pentru **regimul special UE** (OSS), prin care declară și plătește, printr-o singură declarație depusă în România, TVA-ul datorat în toate statele de consum.
- Regimul special este reglementat distinct, la art. 315 din Codul fiscal, și presupune o declarație specifică (D398), separată de deconturile de TVA obișnuite.

## Ce se greșește în practică

- Se aplică din reflex cota de TVA românească la toate vânzările online către clienți din UE, ignorând că locul livrării se mută, prin lege, în statul de destinație.
- Se confundă vânzarea la distanță de bunuri (marfă expediată dintr-un stat membru în altul) cu exportul sau cu livrarea intracomunitară către o altă firmă (B2B) — regimul OSS vizează exclusiv vânzările către persoane neimpozabile (consumatori finali).
- Se amână înregistrarea în regimul OSS până apar probleme, deși opțiunea trebuie exercitată din timp și presupune raportare trimestrială, cu penalități pentru declarare eronată a cotelor din alte state.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează declarația D398 pentru regimurile speciale OSS (UE, non-UE, import), dar **aceasta este o declarație manuală**: aplicația nu ține evidența automată a operațiunilor de vânzare la distanță pe stat de consum și cotă de TVA aplicabilă în fiecare țară — toate valorile trebuie introduse de contabil (`core/d398.py`). Aplicația validează structura declarației față de validatorul oficial ANAF, dar nu calculează singură TVA-ul datorat în funcție de destinația mărfii pentru fiecare comandă online.

[iConta.eu](/)
