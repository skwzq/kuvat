# Kuvagalleria

## Sovelluksen toiminnot
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään sovellukseen kuvia.
- Käyttäjä pystyy lisäämään kuviin avainsanoja ja kuvatekstin.
- Käyttäjä pystyy poistamaan lisäämiään kuvia sekä muokkaamaan kuvien otsikkoa, kuvatekstiä ja avainsanoja.
- Käyttäjä näkee sovellukseen lisätyt kuvat.
- Käyttäjä pystyy etsimään kuvia yhdellä tai useammalla hakusanalla, joko kaiken kuviin liittyvän tekstin tai pelkkien avainsanojen perusteella.
- Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät kuvat.
- Käyttäjä pystyy kommentoimaan sovellukseen lisättyjä kuvia sekä muokkaamaan ja poistamaan lisäämiään kommentteja.

## Sovelluksen asennus
Asenna `flask`-kirjasto:
```
$ pip install flask
```
Luo tietokannan taulut:
```
$ sqlite3 database.db < schema.sql
```
Voit käynnistää sovelluksen näin:
```
$ flask run
```
