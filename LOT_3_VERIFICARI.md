# LOTUL 3 — verificări pentru 30 de pași

Fiecare verificare spune **ce trebuie să fie adevărat DUPĂ pas**, nu că pasul a mers.

Unde nu pot scrie o verificare fără să știu ceva ce nu am, o spun.

---

## Ce se vede din garda afișată, înainte de pași

Cele trei lucruri pe care le-ai numit sunt mai grave împreună decât separat, iar toate trei sunt în același lanț:

**`plan-conturi` scrie fără rol** nomenclatorul pe care tocmai l-am făcut obligatoriu. Cine poate adăuga un cont poate face să treacă orice refuz al lui `cont_valid`.

**`facturi/{id}/contabilizeaza` scrie evidență fără rol.**

**Cele patru rute de jurnal — creare, editare, ștergere, validare — sunt toate fără rol, inclusiv validarea.** Validarea e ce transformă o ciornă în evidență.

Deci: cineva fără niciun rol poate adăuga un cont, scrie o notă cu el, și o valida. Lanțul complet, fără nicio verificare de rol pe niciun pas.

Aia nu e o poziție din R55. E R55 întreagă, într-un singur traseu.

---

## T29 — Regimuri speciale de TVA (4)

**Verificări comune celor patru:**

- nota respectă partida dublă: total debit = total credit
- conturile există în planul firmei (acum se refuză, prin `cont_valid`)
- perioada nu e închisă
- baza și TVA-ul din notă coincid cu ce va apărea în declarație, sau divergența se arată cu ambele cifre

### `POST /tenants/{tenant_id}/achizitie-neinregistrat`
*cere_rol · rol:admin_firma · scrie inregistrari, inregistrari_linii*

- operațiunea apare în D394 ca tip N, cu `tip_partener=2` — verificat pe declarația generată, nu pe intenția din cod
- persoana fizică nu are cod fiscal, deci nu se cere; dar se cere o identificare, altfel operațiunea n-are partener
- TVA-ul nu se deduce — achiziția de la neînregistrat nu poartă TVA deductibilă
- dacă atinge stocul prin modul, mișcarea de stoc are aceeași dată cu nota

### `POST /tenants/{tenant_id}/import-extracomunitar`
*cere_cabinet · FĂRĂ ROL · scrie inregistrari, inregistrari_linii*

- baza de TVA la import = valoarea vamală + taxa vamală + accize + accesorii până la primul loc de destinație. Verifică pe cifre, nu pe formulă
- cu certificat de amânare, TVA-ul nu se plătește în vamă: se înregistrează simultan colectat și deductibil, iar cele două se anulează în decont
- fără certificat, TVA-ul plătit în vamă e deductibil pe baza declarației vamale, nu a facturii furnizorului
- cota aplicată e cea de la data operațiunii, cerută din registru
- **fără rol, deși scrie evidență** — R55

### `POST /tenants/{tenant_id}/export-extracomunitar`
*cere_cabinet · FĂRĂ ROL · scrie inregistrari, inregistrari_linii*

- exportul e scutit cu drept de deducere; nu se colectează TVA
- scutirea cere **dovada exportului** — declarația vamală de export. Fără ea, operațiunea nu e scutită, iar ruta primește `dovada_export` ca text liber
- verifică ce se întâmplă când `dovada_export` lipsește sau e o frază: se refuză, sau se scutește pe încredere?
- țara clientului e din afara UE — o țară din UE face operațiunea livrare intracomunitară, nu export
- **fără rol, deși scrie evidență** — R55

### `POST /tenants/{tenant_id}/achizitie-necorporala`
*cere_rol · rol:admin_firma · scrie inregistrari, inregistrari_linii, mijloace_fixe*

- durata normală de funcționare vine din catalog pentru tipul respectiv; `dnf_luni` din corp nu o poate coborî sub minim
- valoarea sub pragul de imobilizare nu produce mijloc fix — e cheltuială. Verifică pragul la data operațiunii
- rândul din `mijloace_fixe` și nota din `inregistrari` au aceeași valoare de intrare
- amortizarea începe din luna următoare punerii în funcțiune, nu din luna achiziției

