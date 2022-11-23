class globalVariables:
    # I wanna test everything by making simple get requests
    STRICT = False
    # And this for just some debugging things
    DEBUG = True

    @staticmethod
    def isEmpty(string):
        return string is not None and string.__len__() > 0