import os, sys
import web
import simplejson

path = os.path.dirname(__file__)
sys.path.append("%s/" %path)

import valentunes
import config

urls = (
    '/call', 'Call',
    '/change', 'Change',
)

class Change:
    def GET(self):
        args = web.input()
        ## Check required parameters
        if '_uid' not in args.keys():
            return "_uid parameter required (user ID)"
        ## Go !
        switch = valentunes.Switcher(args)
        return switch.go()

class Call:
    
    def POST(self):
        args = web.input()
        
        ## Get data
        if 'data' in args.keys():
            
            ## Parse JSON
            data = simplejson.loads(args['data'])
            
            ## Required parameters
            if 'to' not in data.keys():
                return "to parameter required (name of the person you want to call)"
            _to = data['to']
            if 'from' not in data.keys():
                return "from parameter required (your name)"
            _from = data['from']
            if 'phone' not in data.keys():
                return "phone parameter required (phone number to ring)"
            _phone = data['phone']
            if 'songs' not in data.keys():
                return "songs parameter required (list of songs)"
            _songs = data['songs']
            
            ## Additional parameters
            _message = ''
            if 'message' in data.keys():
                _message = data['message']
            _voice = 'man'
            if 'voice' in data.keys():
                _voice = data['voice']

            ## Go !
            return valentunes.Valentunes(_phone, _songs, _from, _to, message = _message, voice = _voice).call()

        else:
            return "KO"

application = web.application(urls, globals()).wsgifunc()