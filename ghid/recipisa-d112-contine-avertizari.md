---
title: Ce faci dacă recipisa D112 conține avertizări?
description: O D112 cu atenționări (ATT) este preluată. Numai erorile fatale (ERR) blochează preluarea, potrivit structurii XML publicate de ANAF pentru formularul aprobat prin OPANAF 605/2026. Verifici fiecare mesaj, iar dacă avertizarea arată o eroare reală corectezi prin D112 rectificativă (Codul de procedură fiscală art. 105 alin. (1) și (3)).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce faci dacă recipisa D112 conține avertizări?

O avertizare nu înseamnă că declarația a fost respinsă. În documentația tehnică a D112, ANAF distinge două categorii de mesaje. Potrivit structurii D112 (versiunea aplicabilă din luna de raportare 07/2026, conform ordinului comun nr. 605/95/928/2.314/2026), „Declaratiile cu erori fatale (ERR) nu se preiau", iar „Declaratiile cu atentionari (ATT) se preiau cu specificarea mesajului de atentionare aferent".

Declarația cu atenționări este deci depusă. Mesajul îți semnalează însă o neconcordanță care trebuie verificată.

### ERR și ATT: diferența

- **ERR (eroare fatală).** Declarația nu este preluată și se consideră nedepusă. Trebuie corectată și retransmisă ca declarație inițială.
- **ATT (atenționare).** Declarația este preluată, iar recipisa conține textul atenționării. Validatorul a găsit o valoare care diferă de regula de calcul sau de format, dar nu a blocat depunerea.

### Exemple de atenționări din structura D112

- Adresă de e-mail invalidă la sediul social sau la domiciliul fiscal: „ATT E-mail sediu social eronat". Datele declarate nu sunt afectate, dar merită actualizată adresa.
- Baza de calcul CAM: „ATT – C4_baza difera de suma calculata". Validatorul compară baza CAM declarată cu suma bazelor pe asigurați. O diferență indică de regulă o eroare de calcul sau de completare.
- Valoarea CAM: „ATT – C4_ct difera de suma calculata". Structura calculează CAM-ul cu cota de 2,25%.
- Indicatorii CAM la nivel de asigurat. O bază CAM declarată deși indicatorul CAM este „false" generează o atenționare.

### Ce faci concret

1. Citește mesajul exact din recipisă și identifică secțiunea și câmpul la care se referă.
2. Compară valoarea din declarație cu statul de plată și cu regula din structura D112.
3. Dacă atenționarea este doar formală (de exemplu, e-mailul) și sumele sunt corecte, nu este nevoie de rectificativă. Notează verificarea în dosarul lunii.
4. Dacă atenționarea arată o sumă greșită, depune o D112 rectificativă. Codul de procedură fiscală, art. 105 alin. (1), permite corectarea declarației de impunere în termenul de prescripție, iar alin. (3) prevede că aceasta se face „prin depunerea unei declarații rectificative".
5. Ține cont de regulile tehnice ale rectificativei. Potrivit structurii D112, rectificativa „nu se poate prelua decat daca exista o declaratie initiala", iar în aceeași zi nu se primesc o declarație inițială și una rectificativă pentru aceeași perioadă.

### Exemplu

Pentru august 2026, recipisa D112 conține mesajul „C4_baza difera de suma calculata". Declarația are C4_baza = 50.000 lei, dar suma bazelor CAM pe asigurați este 52.000 lei. Diferența provine dintr-un salariat omis la totalizare. CAM-ul datorat corect este 2,25% × 52.000 = 1.170 lei, nu 1.125 lei. Depui a doua zi o rectificativă cu baza de 52.000 lei și CAM de 1.170 lei și plătești diferența de 45 de lei.

### De reținut

- ATT înseamnă declarație preluată cu atenționare. ERR înseamnă declarație nepreluată.
- Fiecare atenționare se verifică. Cele care privesc sume ascund de regulă o eroare reală.
- Corectarea sumelor se face prin D112 rectificativă (Codul de procedură fiscală art. 105 alin. (3)), numai după ce declarația inițială a fost preluată.
- Păstrează recipisa și nota de verificare pentru fiecare lună cu atenționări.
