---
title: "Am omis evaluarea producției neterminate"
description: "Ce prevăd reglementările contabile despre evaluarea la inventar a producției în curs de execuție și cum se corectează o omisiune constatată ulterior."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Am omis evaluarea producției neterminate

Producția în curs de execuție (semifabricatele, lucrările neterminate, serviciile în curs) face parte din categoria stocurilor și este supusă acelorași reguli de evaluare la inventar ca orice alt stoc. Omiterea ei la închiderea exercițiului financiar denaturează atât bilanțul (active circulante subevaluate), cât și contul de profit și pierdere (cheltuieli supraestimate, pentru că munca „prinsă" în produsul neterminat nu a fost încă recunoscută ca stoc).

## Temeiul legal

::: ghid-temei
„Activele de natura stocurilor se evaluează la cost, mai puțin ajustările pentru depreciere constatate. Ajustări pentru depreciere se constată inclusiv pentru stocurile fără mișcare. În cazul în care valoarea contabilă a stocurilor este mai mare decât valoarea de inventar, valoarea stocurilor se diminuează până la valoarea realizabilă netă, prin constituirea unei ajustări pentru depreciere."
— OMFP nr. 1802/2014 pentru aprobarea Reglementărilor contabile privind situațiile financiare anuale individuale și situațiile financiare anuale consolidate, pct. 88 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Producția în curs de execuție intră explicit în categoria stocurilor căreia i se aplică această regulă — reglementările contabile enumeră, printre elementele de stocuri, „semifabricatele, prin care se înțelege produsele al căror proces tehnologic a fost terminat într-o secție (fază de fabricație) și care trec în continuare în procesul tehnologic al altei secții (faze de fabricație)". Practic:

- Evaluarea se face la **cost**, mai puțin ajustările pentru depreciere constatate la inventariere.
- Dacă valoarea contabilă e mai mare decât valoarea de inventar (recuperabilă), diferența se recunoaște printr-o ajustare pentru depreciere — nu se lasă „așa cum e" în evidență.
- Inventarierea și evaluarea la finalul exercițiului sunt obligatorii pentru toate elementele de natura activelor, inclusiv producția neterminată — nu doar pentru stocurile de materii prime sau mărfuri.

## Ce se greșește în practică

- Se inventariază materiile prime și mărfurile, dar se omite producția în curs de execuție, considerându-se (greșit) că nu are valoare cât timp nu a fost finalizată și vândută.
- Se lasă costurile aferente producției neterminate pe cheltuieli, în loc să fie recunoscute ca stoc — efect direct: rezultatul contabil al perioadei este subevaluat.
- Se constată omisiunea abia la controlul fiscal sau la auditul de sfârșit de an, când corectarea presupune deja o rectificare a situațiilor financiare/declarației, nu doar o simplă notă contabilă în perioada curentă.

## Ce face iConta.eu

Pentru acest subiect nu am găsit în cod o funcție dedicată calculării sau evaluării automate a producției în curs de execuție (modulul de inventariere al aplicației, `core/inventariere.py`, acoperă plusurile și minusurile de stocuri și mijloace fixe constatate la inventar, dar nu construiește el însuși valoarea producției neterminate — aceasta rămâne o evaluare pe care contabilul o introduce, pe baza documentelor de execuție). Corectarea unei omisiuni de acest tip rămâne, la acest moment, un proces manual în aplicație.

[iConta.eu](/)
