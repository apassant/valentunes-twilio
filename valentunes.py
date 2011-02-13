import uuid
import os, sys

path = os.path.dirname(__file__)
sys.path.append("%s/" %path)

import twilio
import config

class Valentunes:
    
    def __init__(self, args):
        ## Phone number
        self._phone = args._phone

        ## Message
        message = "Hello %s, this is %s. Here is a song for you, happy Valentine's day !" %(args._to, args._from)
        if '_msg' in args.keys():
            self._message = "%s %s" %(message, args._msg)
        else:
            self._message = message
        
        ## Song
        if '_song' in args.keys():
            self._song = args._song
        else:
            self._song = config.DEFAULT_SONG
        
        ## Voice
        if '_voice' in args.keys():
            if args._voice == 'woman':
                self._voice = twilio.Say.WOMAN
        else:
            self._voice = twilio.Say.MAN

        ## Lang
        if '_lang' in args.keys():
            if args._lang == 'es':
                self._lang = twilio.Say.ENGLISH
            if args._lang == 'fr':
                self._lang = twilio.Say.FRENCH
            if args._lang == 'de':
                self._lang = twilio.Say.GERMAN
        else:
            self._lang = twilio.Say.ENGLISH
                
    def call(self):
        
        global path
        
        ## Generate Twilio message
        r = twilio.Response()
        r.addSay(
            self._message,
            voice = self._voice,
            language = self._lang,
        )
        r.addPlay(self._song)

        ## Save message file
        name = uuid.uuid4()
        f = open("%s/data/%s" %(path, name), 'w')
        f.write('<?xml version="1.0" encoding="UTF-8" ?>\n %s' %r)
        f.close()

        ## Ring the phone
        account = twilio.Account(config.ACCOUNT_SID, config.ACCOUNT_TOKEN)
        d = {
            'From' : config.CALLER_ID,
            'To' : self._phone,
            'Url' : config.ROOT + "/data/%s" %name,
        }
        try:
            request = account.request('/%s/Accounts/%s/Calls' %(config.API_VERSION, config.ACCOUNT_SID), 'POST', d)
        except Exception, e:
            print e
            print e.read()