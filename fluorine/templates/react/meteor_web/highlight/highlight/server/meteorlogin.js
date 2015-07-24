
Accounts.validateLoginAttempt(function(obj){

	obj.allowed = true;
	console.log("Allowed ", obj.allowed);
	console.log("User ", obj.user);
	console.log("methodArguments ", obj.methodArguments);
	console.log("sha-256 ", Package.sha.SHA256("8950388"));
	userdata = obj.methodArguments[0]
	if (userdata != null){
		user = userdata.user.email;
		password = userdata.password.digest;
		console.log("pedido ", user, password);
		result = HTTP.post("http://localhost:8000/api/method/fluorine.utils.meteor.meteorlogin.verifylogin", {params:{username:user,digest:password}})
		msg = result.data.message;
		if (msg && msg == user){
			console.log("login OK for user ", msg)
		}
	}

	console.log("the result is ", result);

	console.log("error: ", obj.error)
	return true;
})
