

class UnsufficientFunds(Exception):
    
    _msg = 'Some!'

    def __init__(self):
        super().__init__(self._msg)
