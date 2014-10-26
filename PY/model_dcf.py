#!/usr/bin/env python

#standard python libs
import config
import logging
import time
import math
import os
from math import exp
from math import log

#third party libs
from config import STR_TO_DICTIONARY_MAPPING as std
from config import get_range_of_years_dict
from config import dictionaries

dcf_calc_display = []
dcf_dict = {}
dcf_ip = {}
cfd = {}
ccd = {}
csd = {}
cdd = {}

def initialize_dcf_vars():
    global dcf_dict
    global dcf_ip
    global cfd
    global ccd
    global csd
    global cdd

    dcf_dict = std['dcf_calc_dict']
    dcf_ip = std['dcf_ippar_dict']
    cfd = std['corp_fin_dict']
    ccd = std['corp_calc_dict']
    csd = std['corp_schd_dict']
    cdd = std['corp_dat_dict']

def initialize_dcf_dict_display():
    global dcf_calc_display
    dcf_calc_display = [('Earnings', 'Earnings', cfd, "'$0,0.00'"),
  		        ('Net interest', 'Net interest', cfd, "'$0,0.00'"),
		        ('EBIT', 'EBIT', dcf_dict,  "'$0,0.00'"),
		        ('R&D adjustment', 'R&D adjustment', dcf_dict, "'$0,0.00'"),
		        ('R&D expense', '   R&D expense', cfd, "'$0,0.00'"),
		        ('R&D amortization', '   R&D amortization', dcf_dict, "'$0,0.00'"),
                        ('imputed interest expense on operational lease', 'Imputed interest', dcf_dict, "'$0,0.00'"),
		        ('debtized operational lease', '   Debtized lease', dcf_dict, "'$0,0.00'"),
		        ('Pre-tax Debt Rate', '   Pre-tax interest', cfd, "'0.00%'"),
		        ('Adjusted EBIT', 'Adjusted EBIT', dcf_dict, "'$0,0.00'"),
		        ('IT rate', 'Average Tax rate', cfd, "'0.00%'"),
		        ('Adjusted EBIT(1-t)', 'EBIT(1-T)', dcf_dict, "'$0,0.00'"),
		        ('Tax benefit due to expensing capital', 'Additional tax benefit', dcf_dict, "'$0,0.00'"),
		        ('Adjusted operating income', 'Adjusted operating income', dcf_dict, "'$0,0.00'"),
		        ('Stated Capital Spending', 'Capital Expenses', cfd, "'$0,0.00'"),
		        ('Depreciation', '(-) Depreciation', cfd, "'$0,0.00'"),
		        ('Net capital expense stated', 'Net Capital Expenses', dcf_dict, "'$0,0.00'"),
		        ('R&D expense', '(+) R&D expense', cfd, "'$0,0.00'"),
		        ('R&D amortization', '(-) R&D amortization', dcf_dict, "'$0,0.00'"),
		        ('Acquisitions', '(+) Acquisitions', cfd, "'$0,0.00'"),
		        ('Operations Lease Expense', '(+) Operations Lease Expense', cfd, "'$0,0.00'"),
		        ('Depreciation on Leased Assets', '(-) Depreciation on Leased Assets', cfd, "'$0,0.00'"),
		        ('Adjusted net capital expense', 'Adjusted net capital expense', dcf_dict, "'$0,0.00'"),
		        ('Non cash working capital this year', 'Non cash WC', dcf_dict, "'$0,0.00'"),
		        ('Non cash working capital delta', 'Non cash WC delta', dcf_dict, "'$0,0.00'"),
		        ('FCF to firm', 'FCF to firm', dcf_dict, "'$0,0.00'"),
		        ('Firm Value', 'Firm Value', dcf_dict, "'$0,0.00'")]

# get_wacc returns the Weighted Average Cost of Capital for a given ticker
# If the WACC @ Terminal stage is different from the WACC @ equilibrium,
# this function will return both the values.
def get_wacc (ticker):
    global dcf_ip

    if (ticker, 'global') in dcf_ip:
        wacc = float(dcf_ip[(ticker, 'global')]['WACC'])
    else:
        wacc = 0.1 # the right thing to do here is to pickup a default variable from a dictionary

    if (ticker, 'Terminal') in dcf_ip:
        wacc_terminal = float(dcf_ip[(ticker, 'Terminal')]['WACC'])
    else:
        wacc_terminal = wacc

    return wacc, wacc_terminal
   
