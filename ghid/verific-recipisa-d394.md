---
title: "Cum verific recipisa D394?"
description: "Cum se verifică starea declarației 394 după depunere, conform instrucțiunilor ANAF, și de ce iConta.eu nu automatizează încă acest pas pentru D394."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific recipisa D394?

D394 nu folosește literal cuvântul „recipisă" în instrucțiunile ei de completare — termenul consacrat acolo e „starea declarației". Dar mecanismul e cel cunoscut de la orice declarație depusă electronic la ANAF: după depunere, contribuabilul trebuie să verifice pe portal dacă documentul a fost acceptat sau conține erori.

## Temeiul legal

::: ghid-temei
„3.4. Verificarea faptului că este o declaraţie corectă reprezintă un proces ulterior depunerii, care se desfăşoară pe serverele centrale. După depunerea prin internet sau la ghişeu a formularului (394) [...] starea acesteia se poate verifica accesând portalul Agenţiei Naţionale de Administrare Fiscală. 3.5. În cazul în care pe pagina de vizualizare a stării declaraţiei (394) se afişează un mesaj cu erorile pe care le conţine documentul depus, contribuabilul trebuie ca, în termen de 3 zile lucrătoare, să corecteze toate erorile comunicate şi să reia procesul de depunere a declaraţiei (394)."
— OPANAF 3769/2015, Anexa 3 pct.3.4-3.5 (sursă: anaf_surse/opanaf_3769_2015_d394_baza.txt:1288-1297)
:::

- Verificarea corectitudinii declarației nu e instantanee — se face ulterior depunerii, pe serverele ANAF, nu în momentul încărcării fișierului.
- Starea declarației (echivalentul a ceea ce, colocvial, se numește „recipisă") se verifică accesând portalul ANAF, nu prin vreo confirmare automată trimisă contribuabilului.
- Dacă starea afișează erori, contribuabilul are un termen strict de **3 zile lucrătoare** pentru a le corecta și a redepune declarația — depășirea termenului poate echivala cu nedepunerea declarației.

## Ce se greșește în practică

- Se consideră declarația „gata" imediat după încărcarea fișierului pe portal, fără a mai verifica ulterior starea afișată de ANAF.
- Se ratează termenul de 3 zile lucrătoare pentru corectarea erorilor semnalate, pentru că verificarea stării nu e făcută sistematic după fiecare depunere.
- Se confundă validarea locală (cu validatorul instalat pe calculator, înainte de depunere) cu verificarea finală de pe portalul ANAF, care e singura relevantă pentru statutul oficial al declarației.

## Ce face iConta.eu

Aici e important de spus onest ce anume automatizează aplicația și ce nu. iConta **validează local** fișierul D394 înainte de depunere, rulând validatorul oficial ANAF instalat (`core/duk.py`, `valideaza()`) — asta prinde majoritatea erorilor de structură înainte ca fișierul să ajungă pe portal. Pentru **e-Factura**, aplicația are un mecanism separat de interogare automată a stării mesajelor la ANAF și de descărcare a recipisei (`core/spv_poll.py`), care rulează periodic și salvează recipisa primită.

**Acest mecanism de interogare automată a recipisei nu există pentru D394.** Depunerea declarației 394 se face manual prin SPV, iar verificarea stării declarației după depunere — inclusiv citirea eventualelor erori și redepunerea în termenul de 3 zile — rămâne un pas pe care contabilul îl face direct pe portalul ANAF, în afara aplicației.

[iConta.eu](/)
