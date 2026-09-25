---
title: "Cât poate plăti o firmă în numerar unei persoane fizice?"
description: "Plafonul zilnic de 10.000 lei pentru plățile în numerar către o persoană fizică, conform Legii 70/2015."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cât poate plăti o firmă în numerar unei persoane fizice?

O firmă achită o factură, un drept de autor, o cesiune de creanță sau restituie un împrumut către o persoană fizică, în numerar. Plafonul aplicabil nu e cel folosit între firme (5.000 lei), ci unul separat, dedicat expres relației firmă–persoană fizică.

## Temeiul legal

::: ghid-temei
„(4) Operațiunile de plăți în numerar efectuate de persoanele prevăzute la art. 1 alin. (1), către persoane fizice, reprezentând contravaloarea unor achiziții de bunuri sau a unor prestări de servicii, dividende, cesiuni de creanțe sau alte drepturi și restituiri de împrumuturi sau alte finanțări se efectuează cu încadrarea în plafonul zilnic de 10.000 lei către o persoană. Sunt interzise plățile fragmentate în numerar către o persoană, pentru tranzacțiile mai mari de 10.000 lei."
— Legea 70/2015, art. 4 alin. (4) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Elementele-cheie:

- **Plafonul e 10.000 lei pe zi, către aceeași persoană fizică** — nu 5.000 lei, cum e cazul plăților către alte firme (art. 3 alin. (1) lit. c)).
- Plafonul acoperă o listă largă de operațiuni: achiziții de bunuri, prestări de servicii, dividende, cesiuni de creanțe sau alte drepturi, restituiri de împrumuturi sau alte finanțări — nu doar simple cumpărări.
- **Fragmentarea e interzisă expres**: dacă suma datorată depășește 10.000 lei, firma nu poate împărți plata în mai multe tranșe în numerar, pe zile diferite, ca să rămână sub plafon fiecare tranșă — legea sancționează exact această manevră.
- Nerespectarea plafonului sau interdicției de fragmentare e contravenție, sancționată cu amendă de 10% din suma care depășește plafonul, dar nu mai puțin de 100 lei (art. 12 alin. (1)).

## Ce se greșește în practică

- Se aplică din reflex plafonul de 5.000 lei (cel dintre firme) și la plățile către persoane fizice — cele două plafoane sunt distincte și nu se confundă.
- Se împarte o plată mai mare de 10.000 lei în două zile consecutive, crezând că fragmentarea pe zile diferite scapă de interdicție — legea interzice fragmentarea indiferent de intervalul de timp ales pentru a evita plafonul.
- Se ignoră faptul că plafonul e "pe persoană", nu "pe operațiune" — mai multe plăți mici, către aceeași persoană, în aceeași zi, se cumulează la calculul plafonului.

## Ce face iConta.eu

La data acestui ghid, `core/casa.py` are constanta `PLAFON_PF = Decimal("10000")`, folosită în funcția `verifica_plafon()` pentru a semnala, ca avertisment, orice plată sau încasare cumulată către/de la o persoană fizică ce depășește 10.000 lei într-o zi. Verificarea acoperă exact plafonul din art. 4 alin. (4), pe baza operațiunilor introduse în registrul de casă al aplicației.

[iConta.eu](/)
