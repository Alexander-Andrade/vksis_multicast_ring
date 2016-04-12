import struct
from FrameType import*
import pickle
from socket import*


class Frame:
    #for all on the bus
    NOT_ADDRESSED = ('255.255.255.255',0)

    def __init__(self,**kwargs):
        self.dst_addr = kwargs.get('dst_addr', Frame.NOT_ADDRESSED)
        self.src_addr = kwargs.get('src_addr', Frame.NOT_ADDRESSED)
        self.type = kwargs.get('type',FrameType.Data)
        self.data = kwargs.get('data',b'')
        self.frame = kwargs.get('frame',b'')
        if self.frame != b'':
            self.unpack()

    
    def pack(self):
        data = self.data if type(self.data) is bytes else pickle.dumps(self.data)
        self.frame = struct.pack('!4sH4sHB',inet_aton(self.dst_addr[0]), self.dst_addr[1], inet_aton(self.src_addr[0]), self.src_addr[1], self.type.value) + data
        return self.frame
         
    def unpack(self, frame=None):
        if frame:
            self.frame = frame
        header_size = struct.calcsize('4sH4sHB')
        b_dst_addr_0, dst_addr_1, b_src_addr_0, src_addr_1, type_val = struct.unpack('!4sH4sHB',self.frame[:header_size])
        self.dst_addr = ( inet_ntoa(b_dst_addr_0), dst_addr_1)
        self.src_addr = ( inet_ntoa(b_src_addr_0), src_addr_1)
        self.type = FrameType(type_val)
        bytes_data = self.frame[header_size:]
        if len(bytes_data):
            self.data = pickle.loads(bytes_data)
        return(self.dst_addr , self.src_addr, self.type, self.data)

    def __repr__(self):
            return 'Frame (dst_addr={},src_addr={},type={},data={})'.format(self.dst_addr, self.src_addr,self.type, self.data)

    def __bytes__(self):
        return self.frame if self.frame != b'' else self.pack()

    

    
        
    