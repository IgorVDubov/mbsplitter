class Singleton:  # pylint: disable=too-few-public-methods
    """Singleton base class.

    https://mail.python.org/pipermail/python-list/2007-July/450681.html
    """

    def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
        """Create a new instance."""
        if "_inst" not in vars(cls):
            cls._inst = object.__new__(cls)
        return cls._inst


class SourceTypes(Singleton):
    MODBUS_TCP = 1
    
    
class Formats(Singleton):
    CO = 1
    DI = 2
    HR = 3
    IR = 4
    
class ModbusFuncs(Singleton):
    READ_CO = 1
    READ_DI = 2
    READ_HR = 3
    READ_IR = 4
    WRITE_CO = 5
    WRITE_HR = 6
    WRITE_MULT_CO = 15
    WRITE_MULT_HR = 16
    

class DeviceProtocol(Singleton):
    MODBUS='ModBus'

