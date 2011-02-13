import uuid
import os, sys
import web

path = os.path.dirname(__file__)
sys.path.append("%s/" %path)

import twilio
import config

urls = (
    '/.*', 'Caller',
)

class Caller:
    
    def call(self, args):
        
        ## Mandatory parameters
        _to = args._to
        _from = args._from
        _phone = args._phone

        ## Song
        if '_song' in args.keys():
            _song = args._song
        else:
            _song = config.DEFAULT_SONG
        
        ## Voice
        if '_voice' in args.keys():
            if args._voice == 'woman':
                _voice = twilio.Say.WOMAN
        else:
            _voice = twilio.Say.MAN

        ## Lang
        if '_lang' in args.keys():
            if args._lang == 'es':
                _lang = twilio.Say.ENGLISH
            if args._lang == 'fr':
                _lang = twilio.Say.FRENCH
            if args._lang == 'de':
                _lang = twilio.Say.GERMAN
        else:
            _lang = twilio.Say.ENGLISH
                    

        ## Generate Twilio message
        r = twilio.Response()
        r.addSay("Hello %s, this is %s. I got a song for you, happy Valentine's day !" %(_to, _from), 
            voice = _voice, 
            language = _lang,
            )
        r.addPlay(_song)

        ## Save message file
        name = uuid.uuid4()
        f = open("%s/data/%s" %(path, name), 'w')
        f.write('<?xml version="1.0" encoding="UTF-8" ?>\n %s' %r)
        f.close()

        ## Ring the phone
        account = twilio.Account(config.ACCOUNT_SID, config.ACCOUNT_TOKEN)
        d = {
            'From' : config.CALLER_ID,
            'To' : _phone,
            'Url' : config.ROOT + "/data/%s" %name,
        }
        try:
            request = account.request('/%s/Accounts/%s/Calls' %(config.API_VERSION, config.ACCOUNT_SID), 'POST', d)
        except Exception, e:
            print e
            print e.read()

    def GET(self):
        args = web.input()
        ## Check reuired parameters
        if '_to' not in args.keys():
            return "_to parameter required (name of the person you want to call)"
        if '_from' not in args.keys():
            return "_from parameter required (your name)"
        if '_phone' not in args.keys():
            return "_phone parameter required (phone number to ring)"
        ## Go !
        return self.call(args)

application = web.application(urls, globals()).wsgifunc()