---
title: "Calendar fiscal pentru PFA în 2026: toate scadențele"
description: "Ce arată (și ce nu arată) ecranul Termene din iConta.eu pentru un PFA — nu un calendar fiscal complet al tuturor obligațiilor unui PFA."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Calendar fiscal pentru PFA în 2026: toate scadențele

Precizare importantă înainte de a începe: acest ghid explică strict ce arată — și, mai important, ce nu arată — ecranul „Termene” din iConta.eu pentru un PFA (regim de „partidă simplă”). Nu e un calendar fiscal complet al tuturor obligațiilor unui PFA (de exemplu, impozitul pe venit sau contribuțiile de asigurări nu fac obiectul cercetării pe care se bazează acest ghid și nu sunt tratate aici).

## Temeiul legal

::: ghid-temei
Motorul comun de calcul al scadențelor „exclude structural D100/D101/D406 din motor” pentru regimul de „partidă simplă” (PFA) — marcaj intern de cod `neaplic_statut`.
:::

Documentația funcțională a aplicației nu leagă acest comportament de un articol de lege citat verbatim în cercetarea disponibilă — e o regulă de aplicare internă, verificată direct în codul motorului de scadențe.

## Ce se greșește în practică

- Se așteaptă ca un PFA să vadă pe ecranul „Termene” aceleași declarații ca o firmă cu personalitate juridică (SRL etc.) — D100 (impozit micro/profit), D101 (impozit pe profit anual) și D406 (SAF-T) nu se aplică structural unui PFA și nu vor apărea niciodată pentru el pe acest ecran, indiferent de situația lui.
- Se ia acest ecran drept sursă completă pentru obligațiile specifice unui PFA — el a fost verificat doar pentru excluderea celor trei declarații de mai sus, nu pentru declarațiile specifice regimului de venit al unui PFA.

## Ce face iConta.eu

Pentru o firmă/entitate marcată cu regim fiscal de „partidă simplă” (PFA), motorul comun de scadențe folosit de ecranul „Termene” exclude explicit trei declarații care nu i se aplică din punct de vedere structural: D100, D101 și D406. Indiferent de vectorul fiscal completat, aceste trei nu vor apărea niciodată în calendarul de scadențe al unui PFA.

Ca și pentru celelalte tipuri de firme, ecranul necesită ca vectorul fiscal al PFA-ului să fie completat (regimul fiscal e un câmp obligatoriu, fără valoare implicită) — altfel PFA-ul apare în secțiunea „neevaluate”, cu mesajul „Vector fiscal necompletat — nu pot evalua obligațiile firmei.” Ecranul e disponibil doar conturilor de cabinet cu portofoliu, arată strict scadențele din următoarele 60 de zile și nu se actualizează live, ci pe baza unei recalculări periodice de fundal.

Dincolo de această excludere structurală, dosarul de cercetare pe care se bazează acest ghid nu documentează ce alte declarații apar efectiv pe ecran pentru un PFA — pentru un calendar complet al obligațiilor unui PFA (impozit pe venit, contribuții sociale), recomandăm verificarea directă cu un consultant fiscal sau cu sursele ANAF dedicate PFA.

[iConta.eu](/)