def calc_terminal_fcf_to_firm (ticker):
    global dcf_dict
    global dcf_ip

    first_year, last_year = get_range_of_years_dict(dcf_dict, ticker)
    wacc, wacc_terminal = get_wacc(ticker)

    final_year_fcf_to_firm = dcf_dict[(ticker, last_year)]['FCF to firm']
    terminal_growth_rate = dcf_ip[(ticker, 'Terminal')]['growth']
    dcf_dict[(ticker, 'Terminal')] = {'FCF to firm': final_year_fcf_to_firm*(1+terminal_growth_rate)/(wacc_terminal - terminal_growth_rate)}

# Return growth given start value, End value and number of years transpired
def calc_rate_of_growth (start_val, end_val, n):
    return math.exp(math.log(end_val/start_val)/n)-1.0 

# If R&D expense amortization calendar has n years and we have n years of data, 
# the calculation is straight forward. sum of 1/n of each year's r&d expense for the past n years will give the amortization
# But if we have less than n years of data, we need to make some hieuristics
#
def calc_rnd_amortization(ticker, cur_year, amort_years):
    start_year, end_year = get_range_of_years_dict(cfd, ticker)
    amort = 0.0
    if ((cur_year - amort_years) >= start_year): # we have enough data for amortization
        for i in range(amort_years):
            amort = amort + float(cfd[ticker, cur_year-(i+1)]['R&D expense'])/amort_years
        return amort

    numyears_of_data = cur_year - start_year
    for i in range(numyears_of_data): # Get real data as much as available
        amort = amort + float(cfd[ticker, cur_year-(i+1)]['R&D expense'])/amort_years

    rate = calc_rate_of_growth(cfd[ticker, start_year]['R&D expense'], cfd[ticker, end_year]['R&D expense'], end_year-start_year)
    #Use this rate of growth to intrapolate the R&D expense of past years
    numyears_of_intrapolation = amort_years - numyears_of_data #Say we had only 3 years of data whereas the amort calendar needed 5 years of data ... 
    for i in range(numyears_of_intrapolation): # ... Use the intrapolated value for 2 remaining years
        amort = amort + float(cfd[ticker, start_year]['R&D expense'])/(1+rate)**(i+1)/amort_years
    return amort

