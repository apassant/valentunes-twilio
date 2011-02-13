import os, sys
import web

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
    
    def GET(self):
        args = web.input()

        ## Check required parameters
        if '_to' not in args.keys():
            return "_to parameter required (name of the person you want to call)"
        if '_from' not in args.keys():
            return "_from parameter required (your name)"
        if '_phone' not in args.keys():
            return "_phone parameter required (phone number to ring)"

        ## No songs ?
        if '_songs' not in args.keys():
            songs = [(config.DEFAULT_SONG_TITLE, config.DEFAULT_SONG),
                       (config.DEFAULT_SONG_TITLE, config.DEFAULT_SONG)]
        else:
            songs = args._songs

        ## Additional parameters
        options = {}
        if '_msg' in args.keys():
            options['_msg'] = args._msg
        if '_voice' in args.keys():
            options['_voice'] = args._voice

        ## Go !
        val = valentunes.Valentunes(args._phone, songs, args._from, args._to, options = options)
        return val.call()

application = web.application(urls, globals()).wsgifunc()