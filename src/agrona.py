"""
Agrona - the MobServ monitoring system
"""
from   mwacs          import parsing
from   event.base     import Listener, Notifier
from   event.handling import EventHandler
from   urllib         import urlopen
from   time           import sleep
import logging, config, xmlrpclib, socket

class Agrona(Listener, Notifier):
    """
    The basic Agrona process in class form
    """

    def __init__(self):
        """
        Initialises our Agrona instance
        """
        self.url     = "http://www.mobserv.com/mwacs/status.php?cType=xml2"
        self.running = False
        logging.info("Running initial parse of MWACS data")
        url          = urlopen(self.url)
        self.hosts   = parsing.parse(url, None)

        # We need to register this an event handler as a listener with all hosts
        self.eventHandler = EventHandler()
        for host in self.hosts.values():
            host.addListener(self.eventHandler, True)

    def run(self):
        """
        Runs the main loop of the agrona process
        """
        self.running = True
        while (self.running):
            sleep(config.SLEEP_TIME)
            logging.info("Running main loop")
            self.hosts = parsing.parse(urlopen(self.url), self.hosts)

            # Update MWACS; let it know we're still going
            try:
                server = xmlrpclib.ServerProxy(config.MWACS_WS_URL)
                server.mwacs.logStatus("agrona", "running", socket.gethostname())
            except Exception, e:
                logging.error("Couldn't update MWACS entry: " + e)

            # Some debugging
            # TODO - Remove this once we're confident that everything works
            # Or at least make sure that the log level is not DEBUG(!)
            for host in self.hosts.values():
                logging.debug("Host " + str(host))

                for prop in host.props.values():
                    logging.debug("\tProperty " + str(prop))

                for proc in host.procs.values():
                    logging.debug("\tProcess " + str(proc))

                    for prop in proc.props.values():
                        logging.debug("\t\tProperty " + str(prop))

if __name__ == '__main__':
    # Set up our logging
    logging.basicConfig(level=config.LOG_LEVEL,
                        format=config.LOG_FORMAT)#,
#                        filename=config.LOG_FILE),
#                        filemode='w')

    agrona = Agrona()
    agrona.run()