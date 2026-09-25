---
title: "Limitarea accesului la cont pentru angajați 2026"
description: "Ce cere controlul intern din reglementările contabile privind separarea funcțiilor și accesul limitat la datele financiar-contabile, și cum implementează iConta.eu accesul pe rol pentru utilizatorii angajați ai unui cabinet."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Limitarea accesului la cont pentru angajați 2026

„Limitarea accesului la cont" pentru angajați nu e o obligație fiscală de sine stătătoare cu un act normativ dedicat, ci decurge din principiile de control intern pe care le cer reglementările contabile — separarea funcțiilor și restrângerea accesului la sistemul financiar-contabil doar la informațiile necesare fiecărui rol. Practic, un angajat cu acces la contabilitatea firmei nu ar trebui să aibă acces nelimitat la toate datele, ci doar la ce îi e necesar pentru sarcinile lui.

## Temeiul legal

::: ghid-temei
„570. - Activitățile de control fac parte integrantă din procesul de gestiune prin care entitatea urmărește atingerea obiectivelor propuse. Controlul vizează aplicarea normelor și procedurilor de control intern, la toate nivelurile ierarhice și funcționale: aprobare, autorizare, verificare, evaluarea performanțelor operaționale, securizarea activelor, separarea funcțiilor."
— OMFP 1802/2014, Capitolul 11 „Controlul intern", pct. 570 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

În aceeași secțiune, referitor la accesul la informațiile contabile și financiare:

::: ghid-temei
„Sunt necesare, de asemenea: – identificarea cu claritate a persoanelor responsabile cu elaborarea informațiilor contabile și financiare publicate sau care participă la elaborarea situațiilor financiare; – accesul fiecărui colaborator implicat în procesul elaborării de informații contabile și financiare, la informațiile necesare controlului intern [...]"
— OMFP 1802/2014, Capitolul 11 „Controlul intern", pct. 573 alin. (2) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Textul nu fixează o listă tehnică de permisiuni — el stabilește principiul: accesul unui colaborator (inclusiv al unui angajat) la sistemul financiar-contabil trebuie corelat cu rolul lui real, iar separarea funcțiilor (cine introduce o operațiune, cine o validează, cine are vizibilitate completă) e parte a controlului intern pe care entitatea trebuie să îl asigure.

## Ce se greșește în practică

- Se dă tuturor angajaților cu atribuții contabile același nivel de acces, „ca să fie mai simplu", ignorând principiul separării funcțiilor din pct. 570.
- Se confundă „limitarea accesului la cont" cu o obligație legală specifică pentru 2026 — nu există, în legislația verificată, un act normativ dedicat exclusiv acestui subiect; el rămâne un principiu general de control intern, aplicabil oricând, nu o noutate legislativă a anului.
- Se lasă un angajat plecat din firmă cu acces activ la sistem — separarea funcțiilor și securizarea activelor (pct. 570) presupun și revocarea promptă a accesului la încetarea unui rol.

## Ce face iConta.eu

iConta.eu implementează accesul diferențiat pe rol prin funcționalitatea de **autentificare și sesiuni** (`core/auth_api.py`): fiecare utilizator primește un token cu rolul lui — superadmin, admin firmă, **angajat** sau client — iar accesul e limitat la propriul cabinet, respectiv la propriile firme, în funcție de acest rol. Un utilizator cu rol de angajat nu vede, prin construcție, date din afara cabinetului la care e alocat.

Acest ghid a fost, inițial, asociat funcționalității **F135 — Pontaj angajați** (`core/pontaj.py`), care ține evidența zilelor lucrate/absente ale salariaților unei firme cliente, dar aceasta e o funcționalitate complet diferită — un registru informativ de prezență, fără nicio legătură cu drepturile de acces în sistem ale utilizatorilor iConta.eu. Subiectul acestui ghid ține, funcțional, de autentificare și roluri, nu de pontaj — nu am forțat această legătură.

[iConta.eu](/)
