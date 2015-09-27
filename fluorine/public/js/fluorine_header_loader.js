
if (typeof frappe_meteor === 'undefined')
	frappe_meteor = {};

frappe_meteor.sid_length = 56;


is_valid_sid = function(sid){
    var sid = sid || frappe.get_cookie("sid");
    if (sid && sid.length >= frappe_meteor.sid_length)
        return true;

    return false;
}


/*frappe.call({
           freeze: true,
		   freeze_message: "Preparing for meteor, please wait...",
	       "method": "fluorine.utils.boot.get_js_css_files",
	       callback: function(response_data){
               if (response_data && response_data.message){
                    var js = response_data.message[0];

                    for (var i=0; i<js.length; i++){
                        //console.log("msg ", js[i]);
                        $('<script type="text/javascript" src='+ js[i] + '></script>').appendTo(document.body);
                    }


               }
           }
});*/


$(document).on('app_ready', function(ev){
	console.log("frappe is ready!!!!");
	$('.case-wrapper[data-name="Fluorine Admin"]').hide();
    if(frappe.boot['Fluorine'] && frappe.boot['Fluorine'].site){
        frappe.require(repl("/assets/css/%(sitename)s.css", {"sitename": frappe.boot['Fluorine'].site}));
        frappe.require(repl("/assets/js/%(sitename)s.min.js", {"sitename": frappe.boot['Fluorine'].site}));
    }
    //$("#toolbar-user").prepend(repl("<li><a href='%(pathname)s/admin'>Admin</a></li><li class='divider'></li>", {"pathname": pathname}));
    //$(".offcanvas-container").hide();
    var sid = frappe.get_cookie("sid");
    if (typeof(Meteor) !== "undefined" && is_valid_sid(sid)){
        /*Meteor.frappe_login(sid, function(result){
            console.log("Result from login into meteor 2 ", result);
        });*/
        $('.case-wrapper[data-name="Fluorine Admin"]').show();
        console.log("valid login sid ", sid);
    }

});