# Calculate EBIT, R&D adjustment, Imputed interest expense on operational lease, Adjusted EBIT, Adjusted Net capital expense, Adjusted WC delta 
# and ultimately the Free cash Flow
# TBD: Before starting, make sure the corp_fin_dict[(ticker,year)] values are sane. If needed, for those with no data, we need to intrapolate with historical multiples/margins
def calc_fcf_to_firm (ticker, year):
    dcf_dict[(ticker, year)] = {}
    dcf_dict[(ticker, year)]['EBIT'] = cfd[(ticker,year)]['Earnings']/(1 - cfd[(ticker,year)]['IT rate']) + cfd[(ticker,year)]['Net interest']
    dcf_dict[(ticker, year)]['R&D amortization']= calc_rnd_amortization(ticker, year, 5) # change 5 to fetch from industry database
    dcf_dict[(ticker, year)]['R&D adjustment'] = cfd[(ticker,year)]['R&D expense'] - dcf_dict[(ticker, year)]['R&D amortization']

    dcf_dict[(ticker, year)]['debtized operational lease'] = csd[(ticker,year,'op lease commitment')]['PV of years 1 through n'] + csd[(ticker,year,'op lease commitment')]['PV of thereafter annuitized'] 
    ccd[(ticker, year)]['debtized operational lease'] = dcf_dict[(ticker, year)]['debtized operational lease'] / cfd[(ticker, year)]['Revenue']

    dcf_dict[(ticker, year)]['imputed interest expense on operational lease'] = dcf_dict[(ticker, year)]['debtized operational lease'] * cfd[(ticker,year)]['Pre-tax Debt Rate']
    dcf_dict[(ticker, year)]['Adjusted EBIT'] = dcf_dict[(ticker, year)]['EBIT'] + dcf_dict[(ticker, year)]['R&D adjustment'] + dcf_dict[(ticker, year)]['imputed interest expense on operational lease']
    dcf_dict[(ticker, year)]['Adjusted EBIT(1-t)'] = dcf_dict[(ticker, year)]['Adjusted EBIT'] * (1 - cfd[(ticker,year)]['IT rate'])
    dcf_dict[(ticker, year)]['Tax benefit due to expensing capital'] = ((dcf_dict[(ticker, year)]['R&D adjustment'] + dcf_dict[(ticker, year)]['imputed interest expense on operational lease'])
									* cfd[(ticker,year)]['IT rate'])
    dcf_dict[(ticker, year)]['Adjusted operating income'] = dcf_dict[(ticker, year)]['Adjusted EBIT(1-t)'] + dcf_dict[(ticker, year)]['Tax benefit due to expensing capital']
    dcf_dict[(ticker, year)]['Net capital expense stated'] = cfd[(ticker,year)]['Stated Capital Spending'] - cfd[(ticker,year)]['Depreciation']

    dcf_dict[(ticker, year)]['Adjusted net capital expense'] = (  dcf_dict[(ticker, year)]['Net capital expense stated'] 
								+ cfd[(ticker,year)]['R&D expense'] - dcf_dict[(ticker, year)]['R&D amortization']
								+ cfd[(ticker,year)]['Acquisitions']
								+ cfd[(ticker,year)]['Operations Lease Expense'] - cfd[(ticker,year)]['Depreciation on Leased Assets'])
    ccd[(ticker, year)]['Adjusted net capital expense'] = dcf_dict[(ticker, year)]['Adjusted net capital expense'] / cfd[(ticker, year)]['Revenue']

    dcf_dict[(ticker, year)]['Non cash working capital this year'] = ( cfd[(ticker,year)]['Accounts Receivable'] + cfd[(ticker,year)]['Inventory'] + cfd[(ticker,year)]['Other Current Assets']
								       - (cfd[(ticker,year)]['Accounts Payable'] + cfd[(ticker,year)]['Other Current Liabilities']) )
    ccd[(ticker, year)]['Non cash working capital this year'] = dcf_dict[(ticker, year)]['Non cash working capital this year'] / cfd[(ticker, year)]['Revenue']

    start, end = get_range_of_years_dict(cfd, ticker)
    if (year != start):
        dcf_dict[(ticker, year)]['Non cash working capital delta'] = dcf_dict[(ticker, year)]['Non cash working capital this year'] - dcf_dict[(ticker, year-1)]['Non cash working capital this year']
    else: # If we dont have data about last year, use revenue multiple as a proxy
        rev_rate = calc_rate_of_growth(cfd[(ticker,start)]['Revenue'], cfd[(ticker, end)]['Revenue'], end-start)
        # Now intrapolate past year's revenue (for which we dont have data)
        last_year_rev = cfd[(ticker, year)]['Revenue']/(1+rev_rate)
        # Now use the revenue multiple of WC to proxy last year's WC
        non_cash_wc_last_year = last_year_rev * ccd[(ticker, year)]['Non cash working capital this year']
        dcf_dict[(ticker, year)]['Non cash working capital delta'] = dcf_dict[(ticker, year)]['Non cash working capital this year'] - non_cash_wc_last_year

    dcf_dict[(ticker, year)]['FCF to firm'] = ( dcf_dict[(ticker, year)]['Adjusted operating income'] 
						- (dcf_dict[(ticker, year)]['Adjusted net capital expense'] + dcf_dict[(ticker, year)]['Non cash working capital delta']) )
   
def calc_firmvalue_dcf (ticker, year):
    global dcf_dict

    wacc, wacc_terminal = get_wacc(ticker)
    
    if (ticker, year+1) in dcf_dict:
       dcf_dict[(ticker, year)]['Firm Value'] = dcf_dict[(ticker, year)]['FCF to firm'] + float(calc_firmvalue_dcf(ticker, year+1))/(1+wacc)
       return dcf_dict[(ticker, year)]['Firm Value']
    else: # Terminal case
       dcf_dict[(ticker, year)]['Firm Value'] = dcf_dict[(ticker, year)]['FCF to firm'] + dcf_dict[(ticker, 'Terminal')]['FCF to firm']/(1+wacc_terminal)
       return dcf_dict[(ticker, year)]['Firm Value']

