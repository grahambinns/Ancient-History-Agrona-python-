# Agrona (python version)

A monitoring daemon for a custom XML reporting service written in Python.

This was written around nine years ago and was a port of a PHP(!) daemon (which I'll throw up onto github some time for comparison).

The daemon connects to a webservice that reports the status of various other servers and services in XML form. Agrona (all of the daemons in the company I was working for at the time were named after gods in the Celtic diaspora) parses that XML and sends out email alerts should a service be down, or outside of a given set of parameters.
