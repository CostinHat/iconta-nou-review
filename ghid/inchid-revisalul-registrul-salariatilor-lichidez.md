---
title: "Cum închid Revisalul/registrul salariaților când lichidez firma"
description: "Ce obligații rămân privind registrul general de evidență a salariaților atunci când angajatorul își încetează activitatea, potrivit Codului muncii."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum închid Revisalul/registrul salariaților când lichidez firma

Când o firmă intră în lichidare, contractele de muncă ale salariaților încetează, iar angajatorul trebuie să reflecte asta corect în registrul general de evidență a salariaților (sistemul curent: REGES-ONLINE). Întrebarea „cum se închide registrul" ascunde, de fapt, două obligații distincte: încetarea fiecărui contract individual și încetarea existenței angajatorului însuși.

## Temeiul legal

::: ghid-temei
„Contractul individual de muncă încetează de drept: [...] b) la data rămânerii irevocabile a hotărârii judecătorești de declarare a morții sau a punerii sub interdicție a salariatului ori a angajatorului persoana fizică, dacă aceasta antrenează lichidarea afacerii."
— Legea nr. 53/2003 (Codul muncii), art. 56 lit. b) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)
:::

**Limitare declarată:** textul de mai sus tratează explicit doar cazul angajatorului persoană fizică; pentru angajatorul persoană juridică aflat în dizolvare/lichidare, sursele verificate nu conțin un articol distinct din HG nr. 295/2025 (actul care reglementează REGES-ONLINE) care să detalieze o procedură specială de „închidere a registrului" la încetarea firmei. Ce rămâne cert, din mecanismul general al registrului:

- **Fiecare contract individual de muncă** trebuie să aibă înregistrată, în registru, data și temeiul încetării — indiferent de motiv, inclusiv încetarea determinată de lichidarea angajatorului.
- Obligația de raportare a modificărilor/încetărilor în registru (termene de 3, 10 sau 20 de zile lucrătoare, după caz, conform HG nr. 295/2025) rămâne valabilă **până la radierea firmei** din registrul comerțului — cât timp firma există ca subiect de drept, obligațiile de raportare în REGES-ONLINE continuă.
- Nu există un „buton" legal separat de închidere a registrului la nivel de angajator; registrul reflectă, pentru fiecare salariat, încetarea contractului, iar odată radiată firma, ea nu mai poate genera noi înregistrări.

## Ce se greșește în practică

- Se presupune că radierea firmei din Registrul Comerțului închide automat și înregistrările din REGES-ONLINE — cele două sisteme sunt separate, iar încetarea fiecărui contract individual trebuie transmisă explicit, înainte de radiere.
- Se lasă neînregistrate în registru încetările determinate de lichidare, considerându-se că „oricum firma se desființează" — răspunderea contravențională pentru netransmiterea la termen rămâne valabilă cât timp firma există.
- Se confundă încetarea contractului angajatorului persoană fizică (art. 56 lit. b), aplicabil doar PFA-urilor/întreprinderilor individuale care au calitatea de angajator persoană fizică) cu situația firmelor persoane juridice aflate în lichidare — regimul lor de încetare a contractelor se supune altor temeiuri din Codul muncii (de regulă concediere pentru motive care nu țin de persoana salariatului, din cauza încetării activității angajatorului).

## Ce face iConta.eu

Verificat în cod: `core/reges_client.py` conține funcția `mesaj_incetare_contract`, care generează mesajul de tip `ActiuneIncetare` transmis către REGES-ONLINE pentru încetarea unui contract individual de muncă, pe baza datei și temeiului de încetare. Aplicația **nu are o funcționalitate separată de „închidere a registrului" la nivelul întregii firme** — nu există în cod o acțiune dedicată radierii angajatorului din registru la lichidare. Practic, contabilul folosește mecanismul existent de încetare a contractelor, pentru fiecare salariat în parte, iar radierea firmei din Registrul Comerțului rămâne un pas separat, în afara aplicației.

[iConta.eu](/)
