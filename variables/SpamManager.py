import time


class spamManager:
    '''
        0: created war
    '''

    class typeRequest:
        def __init__(self, type):
            self.time = time.time()
            self.type = type

    def __init__(self):
        self.clients = {}

    '''
        True/False means ban
    '''
    def isSpamming(self, ip, kind):
        if not self.clients.__contains__(ip):
            self.clients[ip] = []
        if self.hasSpammed(self.clients[ip], kind):
            return True
        self.clients[ip].append(self.typeRequest(kind))
        return False

    @staticmethod
    def hasSpammed(client, kind):
        count = 0
        for req in client:
            if req.type == kind:
                count += 1
        if kind == 0:
            if count >= 10:
                return True
        return False

    def update(self):
        for i in self.clients:
            for j in range(len(self.clients[i])):
                if time.time() - self.clients[i][j].time >= 60 * 1:
                    self.clients[i].pop(j)
                    j -= 1

