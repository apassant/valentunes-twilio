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
        
        _to = args._to
        _from = args._from
        _phone = args._phone
        
        _voice = twilio.Say.MAN
        _lang = twilio.Say.ENGLISH
        _song = config.DEFAULT_SONG

        ## Generate twilio message
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