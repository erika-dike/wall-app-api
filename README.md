# Wallie-Api
> The API portion of the [https://github.com/andela-cdike/wallie](wallie) app.


This repo hosts the python and Django backend of the wallie application. It provides an [https://wallie-api.herokuapp.com/admin](admin interface) and a [https://wallie-api.herokuapp.com/api/v1/core/posts/](browsable API) interface for seeing the payload returned by the different endpoints.

This app also features web sockets so users receive real time updates as messages are posted on the board.


## Technologies
+ [python 2.7](https://www.python.org/download/releases/2.7/)
+ [Django 1.11](https://www.djangoproject.com/)
+ [Channels for websockets](https://channels.readthedocs.io/en/stable/inshort.html)
+ [Postgres](https://www.postgresql.org/)
+ [Redis](https://redis.io/)

## Pre-requisites
+ Python

## Installation

1. Clone the repo:

```sh
$ git clone https://github.com/andela-cdike/wall-app-api
```

2. Navigate to root folder

```sh
$ cd wall-app-api
```

3. Install dependencies

```sh
$ pip install -r requirements
```

3. Run the server

```sh
$ cd wall_app
$ python manage.py runserver
```

## Tests
Run tests with

```sh
$ cd wall_app
$ python manage.py test
```

## Meta

Erika Dike – [@rikkydyke](https://twitter.com/rikkydyke) – chukwuerikadike@gmail.com

## License
Distributed under the MIT license. See ``LICENSE`` for more information.
