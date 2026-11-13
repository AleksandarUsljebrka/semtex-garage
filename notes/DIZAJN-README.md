# Handoff: Semtex Garage - početna stranica

## Overview
Jednostranični sajt (početna) za Semtex Garage, auto servis za reparaciju farova u Novom Sadu. Cilj: posetilac zove ili piše (poziv, Viber, WhatsApp, Instagram). Bez cena na sajtu. Jezik: srpski, latinica.

## About the Design Files
`Semtex Garage.dc.html` je **dizajn referenca napravljena u HTML-u** (prototip sa izgledom i ponašanjem), ne produkcioni kod. Zadatak je da se dizajn **ponovo napravi u okruženju ciljnog projekta** (React, Next.js, Astro, čist HTML/CSS...) njegovim obrascima i bibliotekama. Ako okruženje ne postoji, izabrati najprikladniji framework (preporuka: Astro ili Next.js, sajt je statičan).
Fajl se otvara direktno u browseru (`support.js` je runtime tog formata, ne treba ga prenositi). Sav stil je inline; pri implementaciji prebaciti u CSS/tokene.

## Fidelity
**High-fidelity.** Boje, tipografija, razmaci i animacije su konačni. Napraviti ih piksel-tačno.

## Screens / Views
Jedna stranica, sekcije redom. Širina sadržaja max 1100px, bočni padding 24px, vertikalni padding sekcija `clamp(64px, 9vw, 112px)`.

### 1. Zaglavlje (sticky, z-index 10)
- Pozadina `#111`, donja linija `#2a2a2a`. Visina oko 73px (hero koristi `100vh - 73px`).
- Levo: logo `img/logo.jpg` 48x48 okrugao + "Semtex Garage" (Barlow Condensed 700, 24px, uppercase, letter-spacing .04em, bela).
- Desno: linkovi Usluge, Radovi, Recenzije, Kontakt (15px, `#d8d8d8`, hover bela) + dugme "Pozovi" (`#d62a1e`, bela, padding 10x18, radius 6px, hover `#b01f15`).

### 2. Hero
- Pozadina `#060606`, overflow hidden. Visina min `min(100vh - 73px, 820px)`.
- Tekst levo (max-width 560px): eyebrow "Reparacija farova, Novi Sad" (14px, uppercase, letter-spacing .14em, `#ff6a5e`, 600); h1 "Da tvoj auto progleda." (Barlow Condensed 700, `clamp(52px, 8vw, 96px)`, line-height .95, uppercase); opis 18px/1.55 `#e2e2e2`, max 46ch; dugmad Pozovi (puna crvena), Viber, WhatsApp, Instagram (outline 1px bela, hover bela pozadina taman tekst). Dugmad: radius 6px, 16px/600.
- Pozadina desno: automobil (Audi u radionici), 3 sličice u istom kadru: `hero-1.png` (farovi ugašeni), `hero-2.png` (pale se), `hero-3b.png` (upaljeni). 820x461, poravnate u isti kadar (nisu originali: 02 i 03 su skalirani i spojeni sa 01 maskom da se ne vide ivice). Za veći kvalitet tražiti originale u visokoj rezoluciji u istom kadru.
- Stage: `aspect-ratio 820/461`, širina 100%, zalepljen dole desno. Maska: levo `transparent -> #000` do 16%, gore do 14% (`mask-composite: intersect`). Preko njega gradijent za čitljivost teksta: `linear-gradient(90deg, rgba(6,6,6,.92) 0, rgba(6,6,6,.6) 34%, transparent 62%)`.
- Mobilni (<768px): tekst gore, ispod kvadratni prozor (`aspect-ratio 1/1.05`, overflow hidden) u kom je stage široka 190% i pomerena `left: -76%` da automobil popuni širinu. Maska samo odozgo (0 -> 22%). Gradijent za tekst se ne koristi.

