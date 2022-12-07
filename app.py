"""
    TODO:
    - Create database

    NOTE: for now i havent run this code once. I have no idea if it works.
          I'm waiting for more code before testing it
    - Take who is in war based on distance
"""
import threading
import time

from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from Globals import globalVariables
from variables.AeqTerrs import aeqTerrs
from variables.SpamManager import spamManager
from variables.WarManager import warManager


class Server:


    def __init__(self, name):
        self.app = Flask(name)
        self.limiter = Limiter(
            self.app,
            key_func=get_remote_address,
            # Maybe it's too high, but eh who cares
            default_limits=["99/minute"],
            storage_uri="memory://",
        )
        self.blockedIp = []
        self.players = {}
        self.inWars = False
        self.warTime = -1
        self.active = True
        self.terrs = aeqTerrs()
        self.managerWar = warManager(self.terrs)
        self.managerSpam = spamManager()

        '''
            Why would anyone go to the index?
            Because he is testing! 
            Oh yeha we also redirect who get rate limited
        '''
        @self.app.route('/')
        @self.app.errorhandler(429)
        @self.limitUser
        def __index():
            if globalVariables.STRICT:
                self.addIpBlocked(request.remote_addr)
            if globalVariables.DEBUG:
                print("Why are you here " + request.remote_addr)
            return "Index"

        '''
            This may not be sure, but i want this in case someone of us get banned
        '''
        @self.app.route('/discover', methods=['GET', 'POST'])
        @self.limiter.limit("4/minute")
        @self.limitUser
        def discover(ip):
            player = request.args.get('player')
            if globalVariables.STRICT and (request.method == 'GET' or globalVariables.isEmpty(self.players) or request.headers.get('test') is not None):
                self.addIpBlocked(ip)
            else:
                if not self.players.__contains__(player):
                    self.players[player] = {
                        "ip": [],
                        "count": 0
                    }
                self.players[player]["ip"].append(request.remote_addr)
                if globalVariables.DEBUG:
                    print(player + ": " + request.remote_addr)
            return "Yes"

        '''
            This function is an extra confermation if
            People are actually doing wars or not.
            We want to add multiple steps, even if they seems useless.
            When someone is coding they may forget a detail, and then they get banned.

            Oh yeha and the route is test so that maybe people think it's useless :P
            Here we ban if the request is get
        '''
        @self.app.route('/test', methods=['GET', 'POST'])
        @self.limitUser
        def test(ip):
            if globalVariables.STRICT and request.method == 'GET':
                self.blockedIp.append(ip)
            else:
                self.inWars = True
                self.warTime = time.time()
                if globalVariables.DEBUG:
                    print("started war timer")
            return "Yes"

        '''
            Here we ban someone if they make a get request
            Params:
            - players
            - location
        '''
        @self.app.route('/startWar', methods=['GET', 'POST'])
        @self.warCheck
        @self.limitUser
        def startWar(ip):
            players = request.args.get('players')
            location = request.args.get('terr')
            # Ban
            if globalVariables.STRICT and (globalVariables.isEmpty(players) or globalVariables.isEmpty(location) or request.method == 'GET'):
                if globalVariables.DEBUG:
                    print("A guy spammed a bit " + ip)
                self.blockedIp.append(ip)
                return "Yes"

            # If we already have it in the war list then we know they are both in war
            if (war := self.managerWar.locationInWar(location)) is not None:
                war.increasePreConfermation()
                if globalVariables.DEBUG:
                    print("Increased war " + war)
            else:
                # And also spam manager
                if self.managerSpam.isSpamming(ip, 0):
                    self.blockedIp.append(ip)
                    return "Yes"
                else:
                    # Else, just append it
                    self.managerWar.addWar(players, ip, location)
                    if globalVariables.DEBUG:
                        print("New war " + players)
            return "Yes"

        '''
            We ban with a post request
            Params:
            - Win/Loose
            - Players
            - Location
        '''
        @self.app.route('/endWar', methods=['GET', 'POST'])
        @self.warCheck
        @self.limitUser
        def endWar(ip):
            players = request.args.get('players')
            situation = request.args.get('situation')
            location = request.args.get('location')
            # Ban.
            if globalVariables.STRICT and (globalVariables.isEmpty(situation) or globalVariables.isEmpty(location) or request.method == 'POST'):
                self.addIpBlocked(ip)
                return "Yes"
            self.managerWar.feedback(players, situation, location, ip)

            return 'Yes'

    # Main function that update aeq terrs and war variables
    def mainChecker(self):
        while self.active:
            self.terrs.update()
            self.updateVariables()
            time.sleep(10)

    '''
        Function that
        - Reset the inWars variable after 6 minutes nobody has done a war
        - Get every people that did an ffa, and increase the counter
    '''
    def updateVariables(self):
        self.managerSpam.update()
        if self.inWars:
            if time.time() - self.warTime > 60 * 6:
                self.inWars = False
            players = self.managerWar.ffaUpdate()
            for player in players:
                if self.players.__contains__(player):
                    self.players[player]["counter"] += 1


    # region Utils
    def addIpBlocked(self, ip):
        if not self.blockedIp.__contains__(ip):
            print("Banned " + ip)
            self.blockedIp.append(ip)

    # endregion

    # region Wrappers
    def limitUser(self, func):
        def wrap(_=None):
            if not self.blockedIp.__contains__(request.remote_addr):
                # If the header doesnt have the "test" tag we know it's somekind of artificial request
                if not globalVariables.STRICT or request.headers.get('test') is not None:
                    return func(request.remote_addr)
                else:
                    self.blockedIp.append(request.remote_addr)
                    return "Yes"
            else:
                # We always return yes so that people have no idea if they have been banned or not
                return "Yes"

        wrap.__name__ = func.__name__
        return wrap

    def warCheck(self, func):
        def wrap(_=None):
            if not self.blockedIp.__contains__(request.remote_addr):
                if self.inWars:
                    return func(request.remote_addr)
                else:
                    self.blockedIp.append(request.remote_addr)
                    return "Yes"
            else:
                return "Yes"

        wrap.__name__ = func.__name__
        return wrap

    # endregion

    def run(self, host, port):
        threading.Thread(target=self.mainChecker).start()
        self.app.run(host=host, port=port)


def main():
    server = Server(__name__)
    server.run(host='127.0.0.1', port=5000)


if __name__ == '__main__':
    main()
