---
title: "Ce faci dacă D101 nu corespunde cu D100?"
description: "Ce prevede legea când declarația anuală de impozit pe profit (D101) nu se potrivește cu sumele declarate în cursul anului prin D100, și cum se corectează fiecare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce faci dacă D101 nu corespunde cu D100?

D100 declară, trimestrial, plățile anticipate sau impozitul pe profit curent; D101 este declarația anuală de impozit pe profit, care definitivează situația. Dacă la închiderea anului observi o neconcordanță între ce ai declarat prin D100 în cursul anului și ce rezultă corect prin D101, cele două declarații nu se „împacă" printr-o singură corecție comună — fiecare are propriul mecanism de rectificare.

## Temeiul legal

::: ghid-temei
„3. În cazul în care persoana juridică responsabilă corectează declarația depusă, declarația rectificativă se întocmește pe același model de formular, înscriind «X» în spațiul special prevăzut în acest scop. [...] Declarația nu poate fi depusă și nu poate fi corectată după anularea rezervei verificării ulterioare, cu excepțiile prevăzute la art. 105 alin. (6) din Legea nr. 207/2015 privind Codul de procedură fiscală."
— OPANAF 206/2025 (instrucțiuni de completare a formularului 101) (sursă: anaf_surse/opanaf_206_2025_d101.txt)
:::

- Corecția D101 se face **prin D101 însuși**, bifând căsuța „Declarație rectificativă" de pe formular — nu printr-o declarație separată de tip 710.
- Temeiul general al dreptului de corecție e comun tuturor declarațiilor de impunere: „Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale" — CPF (Legea 207/2015), art. 105 alin. (1).
- Excepția „notificare de conformare" există și pentru D101: rectificarea se poate face „ca urmare a unei notificări de conformare, în condițiile Legii nr. 207/2015 privind Codul de procedură fiscală" (aceeași sursă), situație în care se bifează separat această căsuță pe formular.

## Ce se greșește în practică

- Se presupune că formularul 710 poate corecta D101 — 710 corectează exclusiv obligațiile declarate prin D100 (autoimpunere/reținere la sursă, coduri 121 și 103), nu declarația anuală D101.
- Se corectează doar D101, fără să se verifice dacă plățile anticipate raportate anterior prin D100 mai reflectă corect realitatea — o neconcordanță reală poate cere corectarea ambelor declarații, fiecare prin mecanismul ei propriu.
- Se depune o rectificativă D101 fără să se bifeze corect distincția dintre „rectificativă" obișnuită și „rectificativă ca urmare a unei notificări de conformare" — bifa greșită schimbă temeiul legal invocat față de ANAF.

## Ce face iConta.eu

D101 are, în iConta.eu, propriul ecran și propriul mecanism de rectificare — o corecție a declarației anuale se face din formularul D101, nu prin funcționalitatea D710. iConta.eu **compară automat** rândul 50 din D101 (plățile anticipate/impozitul declarat pe parcursul anului, așa cum le-a trecut contabilul în declarația anuală) cu suma „de plată" declarată efectiv, trimestrial, prin cele patru D100 depuse prin aplicație pe anul respectiv — o constatare dedicată („D101 vs D100 depuse (plăți anticipate)"), parte din controlul fiscal încrucișat. Când sumele nu coincid (peste toleranța de rotunjire), aplicația semnalează divergența cu roșu și un remediu sugerat; când aplicația nu a văzut vreo depunere D100 pe un trimestru, marchează constatarea ca „nu pot confrunta" (gri), nu ca verde tacit. Dacă identifici o diferență reală, corectarea D100-urilor greșite se face prin formularul 710 (funcționalitatea descrisă în acest ghid pentru codurile 121/103), iar corectarea D101 se face separat, prin propriul ecran de declarație rectificativă D101.

[iConta.eu](/)
