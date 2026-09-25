---
title: "Cum corectezi contabil o achiziție care trebuia înregistrată ca mijloc fix?"
description: "Procedura corectă de corectare a unei erori contabile atunci când o achiziție a fost trecută greșit pe cheltuieli în loc de imobilizări corporale."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectezi contabil o achiziție care trebuia înregistrată ca mijloc fix?

Dacă o achiziție care depășea pragul legal de încadrare ca mijloc fix a fost trecută direct pe cheltuieli, în loc să fie recunoscută ca imobilizare corporală și amortizată, avem o eroare contabilă clasică. Reglementările contabile tratează diferit erorile din exercițiul curent față de cele din exerciții anterioare deja închise — iar tratamentul corect depinde de acest moment.

## Temeiul legal

::: ghid-temei
„65. - (1) Erorile constatate în contabilitate se pot referi fie la exercițiul financiar curent, fie la exercițiile financiare precedente. [...] 67. - (1) Corectarea erorilor aferente exercițiului financiar curent se efectuează pe seama contului de profit și pierdere. [...] 68. - (1) Corectarea erorilor aferente exercițiilor financiare precedente nu determină modificarea situațiilor financiare ale acelor exerciții."
— OMFP nr. 1.802/2014, pct. 65, 67 și 68 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Dacă eroarea aparține **exercițiului financiar curent** (necheiat încă), corectarea se face direct: se stornează înregistrarea greșită (cheltuială) și se recunoaște activul ca imobilizare corporală, pe seama contului de profit și pierdere.
- Dacă eroarea aparține unui **exercițiu financiar precedent, deja închis**, corectarea nu modifică situațiile financiare deja depuse ale acelui exercițiu — impactul se reflectă prin **contul 1174 „Rezultatul reportat provenit din corectarea erorilor contabile"**, conform planului de conturi general din aceleași reglementări (pct. 594).
- Odată recunoscută corect ca imobilizare corporală, achiziția trebuie amortizată pe durata normală de utilizare rămasă, nu retroactiv pe toată perioada scursă de la achiziție.
- Corectarea unei erori contabile din exerciții anterioare poate avea și efect fiscal (impozit pe profit recalculat pentru perioadele afectate), care se tratează separat, prin declarații rectificative, potrivit Codului de procedură fiscală.

## Ce se greșește în practică

- Se corectează eroarea „la zi", pe cheltuiala curentă, chiar dacă eroarea aparține unui exercițiu anterior deja închis — ceea ce denatură rezultatul exercițiului curent în loc să afecteze rezultatul reportat.
- Se omite calculul amortizării retroactive corecte de la data reală a punerii în funcțiune, tratând bunul ca și cum ar fi fost achiziționat abia acum.
- Se ignoră impactul fiscal al corecției (impozitul pe profit al anilor anteriori a fost calculat greșit, cu o cheltuială integral dedusă în loc de amortizare eșalonată) și nu se depun declarații rectificative.
- Se confundă pragul valoric de încadrare ca mijloc fix (stabilit prin act normativ și actualizat periodic) cu o apreciere subiectivă „e prea mică suma ca să conteze" — pragul legal e cel care decide, nu mărimea percepută a cheltuielii.

## Ce face iConta.eu

Din verificarea codului, iConta.eu menține **o singură sursă canonică pentru pragul valoric de încadrare ca mijloc fix** (modulul `obiecte_inventar.py`), astfel încât la introducerea unei noi achiziții aplicația poate semnala corect dacă suma depășește pragul legal în vigoare la data respectivă — reducând riscul exact al erorii descrise mai sus, pentru achizițiile viitoare. Pentru corectarea unei erori deja produse în trecut (o achiziție anterioară deja înregistrată greșit pe cheltuieli), aplicația nu are un flux dedicat de „corectare retroactivă" — nota contabilă de corecție și eventuala declarație rectificativă rămân operațiuni manuale ale contabilului.

[iConta.eu](/)
