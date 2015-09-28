frappe.provide("fluorine");


cur_frm.cscript.onload = function(doc){
	check_production_mode(doc);
}


cur_frm.cscript.fluor_update_fluorine_apps_btn = function(doc){
	var cs = cur_frm.cscript;

	frappe.call({
		   freeze: true,
		   freeze_message: "Checking For Application Updates...",
		   method:  "fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity.check_apps_updates"
	});
}

cur_frm.cscript.refresh = function(doc){
	var cs = cur_frm.cscript;

	if(doc.fluorine_state === "off"){
		hide_field(["fluorine_reactivity"]);
		//doc.fluor_dev_mode = 0;
	}else{
		unhide_field(["fluorine_reactivity"]);
	}

	if (doc.check_mongodb == 1){
		unhide_field(["mongodb"]);
	}else{
		hide_field(["mongodb"]);
	}
}

cur_frm.cscript["fluorine_state"] = function(doc){
	if(doc.fluorine_state === "off"){
		hide_field(["fluorine_reactivity"]);
	}else{
		unhide_field(["fluorine_reactivity"]);
	}
}

cur_frm.cscript["fluor_dev_mode"] = function(doc){
	/*if (cur_frm.cscript.devmode === 1){
		hide_field(["update_fluor_apps"]);
	}else{
		unhide_field(["update_fluor_apps"]);
	}*/
}

cur_frm.cscript["check_mongodb"] = function(doc){
	if (doc.check_mongodb == 1){
		unhide_field(["mongodb"]);
	}else{
		hide_field(["mongodb"]);
	}
}

$(document).on("save", function(ev, doc){
	if (doc.fluor_dev_mode == 0 && doc.fluorine_state === "off"){
		msgprint("Please issue `bench fluorine set-state production` to enter in production mode.");
	}else if(doc.fluor_dev_mode == 1 && doc.fluorine_state === "on"){
		msgprint("Please issue `bench fluorine set-state develop` to enter in developer mode and then `bench start` and go to 'http://localhost'.");
	}else if(doc.fluor_dev_mode == 0 && doc.fluorine_state === "off"){
		msgprint("Please issue `bench start` and got to 'http://localhost:8000' to enter in original frappe web.");
	}

	check_production_mode(doc);
});


check_production_mode = function(doc){
	var cs = cur_frm.cscript;
	if(doc.fluor_dev_mode == 0 && doc.fluorine_state === "off"){
		cs.devmode = 0;
		//unhide_field(["make_meteor_file"]);
	}else{
		//hide_field(["make_meteor_file"]);
		cs.devmode = 1;
	}
}