---

## T02 — Factura emisă (13)

### `PUT /tenants/{tenant_id}/facturi/numerotare`
*cere_rol · rol:admin_firma*

- schimbarea seriei sau a numărului de start **nu poate produce un număr deja folosit** — se refuză, cu numărul care ar fi intrat în conflict
- numerotarea nu se poate reduce sub ultimul număr emis
- schimbarea se consemnează: cine, când, de la ce la ce. E P15 — seria nu are goluri și nu se reia

### `PUT /tenants/{tenant_id}/facturi/{factura_id}/notificare`
*cere_rol · rol:admin_firma*

- oprirea notificărilor pe o factură nu schimbă scadența și nu afectează calculul de întârziere
- starea se consemnează cu autorul — e o decizie despre relația cu clientul

### `POST /tenants/{tenant_id}/facturi/{factura_id}/email`
*cere_rol · rol:admin_firma · artefact predat*

- trimiterea e un **eveniment de predare**: cui, când, la ce adresă, cu ce atașament
- se trimite exemplarul emis, cu amprenta lui — nu o regenerare la momentul trimiterii
- o a doua trimitere e un al doilea eveniment, nu suprascrie primul
- eșecul trimiterii e o stare, nu o eroare pierdută: factura rămâne netrimisă și se vede

### `POST /tenants/{tenant_id}/facturi-recurente`
### `PUT /tenants/{tenant_id}/facturi-recurente/{sid}`
### `DELETE /tenants/{tenant_id}/facturi-recurente/{sid}`
*cere_context · FĂRĂ ROL*

- șablonul recurent nu emite nimic singur — emiterea trece prin `facturi/emite`, cu regulile ei
- modificarea unui șablon nu atinge facturile deja emise din el
- ștergerea nu atinge facturile emise; dacă șablonul are facturi, se spune câte
- data următoarei emiteri se recalculează la modificare, iar dacă ar cădea în trecut se refuză

### `POST /tenants/{tenant_id}/facturi/emite`
*cere_rol · rol:admin_firma · artefact predat*

- factura primește **următorul număr din serie**, fără goluri; două emiteri simultane nu produc același număr
- exemplarul se îngheață cu amprenta; o regenerare ulterioară produce alt exemplar, nu îl rescrie pe primul
- nota contabilă generată respectă partida dublă, iar conturile vin din mapare, nu din literali
- mișcările de stoc au aceeași dată cu factura
- factura fără cod fiscal de partener se refuză — nu intră în D394 și nu se corelează în VIES

### `POST /tenants/{tenant_id}/facturi/{factura_id}/storno`
*cere_rol · rol:admin_firma*

- stornarea e un **document nou**, care o referă pe cea stornată. Factura originală rămâne, cu numărul ei
- suma stornată nu depășește suma facturii
- nota de stornare inversează exact nota originală — nu o șterge
- o factură deja stornată nu se stornează a doua oară

### `POST /tenants/{tenant_id}/facturi`
*cere_rol · rol:admin_firma*

- **nu pot scrie verificarea fără să știu ce o deosebește de `/facturi/emite`.** Creează ciornă? Emite direct? De completat din cod
- dacă emite, se aplică verificările de la `emite`

### `DELETE /tenants/{tenant_id}/facturi/{factura_id}`
*cere_rol · rol:admin_firma*

- **o factură emisă nu se șterge.** Se stornează. Ștergerea ar produce un gol în serie
- o factură cu notă contabilă nu se șterge — se rupe lanțul P14
- dacă ștergerea e permisă pe ciorne, verifică ce o deosebește de o factură emisă; iar dacă nu există distincția, aia e constatarea

### `POST /api/v1/firme/{tenant_id}/facturi`
*cere_api_key · FĂRĂ ROL*

