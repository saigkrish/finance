#!/usr/bin/env python
#Corporate financial exogenous variables indexed by the tuple (<ticker>, yyyy)
#Value is a dictionary for every exogenous variable; Examples below
#{'Revenue':48607, 'Earnings':10866, 'IT rate': 0.208}
import sys
sys.path.append('/usr/lib/cgi-bin/mysite')
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

from django.contrib.auth.models import User

users = ['guest', 'sai']
dict_strs = ['corp_fin_dict', 'corp_calc_dict', 'industry_dict', 'corp_schd_dict', 'dcf_calc_dict', 'dcf_ippar_dict', 'corp_dat_dict', 'macro_par_dict']
dictionaries = dict()

GLOBAL_MACRO_PARAMS_DICT = dict() 
GLOBAL_INDUSTRY_DICT = dict()  #Premium-user ::  Global
GLOBAL_CORP_DICT = dict() 

GLOBAL_CORP_FIN_DICT = dict()  #Premium-user ::  Global
GLOBAL_CORP_CALC_DICT = dict()  #Premium-user ::  Global
GLOBAL_CORP_FIN_SCHED_DICT = dict()  #Premium-user ::  Global

GLOBAL_DCF_CALC_DICT = dict()  #Premium-user ::  Global
GLOBAL_DCF_INPUT_PARAMS_DICT = dict()  #Per-user ::  Global

STR_TO_DICTIONARY_MAPPING = {}

def uglyfinance_init():
    global users
    global dict_strs

    global GLOBAL_MACRO_PARAMS_DICT
    global GLOBAL_INDUSTRY_DICT
    global GLOBAL_CORP_DICT
    global GLOBAL_CORP_FIN_DICT
    global GLOBAL_CORP_CALC_DICT
    global GLOBAL_CORP_FIN_SCHED_DICT
    global GLOBAL_DCF_CALC_DICT
    global GLOBAL_DCF_INPUT_PARAMS_DICT
    global STR_TO_DICTIONARY_MAPPING
    
    # Get the users from django user database; remove root
    for u in User.objects.all():
        if (u.username == 'root'):
            continue
        dictionaries[u.username] = dict()
        for j in range(len(dict_strs)):
            dictionaries[u.username][dict_strs[j]] = dict()

    GLOBAL_MACRO_PARAMS_DICT = dictionaries['guest']['macro_par_dict']
    GLOBAL_INDUSTRY_DICT = dictionaries['guest']['industry_dict']
    GLOBAL_CORP_DICT = dictionaries['guest']['corp_dat_dict']
    GLOBAL_CORP_FIN_DICT = dictionaries['guest']['corp_fin_dict']
    GLOBAL_CORP_CALC_DICT = dictionaries['guest']['corp_calc_dict']
    GLOBAL_CORP_FIN_SCHED_DICT = dictionaries['guest']['corp_schd_dict']
    GLOBAL_DCF_CALC_DICT = dictionaries['guest']['dcf_calc_dict']
    GLOBAL_DCF_INPUT_PARAMS_DICT = dictionaries['guest']['dcf_ippar_dict']

    STR_TO_DICTIONARY_MAPPING['corp_fin_dict'] = GLOBAL_CORP_FIN_DICT
    STR_TO_DICTIONARY_MAPPING['corp_calc_dict'] = GLOBAL_CORP_CALC_DICT
    STR_TO_DICTIONARY_MAPPING['industry_dict'] = GLOBAL_INDUSTRY_DICT
    STR_TO_DICTIONARY_MAPPING['corp_schd_dict'] = GLOBAL_CORP_FIN_SCHED_DICT
    STR_TO_DICTIONARY_MAPPING['dcf_calc_dict'] = GLOBAL_DCF_CALC_DICT
    STR_TO_DICTIONARY_MAPPING['dcf_ippar_dict'] = GLOBAL_DCF_INPUT_PARAMS_DICT
    STR_TO_DICTIONARY_MAPPING['corp_dat_dict'] = GLOBAL_CORP_DICT
    STR_TO_DICTIONARY_MAPPING['macro_par_dict'] = GLOBAL_MACRO_PARAMS_DICT
    
