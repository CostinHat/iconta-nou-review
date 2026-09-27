---
title: Trebuie să emit alt număr de factură dacă XML-ul a fost respins?
description: Nu este obligatoriu. O factură respinsă la validare nu a primit sigiliul Ministerului Finanțelor și nu a ajuns la client, iar OUG 120/2021 art. 4 alin. (5) prevede că, după corectarea erorilor, factura se transmite din nou în același sistem. Dacă preferi un număr nou, Codul fiscal art. 330 alin. (1) lit. a) permite anularea facturii netransmise și emiterea alteia.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Trebuie să emit alt număr de factură dacă XML-ul a fost respins?

Nu trebuie. O factură respinsă de RO e-Factura pentru erori de structură nu a fost comunicată clientului, deci nu a produs efecte ca factură. Corectezi erorile și o retransmiți, de regulă cu același număr și aceeași dată. Legea îți permite și varianta cu număr nou, dar atunci numărul inițial trebuie să rămână justificat în secvență, ca document anulat.

### Ce se întâmplă juridic la respingere

OUG 120/2021, art. 4:
- **alin. (4)**: dacă factura respectă structura, se aplică sigiliul electronic al Ministerului Finanțelor și factura se comunică de îndată destinatarului;
- **alin. (5)**: dacă nu respectă structura, emitentul primește un mesaj cu erorile identificate. „După corectarea erorilor identificate, factura electronică se transmite în cadrul aceluiași sistem";
- **alin. (6)**: originalul facturii este fișierul XML însoțit de sigiliul electronic al Ministerului Finanțelor.

Un XML respins nu are sigiliu, deci nu există un original care să fi ajuns la client. Codul fiscal art. 319 alin. (1^1) arată că, între persoane impozabile stabilite în România, sunt considerate facturi numai cele care îndeplinesc condițiile din OUG 120/2021. Alin. (5) vorbește despre retransmiterea aceleiași facturi după corectare, nu despre emiterea alteia.

### De ce numărul poate rămâne același

Art. 319 alin. (20) lit. a) cere un număr de ordine care identifică factura în mod unic. Cum varianta respinsă nu a devenit factură, retransmiterea sub același număr nu creează două facturi cu același număr.

### Varianta cu număr nou

Codul fiscal art. 330 alin. (1) lit. a): dacă factura nu a fost transmisă beneficiarului, ea „se anulează și se emite o nouă factură". Poți deci anula documentul respins și emite unul nou, cu număr nou. În acest caz:
- numărul vechi rămâne gol în serie și trebuie documentat intern ca anulat. OMFP 2634/2015, anexa 1, cere numere secvențiale, stabilite prin proceduri proprii;
- noul XML se transmite în termen.

Varianta nu e greșită, dar complică reconcilierea seriei fără niciun avantaj.

### Atenție la termen

Termenul de transmitere este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită pentru emiterea facturii prevăzută la art. 319 alin. (16) (OUG 120/2021, art. 10 alin. (7), în forma dată de OUG 89/2025). Respingerea nu prelungește termenul. Exemplu: o factură emisă pe 3 martie și respinsă pe 4 martie poate fi retransmisă corectată cu aceeași dată până la finalul celei de-a cincea zile lucrătoare de la 3 martie.

### Pași practici

1. Citește mesajul de erori și corectează datele în programul de facturare, nu direct în XML.
2. Retransmite cu același număr și aceeași dată.
3. Verifică primirea sigiliului. Abia de atunci factura există pentru client.
4. Dacă alegi totuși număr nou, notează în registrul intern al seriei anularea numărului vechi.

### De reținut
- Factura respinsă nu a ajuns la client și nu are sigiliu (OUG 120/2021, art. 4 alin. (4)-(6)).
- După corectare, aceeași factură se retransmite (art. 4 alin. (5)).
- Numărul nou e permis, dar nu obligatoriu (Codul fiscal art. 330 alin. (1) lit. a)).
- Respingerea nu prelungește termenul de 5 zile lucrătoare.