# Return the String s that contains the entire html dump of the Discounted cash Flow calculations
def get_dcf_dict_dump(ticker, start, end):
    global cdd
    global dcf_calc_display  
    s = r"""<table class="table-fill">
<thead>
<tr>
<th class="text-center"><img src=""" + cdd[ticker]['Logo'] + r""" height="42" width="42" /></th>

"""
    for i in range(end-start+1):
        s += '<th class="text-left">'+str(start+i)+'</th>\n'
    s += '<th class="text-left">Terminal</th>\n'

    s += r"""</tr>
</thead>
<tbody class="table-hover">
"""
# Even though the dereferences sound cryptic, it is very simple.
# Every dcf_calc_display[i] is a 4 tuple. (varname, displayname, dict, format)
# so, if you want the value of the variable, you have to do a dict(ticker, yyyy).
# dict itself is 3rd tuple in dcf_calc_display[i]. so, dcf_calc_display[i][2]
# once you have a dict you have to index w/ (ticker, yyyy). The key you are interested in
# is given in varname tuple @ dcf_calc_display[i][0]  
    for i in range(len(dcf_calc_display)):        
        s += '<tr>\n<td class="text-left-XLwidth">' + dcf_calc_display[i][1] + '</td>\n'
        for j in range(end-start+1):
           s += '<td class="text-left"><div contenteditable><script type="text/javascript">document.write(numeral(' + str(dcf_calc_display[i][2][(ticker, start+j)][dcf_calc_display[i][0]]) + ').format(' + dcf_calc_display[i][3] + '))</script></div></td>\n'
        if (dcf_calc_display[i][0] == 'FCF to firm'): # Add terminal value
           s += '<td class="text-left"><div contenteditable><script type="text/javascript">document.write(numeral(' + str(dcf_calc_display[i][2][(ticker, 'Terminal')][dcf_calc_display[i][0]]) + ').format(' + dcf_calc_display[i][3] + '))</script></div></td>\n'
        s += '</tr>\n' #and then add end of row character

    s += r"""</tbody>
</table>

"""

    return s
 
#TBD: Move it to a non-blocking thread, so the daemon can get started asap. Also, to limit the queries to start only after templates are written, prepare a "DONE" semaphore
def write_detailed_ticker_templates():
    global cdd
    global dcf_ip
    global dcf_dict
    dir_base = '/usr/lib/cgi-bin/mysite/fin/templates/fin/table_'
    dir_tail = '.html'
    html_hdr = get_html_header("Under the hood")
    body_top = get_html_body_top("/fin/table/ins_command_here")
    for ticker in cdd.keys():
       file_name = dir_base+ticker+dir_tail
       if (os.path.isfile(file_name)):
           os.unlink(file_name)
       f = open(file_name, 'w')

       f.write(html_hdr) # HTML header points to CSS etc.
       f.write(body_top.replace("ins_command_here",ticker))

       # Capture the first str replace in a new string, s. Then use a simple for loop. Ah.. dont you love python!
       s = get_dcf_ip_params_hdr() + get_dcf_ip_params_line_template() 
       s = s.replace('ins_logo_here', cdd[ticker]['Logo'])
       mapping = [('ins_ticker_here',""),
	 	  ('ins_rev_growth',str(dcf_ip[(ticker, 'stage1')]['revenue growth'])),
		  ('ins_ear_growth',str(dcf_ip[(ticker, 'stage1')]['earnings growth'])),
		  ('ins_numstage_years',str(dcf_ip[(ticker, 'stage1')]['num years in stage'])),
		  ('ins_terminal_growth',str(dcf_ip[(ticker, 'Terminal')]['growth'])),
		  ('ins_market_ret',str(dcf_ip[(ticker, 'global')]['Rm'])),
		  ('ins_rf',str(dcf_ip[(ticker, 'global')]['Rf'])),
		  ('ins_beta',str(dcf_ip[(ticker, 'global')]['beta'])),
		  ('ins_ke',str(dcf_ip[(ticker, 'global')]['Ke'])),
		  ('ins_kd',str(dcf_ip[(ticker, 'global')]['Kd'])),
		  ('ins_wacc',str(dcf_ip[(ticker, 'global')]['WACC'])),
		  ('ins_terminal_wacc',str(dcf_ip[(ticker, 'Terminal')]['WACC']))]
       for k, v in mapping:
           s = s.replace(k,v)
       s += get_dcf_ip_params_tail()
       f.write(s) # All of DCF Input parameters for one ticker are right here
       start_year, end_year = get_range_of_years_dict(dcf_dict, ticker)
       initialize_dcf_dict_display()
       s = get_dcf_dict_dump(ticker, start_year, end_year)
       f.write(s)
       f.close()

