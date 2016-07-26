"""Validates config file before sending."""
import re


def parse_ip4_address(s):
    """parse an ip4 address."""
    # split string into octets
    octets_s = s.split(".")
    octets = []

    # more than four octets?
    if (len(octets_s) != 4):
        return False

    index = 0
    # validate each octet
    for octet in octets_s:

        # validate it's actually an integer
        if not octet.isdigit():
            return False

        # convert to integer
        intConvert = int(octet)

        if intConvert < 0 or intConvert > 255:
            return False
        octets.append(intConvert)
        index = index + 1

    # valid address
    return octets


def parse_ip4_netmask(octets):
    """parse an ip4 netmask and check validity."""
    size = 0
    index = 0
    for octet in octets:
        # ensure no gaps between octets
        print index * 8
        print size * 8
        print octet

        if not index * 8 == size * 8 and not octet == 0:
            return False
        else:
            index = index + 1

        if octet == 255:
            size = size + 1
        elif octet == 254:
            size = size + 1
        elif octet == 252:
            size = size + 1
        elif octet == 248:
            size = size + 1
        elif octet == 240:
            size = size + 1
        elif octet == 224:
            size = size + 1
        elif octet == 192:
            size = size + 1
        elif octet == 128:
            size = size + 1
        elif octet == 0:
            break
        else:
            return False

    # valid
    return size * 8


def parse_ip4_netsize2mask(size):
    octets = []
    full = size / 8
    rem = size % 8

    # pad first octets with 255
    i = 0
    while(i < full):
        octets[i] = 255
        i += 1

    # insert important octet
    if(rem == 0):
        octets[i] = 0
        i += 1
    elif(rem == 1):
        octets[i] = 128
        i += 1
    elif(rem == 2):
        octets[i] = 192
        i += 1
    elif(rem == 3):
        octets[i] = 224
        i += 1
    elif(rem == 4):
        octets[i] = 240
        i += 1
    elif(rem == 5):
        octets[i] = 248
        i += 1
    elif(rem == 6):
        octets[i] = 252
        i += 1
    elif(rem == 7):
        octets[i] = 254
        i += 1
    else:
        # impossible
        return False

    while(i < 4):
        octets[i] = 0

    # finished
    return octets


def validate_ip4_address(octets):
    """ensure network ip is valid."""
    if octets[0] == 0 or octets[0] == 127 or (octets[0] > 224 and octets[0] < 240):
        return False
    if octets[0] == 255 and octets[1] == 255 and octets[2] == 255 and octets[3] == 255:
        return False

    return True


def mask_ip4_address(ip, mask):
    """Mask the ip address."""
    ret = []
    i = 0
    while i < 4:
        ret[i] = ip[i] & mask[i]

    return ret


def compare_ip4_address(ip, ip2):
    """compare two ip4 addresses."""
    i = 0
    while(i < 4):
        if(not ip[i] == ip2[i]):
            return False
        i += 1
    return True


def validate_ip4(ip_s, netmask_s, gateway_s):
    """Validate ip4 address."""

    # ip
    ip = parse_ip4_address(ip_s)
    # if our ip address is not a real address
    if not ip:
        return False
    if not validate_ip4_address(ip):
        return False

    # netmask
    netmask = parse_ip4_address(netmask_s)
    if not netmask:
        return False
    netsize = parse_ip4_netmask(netmask)
    if netsize < 8 or netsize > 30:
        return False

    # network
    ip_net = mask_ip4_address(ip, netmask)

    # gateway
    if gateway_s:
        gateway = parse_ip4_address(gateway_s)
        if not gateway:
            return False
        if not validate_ip4_address(gateway):
            return False

        gateway_net = mask_ip4_address(gateway, netmask)
        # gateway is on ip network
        i = 0
        while i < 4:
            if not ip_net[i] == gateway_net[i]:
                return False
            i += 1

        if compare_ip4_address(gateway, ip):
            return False

    # gateway and ip are not broadcast
    broadcast = []
    i = 0
    while i < 4:
        broadcast[i] = ip_net[i] | (~netmask[i] & 0xFF)
        i += 1

    if compare_ip4_address(broadcast, ip):
        return False
    if gateway_s and compare_ip4_address(broadcast, gateway):
        return False

    # general rules
    if netsize >= 24:
        if ip[3] == 255 or ip[3] == 0:
            return False
        if gateway_s and (gateway[3] == 255 or gateway[3] == 0):
            return False

    # valid!
    return True


def parse_ip4_address2string(a):
    return '' + a[0] + '.' + a[1] + '.' + a[2] + '.' + a[3]


def config_validate(config):
    """validate entire config."""
    for iface, ifconfig in config.iteritems():
        for protocol, pconfig in ifconfig['protocol'].iteritems():
            if not protocol == "inet":
                # TODO log error on screen
                return False
            if "method" not in pconfig:
                # TODO log error on screen
                return False
            method = pconfig['method']
            if not method == "static" and not method == "dhcp" and not method == "loopback":
                # TODO echo warning on screen
                print "warning"
            address = None
            netmask = None
            gateway = None
            for option, value in pconfig.iteritems():
                print option
                if option == 'method':
                    continue
                elif option == 'address':
                    address = value
                elif option == 'netmask':
                    netmask = value
                elif option == 'gateway':
                    gateway = value
                else:
                    # TODO print warning to screen
                    print "else block"
            if address and netmask:
                if not validate_ip4(address, netmask, gateway):
                    # TODO print error to screen
                    return False
                elif method == "static":
                    # TODO print error to screen
                    return False
    # valid
    return True
