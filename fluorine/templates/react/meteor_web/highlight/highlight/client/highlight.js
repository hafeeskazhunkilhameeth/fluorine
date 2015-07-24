Session.set("hl", "");
Session.setDefault("classename", "highlight");

Template.registerHelper("highlight", function(key, arg1){
	console.log("highlight func args: ", key, arg1);
	Template[key].events({
	'click .highlight': function (ev) {
		ev.stopPropagation();
		console.log("Jinja2 template data: ", EJSON.parse(arg1));
	  }
	});
	if (Session.get("hl") == key || Session.get("hl") == "all"){
		classe = Session.get("classename");
	}else{
		classe = "nohighlight";
	}
	return classe;
});


digest = function(password){

	f1 = Package.CryptoJS.SHA1(password);
	return Package.CryptoJS.SHA1(f1).toString(Package.CryptoJS.enc.Hex);
}

Accounts._hashPassword = function (password) {                                                                // 60
  return {                                                                                                    // 61
    digest: digest(password),                                                                                 // 62
    algorithm: "sha-1"                                                                                      // 63
  };                                                                                                          // 64;
}