def get_dfcf_ip_html_header():
    s = r"""
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8" />
	<title>DFCF Input Parameters</title>
	<meta name="viewport" content="initial-scale=1, maximum-scale=1, width=device-width">
	<link rel="stylesheet" type="text/css" href="/data_table_style.css">
        <script src="/uglyfinance_dfcf_input_helper.js"></script>
        <script src="//code.jquery.com/jquery-1.10.2.js"></script>
	<script src="//cdnjs.cloudflare.com/ajax/libs/numeral.js/1.4.5/numeral.min.js"></script>
	<script>
var data = {%%insert_initializing_data_here%%
           };
           var changeset = {%%insert_changeset_data_here%%};
	   var bgd;

	</script>
</head>
"""
    return s

def get_dfcf_html_body_top_guest():
    s = r"""
   <!-- Start Header -->
    <div id="header">
        <!-- Logo -->
        <a href="/fin/dfcf_input" id="logo" >theuglyfinancesite.com</a>
        <!-- Login/Sign up -->
        <div id="user_auth">
            <form id="log_signin" method="post" action="/fin/dfcf_input">
            {% csrf_token %}
                <input type="text" id="username" value="" placeholder="User" name="username" tabindex="1"/> 
                <input type="password" id="password" name="password" placeholder="Password" value="" autocomplete="off" tabindex="2" maxlength="32"/>
                <input type="submit" value="Log In" >
                <input type="submit" value="Sign Up" >
            </form> <!-- End Credentials form -->
        </div> <!-- End user auth -->

    </div> <!-- End Header  -->

<div id="fin_body"> <!-- Fin body header -->
"""
    return s

def get_dfcf_html_body_top_user(user):
    s = r"""
    <!-- Start Header -->
    <div id="header">
        <!-- Logo -->
        <a href="/fin/dfcf_input" id="logo" >theuglyfinancesite.com</a>
        <!-- Logout -->
        <div id="user_auth">
            <form id="log_signout" method="post" action="/fin/dfcf_input/logout">
            {% csrf_token %}
                <div> Welcome! %%user%% </div>
                <input type="submit" value="Log Out" >
            </form> <!-- End Credentials form -->
        </div> <!-- End user auth -->

    </div> <!-- End Header  -->

<div id="fin_body"> <!-- Fin body header -->

<form id="form2" name="form2" method="post" action="/fin/dfcf_input_modify">
{% csrf_token %}
<div>
<input type="submit" id="submitButton" name="submitButton" value="Modify">
</div>
</form>

<script>

var form = document.getElementById('form2');
if (form.attachEvent) {
    form.attachEvent("onsubmit", function() { return processForm(event, data, changeset); });
} else {
   form.addEventListener("submit", function() { return processForm(event, data, changeset); });
}

</script>
"""
    
    s = s.replace('%%user%%',user)
    return s

def get_dfcf_html_body_top(user):
    s = r"""
<body onload="Initialize()">
"""

    if (user == 'guest'):
        s += get_dfcf_html_body_top_guest()
    else:
        s += get_dfcf_html_body_top_user(user) 
    return s

