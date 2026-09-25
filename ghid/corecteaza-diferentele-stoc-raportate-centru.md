---
title: "Cum se corectează diferențele de stoc raportate de un centru de fulfillment?"
description: "Ce spune legea despre înregistrarea plusurilor și lipsurilor constatate la inventariere, aplicat la diferențele raportate de un depozit/centru de fulfillment terț."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se corectează diferențele de stoc raportate de un centru de fulfillment?

Când marfa este depozitată la un centru de fulfillment terț (de exemplu pentru comerț online), rapoartele periodice ale operatorului pot semnala diferențe față de evidența proprie a firmei — plusuri sau lipsuri de stoc. Din punct de vedere contabil, aceste diferențe se tratează exact ca rezultatele unei inventarieri, indiferent că bunurile nu se află fizic la sediul firmei.

## Temeiul legal

::: ghid-temei
„40. - (1) În situația constatării unor plusuri în gestiune, bunurile respective se evaluează potrivit reglementărilor contabile aplicabile. (2) În cazul constatării unor lipsuri imputabile în gestiune, administratorii trebuie să impute persoanelor vinovate bunurile lipsă la valoarea lor de înlocuire."
— OMFP nr. 2861/2009 pentru aprobarea Normelor privind organizarea și efectuarea inventarierii elementelor de natura activelor, datoriilor și capitalurilor proprii, pct. 40 alin. (1)-(2) (sursă: anaf_surse/omfp_2861_2009.txt)
:::

Aplicat la o diferență raportată de un centru de fulfillment:

- **Un plus de stoc** constatat (bunuri raportate de operator în cantitate mai mare decât evidența proprie) se **evaluează și se înregistrează în gestiune**, la valoarea stabilită potrivit reglementărilor contabile — nu se ignoră doar pentru că bunul „nu a fost pierdut" de firmă.
- **O lipsă de stoc imputabilă** (marfă dispărută, deteriorată sau nepredată din vina operatorului) trebuie **imputată persoanei vinovate** — în acest caz, de regulă, centrului de fulfillment, în baza contractului de prestări servicii logistice — la **valoarea de înlocuire**, definită ca prețul de achiziție al unui bun similar, cu taxele nerecuperabile, inclusiv TVA, și cheltuielile de transport/aprovizionare aferente.
- Constatarea diferenței trebuie să rezulte dintr-o **inventariere efectivă** (proces-verbal, confruntare între evidența proprie și raportul operatorului), nu doar dintr-o simplă notificare informală a discrepanței — documentul de inventariere e cel care justifică, contabil și fiscal, înregistrarea plusului/lipsei.
- Dacă lipsa nu poate fi imputată unei persoane vinovate identificate (de exemplu, contractul cu operatorul exclude răspunderea pentru anumite tipuri de pierderi), tratamentul fiscal al lipsei neimputabile urmează regulile generale privind deductibilitatea pierderilor din gestiune, distincte de cele pentru lipsurile imputabile.

## Ce se greșește în practică

- Se ajustează stocul direct pe baza raportului operatorului de fulfillment, fără un proces-verbal de inventariere propriu care să documenteze diferența constatată și decizia de tratament (imputare sau nu).
- Se înregistrează lipsa la costul de achiziție inițial al bunului, în loc de valoarea de înlocuire (costul de achiziție al unui bun similar la data constatării pagubei), care poate diferi semnificativ, mai ales pentru bunuri cu preț volatil.
- Se omite imputarea lipsurilor către operatorul de fulfillment, atunci când contractul de prestări servicii îi atribuie răspunderea, tratând orice diferență ca pe o pierdere pur internă a firmei.

## Ce face iConta.eu

iConta.eu are un modul de inventariere care înregistrează rezultatele constatate (plusuri pe cont de stoc 371, respectiv mijloace fixe pe 2131) și generează notele contabile aferente. Aplicația nu are o integrare directă cu rapoartele centrelor de fulfillment terțe pentru identificarea automată a diferențelor de stoc — contabilul introduce manual, pe baza raportului primit de la operator și a propriului proces-verbal de inventariere, plusurile și lipsurile constatate, iar aplicația generează notele contabile corespunzătoare.

[iConta.eu](/)
