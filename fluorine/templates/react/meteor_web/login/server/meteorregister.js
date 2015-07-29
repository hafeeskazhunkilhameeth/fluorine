
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
	},
	forgot_password: function(email){
		var result = frappe.forgot_password(email);
		if (result.error)
			return;
		console.log("result from forgot password ", result);
		return "OK";
	},
	frappe_logout: function(cookie){
		var result = frappe.logout(cookie);
		console.log("result from logout ", result);
		var res;
		if (result.error){
			res = result;
		}
		else{
			Meteor.users.update(this.userId, {$set: {"profile.frappe_logout": true}});
			res = {cookies: result.headers["set-cookie"]};
		}
		return res;
	}
});