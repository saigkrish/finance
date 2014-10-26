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
from config import STR_TO_DICTIONARY_MAPPING as std
from config import dictionaries
from config import uglyfinance_init
from config import statically_load_dictionaries
from config import statically_load_dcf_ip_params
from config import get_range_of_years_dict
from model_dcf import calc_fcf_to_firm
from model_dcf import calc_terminal_fcf_to_firm
from model_dcf import calc_firmvalue_dcf
from model_dcf import write_templates
from model_dcf import initialize_dcf_vars

def load_dictionaries():
    global std
    global dictionaries

    for key in std.keys():
        print 'Elements in ' + key + ' :: ' + repr(len(std[key]))
        print std[key].keys()
    #    print std[key]
    print dictionaries.keys()

    # Now baselining all the users to what we have with global data base; This initialization should change to getting it directly from the database for that user
    for user in dictionaries.keys():
        if ((user == 'root') or (user == 'guest')):
            continue
        for key in std.keys():
            dictionaries[user][key] = dictionaries['guest'][key].copy()
            print 'For User ' + user + ':  Elements in ' + key + ' :: ' + repr(len(std[key]))
            print dictionaries[user][key].keys()

class FINSERVER(object):
    def get_data(self, dstr, key, param):
	global std
	logger = logging.getLogger('Daemon Log')
	if dstr not in std: #Bad dictionary
	   err_str = dstr + ': No such dictionary\n'
	   logger.error(err_str)
           return {'Success':0, 'Err msg': err_str}
        else:
	   d = std[dstr]
	   if key not in d: #either ticker is not there or no value in that ticker for a given year
	      err_str = str(key) + ': No such key in dictionary: ' + dstr + '\n'
	      logger.error(err_str)
	      return {'Success':0, 'Err msg': err_str}
    	   elif param not in d[key]: #No such parameter
	      err_str = str(param) + ': No such Parameter in ' + dstr + '[' + str(key) + ']' + '\n'
	      logger.error(err_str)
	      return {'Success':0, 'Err msg': err_str}
           else: #success
	      value = d[key][param]
	      succ_str = dstr + '[' + str(key) + ']' + '[' + str(param) + '] is: ' + repr(value) + '\n'
	      logger.info(succ_str) 
	      return {'Success':1, 'Err msg': 'None', 'Value':value}
          
finserver = FINSERVER()
logger = logging.getLogger('Daemon Log')
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/var/log/fin_daemon/fin_daemon.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

daemon_runner = Pyro4.Daemon()
uri = daemon_runner.register(finserver)
print "Ready. Object uri =", uri      # print the uri so we can use it in the client later
logger.info('Object uri = %s\n', uri)

fout = open('/var/log/fin_daemon/fin_daemon.uri', 'w')
fout.write(str(uri) + '\n')
fout.close()

# Initialize and statically load - To be replaced by reading from database
uglyfinance_init()
statically_load_dictionaries() # temporary arrangement until read from Database
statically_load_dcf_ip_params('csco', 0.0848, 0.0855) # temporary arrangement / scaffolding
statically_load_dcf_ip_params('jnpr', 0.0948, 0.1) # temporary arrangement / scaffolding
statically_load_dcf_ip_params('msft', 0.0548, 0.0655) # temporary arrangement / scaffolding

# Trigger DCF calculations
initialize_dcf_vars()
start, end = get_range_of_years_dict(std['corp_fin_dict'], 'csco')
for i in range (end-start+1):
    calc_fcf_to_firm('csco', start+i)
calc_terminal_fcf_to_firm('csco')
calc_firmvalue_dcf('csco', start)

load_dictionaries()
write_templates()
# debugging scafold - one for each type of error and last success
#print finserver.get_data('corp_fin_dic', ('csco', 2014), 'Revenu')
#print finserver.get_data('corp_fin_dict', ('csco', 2014), 'Revenu')
#print finserver.get_data('corp_fin_dict', ('csco', 2013), 'Revenu')
#print finserver.get_data('corp_fin_dict', ('csco', 2013), 'Revenue')

#daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.requestLoop()
