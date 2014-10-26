#!/usr/bin/env python
#Corporate financial exogenous variables indexed by the tuple (<ticker>, yyyy)
#Value is a dictionary for every exogenous variable; Examples below
#{'Revenue':48607, 'Earnings':10866, 'IT rate': 0.208}

GLOBAL_CORP_FIN_DICT = dict() 
GLOBAL_CORP_CALC_DICT = dict()
GLOBAL_INDUSTRY_DICT = dict()
GLOBAL_CORP_FIN_SCHED_DICT = dict()
GLOBAL_DCF_CALC_DICT = dict()
GLOBAL_DCF_INPUT_PARAMS_DICT = dict()
GLOBAL_CORP_DICT = dict()
GLOBAL_MACRO_PARAMS_DICT = dict()

STR_TO_DICTIONARY_MAPPING = {'corp_fin_dict':GLOBAL_CORP_FIN_DICT, 'corp_calc_dict':GLOBAL_CORP_CALC_DICT, \
			     'industry_dict':GLOBAL_INDUSTRY_DICT, 'corp_schd_dict':GLOBAL_CORP_FIN_SCHED_DICT, \
			     'dcf_calc_dict':GLOBAL_DCF_CALC_DICT, 'dcf_ippar_dict':GLOBAL_DCF_INPUT_PARAMS_DICT, \
			     'corp_dat_dict':GLOBAL_CORP_DICT,     'macro_par_dict':GLOBAL_MACRO_PARAMS_DICT}

def statically_load_dictionaries():
	fundamentals = {'Revenue': 48607, 'Earnings': 10866, 'IT rate': 0.208, 'R&D expense': 5942, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':5389, \
		    'Stated Capital Spending':1186, 'Depreciation': 2351, 'Accounts Receivable': 5470, 'Accounts Payable': 1029, 'Inventory': 1476, \
		    'Other Current Assets': 1312, 'Other Current Liabilities': 5048, 'Acquisitions': 6982, 'Operations Lease Expense': 416, \
		    'Operating Lease Assets': 326, 'Depreciation on Leased Assets': 203, 'Cash Assets': 50610}
	rev = long(fundametals('Revenue'))
	p_key = ('csco', 2013)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = long(fundamentals[f_key])/rev
		
	fundamentals = {'Revenue': 47000, 'Earnings': 10485, 'IT rate': 0.2, 'R&D expense': 6110, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':5333, \
		    'Stated Capital Spending':1333, 'Depreciation': 2550, 'Accounts Receivable': 4443, 'Accounts Payable': 1051, 'Inventory': 1528, \
		    'Other Current Assets': 1292, 'Other Current Liabilities': 4841, 'Acquisitions': 3000, 'Operations Lease Expense': 381, \
		    'Operating Lease Assets': 282, 'Depreciation on Leased Assets': 169, 'Cash Assets': 50469}
	rev = long(fundametals('Revenue'))
	p_key = ('csco', 2014)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = long(fundamentals[f_key])/rev

	fundamentals = {'Revenue': 46061, 'Earnings': 10017, 'IT rate': 0.219, 'R&D expense': 5488, 'Pre-tax Debt Rate': 0.0454, 'Common Stocks Outstanding':5298, \
		    'Stated Capital Spending':1113, 'Depreciation': 2602, 'Accounts Receivable': 4369, 'Accounts Payable': 859, 'Inventory': 1663, \
		    'Other Current Assets': 1230, 'Other Current Liabilities': 4785, 'Acquisitions': 398, 'Operations Lease Expense': 404, \
		    'Operating Lease Assets': 300, 'Depreciation on Leased Assets': 181, 'Cash Assets': 48716}
	rev = long(fundametals('Revenue'))
	p_key = ('csco', 2012)
	GLOBAL_CORP_FIN_DICT[p_key] = fundamentals
	for f_key in fundamentals.keys():
	    if f_key not in ['Revenue', 'IT rate', 'Pre-tax Debt Rate', 'Common Stocks Outstanding']:
		GLOBAL_CORP_CALC_DICT[p_key][f_key] = long(fundamentals[f_key])/rev

