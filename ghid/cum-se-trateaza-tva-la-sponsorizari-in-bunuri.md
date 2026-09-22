---
title: Cum se tratează TVA la sponsorizări în bunuri?
description: Acordarea gratuită de bunuri sau servicii în cadrul unei acțiuni de sponsorizare nu este asimilată unei livrări/prestări cu plată supuse TVA, dar numai „în condițiile stabilite prin normele metodologice” — condiții pe care sursele verificate nu le detaliază, deci trebuie confirmate separat înainte de a aplica scutirea.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se tratează TVA la sponsorizări în bunuri?

Sponsorizarea nu înseamnă mereu bani transferați direct către beneficiar — de multe ori firma donează bunuri (echipamente, produse proprii, marfă) sau prestează gratuit un serviciu. Pe lângă întrebarea „cât pot scădea din impozitul pe profit”, apare o întrebare separată, de TVA: dă naștere transferul gratuit al acestor bunuri sau servicii unei obligații de colectare a TVA, ca și cum ar fi o livrare/prestare cu plată?

## Temeiul legal

::: ghid-temei
„Nu constituie livrare de bunuri..., fără a se limita la acestea, operațiuni precum: ... c) acordarea de bunuri de mică valoare, în mod gratuit, în cadrul acțiunilor de sponsorizare, de mecenat, de protocol/reprezentare, în condițiile stabilite prin normele metodologice.”

— *Codul fiscal, art. 270 alin. (8) lit. c).*

„Nu constituie prestare de servicii efectuată cu plată... operațiuni precum: a) utilizarea bunurilor care fac parte din activele folosite în cadrul activității economice a persoanei impozabile sau prestarea de servicii în mod gratuit, în cadrul acțiunilor de sponsorizare, mecenat sau protocol, în condițiile stabilite prin normele metodologice.”

— *Codul fiscal, art. 271 alin. (5) lit. a).*
:::

## Ce înseamnă, practic, „nu constituie livrare/prestare”

Regula generală de TVA este că, dacă ați dedus TVA la achiziția unui bun și apoi îl dați gratuit, operațiunea e tratată ca o livrare către sine (autolivrare) și trebuie să colectați TVA la valoarea bunului — pentru a compensa deducerea inițială. Art. 270 alin. (8) lit. c) și art. 271 alin. (5) lit. a) scot **sponsorizarea** de sub această regulă: cât timp bunurile date sau serviciile prestate gratuit se încadrează în acțiunea de sponsorizare, operațiunea nu e asimilată unei livrări/prestări cu plată, deci nu apare, în principiu, o obligație suplimentară de colectare a TVA doar din acest motiv.

Textul de lege condiționează însă expres scutirea de două elemente:

- pentru bunuri, condiția explicită este ca acestea să fie „de mică valoare" (art. 270 alin. 8 lit. c);
- pentru bunuri și servicii deopotrivă, aplicarea se face „**în condițiile stabilite prin normele metodologice**” — adică regulile exacte (praguri, mod de calcul, eventuale plafoane) nu sunt în textul de bază al Codului fiscal, ci într-un act separat.

**Limitare a sursei verificate:** normele metodologice care detaliază pragul „de mică valoare” și condițiile de aplicare nu se află, ca text separat, în sursele verificate pentru acest dosar. Nu inventăm aici un plafon numeric — pentru un caz concret (mai ales dacă valoarea bunurilor donate e semnificativă), confirmați pragul și condițiile exacte în normele metodologice ale art. 270/271 înainte de a aplica scutirea.

::: ghid-exemplu
O firmă cumpără calculatoare, deduce TVA la achiziție, apoi le donează unei asociații în cadrul unui contract de sponsorizare. Dacă operațiunea se încadrează în condițiile din normele metodologice pentru „bunuri de mică valoare acordate gratuit în cadrul acțiunilor de sponsorizare”, transferul nu e asimilat unei livrări cu plată, deci nu se colectează TVA suplimentar la ieșirea bunurilor, iar TVA-ul dedus la achiziție rămâne dedus. Dacă bunurile nu se încadrează în acele condiții (de exemplu depășesc pragul de valoare stabilit prin norme), operațiunea devine asimilată unei livrări de bunuri cu titlu oneros, iar firma trebuie să colecteze TVA la valoarea bunurilor donate.
:::

## Ce se greșește în practică

- Se tratează orice bun donat în cadrul unei sponsorizări ca automat scutit de TVA, fără a verifica dacă se încadrează în condițiile din normele metodologice (mai ales pragul de valoare).
- Se analizează doar deductibilitatea la impozitul pe profit și se omite complet întrebarea de TVA, deși sunt două regimuri separate, cu temeiuri legale diferite (art. 25 pentru profit, art. 270/271 pentru TVA).
- Se aplică regula de TVA pentru bunuri (art. 270) și la servicii prestate gratuit, fără a observa că temeiul pentru servicii e un alineat diferit (art. 271 alin. 5 lit. a), cu propriile condiții.
- Se confundă scutirea de TVA la sponsorizare cu cea de la protocol — ambele sunt menționate în același text de lege, dar au, de regulă, praguri și condiții distincte în normele metodologice.
- Se colectează TVA „din prudență” fără verificare, sau invers, nu se colectează deloc, fără a confirma condițiile — ambele extreme pot fi greșite în funcție de valoarea reală a bunurilor.

## Ce face iConta.eu

Funcția `nota_sponsorizare(suma, mod)` din `core/sponsorizari.py` generează nota contabilă doar pentru două moduri: `"contract"` (`6582 = 401`) și `"plata"` (`6582 = 5121`). Modulul menționează în documentația internă și un mod „în natură” (cont din clasa 3xx, pentru ieșirea bunurilor din gestiune), dar **acesta nu este implementat** — apelul funcției cu orice altă valoare decât `"contract"` sau `"plata"` generează eroare.

Practic, pentru o sponsorizare acordată sub formă de bunuri, iConta.eu nu generează automat nici nota de ieșire a bunurilor din gestiune, nici eventuala notă de colectare a TVA dacă operațiunea nu se încadrează în condițiile de scutire. Această sponsorizare trebuie înregistrată și verificată manual, inclusiv sub aspectul TVA descris mai sus.

[iConta.eu](/)
