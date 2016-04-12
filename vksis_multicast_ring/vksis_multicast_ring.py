import sys
import random
from Host import Host


if __name__ == '__main__':
     random.seed()
     host = Host(sys.argv[1],sys.argv[2], min_frame_gap=3 , max_frame_gap=8)
     host.run()