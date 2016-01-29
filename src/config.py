"""
Simple configuration file for Agrona.

TODO: Replace this with something more comprehensive, more flexible, perhaps?
"""
import logging, sys

XMLRPC_SERVER  = "http://www.mobserv.com/ws/neit.php" # Our SMS XMLRPC host
MWACS_URL      = "http://www.mobserv.com/mwacs/status.php?cType=xml2" # Our MWACS URL
MWACS_WS_URL   = "http://www.mobserv.com/mwacs/ws.php" # The MWACS webservice
SLEEP_TIME     = 60                  # Number of seconds to sleep between iterations
LOAD_AVG_HIGH  = 5                   # The point at which we consider a load average to be high
TIMEOUT        = 600                 # The length of time in seconds before a timeout occurs
SMTP_HOST      = 'localhost'         # The server that handles our outgoing mail
DATE_FORMAT    = '%Y-%m-%d %H:%M:%S' # The format to use for datetime strings
ALERTS         = {                   # Message bodies for the alerts we send out
    'ProcessStopped':
        "This is an alert from Agrona, the MobServ Monitoring Daemon.\n" +
        "%s was reported stopped at %s",
    'ProcessTimeout':
        "This is an alert from Agrona, the MobServ Monitoring Daemon.\n" +
        "%s was reported timed out at %s",
    'HostTimeout':
        "This is an alert from Agrona, the MobServ Monitoring Daemon.\n" +
        "%s was reported timed out at %s",
}

# Sender details for alerts
FROM_ADDR      = "agrona@monstermob.com"
FROM_MSISDN    = "82468"
RECIPIENTS     = {                   # Recipients (email and sms) for the alerts
    'email' : (),
    'sms'   : (),
}

# Logging settings
LOG_FORMAT     = '%(asctime)s %(levelname)s %(message)s'
LOG_LEVEL      = logging.DEBUG
LOG_FILE       = sys.stderr