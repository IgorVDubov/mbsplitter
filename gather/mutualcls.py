class NewID:
    '''
    auto increment id generator
    use: id = NewID()
    '''
    _id: int = 0

    def __new__(cls):
        cls._id += 1
        return cls._id

