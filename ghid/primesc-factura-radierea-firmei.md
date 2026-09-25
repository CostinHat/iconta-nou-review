---
title: "Ce fac dacă primesc o factură după radierea firmei?"
description: "Ce se întâmplă din punct de vedere fiscal și juridic când o factură ajunge la o firmă deja radiată din registrul comerțului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă primesc o factură după radierea firmei?

Radierea din registrul comerțului marchează încetarea existenței juridice a societății — nu doar suspendarea temporară a activității. O factură emisă sau primită după această dată nu mai are, din punct de vedere legal, un destinatar care să existe ca persoană juridică, ceea ce ridică probleme atât pentru emitent, cât și pentru foștii asociați/lichidator.

## Temeiul legal

::: ghid-temei
„(1) Dizolvarea societății are ca efect deschiderea procedurii lichidării. [...]
(4) Societatea își păstrează personalitatea juridică pentru operațiunile lichidării, până la terminarea acesteia."
— Legea 31/1990 privind societățile, art. 233 alin. (1) și (4) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

- Personalitatea juridică a societății se păstrează doar pe durata lichidării, exclusiv pentru operațiunile acesteia — nu și după radiere. Odată radiată din registrul comerțului, firma încetează să mai existe ca subiect de drept, deci nu mai poate fi, din punct de vedere legal, nici emitentă, nici destinatară a unei facturi.
- O factură emisă către o firmă deja radiată este, practic, emisă către o entitate inexistentă — codul unic de identificare fiscală nu mai este activ, iar în sistemul RO e-Factura validarea unei astfel de facturi ar trebui, în mod normal, să eșueze din cauza CUI-ului nevalid.
- Dacă bunul livrat/serviciul prestat a avut loc înainte de radiere, dar factura a fost emisă sau primită abia după radiere, corecția corectă este emiterea/reemiterea facturii corect datate, către partea îndreptățită legal la momentul respectiv (de exemplu lichidatorul, dacă lichidarea era încă în derulare, sau fostul asociat/succesor, în cazuri specifice) — nu emiterea unei facturi „către" o firmă care nu mai există.
- Practic, orice document fiscal ajuns după radiere trebuie tratat printr-o analiză punctuală a datei operațiunii economice reale față de data radierii, adesea cu asistență juridică, întrucât Codul fiscal și Codul de procedură fiscală nu prevăd o procedură specifică, unică, pentru „factura primită după radiere" — principiul de bază rămâne cel din Legea 31/1990: nu poate exista act valabil emis către/de o persoană juridică ce nu mai există.

## Ce se greșește în practică

- Se încearcă înregistrarea unei facturi primite după radiere „ca și cum firma ar mai exista", cu riscul ca documentul să nu poată fi validat legal și să nu producă niciun efect fiscal opozabil.
- Se ignoră faptul că, dacă lichidarea era încă în curs la momentul facturii, interlocutorul corect nu mai este administratorul „obișnuit", ci lichidatorul desemnat — abia radierea finală pune capăt oricărei capacități de a mai primi/emite documente.
- Se presupune că o simplă corectură sau anulare rezolvă automat situația, fără să se verifice dacă operațiunea economică de bază chiar a avut loc înainte de radiere (caz în care corecția se poate face retroactiv, cu documentare atentă) sau după (caz în care factura nu are, practic, temei valabil).

## Ce face iConta.eu

iConta.eu are un modul dedicat proceselor de lichidare și radiere a societății (`lichidare.py`), care tratează corect notele contabile ale valorificării activelor, închiderii TVA și partajului final către asociați, conform OMFP 897/2015 și Legii 31/1990. La verificarea codului, aplicația nu are însă o funcție specifică pentru gestionarea facturilor primite după data radierii firmei — această situație depășește ciclul normal de contabilitate curentă și necesită, așa cum arată și temeiul legal de mai sus, o analiză punctuală, de regulă cu sprijin juridic.

[iConta.eu](/)
