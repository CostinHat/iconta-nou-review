---
title: "Poprirea electronică ANAF: din ce moment se consideră comunicată băncii?"
description: "Adresa de poprire încărcată pe platforma e-Popriri până la ora 24.00 se consideră comunicată băncii în prima zi bancară următoare zilei încărcării, la ora de începere a zilei bancare."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Poprirea electronică ANAF: din ce moment se consideră comunicată băncii?

Din prima zi bancară următoare zilei în care adresa de înființare a popririi a fost încărcată pe platforma e-Popriri, la ora de începere a zilei bancare. Regula e în procedura aprobată prin OPANAF 878/2022: sistemul e-Popriri încarcă adresele pentru fiecare bancă până la ora 24.00, iar ele se consideră comunicate abia în prima zi bancară de după încărcare.

Pentru firma debitoare, momentul contează pentru că o poprire „emisă" într-o zi nu produce efecte față de bancă în aceeași zi. Pentru contabil, regula explică de ce blocarea contului apare de regulă în ziua bancară următoare, nu la data din adresa de poprire.

## Temeiul legal

::: ghid-temei
„2.3. Sistemul informatic e-Popriri preia și prelucrează de la U.I.R. adresele de înființare a popririi asupra disponibilităților bănești și le încarcă pe platforma e-Popriri, pentru fiecare instituție de credit, până la ora 24.00. Acestea se consideră a fi comunicate în prima zi bancară următoare zilei încărcării acestora, la ora de începere a zilei bancare."
— Procedura aprobată prin OPANAF 878/2022, cap. II pct. 2.3 (sursă: [OPANAF nr. 878/2022 privind stabilirea mijloacelor electronice de transmitere la distanță a actelor de executare și a procedurii de comunicare a acestora (anexa-procedură, e-Popriri)](https://legislatie.just.ro/Public/DetaliiDocument/254993))

„l) platforma e-Popriri - spațiul privat de pe portalul A.N.A.F., pus la dispoziția instituțiilor de credit, prin intermediul căruia sunt comunicate actele de executare silită prin mijloace electronice de transmitere la distanță."
— Procedura aprobată prin OPANAF 878/2022, cap. I pct. 1.2 lit. l) (sursă: [OPANAF nr. 878/2022 privind stabilirea mijloacelor electronice de transmitere la distanță a actelor de executare și a procedurii de comunicare a acestora (anexa-procedură, e-Popriri)](https://legislatie.just.ro/Public/DetaliiDocument/254993))
:::

::: ghid-temei
„3.4. Din momentul transmiterii de către instituțiile de credit a mesajului cu informațiile privind suma ce poate fi plătită, acestea nu procedează la decontarea documentelor de plată primite, respectiv la debitarea conturilor debitorilor, și nu acceptă alte plăți din conturile acestora până la realizarea plății efective."
— Procedura aprobată prin OPANAF 878/2022, cap. III pct. 3.4 (sursă: [OPANAF nr. 878/2022 privind stabilirea mijloacelor electronice de transmitere la distanță a actelor de executare și a procedurii de comunicare a acestora (anexa-procedură, e-Popriri)](https://legislatie.just.ro/Public/DetaliiDocument/254993))
:::

Elementele regulii:

- **Canalul:** adresele de poprire se generează de organul fiscal, se procesează de Unitatea de Imprimare Rapidă și se încarcă de sistemul e-Popriri pe platforma din spațiul privat al băncilor pe portalul A.N.A.F. (cap. I pct. 1.3-1.4, cap. II pct. 2.1-2.3).
- **Ziua comunicării:** prima zi bancară următoare zilei încărcării. Încărcarea se face până la ora 24.00, deci tot ce s-a încărcat într-o zi intră în aceeași zi de comunicare.
- **Ora comunicării:** ora de începere a zilei bancare. Procedura nu fixează o oră unică și nici nu definește ziua bancară. Ora concretă ține de fiecare bancă.
- **Data și ora se înregistrează automat** în sistemul e-Popriri (cap. II pct. 2.5). Dacă banca nu înființează poprirea, de exemplu pentru că firma nu are cont deschis sau e în insolvență, transmite motivul înapoi.
- **După comunicare, banca răspunde cu sumele pe care le poate plăti.** Din momentul în care trimite acest mesaj, banca nu mai decontează plățile primite și nu mai acceptă alte plăți din conturile debitorului până la plata efectivă (cap. III pct. 3.4).
- **Comunicarea către bancă e altceva decât comunicarea către debitor.** Procedura stabilește momentul față de bancă. Momentul la care firma a luat cunoștință de executare, relevant pentru termenul de contestare, se apreciază separat.

::: ghid-exemplu
Sistemul e-Popriri încarcă o adresă de înființare a popririi pe contul SC Exemplu SRL marți, 3 martie 2026, la ora 16:00. Miercuri, 4 martie, e zi bancară obișnuită, iar banca firmei își începe ziua bancară la ora 09:00.

- Data comunicării către bancă: miercuri, 4 martie 2026. Ora comunicării: 09:00.
- O plată către un furnizor ordonată de firmă marți, 3 martie, la ora 17:00 a fost inițiată înaintea momentului în care poprirea se consideră comunicată băncii. Cum o tratează banca ține de regulile ei de procesare, pe care procedura nu le reglementează.
- După ce banca transmite mesajul cu sumele pe care le poate plăti, plățile ordonate ulterior de firmă nu mai sunt decontate până la plata către ANAF.
:::

## Ce se greșește în practică

- Se consideră că poprirea produce efecte față de bancă din ziua emiterii sau a încărcării, nu din prima zi bancară următoare.
- Se presupune o oră unică pentru toate băncile, deși ora de începere a zilei bancare diferă de la o bancă la alta.
- Data comunicării către bancă se confundă cu data la care firma a aflat de executare, deși sunt momente distincte.
- Firma ordonă plăți în ultimul moment ca să „scape" sume de poprire. Pe lângă riscul juridic, Codul de procedură fiscală (Legea 207/2015) prevede răspunderea solidară a reprezentantului legal care declară cu rea-credință băncii că nu deține alte disponibilități (art. 25 alin. (1) lit. c)).

## Ce face iConta.eu

iConta.eu nu primește actele de executare din sistemul ANAF pentru bănci și nu citește automat mesajele din SPV ale firmei, inclusiv somațiile. Contabilul le urmărește direct. Reținerile din poprire apar în extrasul de cont importat în aplicație (XLS, CSV sau MT940), cu data și suma fiecărei operațiuni. Contabilul alocă reținerile pe obligațiile stinse, iar sistemul învață din corecții.

[iConta.eu](/)