#### Animacija hero-a (jednom, pri učitavanju)
1. Preload i `decode()` sve tri slike.
2. +600ms: `hero-2` opacity 0 -> 1 (450ms, cubic-bezier(.4,0,.2,1)).
3. +350ms (950ms ukupno): `hero-3b` opacity 0 -> 1 (750ms).
4. Odmah od koraka 2: spora kamera, `transform: scale(1 -> 1.025)` 3.6s `cubic-bezier(.2,.6,.2,1)`, origin 72% 62%.
5. Bloom: dva radijalna kruga (14% širine stage-a, `mix-blend-mode: screen`) na farovima, centri (45.6%, 52.5%) i (72.8%, 52%); gradijent `rgba(205,224,255,.8) 0 -> rgba(150,185,255,.28) 28% -> 0 66%`; opacity 0 -> .5 (faza 1) -> .38 (faza 2), 900ms.
6. Snop svetla: elipsa 30% x 9% iz levog fara, rotacija 12deg, blur 8px, `screen`, opacity 0 -> .55 u fazi 2.
7. Bez petlje. `prefers-reduced-motion`: odmah finalno stanje (hero-3b), bez tranzicija.

### 3. Usluge (`#usluge`)
Eyebrow "Usluge", h2 "Šta radimo na farovima" (Barlow Condensed 700, `clamp(40px, 5.5vw, 64px)`, line-height 1, uppercase, max 16ch), uvod "Cenu dajemo posle pregleda ili kad pošalješ slike. Pozovi i dogovorimo." (18px, `#3a3a3a`). Mreža `repeat(auto-fit, minmax(240px, 1fr))`, okvir 1px `#cfcdc8` (gornja i leva linija na mreži, desna i donja na ćeliji), ćelija padding 28/24/32. Svaka: broj (Barlow Condensed 20px, `#c4261b`), naslov 19px/600, opis 16px/1.55.
1. Polimerizacija farova: Požutelo i mutno staklo opet postaje providno.
2. Zamena stakla fara: Kad poliranje ne pomaže, odlepimo staklo i stavimo novo.
3. Reparacija farova: Varimo oštećena kućišta i popravljamo ono što pukne.
4. Dihtovanje i vlaga: Sklanjamo vodu i kondenzaciju iz fara i zatvaramo ga da ne vrati.
5. Poliranje projektora i rozetni: Lupa projektora i hrom rozetne dobijaju sjaj iznutra.
6. LED i Xenon: Xenon D1S menjamo LED sijalicom. Ugrađujemo i bi-LED projektore.
7. Moduli i elektronika: Menjamo LED ploče, diode i module migavca. Popravljamo glavnu ploču fara.
8. Ulepšavanje: Dnevna svetla, cotton prstenovi, crne rozetne.

### 4. Radovi / Pre i posle (`#radovi`)
Pozadina `#fff`, linije `#e1dfda` gore i dole. Slajder sa 6 parova: Opel Insignia, BMW E60, Audi A6, Hyundai ix20, Iveco Daily, Smart ForTwo. Dve kvadratne slike jedna do druge (gap 6px, `auto-fit minmax(340px, 1fr)`), oznake "PRE" (`#141414`) i "POSLE" (`#d62a1e`) gore levo (14px/600, padding 8x14). Ispod: naziv (22px/600), opis, brojač "1 / 6", dugmad strelice 48x48 (leva outline, desna puna crvena). Ispod toga redovi sličica (posle slike), aktivna: opacity 1 + outline 2px `#d62a1e`, ostale opacity .55. Link "Još radova na Instagramu @semtex_garage".
Opisi parova: Opel: Obe plastike fara zamenjene, xenon D1S u LED, poliranje rozetni i lupe projektora. BMW E60: Požuteli i mutni farovi opet su providni. Audi A6: Zamena stakla fara, poliranje rozetni i lupe projektora. ix20: Voda u faru. Dihtovanje i varenje kućišta. Iveco: Mutan fabrički far zamenjen bi-LED projektorima. Smart: Crne rozetne i bi-LED projektor od 3 inča.

### 5. Zašto Semtex
Dve kolone. Levo: eyebrow, h2 "Far rasklapamo, ne glancamo spolja", dva pasusa (vlaga/požutelo/moduli nastaju iznutra), pa dve brojke: "4,5 / 5" (Google ocena, 33 recenzije) i "7.490" (pratilaca na Instagramu). Desno: dve fotografije 3:4 (`rav4-far.jpg`, `iveco-led.jpg`).

### 6. Recenzije (`#recenzije`)
Pozadina `#fff`. Tri citata (Marko B., Dejan M., Vladimir Ž.), tekst doslovno sa Google Mapa (vidi `PODACI-ZA-SAJT.md`), 17px/1.6, potpis 15px/600 + zvezdice `#c4261b`. Link "Pogledaj sve recenzije na Google-u".

