# Kuvagalleria

## Sovelluksen nykyinen tilanne
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään kuvia, joilla on otsikko ja kuvaan liittyvä teksti. Käyttäjä pystyy muokkaamaan otsikkoa ja tekstiä sekä poistamaan lisäämiään kuvia.
- Käyttäjä näkee sovellukseen lisätyt kuvat.
- Käyttäjä pystyy etsimään kuvia hakusanalla.
- Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät kuvat.
- Käyttäjä pystyy lisäämään kuviin avainsanoja.
- Käyttäjä pystyy kommentoimaan sovellukseen lisättyjä kuvia.

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
