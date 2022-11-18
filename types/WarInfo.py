import time


class warInfo:
    '''
        These are gonna be used for deciding if a terr we have lost the war
        Is gonna be used for counting or not
    '''
    startConfermations = 0
    endConfermations = 0
    location = None

    def __init__(self, players, ip):
        self.players = set(players)
        self.ip = ip
        self.start = time.time()

    def increasePreConfermation(self):
        self.startConfermations += 1

    def increasePostConfermation(self):
        self.endConfermations += 1

    def samePlayers(self, players):
        return set(players) == self.players