def get_dcf_ip_params_hdr():
     s = r"""
<table >
<thead>
<tr>
<th class="text-center">Ticker</th>
<th class="tooltip" onfocus="theFocus(this);" onblur="theBlur(this);" title="For 3% Enter 0.03">Revenue<br/>Growth Rate</th>
<th class="tooltip" onfocus="theFocus(this);" onblur="theBlur(this);" title="For 8% Enter 0.08">Earnings<br/>Growth Rate</th>
<th class="tooltip" onfocus="theFocus(this);" onblur="theBlur(this);" title="For 5 yrs Enter 5">#years in stage</th>
<th class="tooltip" onfocus="theFocus(this);" onblur="theBlur(this);" title="For 2% Enter 0.02">Terminal <br/>Growth Rate</th>
<th class="tooltip" onfocus="theFocus(this);" onblur="theBlur(this);" title="For 10% Enter 0.1">Market returns</th>
<th class="tooltip" onfocus="theFocus(this);" onblur="theBlur(this);" title="For 2% Enter 0.02">Risk Free Rate</th>
<th class="tooltip" onfocus="theFocus(this);" onblur="theBlur(this);" title="Between 0.5 and 2">&#946;</th>
<th class="tooltip" onfocus="theFocus(this);" onblur="theBlur(this);" title="For 8.45% Enter 0.0845">Cost of Equity</th>
<th class="tooltip" onfocus="theFocus(this);" onblur="theBlur(this);" title="For 4.5% Enter 0.045">Cost of Debt</th>
<th class="tooltip" onfocus="theFocus(this);" onblur="theBlur(this);" title="For 8.25% Enter 0.0825">WACC</th>
<th class="tooltip" onfocus="theFocus(this);" onblur="theBlur(this);" title="For 7% Enter 0.07">Terminal WACC</th>
<div id="tooltip"></div>
</tr>
</thead>
<tbody>
"""
     return s

