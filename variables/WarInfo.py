import time


class warInfo:

    '''
        These are gonna be used for deciding if a terr we have lost the war
        Is gonna be used for counting or not
    '''
    def __init__(self, players, ip, location):
        self.players = list(set(players))
        self.ip = ip
        self.start = time.time()
        self.startConfermations = 0
        self.endConfermations = 0
        self.location = location
        self.situation = None

    def increasePreConfermation(self):
        self.startConfermations += 1

    def increasePostConfermation(self):
        self.endConfermations += 1

    def samePlayers(self, players):
        return list(set(players)) == self.players

    def __str__(self):
        return f"{self.players} {self.location} {self.situation} {self.startConfermations} {self.endConfermations}"
