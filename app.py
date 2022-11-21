'''
    TODO:
    - Check aeq terrs changes
    - reset variable inWars after a bit
    - Create thread for managing wars and unknown
    - Better ip blocking system
        - Illegal requests
    - Create database
    - People could increase their ffa count if they say that they are loosing
        Kinda have to troubleshoot this
    - Check if multiple people are claiming the same terr

    NOTE: for now i havent run this code once. I have no idea if it works.
          I'm waiting for more code before testing it
    - Take who is in war based on distance
'''
import time

from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from variables.AeqTerrs import aeqTerrs
from variables.UnknownTerr import unknownTerr
from variables.WarInfo import warInfo
import threading

app = Flask(__name__)
wars = []
blockedIp = []
unkown = []
players = {}
inWars = False
warTime = -1
active = True
lockWars = threading.Lock()
terrs = aeqTerrs()

limiter = Limiter(
    app,
    key_func=get_remote_address,
    # Maybe it's too high, but eh who cares
    default_limits=["99/minute"],
    storage_uri="memory://",
)


def addIpBlocked(ip):
    if not blockedIp.__contains__(ip):
        blockedIp.append(ip)


def isEmpty(string):
    return string is not None and string.__len__() > 0


def limitUser(func):
    def wrap():
        if not blockedIp.__contains__(request.remote_addr):
            # If the header doesnt have the "test" tag we know it's somekind of artificial request
            if request.headers.get('test') is not None:
                func(request.remote_addr)
            else:
                blockedIp.append(request.remote_addr)
                return "Yes"
        else:
            # We always return yes so that people have no idea if they have been banned or not
            return "Yes"

    return wrap


def warCheck(func):
    def wrap():
        if not blockedIp.__contains__(request.remote_addr):
            if inWars:
                func(request.remote_addr)
            else:
                blockedIp.append(request.remote_addr)
                return "Yes"
        else:
            return "Yes"

    return wrap


# Some functions for leaning the body of the code
def playersInWar(players):
    for war in wars:
        if war.samePlayers(players):
            return war
    return None


def locationInWar(location):
    for war in wars:
        if war.location == location:
            return war
    return None


'''
    This is when someone get api limited
    We dont wanna know other people that they are api limited, so just say "yes"
'''


@app.errorhandler(429)
def ratelimit_handler():
    addIpBlocked(request.remote_addr)
    return "Yes"


'''
    This may not be sure, but i want this in case someone of us get banned
'''


@app.route('/discover', methods=['GET', 'POST'])
@limiter.limit("4/minute")
def discover():
    player = request.args.get('player')
    if request.method == 'GET' or isEmpty(players) or request.headers.get('test') is not None:
        addIpBlocked(request.remote_addr)
    else:
        if not players.__contains__(player):
            players[player] = []
        players[player].append(request.remote_addr)


'''
    This function is an extra confermation if
    People are actually doing wars or not.
    We want to add multiple steps, even if they seems useless.
    When someone is coding they may forget a detail, and then they get banned.
    
    Oh yeha and the route is test so that maybe people think it's useless :P
'''


@app.route('/test', methods=['GET', 'POST'])
@limitUser
def startWar(_):
    inWars = True
    warTime = time.time()
    return "Yes"


'''
    Params:
    - players
'''


@app.route('/startWar', methods=['GET', 'POST'])
@warCheck
@limitUser
def startWar(ip):
    players = request.args.get('players')
    # I have to decide if we should ban these people or if it's possible that a tcp makes errors
    if isEmpty(players):
        return "Yes"

    # If we already have it in the war list then we know they are both in war
    listPlayers = players.split(",")
    if war := playersInWar(listPlayers) is not None:
        war.increasePreConfermation()
    else:
        # Else, just append it. We need lockers because multithreading can be funny
        lockWars.acquire()
        wars.append(warInfo(players.split(","), ip))
        lockWars.release()
    return "Yes"


'''
    Params:
    - Win/Loose
    - Players
    - Location
'''


@app.route('/endWar', methods=['GET', 'POST'])
@warCheck
@limitUser
def endWar(ip):
    players = request.args.get('players')
    situation = request.args.get('situation')
    location = request.args.get('location')
    # Have to think if this is bannable
    if isEmpty(situation) or isEmpty(location):
        return "Yes"
    # If it's empty, then the message is from someone that is not in war
    if isEmpty(players):
        # If it's from someone in chat, increase post
        if war := locationInWar(location) is not None:
            lockWars.acquire()
            war.increasePostConfermation()
            lockWars.release()
        # Else, we'll think about it later
        else:
            unkown.append(unknownTerr(location, ip, True if situation == "win" else False))
    # If it's not empty then we are in war
    else:
        listPlayers = players.split(",")
        # Get the war, this should always be true
        if war := playersInWar(listPlayers) is not None:
            lockWars.acquire()
            # If it's the first time, set location and win
            if war.location is not None:
                war.location = location
                war.win = True
            # Else, increase confermation
            else:
                war.increasePostConfermation()
            lockWars.release()

    return 'Yes'


'''
    Here we update variables, so:
    - People that are doing ffa
    - is War active
'''


def updateVariables():
    global inWars
    if inWars:
        if time.time() - warTime > 60 * 6:
            inWars = False


def mainChecker():
    while active:
        terrs.update()
        updateVariables()
        time.sleep(10)


if __name__ == '__main__':
    threading.Thread(target=mainChecker).start()
    app.run()
