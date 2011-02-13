import uuid
import os, sys

path = os.path.dirname(__file__)
sys.path.append("%s/" %path)

import twilio
import config

class Switcher:
    
    def __init__(self, args):
        self._uid = args._uid
        self._digit = args.Digits
        
    def go(self):
        global path
        if self._digit == '0':
            f = open("%s/data/%s" %(path, self._uid), 'r')
        elif self._digit in ['1', '2', '3', '4', '5']:
            _file = "%s/data/%s-%s" %(path, self._uid, self._digit)
            if os.path.exists(_file):
                f = open(_file, 'r')
            else:
                f = open("%s/data/%s-menu" %(path, self._uid), 'r')
        else:
            f = open("%s/data/%s-menu" %(path, self._uid), 'r')
        return ''.join(f.readlines())
    
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
        
        ## Song (5 max)
        if '_songs' in args.keys():
            self._songs = args._songs
            if len(self._songs) > 5:
                self._songs = self._songs[:5]
        else:
            self._songs = [
                config.DEFAULT_SONG, 
                config.DEFAULT_SONG
            ]
        
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
        
        ## Generate uniqid
        uid = uuid.uuid4()

        ## Header including change settings
        head = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n" %uid
        
        ## Generate intro message
        r = twilio.Response()
        r.addGather(
            action = config.ROOT + '/cgi.py/change?_uid=%s' %uid,
            method = 'GET'
        ).append(
            twilio.Say(
                self._message,
                voice = self._voice,
                language = self._lang,
            )
        )
        f = open("%s/data/%s" %(path, uid), 'w')
        f.write('%s%s' %(head, r))
        f.close()

        ## Generate menu message
        r = twilio.Response()
        r.addGather(
            action = config.ROOT + '/cgi.py/change?_uid=%s' %uid,
            method = 'GET'
        ).append(
            twilio.Say(
                "This is a menu",
                voice = self._voice,
                language = self._lang,
            )
        )
        f = open("%s/data/%s-menu" %(path, uid), 'w')
        f.write('%s%s' %(head, r))        
        f.close()
        
        ## Generate one message per song
        i = 1
        for s in self._songs:
            r = twilio.Response()
            r.addGather(
                action = config.ROOT + '/cgi.py/change?_uid=%s' %uid,
                method = 'GET'
            ).append(
                twilio.Play(s)
            )
            f = open("%s/data/%s-%s" %(path, uid, i), 'w')
            f.write('%s%s' %(head, r))
            f.close()
            i += 1

        ## Ring the phone with intro message
        account = twilio.Account(config.ACCOUNT_SID, config.ACCOUNT_TOKEN)
        d = {
            'From' : config.CALLER_ID,
            'To' : self._phone,
            'Url' : config.ROOT + "/data/%s" %uid,
        }
        try:
            request = account.request('/%s/Accounts/%s/Calls' %(config.API_VERSION, config.ACCOUNT_SID), 'POST', d)
        except Exception, e:
            print e
            print e.read()