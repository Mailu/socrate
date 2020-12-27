import socket
import tenacity
import urllib.parse
from os import environ
import logging as log

@tenacity.retry(stop=tenacity.stop_after_attempt(100),
                wait=tenacity.wait_random(min=2, max=5))
def resolve_hostname(hostname):
    """ This function uses system DNS to resolve a hostname.
    It is capable of retrying in case the host is not immediately available
    It returns (Address, AddressFamily)
    """
    try:
        res = socket.getaddrinfo(hostname, None)[0]
        return (res[4][0], res[0])
    except Exception as e:
        log.warn("Unable to lookup '%s': %s",hostname,e)
        raise e


def resolve_address(address):
    """ This function is identical to ``resolve_hostname`` but also supports
    resolving an address, i.e. including a port.
    """

    # urlparse() and urlsplit() insists on absolute URLs starting with "//"
    result = urllib.parse.urlsplit('//{}'.format(address))
    hostname, port = result.hostname, result.port
    
    ip_address, address_family = resolve_hostname(hostname)

    if address_family is socket.AF_INET6:
        return "[{}]:{}".format(ip_address, port)

    return "{}:{}".format(ip_address, port)


def get_host_address_from_environment(name, default):
    """ This function looks up an envionment variable ``{{ name }}_ADDRESS``.
    If it's defined, it is returned unmodified. If it's undefined, an environment
    variable ``HOST_{{ name }}`` is looked up and resolved to an ip address.
    If this is also not defined, the default is resolved to an ip address.
    """
    if "{}_ADDRESS".format(name) in environ:
        return environ.get("{}_ADDRESS".format(name))
    return resolve_address(environ.get("HOST_{}".format(name), default))
