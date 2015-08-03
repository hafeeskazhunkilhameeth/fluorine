if (typeof frappe === 'undefined')
	frappe = {};

//not used
frappe.get_translation_dict = function(lang, uid){;
	var userId = Meteor.userId() || uid;
	if (userId === 'undefined')
		return;

	var userinfo = Meteor.users.find(userId).fetch()[0];
	var sid = userinfo.profile.sid;
	//var cookies = frappe.get_frappe_cookie(userId, ["sid"]);
	var trans = frappe.translation(lang);
	console.log("translations ", trans);
	return trans;
}