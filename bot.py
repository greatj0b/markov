from twitchio.ext import commands
import config
from influxdb import InfluxDBClient
import markovify
from datetime import datetime
import re
import sys

sys.path.insert(0, '/home/gr3atj0b/markov')

idb = InfluxDBClient(host=config.influxdb, port=config.influxport, database=config.influx_database)

#init 6 preloaded messages
generated_messages = []
for i in range(6):
    dbtext = ""
    msgs = idb.query("select text from message_content;")
    dbdump = list(msgs.get_points(measurement='message_content'))
    for dbdump_index in dbdump:
        dbtext += dbdump_index["text"] + "\n"
    filtered = "\n".join([ll.rstrip() for ll in dbtext.splitlines() if ll.strip()])
    text_model = markovify.NewlineText(filtered)
    new = text_model.make_sentence(tries=100)
    while not new:
        new = text_model.make_sentence()
    generated_messages.append(new)

class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=config.token, prefix='}', initial_channels=config.channels)

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        if ('markov' not in message.content.casefold() and message.tags.get('display-name').lower() not in config.ignore_list):
            formatted_text = re.sub(r"http\S+", "", message.content)
            current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            if formatted_text == '':
                return
            json_body = [
            {
                "measurement": "message_content",
                "tags": {
                    "channel": message.channel.name
                },
                "time": current_time,
                "fields": {
                    "text": formatted_text
                }
            }]
            #print(message.tags.get('display-name'))
            idb.write_points(json_body)

        if ('markov' in message.content.lower() and message.tags.get('display-name').lower() not in config.ignore_list):

            await message.channel.send(generated_messages[0])
            generated_messages.pop(0)

            dbtext = ""
            msgs = idb.query("select text from message_content;")
            dbdump = list(msgs.get_points(measurement='message_content'))
            for dbdump_index in dbdump:
                dbtext += dbdump_index["text"] + "\n"
            filtered = "\n".join([ll.rstrip() for ll in dbtext.splitlines() if ll.strip()])
            
            #with open('testdata.txt', 'r') as file:
            #    filtered = file.read()

            text_model = markovify.NewlineText(filtered)
            new = text_model.make_sentence(tries=100)
            while not new:
                new = text_model.make_sentence()
            generated_messages.append(new)


        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    @commands.command()
    async def isthebotworking(self, ctx: commands.Context):
        # Here we have a command hello, we can invoke our command with our prefix and command name
        # e.g ?hello
        # We can also give our commands aliases (different names) to invoke with.

        # Send a hello back!
        # Sending a reply back to the channel is easy... Below is an example.
        if (ctx.author.name == 'gr3atj0b'):
            await ctx.send(f'@{ctx.author.name} yes')


bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.
