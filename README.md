# GarlicRain Redist
A cryptocoin faucet based on Django.
## Install instructions
1. Make sure you have Python 3 and Django installed. (To check: `python --version` and `django-admin version`)
1. Install the JSON RPC library: `pip install jsonrpclib-pelix` (sudo may be required)
1. Download the repository on your server.
1. Edit faucet/settings.py: Change your SECRET_KEY to a random string of 50 characters. You should also change ALLOWED_HOSTS to only allow requests from your domain.
1. Edit faucet/faucet_settings.py: This is where most of the faucet configuration goes. You need to set rpc_url to point to your Bitcoin/Altcoin daemon, and optionally change the rest of the variables to customize the faucet.
1. Edit faucetapp/templates/faucetapp/base.html to customize the look of the faucet site, and to edit the footer text.
1. Optional: If you want to enable reCAPTCHA, you need to get the public and private keys from the [reCAPTCHA admin page](https://www.google.com/recaptcha/admin). After registering, select your site. You'll find the sitekey under client side integration (in the HTML snippet reCAPTCHA asks you to embed), and the private key under server side integration.
1. Run `python manage.py migrate` to initialize the database.
1. Optional: Create a Django admin user by running `python manage.py createsuperuser`. This allows you to view the faucet logs under /admin when the server is running.
1. You're done! Run `python manage.py runserver 0.0.0.0` to run the faucet on the Django development server.
1. If you'd like to run the faucet on a production server you should look into integrating Django with a real web server like nginx or Apache.
