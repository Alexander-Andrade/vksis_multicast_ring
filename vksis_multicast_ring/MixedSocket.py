from socket import*
import struct
import pickle
from Frame import Frame
import sys

class MixedSocket(socket):

    def __init__(self,family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None,**kwargs):
        super().__init__(family, type, proto, fileno, **kwargs)
        self.max_msg_size = self.get_recv_bufsize()
      
    def join_group(self,group_addr,interf_addr,multicast_scope=1):
        #self.mreq = struct.pack('4sl',inet_aton(group_addr),INADDR_ANY) if interf_addr==INADDR_ANY else struct.pack('4s4s',inet_aton(group_addr),inet_aton(interf_addr)) 
        self.mreq = struct.pack('4s4s',inet_aton(group_addr),inet_aton(interf_addr))
        self.setsockopt(IPPROTO_IP,IP_ADD_MEMBERSHIP,self.mreq)
        #default                                                        
        self.setsockopt(IPPROTO_IP,IP_MULTICAST_TTL,struct.pack('b',multicast_scope))

    def leave_group(self):
        self.setsockopt(SOL_IP,IP_DROP_MEMBERSHIP,self.mreq)

    def set_send_bufsize(self,value):
        self.setsockopt(SOL_SOCKET, SO_SNDBUF, value)

    def set_receive_bufsize(self,value):
        self.setsockopt(SOL_SOCKET, SO_RCVBUF,value)

    def get_send_bufsize(self):
        return self.getsockopt(SOL_SOCKET, SO_SNDBUF)

    def get_recv_bufsize(self):
        return self.getsockopt(SOL_SOCKET, SO_RCVBUF)

    def set_send_timeout(self,timeOutSec):
        if sys.platform.startswith('win'):
            timeval = timeOutSec * 1000
        elif sys.platform.startswith('linux'):   
            self.setsockopt(SOL_SOCKET, SO_SNDTIMEO, struct.pack("LL",timeOutSec,0) )

    def disable_send_timeout(self):
        if sys.platform.startswith('win'):
            timeval = 0
        elif sys.platform.startswith('linux'):
            self.setsockopt(SOL_SOCKET, SO_SNDTIMEO, struct.pack("LL",0,0))

    def set_recv_timeout(self,timeOutSec):
        if sys.platform.startswith('win'):
            timeval = timeOutSec * 1000
        elif sys.platform.startswith('linux'):   
            self.setsockopt(SOL_SOCKET, SO_RCVTIMEO, struct.pack("LL",timeOutSec,0))

    def disable_recv_timeout(self):
        if sys.platform.startswith('win'):
            timeval = 0
        elif sys.platform.startswith('linux'):
            self.setsockopt(SOL_SOCKET, SO_RCVTIMEO, struct.pack("LL",0,0))

    def recvfrom_with_discarding(self,sender_addr,len):
        while True:
           data,addr = sock.recvfrom(len)
           if addr == sender_addr:
               return data

    def send_obj_to(self,obj,addr):
        serialized_obj = pickle.dumps(obj)
        ser_obj_size = len(serialized_obj)
        self.sendto(struct.pack('!H',ser_obj_size),addr)
        self.sendto(serialized_obj,addr)

    def recv_obj_from(self):
        obj_len,addr = self.recvfrom(1024)
        #prevent the possibility of not reading enother udp-message
        serialized_obj=self.recvfrom_with_discarding(addr,obj_len)
        return pickle.loads(serialized_obj)
    
    def send_frame_to(self,frame,addr):
        bytes_frame = bytes(frame)
        self.sendto(bytes_frame,addr) 

    def recv_frame_from(self,**hints):
        type=hints.get('type')
        src_addr=hints.get('src_addr')
        dst_addr=hints.get('dst_addr')
        while True:
            bytes_frame,addr=self.recvfrom(self.max_msg_size)
            frame = Frame(frame=bytes_frame)
            if type is None and src_addr is None and dst_addr is None:
                return (frame,addr)
            elif type  and type != frame.type: continue
            elif src_addr and src_addr != frame.src_addr : continue
            elif dst_addr and dst_addr != frame.dst_addr : continue

            

                



        
         

    