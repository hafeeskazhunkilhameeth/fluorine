
Meteor.methods({
	frappe_register: function(user){
		try{
			var email = user.email;
			var full_name = user.profile.name;
			console.log("recebido pedido ", full_name + " email " + email);
			var result = HTTP.post("http://localhost:8000/api/method/fluorine.utils.user.meteor_sign_up", {params:{email:email, full_name:full_name}, headers:{"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Accept":"application/json"}});
			//result = HTTP.post("http://localhost:8000", {params:{cmd: "fluorine.utils.user.meteor_sign_up", email:email, full_name:full_name}, headers:{"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Accept":"application/json", "X-Requested-With": "XMLHttpRequest"}});
			console.log("result from sign up ", result);
			return "OK";
		}catch(err){
			console.log("erro: ", err);
			return;
		}
	},
	update_password: function(args){
		try{
			var new_password = args.new_password;
			var old_password = args.old_password;
			var key = args.key;
			var result = HTTP.post("http://localhost:8000/api/method/frappe.core.doctype.user.user.update_password", {params:{new_password: new_password, key: key, old_password: old_password}, headers:{"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Accept":"application/json"}});
			console.log("result from update password ", result);
			return "OK";
		}catch(err){
			console.log("erro: ", err);
			return;
		}
	}
});