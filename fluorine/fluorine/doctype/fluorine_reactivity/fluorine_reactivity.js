frappe.provide("fluorine");


cur_frm.cscript.onload = function(doc){
	cur_frm.cscript.devmode = doc.fluor_dev_mode;
}


cur_frm.cscript.fluor_update_fluorine_apps_btn = function(doc){
	var cs = cur_frm.cscript;

	if(doc.fluorine_state == "off" && doc.fluor_dev_mode == 0){
		frappe.call({
			   freeze: true,
			   freeze_message: "Updating fluorine apps...",
			   method:  "fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity.prepare_to_update"
		 });
     }else{
		msgprint(__("Fluorine State is on or developer mode is check."), __("Fluorine Reactivity"));
     }
}

cur_frm.cscript.refresh = function(doc){
	var cs = cur_frm.cscript;
	if(cur_frm.cscript.devmode === 0){
		unhide_field(["update_fluor_apps"]);
	}else{
		hide_field(["update_fluor_apps"]);
	}

	if(doc.fluorine_state === "off"){
		hide_field(["fluorine_reactivity", "fluorine_base_template"]);
		doc.fluor_dev_mode = 0;
	}else{
		unhide_field(["fluorine_reactivity", "fluorine_base_template"]);
	}

	if (doc.check_mongodb == 1){
		unhide_field(["mongodb"]);
	}else{
		hide_field(["mongodb"]);
	}
}

cur_frm.cscript["fluorine_state"] = function(doc){
	if(doc.fluorine_state === "off"){
		hide_field(["fluorine_reactivity", "fluorine_base_template"]);
	}else{
		unhide_field(["fluorine_reactivity", "fluorine_base_template"]);
	}
}

cur_frm.cscript["fluor_dev_mode"] = function(doc){
	console.log("fluor dev mode clicked");
	if (cur_frm.cscript.devmode === 1){
		hide_field(["update_fluor_apps"]);
	}else{
		unhide_field(["update_fluor_apps"]);
	}
}

cur_frm.cscript["check_mongodb"] = function(doc){
	if (doc.check_mongodb == 1){
		unhide_field(["mongodb"]);
	}else{
		hide_field(["mongodb"]);
	}
}

$(document).on("save", function(ev, doc){
	var cs = cur_frm.cscript;
	console.log("new updated");
	if(doc.fluor_dev_mode === 0 && doc.fluorine_state === "on"){
		cur_frm.cscript.devmode = 0;
		//unhide_field(["make_meteor_file"]);
	}else{
		console.log("on save dev mod ", doc.fluor_dev_mode);
		//hide_field(["make_meteor_file"]);
		cur_frm.cscript.devmode = 1;
	}
});