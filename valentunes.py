import uuid
import os, sys

path = os.path.dirname(__file__)
sys.path.append("%s/" %path)

import twilio
import config
import web

#######################################
## Switching between messages and songs
#######################################
class Switcher:
    
    def __init__(self, args):
        self._uid = args._uid
        self._digit = args.Digits
        
    def go(self):
        global path
        root = "%s/data/%s" %(path, self._uid)
        ## Default file, intro message
        if self._digit == '0':
            f = open(root, 'r')
        ## Songs files, or main menu is not exits
        elif self._digit in ['1', '2', '3', '4', '5']:
            _file = "%s-%s" %(root, self._digit)
            if os.path.exists(_file):
                f = open(_file, 'r')
            else:
                f = open("%s-menu" %root, 'r')
        ## Menu file
        else:
            f = open("%s-menu" %root, 'r')
        web.header("Content-Type","text/html; charset=utf-8")
        return ''.join(f.readlines())
    
################################
## Valentunes wrapper for Twilio
################################
class Valentunes:
        
    def __init__(self, _phone, _songs, _from, _to, **kwargs):
        
        ###############
        ## Phone number
        ###############
        self._phone = _phone

        ################
        ## Songs (5 max)
        ################
        self._songs = _songs
        if len(self._songs) > 5:
            self._songs = self._songs[:5]
        
        ################
        ## Intro message
        ################
        self._message = "Hello %s, this is %s." %(_to, _from)
        if 'message' in kwargs.keys():
            self._message += kwargs['message']

        #################
        ## Voice
        #################
        self._voice = twilio.Say.MAN
        self._args = kwargs

        if 'voice' in kwargs.keys():
            if kwargs['voice'] == 'woman':
                self._voice = twilio.Say.WOMAN
                
    def call(self):
        
        global path
        
        ## Generate uniqid
        uid = uuid.uuid4()
        
        ## XML header
        head = "<?xml version='1.0' encoding='utf-8' ?>\n"

        #########################
        ## Generate intro message
        #########################
        r = twilio.Response()
        r.addSay(
            self._message,
            voice = self._voice,
        )
        ## Automatic redirect to the menu
        r.addRedirect(
            config.ROOT + "/data/%s-menu" %uid,
        )
        ## Save Twilio message
        f = open("%s/data/%s" %(path, uid), 'w')
        f.write('%s%s' %(head, r))
        f.close()

        ###########################################
        ## Generate menu message with list of songs
        ###########################################
        r = twilio.Response()
        i = 1
        listing = ''
        for s in self._songs:
            listing += "Number %s: %s..." %(i, s['title'])
            i += 1
        ## Let user type in the song number (5 secs. delay)
        r.addGather(
            action = config.ROOT + '/cgi.py/change?_uid=%s' %uid,
            method = 'GET',
            timeout = 5
        ).append(
            twilio.Say(
                "%s Type their number and the hash key to listen to them. Type 9 to listen to this list and 0 for the introduction message." %listing,
                voice = self._voice,
            )
        )
        ## Redirect to first song if time-outs
        r.addRedirect(
            config.ROOT + "/data/%s-1" %uid,
        )
        ## Save Twilio message
        f = open("%s/data/%s-menu" %(path, uid), 'w')
        f.write('%s%s' %(head, r))
        f.close()
        
        ################################
        ## Generate one message per song
        ################################
        i = 1
        for s in self._songs:
            r = twilio.Response()
            r.addGather(
                action = config.ROOT + '/cgi.py/change?_uid=%s' %uid,
                method = 'GET',
                timeout = 10
            ).append(
                twilio.Play(s['url'])
            )
            ## Automated redirect to the next one, or to the first one
            root = "%s/data/%s" %(path, uid)
            _file = "%s-%s" %(root, i+1)
            if os.path.exists(_file):
                next = i+1
            else:
                next = 1
            r.addRedirect(
                config.ROOT + "/data/%s-%s" %(uid, next)
            )
            ## Save Twilio message
            f = open("%s/data/%s-%s" %(path, uid, i), 'w')
            f.write('%s%s' %(head, r))
            f.close()
            i += 1

        ####################################
        ## Ring the phone with intro message
        ####################################
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