- ruta cu cheie de API aplică **aceleași reguli** ca ruta din interfață: numerotare, cod fiscal obligatoriu, notă cu conturi valide
- o cheie de API nu are rol, deci nu poate face ce cere admin_firma pe ruta echivalentă — verifică dacă asta e adevărat sau dacă cheia ocolește restricția
- **dacă ocolește: e prag 1.** Un integrator cu cheie ar putea emite facturi pe care un asistent nu le poate emite

### `POST /tenants/{tenant_id}/facturi/{factura_id}/transforma`
*cere_rol · rol:admin_firma · scrie facturi (UPDATE)*

- proforma sau avizul devine factură fiscală cu **numerotare nouă**, din seria de facturi, nu cu numărul proformei
- documentul original rămâne, cu starea „transformat" și legătura către factura rezultată
- nota contabilă se generează la transformare, nu la emiterea proformei — proforma nu e document contabil

### `POST /tenants/{tenant_id}/facturi/{factura_id}/contabilizeaza`
*cere_cabinet · FĂRĂ ROL · scrie inregistrari, inregistrari_linii*

- nota produsă e **ciornă**, nu evidență validată — descrierea o spune, verifică structural
- propunerea de conturi vine din maparea corectată; nu se ghicește din denumire
- ciorna poartă legătura către factura din care a ieșit
- o factură contabilizată de două ori nu produce două note
- **fără rol, deși scrie în `inregistrari`** — R55, iar aici e cea mai vizibilă instanță

---

## T03 — Statul de plată (5)

### `POST /tenants/{tenant_id}/salarii-contare/propunere`
*cere_cabinet · FĂRĂ ROL · calcul*

- propunerea arată **ambele cifre** la fiecare divergență față de D112 — nu doar că există una
- nu scrie nimic; verificat structural
- dacă statul de plată nu e emis pentru luna cerută, se spune, nu se calculează din recalcul

### `POST /tenants/{tenant_id}/salarii-contare`
*cere_cabinet · FĂRĂ ROL · scrie inregistrari, inregistrari_linii*

- nota e ciornă, iar totalurile coincid cu propunerea văzută înainte
- divergența față de D112, dacă a existat la propunere, rămâne consemnată pe notă — nu se stinge prin salvare
- o a doua contare pe aceeași lună nu produce a doua notă
- **fără rol** — R55

### `POST /tenants/{tenant_id}/stat-plata/emite`
*cere_rol · rol:admin_firma · drept:poate_valida*

- statul se îngheață cu amprentă, exemplar numerotat, autor, moment
- cifrele emise nu se mai recalculează la citire; un recalcul care diferă produce contradicție vizibilă, nu rescriere
- emiterea e idempotentă: a doua apăsare produce **al doilea exemplar**, nu suprascrie primul
- pontajul trebuie confirmat; fără el, tichetele nu se acordă, iar statul o spune

### `POST /tenants/{tenant_id}/stat-plata/corectie`
*cere_cabinet · FĂRĂ ROL · drept:poate_valida*

- corecția e **al doilea exemplar**, cu referință la primul. Primul rămâne
- diferența față de exemplarul corectat e vizibilă, pe fiecare cifră schimbată
- corecția nu poate atinge o lună închisă fără redeschidere consemnată

### `POST /tenants/{tenant_id}/stat-plata/motiv`
*cere_cabinet · FĂRĂ ROL · drept:poate_valida*

- motivul marchează contradicția ca **asumată**, nu o stinge — rândul rămâne în listă, cu motivul, cine și când
- un motiv gol se refuză

---

## T04 — Concediul medical (3)

### `POST /tenants/{tenant_id}/salariati/{salariat_id}/concedii`
*cere_rol · rol:admin_firma,angajat*

- codul de indemnizație e din nomenclatorul oficial; unul din afară se refuză
- pentru codurile care cer CNP-ul persoanei îngrijite — 09, 17, 91, 92 — câmpul e obligatoriu la introducere, nu la generarea D112
- un certificat „în continuare" poartă seria, numărul și data celui inițial; fără ele se refuză
- perioada nu se suprapune cu alt certificat al aceluiași salariat
- stagiul de asigurare e verificat, sau codul e dintre cele exceptate — altfel se semnalează
- durata cumulată pe an nu depășește plafoanele: 183 de zile, 45 pentru codul 09, 45 pentru codul 17

