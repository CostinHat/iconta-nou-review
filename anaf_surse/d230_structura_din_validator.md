# D230 — structura recuperata din validatorul oficial ANAF (D230Validator.jar)

Formularul public ANAF linkeaza un XSD STALE (`d230_28012020.xsd`, namespace v1); validatorul oficial cere
namespace v5. Structura reala nu se inventeaza - se CITESTE din bytecode-ul validatorului (numele campurilor
pe clase) si se PROBEAZA camp cu camp pe DUKIntegrator (arbitrul peste anexe). Nu se decompileaza logica, nu
se redistribuie cod ANAF - se citesc numele si mesajele.

## Versiuni si maparea la namespace (citit din d230validator/vNNN/ValidatorImpl.class)
| pachet clasa | namespace declaratie |
|---|---|
| v100 | v1 |
| v101 | v2 |
| v102 | v3 |
| v103 | v3 |
| v104 | v4 |
| v0   | v4 |
| **v1** | **v5** |

**In vigoare = v5 (pachet d230validator/v1).** Determinat pe validator: un XML pentru anul venitului curent
(an=2025) → validatorul cere `namespace='mfp:anaf:dgti:d230:declaratie:v5'`. (v104/namespace v4 e versiunea
anterioara; ea are bifa_sal/bifa_pens/sectiune, scoase in v5.)

## Declaratie230 v5 — atribute (citite din bytecode)
luna, an, nume_c, initiala_c, prenume_c, cif_c (CNP), adresa_c, telefon_c, fax_c, email_c,
den_i, cif_i, adresa_i, telefon_i, fax_i, email_i (imputernicit), totalPlata_A.
- `e_sectiune1`, `e_sectiune2` = campuri INTERNE ale validatorului, NU atribute XML (respinse ca necunoscute).
- `tip` NU exista in v5.

## Bursa_entit v5 — atribute (element copil, 0..n)
bifa_bursa, bifa_entitate, den_entitate, cif_entitate, cont_entitate (IBAN), contract_bursa, doc_plata_bursa,
suma_bursa, suma_entitate, cota, procent, valabilitate_distribuire, acord.
- NU are bifa_sal/bifa_pens/sectiune/cod_sectiune (acelea sunt in v4/pachet v104).

## Reguli citite/probate pe validator
- **R_optiune**: `bifa_entitate=1 => valabilitate_distribuire<>null` (OBLIGATORIU). Probat: fara el → eroare.
- **R_procent**: `procent <= 3.5`. Probat: procent=35 → respins; procent=3.5/2 → valid. Format ZECIMAL (3.5, nu 35).
- **R31**: `totalPlata_A = suma de control`. Probat: fara suma_entitate → calc=0 → totalPlata_A="0" (ANAF determina cuantumul).
- perioada: luna=12 (fix, "perioada de raportare"); an = anul venitului (anul curent - 1).
- CNP (cif_c): 13 cifre + cifra de control (respins la checksum invalid).
- `acord` = OPTIONAL (fara el → tot valid). Probat.

## Ce NU s-a putut determina (nu se ghiceste - se raporteaza ca lipsa)
- **semantica `acord`** (consimtamant?) si valorile valide dincolo de "acceptat de validator" - din act, nu din
  validator. → camp NEPOPULAT deliberat in core/d230.py.
- **`cota`** vs `procent` (ambele exista pe Bursa_entit) - rolul exact al `cota` la redirectionarea catre entitate
  nu reiese din validator (procent e cel legat de R_procent). → NEPOPULAT.
- cazurile bursa privata (bifa_bursa) si imputernicit (tip/den_i) - neimplementate (limitare documentata).

## Sursa autoritara
`/home/costin/duk/dist/lib/D230Validator.jar` (in afara repo, instalat din pachetul oficial ANAF
D230_31012025.zip). Probele: `java -jar DUKIntegrator.jar -v D230 <xml>`.
