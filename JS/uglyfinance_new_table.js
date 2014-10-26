/* tr[1] is the start row for useful data, tr[0] is the header row
   th[x] is the column header; th[TOTALCOLS] will be '+', provision to add more columns; th[0] holds the Ticker
   td[0][y] = exogenous variables in row tr[1] ; td[x][0] holds variable decription
   so, useful data starts from column td[0][1]
 */


function preinputth(e, cindex) {
    //alert (inputth[cindex].value.toString());
    divth[cindex].innerHTML = inputth[cindex].value;
}

function validateth(e, cindex) {
    var valid = true;

    if ((numeral(divth[cindex].innerHTML).format('0000') == "0") || (divth[cindex].innerHTML < start_year) || (divth[cindex].innerHTML > start_year + TOTALCOLS-3)) {
        alert('Year value is not valid');
        valid = false;
    }

    if (valid == true) {
        inputth[cindex].value = divth[cindex].innerHTML;
    }

    divth[cindex].innerHTML = inputth[cindex].value.toString(); 
    divth[cindex].appendChild(inputth[cindex]);
}

/*
 * Div does not have nodeValue field. So create a hidden input type and then set the value field
 * to access it, use indexth[cindex].value
 */
function create_and_append_div_to_th(thisth, cindex, editable, value) {
     d = document.createElement('div');
     d.id = "th"+cindex.toString();
     d.contentEditable=editable;
     d.innerHTML=value.toString();
     d.addEventListener("focus", function() { return preinputth(event, cindex); });
     d.addEventListener("blur", function() { return validateth(event, cindex); });

     inputth[cindex] = document.createElement('input');
     inputth[cindex].type = "hidden";
     inputth[cindex].id = "val" + d.id;
     inputth[cindex].value = value;

     return d;
}

function create_and_append_th(createth, thisrow, rindex, cindex) {
     if (createth == true) {
         th[cindex] = document.createElement('th');
         thisrow.appendChild(th[cindex]);
     }
     if (cindex == 0) { 
         divth[cindex] = create_and_append_div_to_th(th[cindex], cindex, false, "CSCO"); 
     } else {
         divth[cindex] = create_and_append_div_to_th(th[cindex], cindex, false, start_year+cindex-1);
     }
     divth[cindex].appendChild(inputth[cindex]);
     th[cindex].appendChild(divth[cindex]);
}

function populate_th(thisth, nodeval, fn) {
        thisth.innerHTML = nodeval.toString(); 
        thisth.nodeValue = nodeval; 
        if (fn) {
            thisth.removeEventListener("click", fn);
        }
}

function add_minus_appendage() {
         th[TOTALCOLS] = document.createElement('th');
         tr[0].appendChild(th[TOTALCOLS]);
         th[TOTALCOLS].innerHTML = "-";
         th[TOTALCOLS].addEventListener("click", del_column);

         TOTALCOLS++;
}

function add_plus_appendage() {
         th[TOTALCOLS] = document.createElement('th');
         tr[0].appendChild(th[TOTALCOLS]);
         th[TOTALCOLS].innerHTML = "+";
         th[TOTALCOLS].addEventListener("click", add_column);
}

function del_column() {

         if (TOTALCOLS == 2) {return;}

         tr[0].removeChild(th[TOTALCOLS]);
         TOTALCOLS--;

         // disassociate the hiddeninput from div and the div from the th
         divth[TOTALCOLS-1].removeChild(inputth[TOTALCOLS-1]);
         th[TOTALCOLS-1].removeChild(divth[TOTALCOLS-1]);
         populate_th(th[TOTALCOLS-1], "-");
         th[TOTALCOLS-1].addEventListener("click", del_column);

         populate_th(th[TOTALCOLS], "+");
         th[TOTALCOLS].addEventListener("click", add_column);

         for (var i = 1; i <= TOTALROWS; i++){
             divtd[i-1][TOTALCOLS-1].removeChild(inputtd[i-1][TOTALCOLS-1])
             td[i-1][TOTALCOLS-1].removeChild(divtd[i-1][TOTALCOLS-1])
             tr[i].removeChild(td[i-1][TOTALCOLS-1]);
         }

	 var el_id = document.getElementById("myP");
	 el_id.innerHTML= TOTALROWS.toString() + "::::" + TOTALCOLS.toString();
}

function preinputtd(e, rindex, cindex) {
    //alert (inputtd[rindex][cindex].value.toString());
    divtd[rindex][cindex].innerHTML = inputtd[rindex][cindex].value;
}

