import time

import requests
import json

class aeqTerrs:

    ownedTerrs = []
    newTerrs = {}

    def update(self):

        toRemove = []
        for newTerr in self.newTerrs:
            if time.time() - self.newTerrs[newTerr] > 5*60:
                toRemove.append(newTerr)
        for remove in toRemove:
            self.newTerrs.pop(remove)

        terrs = requests.get("https://api.wynncraft.com/public_api.php?action=territoryList")
        terrs = json.loads(terrs.text)
        ownedTerrsNow = []
        for terr in terrs["territories"]:
            name = terrs["territories"][terr]["guild"]
            if name == "Aequitas":
                if not self.ownedTerrs.__contains__(name):
                    self.newTerrs[name] = time.time()
                ownedTerrsNow.append(name)
        self.ownedTerrs = ownedTerrsNow.copy()

