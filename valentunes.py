import twilio
import uuid
import config

## HOW-TO
## - Copy config.dist.py to config.py and edit parameters
## - Run valentunes.py

## @@FIXME : Get parameters from the URL
_to = 'Julie'
_from = 'Alex'
_phone = config.CALLER_ID

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
f = open("./data/%s" %name, 'w')
f.write("%s" %r)
f.close()

## Ring the phone
account = twilio.Account(config.ACCOUNT_SID, config.ACCOUNT_TOKEN)
d = {
    'From' : config.CALLER_ID,
    'To' : _phone,
    'Url' : config.ROOT + "/data/%s" %name,
}
try:
    print account.request('/%s/Accounts/%s/Calls' %(config.API_VERSION, config.ACCOUNT_SID), 'POST', d)
except Exception, e:
    print e
    print e.read()