### `DELETE /tenants/{tenant_id}/salariati/{salariat_id}/concedii/{cm_id}`
*cere_rol · rol:admin_firma,angajat*

- **un certificat care a intrat într-un stat de plată emis nu se șterge** — se corectează prin exemplar nou
- ștergerea recalculează episodul: dacă certificatul șters era inițial, procentul celorlalte din episod se schimbă
- ștergerea unui certificat dintr-o lună declarată în D112 produce contradicție vizibilă

### `POST /tenants/{tenant_id}/calcul-cm`
*cere_cabinet · FĂRĂ ROL · calcul*

- media zilnică se calculează din veniturile a 6 luni, **din sursă**, nu dintr-un tabel intermediar
- lunile lipsă din bază se numesc, cu numărul lor — nu produc tăcut o medie mai mică
- procentul se determină pe **episod cumulat**, nu pe certificat
- diminuarea cu o zi lucrătoare se aplică o dată pe episod, cu excepția codului 51
- plafonul de 12 salarii minime se verifică la media lunară
- regimul aplicabil e cel de la data certificatului **inițial** al episodului, nu de la data calculului

---

## T05 — Nota contabilă (5)

### `POST /tenants/{tenant_id}/plan-conturi`
*cere_context · FĂRĂ ROL · scrie plan_conturi*

- contul adăugat respectă structura planului general: clasa, grupa, sintetic de gradul I și II
- un cont care nu există în planul general de conturi se refuză, sau se marchează ca analitic al unui sintetic existent
- un cont duplicat se refuză
- **fără rol, iar aceasta e ruta care poate anula refuzul lui `cont_valid`.** Cine adaugă un cont face să treacă orice notă cu el — R55, prima instanță de rezolvat

### `POST /tenants/{tenant_id}/jurnal`
*cere_cabinet · FĂRĂ ROL*

- nota respectă partida dublă la creare, nu la validare
- conturile există în plan — acum se refuză
- data notei e într-o perioadă deschisă
- documentul justificativ e cerut: felul, numărul, data. Fără el, nota nu se poate desface — P14
- **fără rol** — R55

### `PUT /tenants/{tenant_id}/jurnal/{nota_id}`
*cere_cabinet · FĂRĂ ROL*

- o notă **validată** nu se editează — se stornează
- editarea unei ciorne păstrează partida dublă
- editarea nu poate muta nota într-o perioadă închisă
- **fără rol** — R55

### `DELETE /tenants/{tenant_id}/jurnal/{nota_id}`
*cere_cabinet · FĂRĂ ROL*

- o notă validată nu se șterge — se stornează. Ștergerea ar rupe lanțul către documentul justificativ
- ștergerea unei ciorne nu atinge documentul din care a ieșit
- **fără rol** — R55

### `POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza`
*cere_cabinet · FĂRĂ ROL*

- validarea verifică **înainte** de a marca: partidă dublă, conturi existente, perioadă deschisă, document justificativ prezent
- nota validată intră în evidență; din acel moment nu se mai editează și nu se șterge
- cine a validat se consemnează
- **fără rol, iar aceasta e ruta care transformă o ciornă în evidență.** E instanța cea mai gravă din cele patru — R55

---

## Ce am observat scriind lotul

**Lanțul complet fără rol:** `plan-conturi` → `jurnal` → `jurnal/{id}/valideaza`. Cineva fără niciun rol poate adăuga un cont, scrie o notă cu el, și o valida ca evidență.

Refuzul pe cont inexistent, construit ieri, nu apără nimic dacă oricine poate adăuga contul.

**Două rute cer completare din cod:** `POST /facturi` (ce o deosebește de `emite`?) și verificarea dacă `api/v1/firme/{id}/facturi` ocolește restricția de rol.

**A doua e prag 1 dacă ocolește:** un integrator cu cheie de API ar putea emite facturi pe care un asistent nu le poate emite din interfață.
