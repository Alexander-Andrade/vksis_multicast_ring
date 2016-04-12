import threading
import struct
import time
import random
import math
from socket import*
from FrameType import FrameType
from net_interface import*
from MixedSocket import MixedSocket
from Frame import Frame
                                            
def random_unum(str_num_type,min=0):
    return random.randrange(min, int(math.pow(2, struct.calcsize(str_num_type)*8)))

class Host:

    def __init__(self,group,group_port,**kwargs):
        #host id unsigned long long
        self.id = random_unum('H')
        self.group_port = int(group_port)
        self.group = group
        self.interf_ip = interface_ip()
        self.group_sock = MixedSocket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
        #can listen a busy port 
        self.group_sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.group_sock.bind((self.interf_ip,self.group_port))
        self.group_sock.join_group(self.group, self.interf_ip)
        self.private_sock = MixedSocket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
        self.min_frame_gap = kwargs.get('min_frame_gap',3)
        self.max_frame_gap = kwargs.get('max_frame_gap',8)
        self.host_as_peer = (self.interf_ip, self.id)
        self.peer_sendto = None
        self.peer_recvfrom = None
        self.is_tail = True
        self.is_head = False
        self.peers = []
        self.max_greeting_reply_time = 3
        self.actions = {FrameType.Data : self.handle_data,
                        FrameType.GreetingRequest : self.handle_greeting_reguest,
                        FrameType.GreetingReply : self.handle_greeting_reply,
                        FrameType.Leaving : self.handle_leaving,
                        FrameType.Jam : self.handle_jam}
        self.stop_sending_thread_event = threading.Event()  
        self.frame_sending_thread = threading.Thread(target=self.frame_sending_routine,args=(self.stop_sending_thread_event,))

    def handle_data(self, frame):
        #skip data
        pass

    def reg_unknown_peer(self,peer):
        if peer not in self.peers:
            self.peers.append(peer)
    
    def stop_sending_thread(self):
        self.stop_sending_thread_event.clear()

    def resume_sending_thread(self):
        self.stop_sending_thread_event.set()

    def handle_greeting_reguest(self, frame):
        if self.is_tail:
            #stop sending data, it overflows udp receive buffer
            self.stop_sending_thread()
            peer = frame.src_addr
            #when this host was the first
            if not self.peers:
                self.is_head = True
            #append self to the end once? while this host is tail
            self.peers.append(self.host_as_peer) 
            self.group_sock.send_frame_to(Frame(dst_addr=peer, src_addr=self.host_as_peer, type=FrameType.GreetingReply, data=self.peers),(self.group,self.group_port))
            #put new tail to the peers
            self.reg_unknown_peer(peer)
            #change topology
            self.peer_sendto = peer
            self.resume_sending_thread()
        if self.is_head:
            self.stop_sending_thread()
            #change topology
            self.peer_recvfrom = peer
            self.resume_sending_thread()

    def handle_greeting_reply(self, frame):
        #get peers-list from other peer 
        self.peers = frame.data
        #change topology
        self.peer_sendto = self.peers[0]
        self.peer_recvfrom = frame.src_addr
        #began sending to peers 
        self.resume_sending_thread()


    def handle_leaving(self, frame):
        #more complex
        if peer in self.peers:
            self.peers.remove(frame.src_addr)

    def delay_to_prepare_frame(self):
        #randomize sending activity
        nextframe_t = random.uniform(self.min_frame_gap, self.max_frame_gap)
        print('prepare new frame={} s'.format(nextframe_t),flush=True)
        #waiting when next frame will be ready to transfer
        time.sleep(nextframe_t)

    def frame_sending_routine(self,stop_sending_thread_event):
        while True:
            self.delay_to_prepare_frame()
            #if there is need to stop srnding messages
            stop_sending_thread_event.wait()
            if self.peers: 
                self.private_sock.send_frame_to(Frame(src_addr=self.host_as_peer, dst_addr=self.peer_sendto, data='data'), (self.group, self.group_port)) 
            
    def am_i_recepient(self, frame):
        #if there is no target address in frame
        #see source address, if it = this host -> this packet ton for tis host
        if frame.dst_addr == Frame.NOT_ADDRESSED and frame.src_addr == self.host_as_peer:
            return False
        elif frame.dst_addr == Frame.NOT_ADDRESSED and frame.src_addr != self.host_as_peer:
            return True
        elif frame.dst_addr == self.host_as_peer:
            return True
        else:
            return False

    def group_listening_and_replies(self):
        while True:
            frame,phis_addr = self.group_sock.recv_frame_from()
            #test if frame is from this host
            if not self.am_i_recepient(frame):
                print('ring transit from {} to {}'.format(frame.src_addr,frame.dst_addr))
                continue
            #mark that the foreign frame arrived
            print(repr(frame))
            self.actions[frame.type](frame)


    def run(self):
        #notify all devices on the bus
        self.group_sock.send_frame_to(Frame(src_addr=self.host_as_peer, type=FrameType.GreetingRequest), (self.group, self.group_port))
        #start sending some data to the peers
        self.frame_sending_thread.start()
        #listen bus and act accordinatly
        self.group_listening_and_replies()