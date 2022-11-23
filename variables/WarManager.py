import threading

import app
from variables.UnknownTerr import unknownTerr
from variables.WarInfo import warInfo


class warManager:
    startedWars = []
    endedWars = []
    unkownEndedWars = []
    lockWars = threading.Lock()

    def __init__(self, terrPointer):
        self.terrPointer = terrPointer

    def addWar(self, players, ip):
        self.lockWars.acquire()
        self.startedWars.append(warInfo(players.split(","), ip))
        self.lockWars.release()

    def feedback(self, players, situation, location, ip):
        # If it's empty, then the message is from someone that is not in war
        if app.Server.isEmpty(players):
            # If it's from someone in chat, increase post
            if war := self.locationInWar(location) is not None:
                self.lockWars.acquire()
                war.increasePostConfermation()
                self.lockWars.release()
            # Else, we'll think about it later
            else:
                self.unkownEndedWars.append(unknownTerr(location, ip, True if situation == "win" else False))
        # If it's not empty then we are in war
        else:
            listPlayers = players.split(",")
            # Get the war, this should always be true
            if war := self.playersInWar(listPlayers) is not None:
                self.lockWars.acquire()
                # If it's the first time, set location and win
                if war.location is not None:
                    war.location = location
                    war.win = True
                # Else, increase confermation
                else:
                    war.increasePostConfermation()
                self.lockWars.release()

    def playersInWar(self, players):
        for war in self.startedWars:
            if war.samePlayers(players):
                return war
        for war in self.endedWars:
            if war.samePlayers(players):
                return war
        return None

    def locationInWar(self, location):
        for war in self.endedWars:
            if war.location == location:
                return war
        return None
