if (typeof frappe_meteor === 'undefined')
	frappe_meteor = {};

frappe_meteor.sid_length = 56;


is_valid_sid = function(sid){
    var sid = sid || frappe.get_cookie("sid");
    if (sid && sid.length >= frappe_meteor.sid_length)
        return true;

    return false;
}