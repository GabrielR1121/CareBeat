class Caree:
    '''
    Class for the Caree
    '''
    def __init__(self, id, first_name, paternal_last_name):

        '''
        Constructor to assign the needed variables
        '''
        self.id = id
        self.first_name = first_name
        self.paternal_last_name = paternal_last_name

    def get_full_name(self):
        '''
        Returns the full name of the Caree
        '''
        return f"{self.first_name} {self.paternal_last_name}"



class Caretaker:
    '''
    Class for the Caree
    '''
    def __init__(self, id):
        '''
        Constructor to assign the needed variables
        '''
        self.id = id


class Medication:
    '''
    Class for the Caree
    '''
    def __init__(self, id, name):
        '''
        Constructor to assign the needed variables
        '''
        self.id = id
        self.name = name
