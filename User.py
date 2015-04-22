# User model
class User:
    def __init__(self):
        self.email = ""
        self.name = ""
    def SetName(self, name):
        print 'Name =', name
        self.name = name
        return self.name
    def GetName(self):
        return self.name
