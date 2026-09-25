---
title: "Dividendele din rezerve: tratament D205"
description: "Ce se întâmplă fiscal când o firmă distribuie rezervele către asociați ca dividende și cum se reflectă operațiunea în D205."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Dividendele din rezerve: tratament D205

Când o firmă decide să distribuie asociaților rezerve constituite anterior (de regulă din profit nerepartizat), operațiunea nu e „gratuită" fiscal. Legea o tratează simultan din două unghiuri: la firmă, ca reintrare în rezultatul fiscal a unei sume dedusă cândva; la asociat, ca dividend supus impozitului reținut la sursă — deci raportabil în D205 ca orice alt dividend plătit.

## Temeiul legal

::: ghid-temei
„Reducerea sau anularea oricărui provizion ori a rezervei care a fost anterior dedusă, inclusiv rezerva legală, se include în rezultatul fiscal, ca venituri impozabile sau elemente similare veniturilor, indiferent dacă reducerea sau anularea este datorată modificării destinației provizionului sau a rezervei, distribuirii provizionului sau rezervei către participanți sub orice formă, lichidării, divizării sub orice formă, fuziunii contribuabilului sau oricărui altui motiv."
— Legea 227/2015 (Codul fiscal), art. 26 alin. (5) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă un tratament în două trepte:

- **La firmă**: dacă rezerva a fost dedusă cândva la calculul profitului impozabil (de exemplu rezerva legală, în limita a 5% din profitul contabil, art. 26 alin. (1) lit. a)), distribuirea ei către asociați o transformă înapoi în venit impozabil (sau element similar veniturilor) în perioada în care are loc distribuirea — indiferent de motivul invocat.
- **La asociat**: distribuirea de sume către participant „drept consecință a deținerii unor titluri de participare" se încadrează, ca regulă generală, în definiția fiscală a dividendului (art. 7 pct. 11 din Codul fiscal), cu excepțiile expres enumerate acolo (majorare de capital prin încorporare de rezerve, lichidare, reducere de capital etc.) — care nu se aplică unei simple distribuiri de rezerve către asociați în bani. Ca dividend, suma intră sub incidența reținerii la sursă cu cota de 16% (art. 43, pentru asociați persoane juridice române, respectiv art. 97 alin. (7), pentru asociați persoane fizice) și se raportează informativ prin D205, alături de celelalte dividende plătite în perioadă.
- Cele două impozite au baze și beneficiari diferiți: impozitul pe profit al firmei asupra rezervei reintrate în rezultatul fiscal, respectiv impozitul pe dividende reținut asociatului — nu se compensează unul cu celălalt.

## Ce se greșește în practică

- Se distribuie rezerva ca „liberă de impozit" pentru că a fost deja constituită din profit impozitat cândva — se ignoră art. 26 alin. (5), care o reimpozitează la firmă exact la momentul distribuirii, dacă a fost dedusă la constituire.
- Se raportează suma altfel decât dividend (de exemplu drept restituire de capital), fără să se verifice dacă operațiunea se încadrează într-adevăr la vreuna dintre excepțiile art. 7 pct. 11 din Codul fiscal.
- Se omite reținerea impozitului pe dividende la momentul plății rezervei distribuite, considerând (greșit) că doar dividendele din profitul anului curent intră sub incidența reținerii la sursă.

## Ce face iConta.eu

La data acestui ghid, generatorul D205 din iConta.eu tratează orice sumă înregistrată ca dividend plătit unui asociat, indiferent de sursa contabilă a acesteia (profit curent sau rezerve distribuite), aplicând reținerea și raportarea standard prevăzută pentru dividende. Aplicația **nu automatizează** verificarea separată a reintegrării rezervei în rezultatul fiscal al firmei la impozitul pe profit — contabilul rămâne responsabil să identifice, la nivelul notei contabile de distribuire, dacă rezerva respectivă a fost cândva dedusă fiscal, pentru a o reintroduce corect în calculul impozitului pe profit al perioadei.

[iConta.eu](/)
