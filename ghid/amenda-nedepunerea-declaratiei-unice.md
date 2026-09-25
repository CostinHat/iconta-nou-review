---
title: "Amenda pentru nedepunerea declarației unice"
description: "Cuantumul amenzii contravenționale pentru nedepunerea la termen a declarației unice privind impozitul pe venit și contribuțiile sociale, potrivit Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amenda pentru nedepunerea declarației unice

Amenda pentru declarația unică netranspusă la termen nu are legătură cu obligațiile fiscale efectiv datorate — e o sancțiune contravențională fixă, aplicabilă indiferent de suma declarată.

## Temeiul legal

::: ghid-temei
„(3) În cazul persoanelor fizice nedepunerea la termenele prevăzute de lege a declarațiilor de venit, precum și a declarației unice privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice constituie contravenție și se sancționează cu amendă de la 50 lei la 500 lei."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 336 alin. (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Detaliile care contează pentru o persoană fizică (inclusiv PFA) aflată în această situație:

- Amenda se situează într-un interval de **50–500 lei**, cu individualizarea concretă lăsată la latitudinea organului constatator, în funcție de circumstanțele faptei.
- Sancțiunea vizează **nedepunerea la termenele legale**, nu doar omisiunea totală — inclusiv o declarație depusă cu întârziere, după termenul-limită, poate atrage această contravenție.
- Este o sancțiune distinctă de eventuale dobânzi/penalități pentru neplata la termen a sumelor datorate prin declarația unică — cele două tipuri de consecințe (amenda contravențională pentru nedepunere și accesoriile pentru neplată) se aplică separat, unul nu îl exclude pe celălalt.

## Ce se greșește în practică

- Se presupune că amenda pentru nedepunere e proporțională cu suma datorată prin declarație — de fapt, e un cuantum fix, în intervalul 50–500 lei, independent de mărimea veniturilor declarate.
- Se confundă amenda pentru nedepunerea declarației unice (art. 336 alin. (3), care vizează persoanele fizice) cu penalitatea de nedeclarare aplicabilă obligațiilor principale stabilite de organul fiscal prin control (art. 181) — sunt sancțiuni diferite, cu temeiuri diferite.
- Se amână depunerea declarației unice considerând amenda „mică" și acceptabilă, ignorând faptul că nedepunerea afectează și alte drepturi condiționate de depunerea la termen (bonificații, eșalonări, termene de prescripție).

## Ce face iConta.eu

La data acestui ghid, iConta.eu oferă evidența contabilă pentru persoane fizice autorizate care conduc contabilitate în partidă simplă (`core/rip_api.py`), din care se pot extrage veniturile realizate relevante pentru declarația unică, dar **nu generează și nu depune** declarația unică propriu-zisă și nu calculează amenda pentru nedepunere — aceasta rămâne o obligație de raportare pe care persoana fizică sau contabilul o gestionează direct pe portalul ANAF, la termenele legale.

[iConta.eu](/)