#get_range_of_years_dict returns the starting year and the ending year of any dictionary indexed by (ticker, yyyy)
#Since the 'FCF to firm' parameter and other calculated values of DCF are stored in the dictionary (GLOBAL_DCF_CALC_DICT)
#indexed by (ticker, yyyy), there is no guarantee that the dictionary keys will be in sorted order. For most of the calculations, 
#we need to know the range of years for which data is available (both exogenous variables and calculated variables)
#This function collects all the keys in the dictionary passed as parameter. If ticker is present in the keys, 
#it copies the keys (eg., [('csco', 2004), ('csco', 2005) ... ]) as a list to the variable t.
#t is an unsorted list of keys that has 'csco' in it. From this list, we sort based on the tuple[1] (year) and store it back in t
#once the list of keys is sorted, we can easily access the first and last years by [0] and [-1]. we return these 2 years to the caller
def get_range_of_years_dict(d, ticker):
    t = []
    for key in d.keys():
        if (ticker in key) and ('Terminal' not in key) and ('global' not in key) :
           t.append(key)
    if len(t) < 1:
       return 0, 0
    t.sort(key=lambda tup: tup[1])
    ticker, first_year = t[0]
    ticker, last_year = t[-1]
    return first_year, last_year

    
# Eventually should go in fin_algos.py
#
# Input::
# lt: List of $$ amounts in nominal terms
# discount_rate: The rate at which present value will be derived by discounting the nominal values
#
# return value:: Present value of the yearly payouts discounted @ discount_rate
#
# Example get_present_value([102, 102, 102, 93.5, 93.5], 4.54%) will return 433.5
# This is the same as 102 divided by (1+.0454)^1 + 102 divided by (1+0.0454)^2 etc.
def get_present_value(lt, discount_rate):
    pv = 0
    for i in range(len(lt)):
        pv = pv + lt[i]/(1+discount_rate)**(i+1)
    return pv

# Eventually should go in fin_algos.py
#
# Input::
# lumpsum: the amount that needs to be annuitized (say you have a million dollars)
# num_annuity: Lumpsum should result in income stream for how many years (say you want that mill to come as a yearly income for 10 years)
# numyears_before_annuity_starts: Say today is 2014 and you want that annuity to start on 2029, this input parameter will be 15
# discount_rate: The rate at which present value will be derived by discounting the nominal values
#
# return value:: Present value of all the annuitized payment
#
# Example get_annuity_value(632, 6, 5, 4.54%) will return 434.57
def get_annuity_value(lumpsum, num_annuity, numyears_before_annuity_starts, discount_rate):
    if (num_annuity > 0 ):
        return ((lumpsum/num_annuity)*(1-(1+discount_rate)**(-num_annuity))/discount_rate)/(1+discount_rate)**numyears_before_annuity_starts
    else: 
        return lumpsum/(1+discount_rate)**(numyears_before_annuity_starts+1)

#sample oplease schedule
#{'num years': 5, 'data': [102.0, 102.0, 102.0, 93.50, 93.50], 'thereafter':632.0}
def calc_op_lease_schedule(*argv):
    ticker, year, sched = argv
    d = GLOBAL_CORP_FIN_SCHED_DICT[ticker,year,sched]
    avg = sum(d['data'])/float(len(d['data']))
    numyears_embedded_in_thereafter = round(d['thereafter']/avg,0)
    d['numyears in thereafter'] = numyears_embedded_in_thereafter

    #Get the pre-tax cost of debt to calculate the Present value of lease commitment
    debt_rate = GLOBAL_CORP_FIN_DICT[ticker,year]['Pre-tax Debt Rate'] #TBD: error check
    d['PV of years 1 through n'] = get_present_value(d['data'], debt_rate)
    d['PV of thereafter annuitized'] = get_annuity_value(d['thereafter'], d['numyears in thereafter'], d['num years'], debt_rate)

