---
title: "Se declară în D390 vânzările prin OSS?"
description: "De ce vânzările raportate prin regimul special OSS (One Stop Shop) nu se declară în D390, ci într-o declarație separată, D398, cu reguli și logică proprii."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Se declară în D390 vânzările prin OSS?

Nu. D390 (declarația recapitulativă) și regimul special OSS servesc scopuri diferite, iar confuzia dintre ele generează frecvent raportări duble sau omisiuni. Vânzările la distanță de bunuri sau serviciile prestate către persoane neimpozabile din UE, raportate prin regimul special OSS, se declară exclusiv prin declarația specială de TVA pentru regimurile speciale (D398) — nu prin declarația recapitulativă D390.

## Temeiul legal

::: ghid-temei
„Regimul special pentru vânzările intracomunitare de bunuri la distanță, pentru livrările de bunuri interne efectuate de interfețele electronice care facilitează aceste livrări și pentru serviciile prestate de persoane impozabile stabilite în Uniunea Europeană, dar nu în statul membru de consum [...]"
— Legea nr. 227/2015 (Codul fiscal), art. 315 (denumirea marginală a articolului, Capitolul XI, Titlul VII) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul regimului OSS, așa cum rezultă din structura Codului fiscal (art. 314 — regimul non-UE pentru servicii, art. 315 — regimul UE, art. 315^2 — regimul de import/IOSS):

- Firma înregistrată în regim special OSS raportează, printr-o singură declarație depusă la statul membru de identificare (România, pentru firmele românești), **TVA-ul datorat în fiecare stat membru de consum**, pentru vânzările la distanță și serviciile către persoane neimpozabile din UE.
- Această raportare se face prin **D398**, nu prin D390 — D390 rămâne rezervată operațiunilor intracomunitare din sfera de aplicare normală a TVA (livrări/achiziții intracomunitare de bunuri, prestări de servicii intracomunitare cu taxare inversă), nu vânzărilor B2C raportate prin regimul special.
- Operațiunile raportate corect prin OSS/D398 nu se mai regăsesc, pentru statul membru de consum respectiv, în decontul normal de TVA (D300) al firmei — regimul special le scoate din circuitul obișnuit de declarare.

## Ce se greșește în practică

- Se raportează aceleași vânzări atât în D390, cât și în D398, dublând declararea unei operațiuni care ar trebui să apară o singură dată, prin regimul special.
- Se omite complet declararea prin D398 a vânzărilor OSS, considerându-se că D390 sau D300 acoperă deja obligația de raportare pentru statele membre de consum.
- Se confundă regimul special OSS pentru vânzări B2C la distanță cu operațiunile intracomunitare B2B obișnuite, care rămân în sfera D390.

## Ce face iConta.eu

La data acestui ghid, iConta.eu poate genera XML-ul declarației D398, pe baza structurii oficiale a validatorului ANAF (`core/d398.py`). Declarația este însă **integral manuală**: aplicația nu ține evidența operațiunilor OSS pe stat de consum și cotă de TVA străină aplicabilă, așa că toate valorile trebuie introduse manual de contabil — iConta.eu nu deduce automat aceste sume din registrele contabile ale firmei.

[iConta.eu](/)
