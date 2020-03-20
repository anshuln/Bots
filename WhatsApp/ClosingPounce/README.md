# ClosingPounce

A simple bot that scrapes messages from a WhatsApp chat and stores them to database. 
The particular use case is to extract quiz questions from a WhatsApp group and host them to a [Google Slides Presentation](https://docs.google.com/presentation/d/1HSdfhNbAkL_wCNuwtmANQXDMgeg2te1LLu_KGMNO-dY/edit?usp=sharing).

## Setup
Requirements -
* `python 3.6` or higher
* Run `pip install -r requirements.txt` to get all required libraries
* Create a `credentials.json` file using [Google OAuth2](https://console.developers.google.com/)  
* Setup the database

Run `python getTok.py` to create the `token.pickle` file containing your credentials.

## Running
Run `python driver.py -h` to get a list of command line options.
* -e scrapes your email get an attachment (whose filename is in `config.json`) 
* -p parses the downloaded log file to extract and store questions into the database
* -u uploads questions to Google Slides

## Contributing
Fork the repo and put in a pull request. I am looking at better options to display the database's contents, as well as ways to get better question and answer scraping from the logs.