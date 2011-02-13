import uuid
import os, sys

path = os.path.dirname(__file__)
sys.path.append("%s/" %path)

import twilio
import config
import web

class Switcher:
    
    def __init__(self, args):
        self._uid = args._uid
        self._digit = args.Digits
        
    def go(self):
        global path
        root = "%s/data/%s" %(path, self._uid)
        if self._digit == '0':
            f = open(root, 'r')
        elif self._digit in ['1', '2', '3', '4', '5']:
            _file = "%s-%s" %(root, self._digit)
            if os.path.exists(_file):
                f = open(_file, 'r')
            else:
                f = open("%s-menu" %root, 'r')
        else:
            f = open("%s-menu" %root, 'r')
        web.header("Content-Type","text/html; charset=utf-8")
        return ''.join(f.readlines())
    
class Valentunes:
    
    def __init__(self, args):
        ## Phone number
        self._phone = args._phone

        ## Lang and default message
        if '_lang' in args.keys():
            if args._lang == 'es':
                self._lang = twilio.Say.SPANISH
                ## Translate in spanish
                message = "Hello %s, this is %s. Here are some song for you, happy Valentine's day !" %(args._to, args._from)
            if args._lang == 'fr':
                self._lang = twilio.Say.FRENCH
                message = "Salut %s, c'est %s. Voila quelques chansons pour toi, bonne Saint-Valentin !" %(args._to, args._from)
            if args._lang == 'de':
                self._lang = twilio.Say.GERMAN
                ## Translate in german
                message = "Hello %s, this is %s. Here are some song for you, happy Valentine's day !" %(args._to, args._from)
        else:
            self._lang = twilio.Say.ENGLISH
            message = "Hello %s, this is %s. Here are some song for you, happy Valentine's day !" %(args._to, args._from)

        ## Additional message
        if '_msg' in args.keys():
            self._message = "%s %s" %(message, args._msg)
        else:
            self._message = message
        
        ## Songs (5 max)
        if '_songs' in args.keys():
            self._songs = args._songs
            if len(self._songs) > 5:
                self._songs = self._songs[:5]
        else:
            self._songs = [
                (config.DEFAULT_SONG_TITLE, config.DEFAULT_SONG),
                (config.DEFAULT_SONG_TITLE, config.DEFAULT_SONG),
            ]
        
        ## Voice
        if '_voice' in args.keys():
            if args._voice == 'woman':
                self._voice = twilio.Say.WOMAN
        else:
            self._voice = twilio.Say.MAN
                
    def call(self):
        global path
        
        ## Generate uniqid
        uid = uuid.uuid4()

        ## Header including change settings
        head = "<?xml version='1.0' encoding='utf-8' ?>\n" %uid
        
        ## Generate intro message
        r = twilio.Response()
        r.addSay(
            self._message,
            voice = self._voice,
            language = self._lang,
        )
        r.addRedirect(
            config.ROOT + "/data/%s-menu" %uid,
        )
        f = open("%s/data/%s" %(path, uid), 'w')
        f.write('%s%s' %(head, r))
        f.close()

        ## Generate menu message with list of songs
        r = twilio.Response()
        i = 1
        listing = ''
        for s in self._songs:
            listing += "Number %s: %s..." %(i, s[0])
            i += 1
        r.addGather(
            action = config.ROOT + '/cgi.py/change?_uid=%s' %uid,
            method = 'GET',
            timeout = 10
        ).append(
            twilio.Say(
                "%s Type their number to listen them, 9 to listen to the list again, or 0 for the introduction." %listing,
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
                method = 'GET',
                timeout = 10
            ).append(
                twilio.Play(s[1])
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