def statically_load_dictionaries():
	fundamentals = {'Revenue': 22045, 'Earnings': 5337, 'IT rate': 0.28, 'R&D expense': 3192, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':6735, \
		    'Stated Capital Spending':613, 'Depreciation': 1199, 'Accounts Receivable': 1825, 'Accounts Payable': 657, 'Inventory': 1207, \
		    'Other Current Assets': 815, 'Other Current Liabilities': 2090, 'Acquisitions': 127, 'Operations Lease Expense': 191, \
		    'Operating Lease Assets': 94, 'Depreciation on Leased Assets': 56, 'Net interest': -700.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2004)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev

	fundamentals = {'Revenue': 24801, 'Earnings': 5741, 'IT rate': 0.286, 'R&D expense': 3322, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':6331, \
		    'Stated Capital Spending':692, 'Depreciation': 1020, 'Accounts Receivable': 2216, 'Accounts Payable': 735, 'Inventory': 1297, \
		    'Other Current Assets': 967, 'Other Current Liabilities': 2094, 'Acquisitions': 1591, 'Operations Lease Expense': 179, \
		    'Operating Lease Assets': 136, 'Depreciation on Leased Assets': 82, 'Net interest': -620.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2005)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev

	fundamentals = {'Revenue': 28484, 'Earnings': 5580, 'IT rate': 0.2690, 'R&D expense': 4067, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':6059, \
		    'Stated Capital Spending':772, 'Depreciation': 1293, 'Accounts Receivable': 3303, 'Accounts Payable': 880, 'Inventory': 1371, \
		    'Other Current Assets': 1584, 'Other Current Liabilities': 2765, 'Acquisitions': 7357, 'Operations Lease Expense': 181, \
		    'Operating Lease Assets': 153, 'Depreciation on Leased Assets': 92, 'Net interest': -637.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2006)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev

	fundamentals = {'Revenue': 34922, 'Earnings': 7333, 'IT rate': 0.2250, 'R&D expense': 4598, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':6100, \
		    'Stated Capital Spending':1281, 'Depreciation': 1413, 'Accounts Receivable': 3989, 'Accounts Payable': 786, 'Inventory': 1322, \
		    'Other Current Assets': 2044, 'Other Current Liabilities': 3422, 'Acquisitions': 4214, 'Operations Lease Expense': 219, \
		    'Operating Lease Assets': 181, 'Depreciation on Leased Assets': 109, 'Net interest': -840.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2007)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev

	fundamentals = {'Revenue': 39540, 'Earnings': 8052, 'IT rate': 0.2150, 'R&D expense': 5325, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':5893, \
		    'Stated Capital Spending':1296, 'Depreciation': 1744, 'Accounts Receivable': 3821, 'Accounts Payable': 869, 'Inventory': 1235, \
		    'Other Current Assets': 2333, 'Other Current Liabilities': 3757, 'Acquisitions': 412, 'Operations Lease Expense': 291, \
		    'Operating Lease Assets': 209, 'Depreciation on Leased Assets': 125, 'Net interest': -813.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2008)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev

	fundamentals = {'Revenue': 36117, 'Earnings': 6134, 'IT rate': 0.2030, 'R&D expense': 5208, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':5785, \
		    'Stated Capital Spending':983, 'Depreciation': 1768, 'Accounts Receivable': 3177, 'Accounts Payable': 675, 'Inventory': 1074, \
		    'Other Current Assets': 2605, 'Other Current Liabilities': 3841, 'Acquisitions': 981, 'Operations Lease Expense': 328, \
		    'Operating Lease Assets': 227, 'Depreciation on Leased Assets': 136, 'Net interest': -371.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2009)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev

	fundamentals = {'Revenue': 40040, 'Earnings': 7767, 'IT rate': 0.1750, 'R&D expense': 5273, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':5655, \
		    'Stated Capital Spending':1018, 'Depreciation': 2030, 'Accounts Receivable': 4929, 'Accounts Payable': 895, 'Inventory': 1327, \
		    'Other Current Assets': 875, 'Other Current Liabilities': 4359, 'Acquisitions': 6186, 'Operations Lease Expense': 364, \
		    'Operating Lease Assets': 255, 'Depreciation on Leased Assets': 144, 'Net interest': -251.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2010)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev

	fundamentals = {'Revenue': 43218, 'Earnings': 9033, 'IT rate': 0.2130, 'R&D expense': 5823, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':5435, \
		    'Stated Capital Spending':1196, 'Depreciation': 2486, 'Accounts Receivable': 4698, 'Accounts Payable': 876, 'Inventory': 1486, \
		    'Other Current Assets': 941, 'Other Current Liabilities': 4734, 'Acquisitions': 288, 'Operations Lease Expense': 428, \
		    'Operating Lease Assets': 293, 'Depreciation on Leased Assets': 169, 'Net interest': -151.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2011)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev

	fundamentals = {'Revenue': 46061, 'Earnings': 10017, 'IT rate': 0.219, 'R&D expense': 5488, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':5298, \
		    'Stated Capital Spending':1113, 'Depreciation': 2602, 'Accounts Receivable': 4369, 'Accounts Payable': 859, 'Inventory': 1663, \
		    'Other Current Assets': 1230, 'Other Current Liabilities': 4785, 'Acquisitions': 398, 'Operations Lease Expense': 404, \
		    'Operating Lease Assets': 300, 'Depreciation on Leased Assets': 181, 'Cash Assets': 48716, 'Net interest': -94.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2012)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev

	fundamentals = {'Revenue': 48607, 'Earnings': 10866, 'IT rate': 0.208, 'R&D expense': 5942, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':5389, \
		    'Stated Capital Spending':1186, 'Depreciation': 2351, 'Accounts Receivable': 5470, 'Accounts Payable': 1029, 'Inventory': 1476, \
		    'Other Current Assets': 1312, 'Other Current Liabilities': 5048, 'Acquisitions': 6982, 'Operations Lease Expense': 416, \
		    'Operating Lease Assets': 326, 'Depreciation on Leased Assets': 203, 'Cash Assets': 50610, 'Net interest': -31.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2013)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev
		
	fundamentals = {'Revenue': 47000, 'Earnings': 10485, 'IT rate': 0.2, 'R&D expense': 6110, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':5333, \
		    'Stated Capital Spending':1333, 'Depreciation': 2550, 'Accounts Receivable': 4443, 'Accounts Payable': 1051, 'Inventory': 1528, \
		    'Other Current Assets': 1292, 'Other Current Liabilities': 4841, 'Acquisitions': 3000, 'Operations Lease Expense': 381, \
		    'Operating Lease Assets': 282, 'Depreciation on Leased Assets': 169, 'Cash Assets': 50469, 'Net interest': -150.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2014)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev

	fundamentals = {'Revenue': 49000, 'Earnings': 10950, 'IT rate': 0.200, 'R&D expense': 6370, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':5300, \
		    'Stated Capital Spending':1325, 'Depreciation': 2620, 'Accounts Receivable': 4900, 'Accounts Payable': 1029, 'Inventory': 1593, \
		    'Other Current Assets': 1470, 'Other Current Liabilities': 5047, 'Acquisitions': 3000, 'Operations Lease Expense': 397, \
		    'Operating Lease Assets': 294, 'Depreciation on Leased Assets': 176, 'Net interest': -150.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2015)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev

	fundamentals = {'Revenue': 52712, 'Earnings': 11727, 'IT rate': 0.2, 'R&D expense': 6853, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':5215.32, \
		    'Stated Capital Spending':1459, 'Depreciation': 2710, 'Accounts Receivable': 5271, 'Accounts Payable': 1107, 'Inventory': 1713, \
		    'Other Current Assets': 1581, 'Other Current Liabilities': 5429, 'Acquisitions': 3000, 'Operations Lease Expense': 427, \
		    'Operating Lease Assets': 316, 'Depreciation on Leased Assets': 190, 'Cash Assets': 48716, 'Net interest': -150.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2016)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev

	fundamentals = {'Revenue': 56705, 'Earnings': 12559, 'IT rate': 0.2, 'R&D expense': 7372, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':5131.99, \
		    'Stated Capital Spending':1606, 'Depreciation': 2803, 'Accounts Receivable': 5670, 'Accounts Payable': 1191, 'Inventory': 1843, \
		    'Other Current Assets': 1701, 'Other Current Liabilities': 5841, 'Acquisitions': 3000, 'Operations Lease Expense': 459, \
		    'Operating Lease Assets': 340, 'Depreciation on Leased Assets': 204, 'Net interest': -150.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2017)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev


	fundamentals = {'Revenue': 61000, 'Earnings': 13450, 'IT rate': 0.2, 'R&D expense': 7930, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':5050.00, \
		    'Stated Capital Spending':1768, 'Depreciation': 2900, 'Accounts Receivable': 6100, 'Accounts Payable': 1281, 'Inventory': 1983, \
		    'Other Current Assets': 1830, 'Other Current Liabilities': 6283, 'Acquisitions': 3000, 'Operations Lease Expense': 494, \
		    'Operating Lease Assets': 366, 'Depreciation on Leased Assets': 220, 'Net interest': -150.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2018)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev

	fundamentals = {'Revenue': 63275.30, 'Earnings': 14105.02, 'IT rate': 0.2, 'R&D expense': 8225.79, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':4969.32, \
		    'Stated Capital Spending':2531.01, 'Depreciation': 3008.17, 'Accounts Receivable': 6328, 'Accounts Payable': 1329, 'Inventory': 2056, \
		    'Other Current Assets': 1898, 'Other Current Liabilities': 6517, 'Acquisitions': 3000, 'Operations Lease Expense': 513, \
		    'Operating Lease Assets': 380, 'Depreciation on Leased Assets': 228, 'Net interest': -150.0}
	rev = float(fundamentals['Revenue'])
	p_key = ('csco', 2019)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	GLOBAL_CORP_CALC_DICT[p_key] = {}
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = float(fundamentals[f_key])/rev

        industry_comps = {'Net capex': 0.088, 'Non-cash working capital': 0.1740, 'R&D amortization years': 5.0}
        p_key = ('Telecom Equipment', 'global')
        GLOBAL_INDUSTRY_DICT[p_key] = industry_comps

        corporate_data = {'Industry': 'Telecom Equipment', 'Size': 'Large cap', 'Logo': '"http://www.brandsoftheworld.com/sites/default/files/styles/logo-original-577x577/public/0019/2765/brand.gif"'}
	p_key = 'csco'
	GLOBAL_CORP_DICT[p_key] = corporate_data

        corporate_data = {'Industry': 'Telecom Equipment', 'Size': 'Large cap', 'Logo': '"http://www.brandsoftheworld.com/sites/default/files/styles/logo-original-577x577/public/0019/2765/brand.gif"'}
	p_key = 'jnpr'
	GLOBAL_CORP_DICT[p_key] = corporate_data

        corporate_data = {'Industry': 'Telecom Equipment', 'Size': 'Large cap', 'Logo': '"http://www.brandsoftheworld.com/sites/default/files/styles/logo-original-577x577/public/0019/2765/brand.gif"'}
	p_key = 'msft'
	GLOBAL_CORP_DICT[p_key] = corporate_data

	schedule = {'num years': 5, 'data': [102.0, 102.0, 102.0, 93.50, 93.50], 'thereafter':632.0}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2004, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2004, 'op lease commitment')

	schedule = {'num years': 5, 'data': [93.67, 93.67, 93.67, 92.0, 92.0], 'thereafter':580.0}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2005, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2005, 'op lease commitment')

	schedule = {'num years': 5, 'data': [93.33, 93.33, 93.33, 98.0, 98.0], 'thereafter':506.0}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2006, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2006, 'op lease commitment')

	schedule = {'num years': 5, 'data': [128.0, 128.0, 128.0, 147.0, 147.0], 'thereafter':673.0}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2007, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2007, 'op lease commitment')

	schedule = {'num years': 5, 'data': [143.67, 143.67, 143.67, 135.50, 135.50], 'thereafter':577.0}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2008, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2008, 'op lease commitment')

	schedule = {'num years': 5, 'data': [142.0, 142.0, 142.0, 117.5, 117.5], 'thereafter':420.0}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2009, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2009, 'op lease commitment')

	schedule = {'num years': 5, 'data': [136.67, 136.67, 136.67, 120.5, 120.5], 'thereafter':310.0}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2010, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2010, 'op lease commitment')

	schedule = {'num years': 5, 'data': [148.33, 148.33, 148.33, 110.0, 110.0], 'thereafter':277.0}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2011, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2011, 'op lease commitment')

	schedule = {'num years': 5, 'data': [147.33, 147.33, 147.33, 83.5, 83.5], 'thereafter':202.0}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2012, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2012, 'op lease commitment')

	schedule = {'num years': 5, 'data': [146.33, 146.33, 146.33, 80.0, 80.0], 'thereafter':183.0}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2013, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2013, 'op lease commitment')

	schedule = {'num years': 5, 'data': [169.2, 169.2, 169.2, 105.75, 105.75], 'thereafter':282.0}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2014, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2014, 'op lease commitment')

	schedule = {'num years': 5, 'data': [176.4, 176.4, 176.4, 110.25, 110.25], 'thereafter':294.0}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2015, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2015, 'op lease commitment')

	schedule = {'num years': 5, 'data': [189.76, 189.76, 189.76, 118.60, 118.60], 'thereafter':316.27}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2016, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2016, 'op lease commitment')

	schedule = {'num years': 5, 'data': [204.14, 204.14, 204.14, 127.59, 127.59], 'thereafter':340.23}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2017, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2017, 'op lease commitment')

	schedule = {'num years': 5, 'data': [219.6, 219.6, 219.6, 137.25, 137.25], 'thereafter':366.0}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2018, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2018, 'op lease commitment')

	schedule = {'num years': 5, 'data': [227.79, 227.79, 227.79, 142.37, 142.37], 'thereafter':379.65}
	GLOBAL_CORP_FIN_SCHED_DICT['csco', 2019, 'op lease commitment'] = schedule
	calc_op_lease_schedule('csco', 2019, 'op lease commitment')

        
        
# This will all change to get values from table
def statically_load_dcf_ip_params(ticker, wacc, wacc_terminal):
    std = STR_TO_DICTIONARY_MAPPING
    GLOBAL_DCF_INPUT_PARAMS_DICT[(ticker, 'stage1')] = {'num years in stage':5}
    GLOBAL_DCF_INPUT_PARAMS_DICT[(ticker, 'stage1')]['revenue growth'] = 0.02
    GLOBAL_DCF_INPUT_PARAMS_DICT[(ticker, 'stage1')]['earnings growth'] = 0.08
    GLOBAL_DCF_INPUT_PARAMS_DICT[(ticker, 'stage2')] = {'num years in stage':0}
    GLOBAL_DCF_INPUT_PARAMS_DICT[(ticker, 'global')] = {'beta':0.96}
    GLOBAL_DCF_INPUT_PARAMS_DICT[(ticker, 'global')]['Rm'] = 0.1
    GLOBAL_DCF_INPUT_PARAMS_DICT[(ticker, 'global')]['Rf'] = 0.01
    GLOBAL_DCF_INPUT_PARAMS_DICT[(ticker, 'global')]['Ke'] = 0.09
    GLOBAL_DCF_INPUT_PARAMS_DICT[(ticker, 'global')]['Kd'] = 0.045
    GLOBAL_DCF_INPUT_PARAMS_DICT[(ticker, 'global')]['WACC'] = float(wacc)
    GLOBAL_DCF_INPUT_PARAMS_DICT[(ticker, 'Terminal')] = {'WACC':float(wacc_terminal)}
    GLOBAL_DCF_INPUT_PARAMS_DICT[(ticker, 'Terminal')]['growth'] = 0.02

    GLOBAL_DCF_CALC_DICT[(ticker, 'Terminal')] = {}


    

