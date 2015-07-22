Session.set("hl", "");
Session.setDefault("classename", "highlight");

Template.registerHelper("highlight", function(key, arg1){
	console.log("highlight func args 4: ", key, arg1);
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
