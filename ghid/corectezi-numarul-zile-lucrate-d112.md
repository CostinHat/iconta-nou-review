---
title: Cum corectezi numărul de zile lucrate în D112?
description: Zilele lucrate greșite în D112 se corectează prin declarație rectificativă completată integral, conform instrucțiunilor aprobate prin OPANAF 605/2026. Contează pentru că numărul de zile intră în calculul CAS minim de la part-time (Codul fiscal art. 146 alin. (5^6)).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectezi numărul de zile lucrate în D112?

Depui o declarație rectificativă pentru luna greșită. Nu poți declara diferența în luna curentă. Instrucțiunile D112 aprobate prin OPANAF 605/2026 (pct. 2.2) spun că rectificativa se folosește și pentru „modificarea unor date pe baza cărora se determină stagiile de cotizare”, iar zilele lucrate sunt exact o astfel de dată.

### Unde apar zilele lucrate în D112

În structura D112 publicată de ANAF, pentru fiecare asigurat, secțiunea B1 conține câmpurile legate de timpul de lucru:
- B1_3: tipul contractului (N pentru normă întreagă, P1–P7 pentru timp parțial);
- B1_4: orele din norma zilnică (6, 7 sau 8);
- B1_6: orele lucrate efectiv în lună;
- B1_7: orele suspendate sau libere;
- B1_15: totalul zilelor lucrate.

Validatorul verifică legăturile dintre aceste câmpuri. B1_15 nu poate depăși numărul zilelor lucrătoare din lună (NZL). La normă întreagă, B1_6 nu poate depăși NZL × B1_4. Dacă modifici zilele, trebuie să modifici și orele, altfel declarația dă eroare.

### De ce contează zilele: CAS minim la part-time

Codul fiscal art. 146 alin. (5^6) prevede că CAS-ul unui salariat nu poate fi mai mic decât cel calculat la salariul minim, „corespunzător numărului zilelor lucrătoare din lună în care contractul a fost activ”. Diferența o suportă angajatorul (alin. (5^9)). Pentru iulie–decembrie 2026, salariul minim este de 4.325 lei (HG 146/2026). Pentru acest calcul, suma se diminuează cu 200 lei (OUG 89/2025, art. III alin. (5) lit. b)). Structura D112 calculează suma-limită astfel: (4.325 − 200) / NZL × (zile lucrate + zile de concediu medical).

### Exemplu

Un salariat cu contract P4 (4 ore pe zi) este angajat pe 15 septembrie 2026. Septembrie are 22 de zile lucrătoare, dintre care 12 cad după data angajării. Din greșeală, în D112 s-au declarat 22 de zile lucrate și 88 de ore.
- Baza minimă declarată greșit: 4.125 / 22 × 22 = 4.125 lei, deci CAS minim de 1.031,25 lei.
- Baza minimă corectă: 4.125 / 22 × 12 = 2.250 lei, deci CAS minim de 562,50 lei (cota de 25%, Codul fiscal art. 138 lit. a)).

Diferența de CAS suportată de angajator scade. Stagiul de cotizare al salariatului se corectează și el.

### Pașii practici

1. Refaci statul de plată al lunii după pontajul corect: zilele lucrate, orele lucrate și orele suspendate.
2. Completezi D112 pe același model ca declarația inițială și bifezi caseta „Declarație rectificativă” (pct. 2.3 din instrucțiuni).
3. Completezi declarația integral, „inclusiv cele care nu diferă față de declarația inițială” (pct. 2.4), deci pentru toți salariații, nu doar pentru cel corectat.
4. Verifici în validator corelațiile dintre B1_15, B1_6 și B1_7.
5. Compari totalurile din rectificativă cu cele din declarația inițială. Dacă rezultă contribuții mai mari, plătești diferența.

Dacă greșeala a fost constatată de organul fiscal printr-o notificare de conformare, bifezi caseta dedicată acestei situații (pct. 2.4 lit. c)).

### De reținut
- Corectarea se face doar prin rectificativă pe luna afectată, completată integral.
- Zilele (B1_15) și orele (B1_6, B1_7) se modifică împreună, pentru că validatorul le compară.
- La part-time, numărul de zile lucrate schimbă direct CAS-ul minim suportat de angajator.
