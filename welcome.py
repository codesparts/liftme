import os
from flask import Flask, jsonify
import sys
import asyncio
import random
import telepot
from telepot.aio.delegate import per_chat_id, create_open, pave_event_space


class Player(telepot.aio.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)
        self._answer = random.randint(0,99)

    def _hint(self, answer, guess):
        if answer > guess:
            return 'larger'
        else:
            return 'smaller'

    async def open(self, initial_msg, seed):
        await self.sender.sendMessage('Guess my number')
        return True  # prevent on_message() from being called on the initial message

    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type != 'text':
            await self.sender.sendMessage('Give me a number, please.')
            return

        try:
           guess = int(msg['text'])
        except ValueError:
            await self.sender.sendMessage('Give me a number, please.')
            return

        # check the guess against the answer ...
        if guess != self._answer:
            # give a descriptive hint
            hint = self._hint(self._answer, guess)
            await self.sender.sendMessage(hint)
        else:
            await self.sender.sendMessage('Correct! Asshole')
            self.close()

    async def on__idle(self, event):
        await self.sender.sendMessage('Game expired. The answer is %d' % self._answer)
        self.close()

TOKEN = '346977723:AAEH6vMSPdozNhyQwhFpDY0N8cRClJySziE'
app = Flask(__name__)


@app.route('/')
def Welcome():
    return app.send_static_file('index.html')


@app.route('/myapp')
def WelcomeToMyapp():
    return 'Welcome again to my app running on Bluemix!'


@app.route('/api/people')
def GetPeople():
    list = [
        {'name': 'John', 'age': 28},
        {'name': 'Bill', 'val': 26}
    ]
    return jsonify(results=list)


@app.route('/api/people/<name>')
def SayHello(name):
    message = {
        'message': 'Hello ' + name
    }
    return jsonify(results=message)


bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, Player, timeout=10),
])


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(bot.message_loop())
    print('Listening ...')
    loop.run_forever()
    app.run(host='0.0.0.0', port=int(port))
