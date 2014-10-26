# To kick off the script, run the following from the python directory:
#   PYTHONPATH=`pwd` python fin_daemon.py start
#   PYTHONPATH=`pwd` python fin_daemon.py stop

#!/usr/bin/env python

#standard python libs
import config
import logging
import time

#third party libs
import Pyro4
from multiprocessing import Process, Pipe

def iterate(finserver):
    #print finserver.get_hello("Sai")

    #ticker, year, earnings = finserver.get_earnings()
    #print "Ticker " + ticker + '::: Year ' + repr(year) + '::: Earnings ' + repr(earnings) + '\n'

    d = finserver.get_data('corp_fin_dic', ('csco', 2014), 'Revenu')
    if (d['Success'] == 0):
       print "ERROR: " + str(d['Err msg'])
    else:
       print "Value is: " + repr(d['Value'])

    d = finserver.get_data('corp_fin_dict', ('csco', 2014), 'Revenu')
    if (d['Success'] == 0):
       print "ERROR: " + str(d['Err msg'])
    else:
       print "Value is: " + repr(d['Value'])

    d = finserver.get_data('corp_fin_dict', ('csco', 2013), 'Revenu')
    if (d['Success'] == 0):
       print "ERROR: " + str(d['Err msg'])
    else:
       print "Value is: " + repr(d['Value'])

    d = finserver.get_data('corp_fin_dict', ('csco', 2013), 'Revenue')
    if (d['Success'] == 0):
       print "ERROR: " + str(d['Err msg'])
    else:
       print "Value is: " + repr(d['Value'])


def f(finserver, conn):
    d = finserver.get_data('corp_fin_dict', ('csco', 2012), 'Revenue')
    conn.send(d)
    d = finserver.get_data('corp_fin_dict', ('csco', 2013), 'Revenue')
    conn.send(d)
    d = finserver.get_data('corp_fin_dict', ('csco', 2014), 'Revenue')
    conn.send(d)
    d = finserver.get_data('corp_fin_dict', ('csco', 2014), 'R&D expense')
    conn.send(d)
    d = finserver.get_data('corp_calc_dict', ('csco', 2014), 'R&D expense')
    conn.send(d)
    d = finserver.get_data('industry_dict', ('Telecom Equipment', 'Terminal'), 'Net capex')
    conn.send(d)
    conn.close()


if __name__ == '__main__':

    fin = open('/var/log/fin_daemon/fin_daemon.uri')
    uri = fin.readline()
    fin.close()

    print "Ready to communicate. Daemon uri =", uri      # print the uri that daemon created
    finserver =  Pyro4.Proxy(uri)
    #iterate(finserver) # Debug scaffolding

    parent_conn, child_conn = Pipe()
    p = Process(target=f, args=(finserver, child_conn,))
    p.start()

    child_conn.close() # dont be alarmed.. pipe wont be closed unless child process closes it as well!
    
    while True:
       try:
          d = parent_conn.recv()   
          if (d['Success'] == 0):
             print "ERROR: " + str(d['Err msg'])
          else:
             print "Value from Child via pipe is: " + repr(d['Value'])
       except EOFError:
          print 'Pipe closed from other end'
	  break
	
    p.join()
