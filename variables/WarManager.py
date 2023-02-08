import threading
import time

from Globals import globalVariables
from variables.WarInfo import warInfo


class warManager:

    lockWars = threading.Lock()

    def __init__(self, terrPointer):
        self.terrPointer = terrPointer
        self.startedWars = []
        self.endedWars = []

    def addWar(self, players, ip, location):
        self.lockWars.acquire()
        self.startedWars.append(warInfo(players.split(","), ip, location))
        self.lockWars.release()

    '''
        This function get called when someone finish a war.
        It's needed for updating started wars into ended wars with the correct way
    '''
    def feedback(self, players, situation, location, ip):
        # If it's empty, then the message is from someone that is not in war
        if globalVariables.isEmpty(players):
            # If it's from someone in chat, increase post
            if (war := self.locationInWar(location)) is not None:
                # If we lost
                if not situation:
                    # TODO: this makes the server crash lol
                    if self.endedWars.index(war) == -1:
                        self.endedWars.append(war)
                        self.startedWars.pop(self.startedWars.index(war))
                self.lockWars.acquire()
                war.increasePostConfermation()
                self.lockWars.release()
                if globalVariables.DEBUG:
                    print("War increase: " + str(war))
            # Else, we'll think about it later
            else:
                if globalVariables.DEBUG:
                    print("Uknwon terr: " + location + " players: " + players + " ip: " + ip)
        # If it's not empty then we are in war
        else:
            listPlayers = players.split(",")
            # Get the war, this should always be true
            if (war := self.playersInWar(listPlayers)) is not None:
                self.lockWars.acquire()
                # If it's the first time, set location and win
                if war.situation is None:
                    war.location = location
                    war.situation = True
                    # Now we need to remove war from the startedWar and put it in endedWar
                    self.endedWars.append(war)
                    self.startedWars.pop(self.startedWars.index(war))
                    if globalVariables.DEBUG:
                        print("War confirmed pre: " + str(war))
                # Else, increase confermation
                else:
                    war.increasePostConfermation()
                    if globalVariables.DEBUG:
                        print("War confirmed post: " + str(war))
                self.lockWars.release()

    '''
        This function return a list with players that have
        done an ffa
    '''
    def ffaUpdate(self):
        self.lockWars.acquire()
        players = []
        for i in range(self.endedWars.__len__()):
            add = False
            if self.endedWars[i].situation:
                if self.wonTerrChecker(self.endedWars[i]) or globalVariables.DEBUG:
                    add = True
            elif self.lostTerrChecker(self.endedWars[i]):
                add = True
            if add:
                if globalVariables.DEBUG:
                    print("War finished: " + str(self.endedWars[i]))
                players.extend(self.endedWars[i].players)
                self.endedWars.pop(i)
                i -= 1
            else:
                # Time checker
                if time.time() - self.endedWars[i].start >= 60*60*5:
                    # SUS
                    print("Sus")
                pass
        self.lockWars.release()
        return players

    '''
        For wars that we won we just check if we have just got that terr
    '''
    def wonTerrChecker(self, war):
        if not globalVariables.STRICT or self.terrPointer.newTerrs.keys().__contains__(war.location):
            return True
        return False

    '''
        For wars we lost, we need:
        1) There must be more peo
    '''
    @staticmethod
    def lostTerrChecker(war):
        return war.startConfermations < war.endConfermations

    '''
        Util that, given a list of players, check if these players are in somekind of war
    '''
    def playersInWar(self, players):
        for war in self.startedWars:
            if war.samePlayers(players):
                return war
        for war in self.endedWars:
            if war.samePlayers(players):
                return war
        return None

    '''
        Givena  location, return the war with that location    
    '''
    def locationInWar(self, location):
        wars = []
        wars.extend(self.startedWars)
        wars.extend(self.endedWars)
        for war in wars:
            if war.location == location:
                return war
        return None
