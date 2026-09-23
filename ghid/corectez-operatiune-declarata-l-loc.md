---
title: "Cum corectez o operațiune declarată cu L în loc de P?"
description: Reclasificarea din L în P funcționează prin panoul de clasificare, dar o limitare recentă și încă neconfirmată pe comportamentul live poate face reclasificarea fără efect pentru anumite facturi.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez o operațiune declarată cu L în loc de P?

O factură emisă intracomunitar e clasificată implicit de aplicație ca L (livrare de bunuri). Dacă, de fapt, operațiunea e o prestare de servicii, trebuie reclasificată ca P — dar, în funcție de modul în care a fost creată factura, corecția prin panoul D390 s-ar putea, la acest moment, să nu fie suficientă.

## Temeiul legal

::: ghid-temei
**OPANAF 705/2020, Anexa 2, Instrucțiuni pct. 1 lit. a) și d)**:
> „a) livrări intracomunitare de bunuri (L); [...] d) prestări intracomunitare de servicii (P) [...]"
:::

Norma tratează L și P ca tipuri de operațiuni distincte — o eroare de încadrare între ele trebuie corectată înainte de depunere, nu lăsată în declarație.

## Ce se greșește în practică

Greșeala tipică este să se presupună că salvarea reclasificării din panoul D390 (mesajul de succes afișat de aplicație la salvare) garantează, automat, că declarația generată reflectă noul tip — conform verificării de mai jos, acest lucru nu mai este întotdeauna adevărat de la o schimbare recentă de comportament.

## Ce face iConta.eu

Pentru o factură emisă prin ecranul **obișnuit** de facturare (nu prin ecranul dedicat de livrare intracomunitară), reclasificarea din L în P din panoul de clasificare D390 (pasul 2) funcționează normal: selectezi operațiunea, alegi tipul P din listă, salvezi, iar declarația regenerată reflectă noul tip.

**Trebuie să fim direcți despre o limitare recentă, pe care recomandăm să o confirmi în aplicația live înainte de a te baza pe ea**: pentru o factură creată prin ecranul dedicat „Livrare intracomunitară", aplicația reține la crearea facturii o axă bunuri/servicii pe document — o schimbare de cod din 16.09.2026, foarte aproape de data ultimei verificări a acestui comportament (17.09.2026). Conform codului citit la acea dată, pentru astfel de facturi tipul D390 este determinat direct din axa înregistrată pe document, iar reclasificarea manuală din panou nu mai are, practic, ce suprascrie — chiar dacă interfața continuă să afișeze un selector funcțional și salvarea pare să reușească. Nu am găsit, în cod, niciun mesaj de avertisment care să anunțe contabilul de această limitare în momentul reclasificării.

Dacă factura ta a fost creată prin acest ecran dedicat și încerci să corectezi L în P, recomandarea sigură este: verifică direct XML-ul generat după reclasificare, pentru a confirma că tipul a fost efectiv schimbat; dacă nu s-a schimbat, singura cale confirmată de corectare este stornarea facturii și reemiterea ei corect (ca prestare de servicii, prin ecranul potrivit), pentru că aplicația nu are, la acest moment, o funcție de editare a axei bunuri/servicii pe o factură deja emisă. Verifică cu iConta.eu comportamentul curent al reclasificării pentru acest caz specific, pentru că e o schimbare foarte recentă și posibil să evolueze.

[iConta.eu](/)
