---
title: "Ce conturi trebuie verificate înainte de calculul impozitului pe profit?"
description: "Ce cere legal calculul rezultatului fiscal și de ce verificarea conturilor de venituri și cheltuieli, înainte de aplicarea cotei de 16%, nu e opțională."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce conturi trebuie verificate înainte de calculul impozitului pe profit?

Impozitul pe profit nu se aplică pe soldul din balanță luat ca atare, ci pe rezultatul fiscal — un calcul care pornește de la conturile de venituri și cheltuieli, dar le trece printr-un filtru legal înainte de a aplica cota de 16%. Fără o verificare prealabilă a acestor conturi, riscul e fie de a plăti impozit în plus (pe venituri deja scutite), fie în minus (fără să scoți cheltuielile nedeductibile).

## Temeiul legal

::: ghid-temei
„Rezultatul fiscal se calculează ca diferență între veniturile și cheltuielile înregistrate conform reglementărilor contabile aplicabile, din care se scad veniturile neimpozabile și deducerile fiscale și la care se adaugă cheltuielile nedeductibile. La stabilirea rezultatului fiscal se iau în calcul și elemente similare veniturilor și cheltuielilor, potrivit normelor metodologice, precum și pierderile fiscale care se recuperează în conformitate cu prevederile art. 31."
— Legea nr. 227/2015 privind Codul fiscal, art. 19 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din formula legii rezultă exact ce merită verificat înainte de aplicarea cotei de impozit:

- **Toate conturile de venituri (clasa 7)** — pentru a identifica dacă printre ele există venituri neimpozabile (de exemplu, veniturile din anularea unor provizioane care nu au fost deductibile la constituire), care trebuie scăzute din baza de calcul.
- **Toate conturile de cheltuieli (clasa 6)** — pentru a identifica cheltuielile nedeductibile total sau parțial (amenzi, penalități, protocol/sponsorizare peste plafon, cheltuieli fără document justificativ), care trebuie adăugate înapoi.
- **Elementele similare veniturilor/cheltuielilor** — ajustări care nu trec, ca atare, prin contul de profit și pierdere, dar intră în calculul fiscal conform normelor metodologice.
- **Pierderea fiscală reportată din anii anteriori (art. 31)** — un sold care nu apare direct în balanța curentă de verificare, dar afectează rezultatul fiscal al anului.

## Ce se greșește în practică

- Se calculează impozitul direct din profitul contabil brut, fără să se treacă în revistă lista de venituri neimpozabile și cheltuieli nedeductibile din Codul fiscal.
- Se verifică doar conturile de cheltuieli, ignorându-se veniturile neimpozabile — ceea ce duce la plata unui impozit mai mare decât cel datorat legal.
- Se omite verificarea pierderii fiscale reportate din anii precedenți, deși ea reduce baza impozabilă a anului curent, conform art. 31.

## Ce face iConta.eu

La generarea declarației D100, iConta.eu calculează automat baza de plată a impozitului pe profit ca diferență cumulată între veniturile și cheltuielile înregistrate (art. 41 CF — calcul cumulat de la 1 ianuarie), dar aplicația afișează explicit un avertisment că **ajustările fiscale prevăzute de art. 19 și următoarele (cheltuieli nedeductibile, venituri neimpozabile) și regularizarea anuală se fac separat, la D101** — nu sunt automatizate în D100. Verificarea manuală a conturilor din lista de mai sus rămâne, deci, un pas al contabilului, înainte de finalizarea declarației anuale.

[iConta.eu](/)
