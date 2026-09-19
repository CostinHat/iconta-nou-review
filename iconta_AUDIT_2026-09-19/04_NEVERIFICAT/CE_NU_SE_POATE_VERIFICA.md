# CE NU SE POATE VERIFICA DE AICI

*Scris ca secțiune proprie, nu topit în altele. O limită nescrisă devine peste o lună o acoperire
presupusă.*

---

## 1. Lucruri pe care le-am găsit, dar care nu se pot verifica **de aici**

Nu sunt scăpări; sunt limite ale poziției mele.

| ce | de ce nu se poate verifica de aici |
|---|---|
| dacă **legea** spune același lucru ca documentul de structură ANAF | cele trei reguli D402 recuperate în lucrarea 4 (`totalPlata_A`, `anul(Data_I)`, `Suma_venit`) sunt confruntate cu `structuraXML_D402_2022.pdf`, **nu** cu OMFP 2727/2015. Dacă norma spune altceva decât documentul, nu se vede din cod |
| dacă **valorile fiscale** sunt încă în vigoare azi | `INVENTAR_A.md` poartă data verificării la sursă pentru fiecare. Unele sunt din 31.07.2026; nimic din cod nu știe ce s-a schimbat după |
| dacă aplicația se comportă la fel **în producție reală** | toate firmele din bază sunt de test; nicio depunere reală la ANAF (R40) |
| dacă instrumentele noastre **ratează** ceva ce nu și-au declarat | fiecare își scrie orbirea în propriul docstring (`04_NEVERIFICAT/NEVERIFICAT.txt`, secțiunea D) — dar *o orbire nedeclarată nu se poate enumera prin construcție* |

---

## 2. Acoperirea de browser — lipsa principală de la punctul (d), scrisă ca atare

**Cea mai mare zonă neacoperită a aplicației e verificarea prin browser, iar ce există e în mare
măsură disjunct de ce urmărește backlogul.** Cifrele, măsurate (`GARZI.md`, 01.09.2026), și
rederivabile cu `04_NEVERIFICAT/deriva_neverificatul.py`, secțiunea F:

- **495 de secțiuni** de checklist de browser, în nouă fișiere;
- **90%** din ce atinge checklistul **nu apare în backlog** (228 din 252 de obiecte);
- **89%** din ce atinge backlogul **n-are nicio verificare de browser** (200 din 224);
- **niciunul** dintre cele nouă fișiere nu e rulat de poartă — sunt **liste scrise, nu probe**.

Ultimul rând e cel care contează cel mai mult pentru un auditor: chiar și acolo unde checklistul
**atinge** un obiect, atingerea e o propoziție scrisă de om, nu o probă pe care o rulează cineva la
fiecare commit. *Nu există Playwright în poartă.*

**Cum s-a ajuns la formularea asta.** Cerința inițială a pachetului numea, la punctul (d),
*„checklistul de browser de la poziția 13 încolo"*. Am raportat că **n-am găsit** un checklist cu
poziții numerotate unde 1–12 ar fi făcute și 13+ nu, și am arătat cele șapte locuri în care am
căutat, în loc să livrez o listă apropiată ca și cum ar fi fost ea. **Costin a corectat formularea
pe 17.09.2026**: artefactul n-are poziții numerotate, iar lipsa se numește exact cum e scrisă mai
sus. *Rândul ăsta rămâne fiindcă istoria întrebării e parte din răspuns: se vede că lipsa n-a fost
rotunjită la ceva convenabil nici când nu se potrivea cu cererea.*
