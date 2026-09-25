---
title: "Veniturile din producția de imobilizări intră în plafonul micro?"
description: "De ce veniturile din producția de imobilizări corporale și necorporale nu se cumulează nici la plafonul de 100.000 euro, nici la baza impozitului micro."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Veniturile din producția de imobilizări intră în plafonul micro?

Nu. Veniturile din producția de imobilizări corporale și necorporale (contul 722, respectiv 721) sunt tratate diferit de restul veniturilor unei microîntreprinderi, atât la verificarea plafonului de 100.000 euro, cât și la calculul propriu-zis al impozitului de 1%.

## Temeiul legal

::: ghid-temei
„(1^1) În aplicarea prevederilor alin. (1) lit. c) limita privind veniturile realizate se verifică luând în calcul veniturile realizate de persoana juridică română [...], iar veniturile care se iau în calcul sunt cele care constituie cifra de afaceri definită potrivit reglementărilor contabile aplicabile [...]."
— Legea 227/2015, art. 47 alin. (1^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie veniturile din orice sursă, din care se scad: [...] c) veniturile din producția de imobilizări corporale și necorporale."
— Legea 227/2015, art. 53 alin. (1) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„GRUPA 70 «CIFRA DE AFACERI NETĂ» [...]: 701, 702, 703, 704, 705, 706, 707, 708, 709. [...] 72. «Venituri din producția de imobilizări» 721. Venituri din producția de imobilizări necorporale 722. Venituri din producția de imobilizări corporale."
— OMFP 1802/2014 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Din combinarea celor trei texte rezultă dublu tratament favorabil:

- **La plafonul de 100.000 euro** (art. 47) — se verifică doar „cifra de afaceri" definită de reglementările contabile, adică grupa de conturi 70 (701-709). Grupa 72 „Venituri din producția de imobilizări" e o grupă separată, care nu intră în cifra de afaceri netă — deci nu se cumulează la plafon.
- **La baza impozitului micro de 1%** (art. 53) — chiar dacă firma e microîntreprindere, veniturile din producția de imobilizări corporale și necorporale se scad explicit din baza impozabilă, deci nu se impozitează.

## Ce se greșește în practică

- Se adună toate veniturile din balanță (inclusiv contul 722) la verificarea plafonului de 100.000 euro, deși doar cifra de afaceri (grupa 70) contează.
- Se impozitează cu 1% și veniturile din producția de imobilizări, deși art. 53 alin. (1) lit. c) le scade explicit din baza de calcul.
- Se confundă „venituri din producția de imobilizări" (cont 722, mijloc fix construit în regie proprie) cu venitul din vânzarea unui mijloc fix (cont 7583), care are alt regim.

## Ce face iConta.eu

iConta.eu calculează baza impozitului micro pornind de la veniturile din orice sursă înregistrate în conturile de clasa 7, dar strict din grupele 70x, 75x și 76x (cu scăderea reducerilor comerciale 709) — motorul de calcul (A8) a fost corectat explicit pentru a nu limita baza doar la contul 70x. Cum interogarea nu însumează deloc grupa 72x, veniturile din producția de imobilizări (721/722) sunt deja excluse automat din baza impozitului micro, chiar dacă în cod nu există o linie dedicată explicit acestei excluderi din art. 53 alin. (1) lit. c) — comportamentul efectiv e totuși conform legii. La data acestui ghid, aplicația nu are însă un modul separat care să verifice plafonul de 100.000 euro pe baza strictă a cifrei de afaceri (grupa 70, fără 75x/76x, conform art. 47 alin. 1^1) — această verificare rămâne manuală, a contabilului, la închiderea perioadei.

[iConta.eu](/)
