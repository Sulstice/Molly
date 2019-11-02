#!/usr/bin/env python3
#
# Main App
#
# -----------------

# Imports
# -------
import random
import os
import string

# Web App Modules
# ---------------
from flask import Flask, request
from pymessenger.bot import Bot

# PDB Modules
# -----------
from pypdb import *

# Access Tokens
# -------------
app = Flask(__name__)
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
VERIFY_TOKEN = os.environ["VERIFY_TOKEN"]
bot = Bot(ACCESS_TOKEN)

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():

    """

    This function will be used to retrieve the message from the user

    """
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    #Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    facebook_message = message['message'].get('text')
                    if facebook_message and "protein" in facebook_message:
                        response_sent_text = get_message(facebook_message)
                        send_message(recipient_id, response_sent_text)
                    elif facebook_message:
                        default_message()
                    #if user sends us a GIF, photo,video, or any other non-text item
                    elif message['message'].get('attachments'):
                        response_sent_nontext = get_message()
                        send_message(recipient_id, response_sent_nontext)

    return "Message Processed"


def verify_fb_token(token_sent):

    """


    Token used for facebook API, information is stored on Heroku Deployed App

    Arguments:
         token_sent (String): The token used to verify to messenger API

    Returns:
        requests (Object): Something tailored for just Facebook.

    """
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message(facebook_message):


    # First process the message
    message_with_punctuation = facebook_message
    table = str.maketrans(dict.fromkeys(string.punctuation))
    stripped_punctuation_message = message_with_punctuation.translate(table)

    import nltk
    words = set(nltk.corpus.words.words())

    # return selected item to the user
    for word in nltk.wordpunct_tokenize(stripped_punctuation_message):
        if word.lower() in words:
            continue
        else:
            protein_code = word

    pdb_file = get_pdb_file(protein_code, filetype='pdb', compression=False)

    return "Here is your protein %s" % pdb_file

def default_message():
    return "Awesome!"

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