function validatetd(e, rindex, cindex) {
    var valid = true;
    var ih = divtd[rindex][cindex].innerHTML; 

    // Check if what is inputed is not a garbage
    switch(htmlformat[rindex]) {
    case 'percent':
	 if(numeral(ih).format('0.00%') == "0.00%") {
	     valid = false;
	 } else if (ih > 1) {
             alert ('Input 0.3 for 30%');
             valid = false;
         }
	 break;
    case 'dollar':
	 if(numeral(ih).format('$0,0.00') == "$0.00") {
	     valid = false; 
	 }
	 break;
    case 'number':
	 if(numeral(ih).format('0,0') == "0") {
	     valid = false; 
	 }
	 break;
    default: 
	 if (ih == 0) {
	     valid = false;
	 }
    }         

    // Change the value of the hidden element to non-formatted modified value if input is valid
     if (valid == true) {
	 inputtd[rindex][cindex].value = ih;
     }

    // Change the innerHTML of the div to formatted value
    switch(htmlformat[rindex]) {
    case 'percent':
	 divtd[rindex][cindex].innerHTML= numeral(inputtd[rindex][cindex].value).format('0.00%');
	 break;
    case 'dollar':
	 divtd[rindex][cindex].innerHTML= numeral(inputtd[rindex][cindex].value).format('$0,0.00');
	 break;
    case 'number':
	 divtd[rindex][cindex].innerHTML= numeral(inputtd[rindex][cindex].value).format('0,0');
	 break;
    default: 
	 el_id.innerHTML = v_id.value;
    }         

    divtd[rindex][cindex].appendChild(inputtd[rindex][cindex]);
}

function create_and_append_div_to_td(thistd, rindex, cindex, editable) {
     d = document.createElement('div');
     d.id = "td"+rindex.toString()+cindex.toString();
     d.contentEditable=editable;
     switch (htmlformat[rindex]) {
     case 'dollar':
         d.innerHTML = numeral(0).format('$0,0.00');
         break;
     case 'percent':
         d.innerHTML = numeral(0).format('0.00%');
         break;
     case 'number':
         d.innerHTML = numeral(0).format('0,0');
         break;
     default:
         break;
     }
     d.addEventListener("focus", function() { return preinputtd(event, rindex, cindex); });
     d.addEventListener("blur", function() { return validatetd(event, rindex, cindex); });

     inputtd[rindex][cindex] = document.createElement('input');
     inputtd[rindex][cindex].type = "hidden";
     inputtd[rindex][cindex].id = "val" + d.id;
     inputtd[rindex][cindex].value = 0;

     return d;
}

function create_and_append_cell(thisrow, rindex, cindex) {

         td[rindex][cindex] = document.createElement('td');

	 if (cindex == 0) { // All the titles will come in this column
	     td[rindex][cindex].innerHTML = exog_vars[rindex];
	 } else {
             divtd[rindex][cindex] = create_and_append_div_to_td(td[rindex][cindex], rindex, cindex, true);
             divtd[rindex][cindex].appendChild(inputtd[rindex][cindex]);
             td[rindex][cindex].appendChild(divtd[rindex][cindex]);
         }
         td[rindex][cindex].nodeValue = 0;
         thisrow.appendChild(td[rindex][cindex]);
}

function add_column() {

         // Overwrite the del_column pointer and the "-" symbol with the appropriate year
         populate_th(th[TOTALCOLS-1], "", del_column);
         create_and_append_th(false, tr[0], 0, TOTALCOLS-1);

         for (var i = 1; i <= TOTALROWS; i++){
             create_and_append_cell(tr[i], i-1, TOTALCOLS-1);
         }

         // Overwrite the add_column pointer and the "+" symbol with "-"
         populate_th(th[TOTALCOLS], "-", add_column);
         th[TOTALCOLS].addEventListener("click", del_column);

         // increment the TOTALCOLS; This is the place where the number of cols get more than initial number of total columns
         TOTALCOLS++;

         // add - and +
         add_plus_appendage();

	 var el_id = document.getElementById("myP");
	 el_id.innerHTML= TOTALROWS.toString() + "::::" + TOTALCOLS.toString();
}

function insert_table () {
     for (var i = 0; i < INITROWS; i++){
         td[i] = new Array();
         divtd[i] = new Array();
         inputtd[i] = new Array();
     }

     tr[0] = document.createElement('tr');   
     for (var col = 0; col < INITCOLS; col++){
         create_and_append_th(true, tr[0], 0, col);
     }

     table.appendChild(tr[0]);

     for (var i = 1; i <= INITROWS; i++){
         tr[i] = document.createElement('tr');   
         for (var col = 0; col < INITCOLS; col++){
             create_and_append_cell(tr[i], i-1, col);
         }
         table.appendChild(tr[i]);
     }
     TOTALCOLS = INITCOLS;
     TOTALROWS = INITROWS;

     // add - and +
     add_minus_appendage();
     add_plus_appendage();
     document.body.appendChild(table);
}
