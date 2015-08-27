# Automated surveys (Django)
[![Build Status](https://travis-ci.org/TwilioDevEd/automated-survey-django.svg?branch=master)](https://travis-ci.org/TwilioDevEd/automated-survey-django)

Use Twilio to conduct automated phone surveys.

## Quickstart

### Heroku

This project is preconfigured to run on [Heroku](https://www.heroku.com/). Deploy it now:

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/TwilioDevEd/automated-survey-django)

To view your app, click the **...** menu in the top right corner and select **Open app**.

### Local development

This project is built using the [Django](https://www.djangoproject.com/) web framework. It runs on Python 2.7+ and Python 3.4+.

To run the app locally, first clone this repository and `cd` into its directory. Then:

1. Create a new virtual environment:
    - If using vanilla [virtualenv](https://virtualenv.pypa.io/en/latest/), run `virtualenv venv` and then `source venv/bin/activate`
    - If using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/), run `mkvirtualenv automated-surveys`
1. Install the requirements with `pip install -r requirements.txt`
1. Start a local PostgreSQL database and create a database called `surveys`
    - If on a Mac, I recommend
      [Postgres.app](http://postgresapp.com/). After install, run `createdb surveys;`
    - If Postgres is already installed locally, you can just run `createdb surveys` from a terminal
1. Run the migrations with `python manage.py migrate`
1. Optionally create a superuser so you can access the Django admin: `python manage.py createsuperuser`.
1. Copy the `.env.example` file to `.env`, and edit it to match your database.
1. Start the development server: `python manage.py runserver`

### Configure Twilio to call your webhooks

You will also need to configure Twilio to call your application when
calls are received

You will need to provision at least one Twilio number with voice
capabilities so the application's users can take surveys. You can buy
a number
[right here](https://www.twilio.com/user/account/phone-numbers/search). Once
you have a number you need to configure your number to work with your
application. Open
[the number management page](https://www.twilio.com/user/account/phone-numbers/incoming)
and open a number's configuration by clicking on it.

![Open a number configuration](https://raw.github.com/TwilioDevEd/automated-survey-django/master/images/number-conf.png)

Next, edit the "Request URL" field under the "Voice" section and point
it towards your ngrok-exposed application `/automated-survey/first-survey/` route. Set
the HTTP method to POST. If you are trying the Heroku
application you need to point Twilio to
`http://<your-app-name>.herokuapp.com/automated-survey/first-survey/`. See the image
below for an example:

You can then visit the application at [http://localhost:8000/](http://localhost:8000/).

Mind the trailing slash.

![Webhook configuration](https://raw.github.com/TwilioDevEd/automated-survey-django/master/images/webhook-conf.png)

## Run the tests

Configure your test database in `.env.test`. You can then run the tests locally using `py.test`

```
$ py.test --cov=automated_survey
```

