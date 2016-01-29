"""
Provides tools for parsing MWACS XML into a series of MWACS objects as
defined in pywacs.mwacsobjects
"""
from xml.dom  import minidom
from entities import MWACSHost, MWACSProcess, MWACSProperty


def parseMWACSData(source):
    """
    Parses MWACS data into a series of MWACSHosts, MWACSProperties and
    MWACSProcesses.

    This method expects XML to be in the form described at
    http://www.mobserv.com/mwacs/status.php?cType=xml2

    source
        A file object containing the MWACS XML to parse
    """

    # Use minidom - why not?
    parsed = minidom.parse(source)

    # This is what we're going to return in the end
    hosts  = {}

    # Loop through the hosts and make them into MWACSHost instances
    for host in parsed.getElementsByTagName('host'):
        mwhost       = MWACSHost(host.getAttribute('name'))
        mwhost.age   = host.getAttribute('age')
        mwhost.value = host.getAttribute('value')

        # Deal with the host's properties
        for prop in host.getElementsByTagName('property'):
            mwprop = MWACSProperty(prop.getAttribute('name') \
                                   ,prop.getAttribute('value'))
            mwhost.addProperty(mwprop)

        # Now its processes
        for proc in host.getElementsByTagName('process'):
            mwproc = MWACSProcess(proc.getAttribute('name') \
                                  ,proc.getAttribute('value') \
                                  ,proc.getAttribute('age'))

            # Parse the process's properties
            for prop in proc.getElementsByTagName('property'):
                pprop = MWACSProperty(prop.getAttribute('name') \
                                      ,prop.getAttribute('value'))
                mwproc.addProperty(pprop)

            mwhost.addProcess(mwproc)

        # Finally, stick the host in the dictionary of hosts
        hosts[mwhost.name] = mwhost

    # Clean up our minidom instance (some versions of Python do not support
    # garbage collection of objects that refer to each other in a cycle)
    parsed.unlink()
    return hosts

def updateMWACSData(src, hosts):
    """
    Takes a list of MWACSHosts (and their associated properties, etc)
    and updates them with the latest data from the MWACS Feed

    src
        A file object containing the MWACS XML data
    hosts
        The list of MWACSHosts to update
    """

    # First things first, get the latest MWACS data from the SRC
    newHosts = parseMWACSData(src)

    # Then it's a simple case of doing teh loop-de-loop and updating
    # the existing hosts with the new data. Honest.
    for hn, nHost in newHosts.items():
        # Check that the new host exists in the old hosts list and
        # Add it if it doesn't
        if not hosts.has_key(hn):
            hosts[hn] = nHost
            continue # No point in staying in the loop after this

        # We need a host to work with
        host = hosts[hn]

        # First, update the host's properties' attributes
        for pn in nHost.props:
            # If the host doesn't have the property, add it
            if not host.props.has_key(pn):
                host.addProperty(nHost.props[pn])
                continue

            # Update the property's value (its name is immutable)
            host.props[pn].value = nHost.props[pn].value

        # Now we do the processes
        for procn, proc in nHost.procs.items():
            # Add it if we ain't got it
            if not host.procs.has_key(procn):
                host.addProcess(nHost.procs[procn])
                continue

            # Update the process's properties
            for pn in proc.props:
                # If the host doesn't have the property, add it
                if not host.props.has_key(pn):
                    host.procs[procn].addProperty(proc.props[pn])
                    continue

                # Update the property's value (its name is immutable)
                host.procs[procn].props[pn].value = proc.props[pn].value

            # Update the process itself
            host.procs[procn].value = proc.value
            host.procs[procn].age   = proc.age

        # Finally, update the host
        host.age  = nHost.age
        hosts[hn] = host

    # Und finallisch, return teh hosts
    return hosts

def parse(src, hosts=None):
    """
    Serves as a wrapper around parseMWACSData and updateMWACSData, so that
    we only need to call this method and it will in turn call those methods
    as necessary

    src
        A file object containing the XML to be parsed

    hosts
        A list of MWACSHosts to update. If none, this list will be created

    returns
        An updated host list
    """

    if hosts is None:
        return parseMWACSData(src)
    else:
        return updateMWACSData(src, hosts)