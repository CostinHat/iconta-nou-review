---
title: "Ce verifică ANAF la un magazin online?"
description: "Obligația de utilizare a caselor de marcat electronice fiscale pentru livrările la domiciliu efectuate de magazine pe bază de comandă, cu temeiul din legea AMEF."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce verifică ANAF la un magazin online?

Acest ghid tratează un singur punct concret de verificare — nu o listă exhaustivă a tot ce poate controla ANAF la un magazin online, ci acela cu cel mai clar temei legal specific: obligația de a emite bon fiscal la livrarea comenzilor, chiar și atunci când plata se face cu cardul online sau ramburs la livrare.

## Temeiul legal

::: ghid-temei
„h) comerțul cu amănuntul prin comis-voiajori, precum și prin corespondență, cu excepția livrărilor de bunuri la domiciliu efectuate de magazine și unitățile de alimentație publică, pe bază de comandă."
— OUG nr. 28/1999, art. 2 alin. (1) lit. h) (sursă: anaf_surse/oug_28_1999.html)
:::

Cum se citește această excepție de la o excepție:

- Regula de bază a OUG 28/1999 e că operatorii economici trebuie să utilizeze **aparate de marcat electronice fiscale** (AMEF) pentru încasările în numerar sau prin card, cu emiterea bonului fiscal la fiecare vânzare cu amănuntul.
- Art. 2 alin. (1) exceptează de la această obligație o listă de activități, printre care „comerțul [...] prin corespondență" — dar textul citat mai sus **exclude explicit din exceptare** „livrările de bunuri la domiciliu efectuate de magazine [...] pe bază de comandă" — adică exact modelul unui magazin online care primește comenzi și livrează la domiciliul clientului.
- Practic, un magazin online care livrează comenzi la domiciliu **nu se încadrează** în excepția de la obligația AMEF — trebuie să emită bon fiscal pentru fiecare livrare, indiferent dacă plata s-a făcut online, în avans, sau la livrare (ramburs), în numerar sau cu cardul curierului.
- Aceasta e una dintre verificările tipice pe care ANAF le poate face la un magazin online: dacă bonurile fiscale corespund livrărilor efectiv realizate, dacă valorile de pe bonuri coincid cu sumele încasate și dacă momentul emiterii respectă obligațiile legale de raportare (inclusiv conectarea caselor de marcat la sistemul informatic al ANAF).

## Ce se greșește în practică

- Se presupune că vânzarea „prin corespondență"/online e automat scutită de obligația de casă de marcat, pe baza excepției generale de la comerțul prin corespondență — excepția nu se aplică livrărilor la domiciliu pe bază de comandă, care e exact modelul obișnuit al unui magazin online.
- Se emite bon fiscal doar pentru plățile încasate direct de firmă (cardul pe site), dar nu și pentru cele încasate ramburs de curier — obligația de emitere a bonului fiscal ține de livrare/vânzare, nu de canalul prin care se face încasarea efectivă.
- Se consideră că factura emisă către client (mai ales dacă e persoană juridică) înlocuiește bonul fiscal pentru vânzările cu amănuntul către persoane fizice — cele două documente au regimuri distincte, iar unul nu substituie automat pe celălalt.

## Ce face iConta.eu

La data acestui ghid, iConta.eu importă și reconciliază datele de la aparatele de marcat electronice fiscale prin modulul dedicat (`core/amef_import.py`), dar nu emite el însuși bonuri fiscale — legătura dintre comenzile unui magazin online și obligația de emitere a bonului fiscal la livrare rămâne o verificare a firmei, în relație cu propriul sistem de casă de marcat.

[iConta.eu](/)
