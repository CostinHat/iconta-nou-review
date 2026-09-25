---
title: "Cum împac casa de marcat cu extrasul de cont"
description: "De ce încasările cu cardul de la aparatul de marcat trebuie regăsite exact în extrasul de cont, ca parte a corectitudinii evidenței cerute de Legea 82/1991."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum împac casa de marcat cu extrasul de cont

Într-un magazin sau restaurant care încasează și cu cardul prin POS, sumele raportate de aparatul de marcat pentru încasările cu cardul trebuie să se regăsească, cu o mică decalare de zile, în extrasul de cont bancar — dacă nu se regăsesc, evidența nu e corectă.

## Temeiul legal

::: ghid-temei
„Registrele de contabilitate se utilizează în strictă concordanță cu destinația acestora și se prezintă în mod ordonat și astfel completate încât să permită, în orice moment, identificarea și controlul operațiunilor contabile efectuate. Articolul 22 Pentru verificarea înregistrării corecte în contabilitate a operațiunilor efectuate, lunar se întocmește balanța de verificare."
— Legea contabilității nr. 82/1991, art. 21-22 (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Cum se aplică principiul la reconcilierea casă de marcat – extras de cont:

- Legea nu detaliază pas cu pas o procedură de "împăcare" casă de marcat–bancă, dar cere expres **verificarea înregistrării corecte** a operațiunilor, lunar, prin balanța de verificare — iar sumele încasate cu cardul prin AMEF trebuie regăsite, la un moment dat, ca intrări în contul bancar.
- Practic, reconcilierea compară: (1) suma încasărilor cu cardul raportate de AMEF în raportul Z, cu (2) sumele efectiv virate de procesatorul de plăți (POS) în contul bancar, care ajung de regulă cu o decalare de o zi sau mai multe, uneori nete de comision.
- Diferența dintre suma brută raportată de AMEF și suma netă intrată în bancă e, de obicei, comisionul de procesare a plăților cu cardul — care trebuie înregistrat distinct (cont 627 "Cheltuieli cu serviciile bancare și asimilate"), nu lăsat ca diferență nereconciliată.

## Ce se greșește în practică

- Se compară suma din raportul Z cu suma din extras în aceeași zi calendaristică — decontarea POS ajunge, de regulă, cu întârziere de 1-3 zile lucrătoare, iar o comparație zi-la-zi găsește diferențe false.
- Se lasă comisionul bancar ca "diferență de rotunjire" nereconciliată, în loc să fie înregistrat explicit ca și cheltuială — denaturează atât soldul de bancă neexplicat, cât și cheltuielile reale ale lunii.
- Se face reconcilierea o singură dată, la final de an, în loc de verificare periodică — o eroare de configurare (ex. AMEF nesincronizat cu terminalul de card) rămâne nedetectată luni de zile.

## Ce face iConta.eu

La data acestui ghid, `core/amef_import.py` importă raportul fiscal de închidere zilnică, iar `core/banca.py` (`contabilizeaza_extras()`) contabilizează liniile din extrasul bancar. Aplicația nu are însă o funcție dedicată de **reconciliere automată** între încasările cu cardul raportate de AMEF și sumele efectiv intrate în bancă de la procesatorul de plăți — compararea celor două fluxuri, identificarea decalajelor de decontare și separarea comisionului rămân, azi, o verificare manuală a contabilului.

[iConta.eu](/)
