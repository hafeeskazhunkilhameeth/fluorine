
Meteor.methods({
	frappe_register: function(user){
		var result = frappe.register(user.email, user.profile.name);
		if (result.error)
			return;
		return "OK";
	},
	update_password: function(args){
		var result = frappe.update_password(args);
		if (result.error)
			return;
		console.log("result from update password ", result);
		return "OK";
	}
});