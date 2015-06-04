frappe.provide("fluorine");


cur_frm.cscript.fluor_make_meteor_file_btn = function(doc){
	var cs = cur_frm.cscript;

	frappe.call({
		   freeze: true,
		   freeze_message: "Making Meteor File...",
	       method:  "fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity.make_meteor_file",
	       args: {devmode: doc.fluor_dev_mode, mthost: doc.fluor_meteor_host, mtport: doc.fluor_meteor_port,
	       			mghost:doc.fluor_mongo_host, mgport: doc.fluor_mongo_port,mgdb: doc.fluor_mongo_database},
     });
}

cur_frm.cscript.refresh = function(doc){
	var cs = cur_frm.cscript;
	if(doc.__islocal !== 1){
		unhide_field(["make_meteor_file"]);
	}

	if(doc.fluorine_state === "off"){
		hide_field(["fluorine_reactivity", "fluorine_base_template"]);
	}else{
		unhide_field(["fluorine_reactivity", "fluorine_base_template"]);
	}
}

cur_frm.cscript["fluorine_state"] = function(doc){
	if(doc.fluorine_state === "off"){
		hide_field(["fluorine_reactivity", "fluorine_base_template"]);
	}else{
		unhide_field(["fluorine_reactivity", "fluorine_base_template"]);
	}
}

$(document).on("save", function(ev, doc){
	var cs = cur_frm.cscript;
	if(doc.__islocal === 1){
		unhide_field(["make_meteor_file"]);
	}
});