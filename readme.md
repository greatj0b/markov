you'll need an influxdb 1.8 server with some sort of data loaded in. 

the only measurement your db needs is 'message_content'. nothing else is scraped. 

i have provided testdata.txt with dummy data you can import. 

https://docs.influxdata.com/influxdb/v1/

other than that install the requirements

pip install -r requirements.txt

edit config.py with your stuff

you'll need your access token from https://twitchtokengenerator.com/

(be sure you're logged in with your bot's account)
