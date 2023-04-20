import struct
from typing import Union 


def getBit(byte,position):
    '''
    return bit at position in byte (from 0)
    '''
    return byte & 1 << position != 0


def packFloatToCDAB(f:float)->list:
    '''
    pack float to 2 words LOW HIGH \n
    return [LOW_16_byte, HIGH_16_byte]
    '''
    b=[i for i in struct.pack('<f',f)]
    return [b[i+1]*256+b[i] for i in range(0,len(b),2)]

def unpackCDABToFloat(two_words:list,round_count:int=None)->Union[float,None]:
    '''
    unpack list [LOW_16bit, HIGH_16bit] \n
    return [LOW_16_byte, HIGH_16_byte] \n
    round to round_count if exist
    '''
    try:
        hex_data=two_words[1].to_bytes(2,byteorder='big')+two_words[0].to_bytes(2,byteorder='big')
    except Exception as e:
        print (f'unpackABCDToFloat: Exception {e} list in parameters: {two_words}')
        return None
    try:
        result=struct.unpack('!f', hex_data)[0]
        if round_count:
            return round(result, round_count)
        else:
            return result
    except Exception:
        print(f"unpackCDABToFloat: can't unpack {two_words}")
        return None

def unpackABCDToFloat(two_words:list,round_count:int=None)->Union[float,None]:
    '''
    unpack list [LOW_16bit, HIGH_16bit] \n
    return [LOW_16_byte, HIGH_16_byte] \n
    round to round_count if exist
    '''
    try:
        hex_data=two_words[0].to_bytes(2,byteorder='big')+two_words[1].to_bytes(2,byteorder='big')
    except Exception as e:
        print (f'unpackABCDToFloat: Exception {e} list in parameters: {two_words}')
        return None
    try:
        result=struct.unpack('!f', hex_data)[0]
        if round_count:
            return round(result, round_count)
        else:
            return result
    except Exception:
        print(f"unpackCDABToFloat: can't unpack {two_words}")
        return None

def tests():
    a=4.01
    print (f'testing pack/unpackCDABToFloat: {a== unpackCDABToFloat(packFloatToCDAB(a),2)}')

if __name__ == "__main__":
    a=unpackABCDToFloat([0,0],2)
    print (getBit(655,0))

    # tests()
    # r=packFloatToCDAB(29.01)
    # print (r)
    # r=packFloatToCDAB(4.01)
    # print (r)
    # f=unpackCDABToFloat(r,2)
    # print(f)
