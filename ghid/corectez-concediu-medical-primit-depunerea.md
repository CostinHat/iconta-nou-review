---
title: "Cum corectez un concediu medical primit după depunerea D112?"
description: "Ce faci când certificatul de concediu medical ajunge la contabilitate după ce D112 a fost deja depusă — două regimuri diferite, în funcție de situație."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez un concediu medical primit după depunerea D112?

Situația e frecventă: salariatul aduce certificatul de concediu medical abia după ce D112 a lunii respective a fost deja depusă. Ce se întâmplă mai departe depinde de un singur lucru: dacă acel certificat e „independent" (privește o perioadă deja închisă) sau dacă e continuarea unui episod care traversează în luna curentă.

## Temeiul legal

::: ghid-temei
„Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. [...] Declarațiile [...] pot fi corectate prin depunerea unei declarații rectificative."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 alin. (1) și (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„Pentru situațiile în care perioada de incapacitate temporară de muncă [...] se prelungește în luna următoare [...], diferențele de indemnizații [...] rezultate ca urmare a recalculării și aferente lunii anterioare celei în care are loc această operațiune, se includ în veniturile lunii în care sunt determinate și se declară în [D112] [...] aferentă aceleiași luni."
— OUG 158/2005, art. 17 alin. (1^2), introdus prin OUG 89/2025 art. VII, în vigoare de la 1 iulie 2026 (sursă: anaf_surse/oug_89_2025.txt)
:::

Cele două situații se rezolvă diferit:

- **Certificatul e independent** (privește o boală/perioadă care nu are legătură cu ceva deja declarat, sau nu prelungește un episod peste luna deja depusă): corectarea se face prin **declarație rectificativă** pentru luna la care se referă certificatul, oricând în termenul de prescripție. Se completează corect certificatul în declarație și se redepune întreaga declarație a acelei luni.
- **Certificatul continuă un episod de boală obișnuită**, iar recalcularea zilelor cumulate schimbă procentul aplicat lunii deja declarate: de la 1 iulie 2026, diferența **nu se mai declară printr-o rectificativă a lunii vechi**, ci se include direct în D112 a lunii în care se face recalcularea — regula introdusă de OUG 89/2025.
- Ambele regimuri presupun ca certificatul să existe efectiv la momentul corectării — declarația rectificativă nu se poate depune fără o declarație inițială valabilă pentru acea perioadă, iar validatorul ANAF respinge o rectificativă depusă în aceeași zi cu declarația inițială.

## Ce se greșește în practică

- Se aplică sistematic declarația rectificativă, chiar și pentru certificate de continuare intrate în vigoare după 1 iulie 2026, deși legea cere altă procedură pentru acest caz.
- Se amână corectarea, considerând că un certificat sosit „prea târziu" nu mai poate fi declarat — termenul legal e cel de prescripție, nu câteva zile.
- Se corectează doar zilele și suma indemnizației, fără să se verifice dacă modificarea afectă și alte secțiuni ale D112 (baza CAS/CASS, totalurile pe firmă).

## Ce face iConta.eu

D112 se generează, în `core/d112.py`, din concediile medicale salvate în fișa fiecărui salariat. Când un certificat sosește după depunere, contabilul îl introduce (sau îl corectează) în fișa salariatului, iar aplicația regenerează declarația lunii cu datele actualizate. Aplicația nu decide singură dacă regenerarea trebuie depusă ca declarație rectificativă a lunii vechi sau inclusă în luna curentă — distincția de mai sus, între cele două regimuri, rămâne verificarea și decizia contabilului la fiecare caz concret.

[iConta.eu](/)
