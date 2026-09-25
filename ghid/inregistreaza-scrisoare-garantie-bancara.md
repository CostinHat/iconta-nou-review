---
title: "Cum se înregistrează scrisoare de garanție bancară"
description: "O scrisoare de garanție bancară e, contabil, un angajament extrabilanțier — cum se evidențiază și ce tip de operațiune dedicată există în iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează scrisoare de garanție bancară

Scrisoarea de garanție bancară e un instrument prin care o bancă se angajează, în numele unui client de-al său, să plătească o sumă unui beneficiar dacă acesta din urmă invocă neîndeplinirea unei obligații contractuale (livrare, execuție lucrări, restituire avans etc.). Din perspectiva firmei care o obține sau o primește, nu presupune, la momentul emiterii, nicio mișcare de bani — de aceea tratamentul ei contabil e diferit de o plată sau o încasare obișnuită.

## Temeiul legal

::: ghid-temei
„Din grupa 80 «Conturi în afara bilanțului» fac parte: Contul 801 «Angajamente acordate» [...] (giruri, cauțiuni, garanții, alte angajamente acordate) [...] Contul 802 «Angajamente primite» [...] (giruri, cauțiuni, garanții, alte angajamente primite) [...] Pentru grupa 80 «Conturi în afara bilanțului» se folosește metoda de înregistrare în partidă simplă, conform căreia înregistrările se fac în debitul și creditul unui singur cont, fără folosirea de conturi corespondente."
— OMFP 1802/2014 pentru aprobarea Reglementărilor contabile privind situațiile financiare anuale individuale și situațiile financiare anuale consolidate, Clasa 8 „Conturi speciale", Grupa 80 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- O scrisoare de garanție bancară e, prin natura ei, un **gir/o garanție** în sensul textului de mai sus — deci intră în grupa conturilor extrabilanțiere 801/802, nu într-o notă contabilă obișnuită cu conturi corespondente.
- Direcția contează: dacă banca **firmei** emite scrisoarea, în favoarea unui terț (firma e cea care „acordă" garanția prin intermediul băncii sale) → contul 8011 „Giruri și garanții acordate". Dacă firma e **beneficiara** unei scrisori emise de banca unui partener → contul 8021 „Giruri și garanții primite".
- Evidența se ține „în partidă simplă" — o singură înregistrare, fără contrapartidă — spre deosebire de o notă contabilă clasică.

## Ce se greșește în practică

- Se încearcă înregistrarea scrisorii de garanție bancară printr-o notă contabilă „normală", cu debit și credit în conturi de bilanț, deși ea nu presupune nicio mișcare de bani la emitere.
- Se ignoră complet scrisoarea de garanție în contabilitate, deși evidența ei extrabilanțieră e obligatorie cât timp angajamentul e valabil (comision aferent, dacă există, se înregistrează separat ca o cheltuială reală).
- Se uită stornarea/închiderea evidenței la expirarea sau eliberarea scrisorii de garanție.

## Ce face iConta.eu

Verificat direct în cod: `core/credite.py` conține o funcție generică de înregistrare a unei garanții (`nota_garantie`, acordată sau primită), care poate genera, la nivel de motor de calcul, exact notele extrabilanțiere descrise mai sus (8011=891 sau 8021=891).

Onest: iConta.eu **nu are** un tip de operațiune dedicat, distinct, numit „scrisoare de garanție bancară" — cu câmpuri specifice precum numărul scrisorii, banca emitentă sau beneficiarul. Din ecranul **Credite bancare** (operațiunea „Garanție"), disponibilă azi în interfață, se poate genera doar nota pentru garanție **primită** (`8021=891`) — formularul nu are un câmp pentru a alege „acordată", deci varianta 8011=891 (relevantă când firma e cea care oferă scrisoarea de garanție) nu poate fi produsă azi din UI, deși motorul de calcul o suportă.

[iConta.eu](/)