def get_dcf_ip_params_line_template():
    s = r"""
<tr>
<form name="%%ins_ticker_here%%">
<td>%%ins_ticker_here%%</td>
<td><div id="%%ins_ticker_here%%-Revenue-Growth-Rate" contenteditable=%%editable%% onfocus="bgd=pre_input(event, 'val-%%ins_ticker_here%%-Revenue-Growth-Rate')" onblur="changeset['%%ins_ticker_here%%']['rev_growth']=data['%%ins_ticker_here%%']['rev_growth']=validate(event, 'val-%%ins_ticker_here%%-Revenue-Growth-Rate', bgd, 'percent')"><script>document.write(numeral(%%ins_rev_growth%%).format('0.00%'))</script></div><input type="hidden" value=%%ins_rev_growth%% id="val-%%ins_ticker_here%%-Revenue-Growth-Rate" ></td>
<td><div id="%%ins_ticker_here%%-Earnings-Growth-Rate" contenteditable=%%editable%% onfocus="bgd=pre_input(event, 'val-%%ins_ticker_here%%-Earnings-Growth_Rate')" onblur="changeset['%%ins_ticker_here%%']['earnings_growth']=data['%%ins_ticker_here%%']['earnings_growth']=validate(event, 'val-%%ins_ticker_here%%-Earnings-Growth_Rate', bgd, 'percent')"><script>document.write(numeral(%%ins_ear_growth%%).format('0.00%'))</script></div> <input type="hidden" id="val-%%ins_ticker_here%%-Earnings-Growth_Rate" value=%%ins_ear_growth%%></td>
<td><div id="%%ins_ticker_here%%-years-in-stage" contenteditable=%%editable%% onfocus="bgd=pre_input(event, 'val-%%ins_ticker_here%%-years-in-stage')" onblur="changeset['%%ins_ticker_here%%']['years_in_stage']=data['%%ins_ticker_here%%']['years_in_stage']=validate(event, 'val-%%ins_ticker_here%%-years-in-stage', bgd, 'year')"><script>document.write(numeral(%%ins_numstage_years%%).format('0.0'))</script></div> <input type="hidden" id="val-%%ins_ticker_here%%-years-in-stage" value=%%ins_numstage_years%%></td>
<td><div id="%%ins_ticker_here%%-terminal-growth-rate" contenteditable=%%editable%% onfocus="bgd=pre_input(event, 'val-%%ins_ticker_here%%-terminal-growth-rate')" onblur="changeset['%%ins_ticker_here%%']['terminal_growth_rate']=data['%%ins_ticker_here%%']['terminal_growth_rate']=validate(event, 'val-%%ins_ticker_here%%-terminal-growth-rate', bgd, 'percent')"><script>document.write(numeral(%%ins_terminal_growth%%).format('0.00%'))</script></div> <input type="hidden" id="val-%%ins_ticker_here%%-terminal-growth-rate" value=%%ins_terminal_growth%%></td>
<td><div id="%%ins_ticker_here%%-market-returns" contenteditable=%%editable%% onfocus="bgd=pre_input(event, 'val-%%ins_ticker_here%%-market-returns')" onblur="changeset['%%ins_ticker_here%%']['market_returns']=data['%%ins_ticker_here%%']['market_returns']=validate(event, 'val-%%ins_ticker_here%%-market-returns', bgd, 'percent')"><script>document.write(numeral(%%ins_market_ret%%).format('0.00%'))</script></div> <input type="hidden" id="val-%%ins_ticker_here%%-market-returns" value=%%ins_market_ret%%></td>
<td><div id="%%ins_ticker_here%%-rf-rate" contenteditable=%%editable%% onfocus="bgd=pre_input(event, 'val-%%ins_ticker_here%%-rf-rate')" onblur="changeset['%%ins_ticker_here%%']['rf_rate']=data['%%ins_ticker_here%%']['rf_rate']=validate(event, 'val-%%ins_ticker_here%%-rf-rate', bgd, 'percent')"><script>document.write(numeral(%%ins_rf%%).format('0.00%'))</script></div> <input type="hidden" id="val-%%ins_ticker_here%%-rf-rate" value=%%ins_rf%%></td>
<td><div id="%%ins_ticker_here%%-beta" contenteditable=%%editable%% onfocus="bgd=pre_input(event, 'val-%%ins_ticker_here%%-beta')" onblur="changeset['%%ins_ticker_here%%']['beta']=data['%%ins_ticker_here%%']['beta']=validate(event, 'val-%%ins_ticker_here%%-beta', bgd, 'beta')">%%ins_beta%%</div> <input type="hidden" id="val-%%ins_ticker_here%%-beta" value=%%ins_beta%%></td>
<td><div id="%%ins_ticker_here%%-ke" contenteditable=%%editable%% onfocus="bgd=pre_input(event, 'val-%%ins_ticker_here%%-ke')" onblur="changeset['%%ins_ticker_here%%']['ke']=data['%%ins_ticker_here%%']['ke']=validate(event, 'val-%%ins_ticker_here%%-ke', bgd, 'percent')"><script>document.write(numeral(%%ins_ke%%).format('0.00%'))</script></div> <input type="hidden" id="val-%%ins_ticker_here%%-ke" value=%%ins_ke%%></td>
<td><div id="%%ins_ticker_here%%-kd" contenteditable=%%editable%% onfocus="bgd=pre_input(event, 'val-%%ins_ticker_here%%-kd')" onblur="changeset['%%ins_ticker_here%%']['kd']=data['%%ins_ticker_here%%']['kd']=validate(event, 'val-%%ins_ticker_here%%-kd', bgd, 'percent')"><script>document.write(numeral(%%ins_kd%%).format('0.00%'))</script></div> <input type="hidden" id="val-%%ins_ticker_here%%-kd" value=%%ins_kd%%></td>
<td><div id="%%ins_ticker_here%%-wacc" contenteditable=%%editable%% onfocus="bgd=pre_input(event, 'val-%%ins_ticker_here%%-wacc')" onblur="changeset['%%ins_ticker_here%%']['wacc']=data['%%ins_ticker_here%%']['wacc']=validate(event, 'val-%%ins_ticker_here%%-wacc', bgd, 'percent')"><script>document.write(numeral(%%ins_wacc%%).format('0.00%'))</script></div> <input type="hidden" id="val-%%ins_ticker_here%%-wacc" value=%%ins_wacc%%></td>
<td><div id="%%ins_ticker_here%%-terminal-wacc" contenteditable=%%editable%% onfocus="bgd=pre_input(event, 'val-%%ins_ticker_here%%-terminal-wacc')" onblur="changeset['%%ins_ticker_here%%']['terminal_wacc']=data['%%ins_ticker_here%%']['terminal_wacc']=validate(event, 'val-%%ins_ticker_here%%-terminal-wacc', bgd, 'percent')"><script>document.write(numeral(%%ins_terminal_wacc%%).format('0.00%'))</script></div> <input type="hidden" id="val-%%ins_ticker_here%%-terminal-wacc" value=%%ins_terminal_wacc%%></td>
</form>
</tr>
"""
    return s
    
def get_dcf_ip_params_tail(user):
    s = r"""
</tbody>
</table>
"""

    if (user != 'guest'):
        s += r"""
<form id="form1" name="form1" method="post" action="/fin/dfcf_input_modify">
{% csrf_token %}
<div>
<input type="submit" id="submitButton" name="submitButton" value="Modify">
</div>
</form>

<script>

var form = document.getElementById('form1');
if (form.attachEvent) {
    form.attachEvent("onsubmit", function() { return processForm(event, data, changeset); });
} else {
   form.addEventListener("submit", function() { return processForm(event, data, changeset); });
}

</script>
"""

    s += r"""
</div> <!-- End Fin body header -->

<p id="myP"></p>
</body>
</html>
"""
    return s

