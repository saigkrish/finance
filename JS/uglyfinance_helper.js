
function Initialize ()  {
	    var el_id = document.getElementById("myP");
	    el_id.innerHTML=JSON.stringify(data);
}

/*
 * Capture the background info and change the background info for the clicked text box
 * Make the box populated with unformatted value that can be edited
 */
function pre_input (e, val_id) {
//  Match the pattern numeral(0.08) for instance
    var el_id = document.getElementById(e.currentTarget.id);
    var back = el_id.style.backgroundColor;
    el_id.style.backgroundColor = "#4E5066";
    el_id.innerHTML = document.getElementById(val_id).value;   
    
    return back;
}

/*
 * If nonsense is entered, numeral.js will return 0.00% or $0.00
 * In that case, keep the old v_id.value. If not, replace v_id.value with the edited value
 */
function validate (e, val_id, back, format) {
    var el_id = document.getElementById(e.currentTarget.id);
    var v_id = document.getElementById(val_id);
    var valid = true;

     el_id.style.backgroundColor = back;

    // Check if what is inputed is not a garbage
    switch(format) {
    case 'percent':
	 if(numeral(el_id.innerHTML).format('0.00%') == "0.00%") {
	     valid = false;
	 }
	 break;
    case 'currency':
	 if(numeral(el_id.innerHTML).format('$0,0.00') == "$0.00") {
	     valid = false; 
	 }
	 break;
    case 'year':
	 if(numeral(el_id.innerHTML).format('0.0') == "0.0") {
	     valid = false; 
	 }
	 break;
    case 'beta':
	 if((numeral(el_id.innerHTML).format('0.00') == "0.00") ||  (el_id.innerHTML < 0.5 || el_id.innerHTML > 2.0)) {
	     valid = false; 
	 }
	 break;
    default: 
	 if (el_id.innerHTML == 0) {
	     valid = false;
	 }
    }         

    // Change the value of the hidden element to non-formatted modified value if input is valid
     if (valid == true) {
	 v_id.value = el_id.innerHTML;
     }

    // Change the innerHTML of the div to formatted value
    switch(format) {
    case 'percent':
	 el_id.innerHTML = numeral(v_id.value).format('0.00%');
	 break;
    case 'currency':
	 el_id.innerHTML = numeral(v_id.value).format('$0,0.00');
	 break;
    case 'year':
	 el_id.innerHTML = numeral(v_id.value).format('0.0');
	 break;
    case 'beta':
	 el_id.innerHTML = numeral(v_id.value).format('0.00');
	 break;
    default: 
	 el_id.innerHTML = v_id.value;
    }         

    // Return the non-formatted value so JS object can be updated
    return v_id.value;
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
	var cookies = document.cookie.split(';');
	for (var i = 0; i < cookies.length; i++) {
	    var cookie = jQuery.trim(cookies[i]);
	    // Does this cookie string begin with the name we want?
	    if (cookie.substring(0, name.length + 1) == (name + '=')) {
		cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
		break;
	    }
	}
    }
    return cookieValue;
}


function processResponse(status, resp_data) {
    document.getElementById("myP").innerHTML = resp_data;
}

function theFocus(obj) {
    var tooltip = document.getElementById("tooltip");
    tooltip.innerHTML = obj.title;
    tooltip.style.display = "block";
    tooltip.style.top = obj.offsetTop - tooltip.offsetHeight + "px";
    tooltip.style.left = obj.offsetLeft + "px";
}

function theBlur(obj) {
    var tooltip = document.getElementById("tooltip");
    tooltip.style.display = "none";
    tooltip.style.top = "-9999px";
    tooltip.style.left = "-9999px";
}

function processForm (e, rawdata) {
    /*Stop the usual form submission event*/
    e.preventDefault();
    // document.getElementById("myP").innerHTML = JSON.stringify(data);
    /* get the elements required for the post method*/
    var csrftoken = getCookie('csrftoken');
    alert(csrftoken);
    var url = document.getElementById("form1").action
    alert(url);
    var jdata = JSON.stringify(rawdata);
    alert(jdata);

    /* post method */
    $.post( url,
	  {csrfmiddlewaretoken: csrftoken,
	   dfcf_ip_params:jdata},
	  function(resp_data, status ) {
	      processResponse(status, resp_data);
	  });      
    return false;
}
