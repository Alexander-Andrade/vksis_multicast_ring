from socket import*

def interface_ip(list=False,**kwargs):
    hostname = kwargs.get('hostname',gethostname())
    proto = kwargs.get('proto',AF_INET)
    hint = kwargs.get('hint')
    addrInfoList = getaddrinfo(hostname,None,proto)
    #127.0.0.0/8 - loopback IP addresses
    ip_list = [addr_info[4][0] for addr_info in addrInfoList if not addr_info[4][0].startswith('127.')] if not hint else \
              [addr_info[4][0] for addr_info in addrInfoList if addr_info[4][0].startswith(hint)]
    if list:
        return ip_list  
    return min(ip_list) if ip_list else None