def write_dfcf_input_parameter_template():
    global cdd
    global dcf_ip
    global dcf_dict
    initial_data = ''
    changeset_data = ''
    editable='true'
   
    for user in dictionaries.keys():
        if (user == 'root'):
            continue
        elif (user == 'guest'):
            file_name = '/usr/lib/cgi-bin/mysite/fin/templates/fin/dfcf_input_parameters.html'
            editable='false'
        else:
            file_name = '/usr/lib/cgi-bin/mysite/fin/templates/fin/' + user + '/dfcf_input_parameters.html'
            editable='true'

        # Create path if it doesnt already exist
        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name))

        # If file exists, scratch it so we start fresh
        if (os.path.isfile(file_name)):
            os.unlink(file_name)

        f = open(file_name, 'w')
        s = get_dfcf_ip_html_header() + \
            get_dfcf_html_body_top(user) + \
            get_dcf_ip_params_hdr()
        d = dictionaries[user]['dcf_ippar_dict']
        for ticker in cdd.keys():
           s += get_dcf_ip_params_line_template()
           # Capture the first str replace in a new string, s. Then use a simple for loop. Ah.. dont you love python!
           mapping = [('%%ins_ticker_here%%',ticker),
    	 	  ('%%ins_rev_growth%%',str(d[(ticker, 'stage1')]['revenue growth'])),
    		  ('%%ins_ear_growth%%',str(d[(ticker, 'stage1')]['earnings growth'])),
    		  ('%%ins_numstage_years%%',str(d[(ticker, 'stage1')]['num years in stage'])),
    		  ('%%ins_terminal_growth%%',str(d[(ticker, 'Terminal')]['growth'])),
    		  ('%%ins_market_ret%%',str(d[(ticker, 'global')]['Rm'])),
    		  ('%%ins_rf%%',str(d[(ticker, 'global')]['Rf'])),
    		  ('%%ins_beta%%',str(d[(ticker, 'global')]['beta'])),
    		  ('%%ins_ke%%',str(d[(ticker, 'global')]['Ke'])),
    		  ('%%ins_kd%%',str(d[(ticker, 'global')]['Kd'])),
    		  ('%%ins_wacc%%',str(d[(ticker, 'global')]['WACC'])),
    		  ('%%ins_terminal_wacc%%',str(d[(ticker, 'Terminal')]['WACC'])),
                  ('%%editable%%', editable)]
           for k, v in mapping:
               s = s.replace(k,v)
    
           changeset_data += ticker+':{}, '
           initial_data += ticker+':{rev_growth:'+ str(d[(ticker, 'stage1')]['revenue growth'])+\
                                  ', earnings_growth:'+ str(d[(ticker, 'stage1')]['earnings growth'])+\
                                  ', years_in_stage:' + str(d[(ticker, 'stage1')]['num years in stage'])+\
                                  ', terminal_growth_rate:' + str(d[(ticker, 'Terminal')]['growth'])+\
                                  ', market_returns:' + str(d[(ticker, 'global')]['Rm'])+\
                                  ', rf_rate:' + str(d[(ticker, 'global')]['Rf'])+\
                                  ', beta:' + str(d[(ticker, 'global')]['beta'])+\
                                  ', ke:'+ str(d[(ticker, 'global')]['Ke'])+\
                                  ', kd:'+ str(d[(ticker, 'global')]['Kd'])+\
                                  ', wacc:'+ str(d[(ticker, 'global')]['WACC'])+\
                                  ', terminal_wacc:'+ str(d[(ticker, 'Terminal')]['WACC'])+'},\n            '
    
           
        s += get_dcf_ip_params_tail(user)
        s = s.replace('%%insert_initializing_data_here%%', initial_data)
        s = s.replace('%%insert_changeset_data_here%%', changeset_data)
        f.write(s) # All of DCF Input parameters for all tickers are right here
        f.close()
        initial_data = ''
        changeset_data = ''
    
     
def write_templates():
    # write_detailed_ticker_templates()
    write_dfcf_input_parameter_template()