### 7. Majstor
Fotografija `majstor.jpg` (4:3) + h2 "Milan" + dva pasusa.

### 8. Kontakt (`#kontakt`) i podnožje
Pozadina `#111`. h2 "Pozovi ili pošalji sliku fara", ista 4 dugmeta. Ispod: kolona sa telefonom, radnim vremenom i adresom (trenutno **placeholderi**) i siva kutija za Google mapu. Podnožje `#0a0a0a`: naziv + Instagram, TikTok linkovi.

## Interactions & Behavior
- **Scroll reveal:** svi direktni elementi sekcija se pojavljuju sa `opacity 0 -> 1` i `translateY(32px) -> 0`, 800ms `cubic-bezier(.2,.7,.2,1)`, kašnjenje po elementu `min(index * 90, 450)ms`, `IntersectionObserver` (threshold .12, rootMargin `0 0 -40px 0`). Mreže (usluge, kartice) animiraju decu, ne kontejner. Hero pozadina se ne animira ovim. Isključeno za reduced motion.
- **Slajder:** strelice i sličice menjaju par, kružno. Bez automatske promene. Preporuka: dodati swipe i tastaturu.
- Hover: dugmad menjaju boju (vidi gore), linkovi `#c4261b` -> `#8f1a12`, nav linkovi `#d8d8d8` -> bela.
- Kontakt linkovi: `tel:`, `viber://chat?number=`, `https://wa.me/`, Instagram. Brojevi su placeholder (`+381`).

## State Management
Samo: indeks slajdera (0-5), faza hero animacije (0, 1, 2), da li je ekran uzak (<768px, za hero raspored). Nema pozivanja servera.

## Design Tokens
- Boje: crna `#060606` (hero), `#111` (zaglavlje, kontakt), `#0a0a0a` (podnožje), tekst `#141414`, sekundarni tekst `#3a3a3a`, pozadina `#f6f5f3`, bela `#fff`, linije `#cfcdc8` / `#e1dfda`, akcent crvena `#d62a1e` (hover `#b01f15`), crvena za tekst na svetlom `#c4261b` (hover `#8f1a12`), svetlija crvena na tamnom `#ff6a5e`, sivi tekst na tamnom `#bdbdbd`, `#d8d8d8`, `#e2e2e2`.
- Fontovi (Google Fonts): **Barlow Condensed** 600/700 za naslove, **IBM Plex Sans** 400/500/600 za tekst.
- Radijus: 6px dugmad, 4px slike u sekcijama. Bez senki, razdvajanje linijama 1px.
- Razmak: grid gap 6-72px (`clamp(32px, 5vw, 72px)` između kolona).
- Prelom: 768px. Mreže su `auto-fit` pa se same lome.

## Assets
- `img/logo.jpg`: Semtex Garage logo, 150x150 sa Instagrama. **Zatražiti original ili vektor.**
- `img/hero-1.png`, `hero-2.png`, `hero-3b.png`: slike automobila za hero (dostavljene od korisnika, obrađene).
- `img/*-pre.jpg`, `*-posle.jpg`, `rav4-far.jpg`, `iveco-led.jpg`: Instagram i Google Mape profila Semtex Garage, tablice uklonjene.
- `img/majstor.jpg`: fotografija majstora, uzeta sa Google profila. Pitati Milana za saglasnost.
- `PODACI-ZA-SAJT.md`: sve prikupljeno o servisu (usluge, recenzije, linkovi, napomene).

## Otvoreno pre objavljivanja
- Broj telefona, Viber, WhatsApp (trenutno `+381` placeholder).
- Adresa (Google Mape pokazuju Temerinsku kao "Trajno zatvoreno"), radno vreme, ugrađena mapa.
- Saglasnost za slike i recenzije, logo u većoj rezoluciji.
- SEO: title, meta opis, Open Graph, `LocalBusiness` schema, lazy loading slika van prvog ekrana.

## Files
- `Semtex Garage.dc.html` - ceo dizajn (markup, stil, logika slajdera, animacije)
- `support.js` - runtime za prikaz reference
- `img/` - korišćene slike
- `PODACI-ZA-SAJT.md` - sadržaj i napomene
