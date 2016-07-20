"""Validates config file before sending."""


def parse_ip4_address(s):
    """parse an ip4 address."""
    # split string into octets
    octets_s = s.split(".")
    octets = []

    # more than four octets?
    if (len(octets_s) != 4):
        return False

    # validate each octet
    # TODO

    return octets
