frappe.provide("fluorine");

cur_frm.cscript.refresh = function(doc){
	var cs = cur_frm.cscript;
	console.log("fluorine_site_names ", doc);
	if(doc.fluorine_site_type === "Dedicated"){
		hide_field(["fluorine_site_depends_of_name"]);
		unhide_field(["ip_address", "fluorine_ddp_conn_url", "fluorine_desk_site_root_prefix", "fluorine_dependents_section"]);
		//doc.fluor_dev_mode = 0;
	}else{
		unhide_field(["fluorine_site_depends_of_name"]);
		hide_field(["ip_address", "fluorine_ddp_conn_url", "fluorine_desk_site_root_prefix", "fluorine_dependents_section"]);
	}
	web_integration(doc.fluorine_frappe_web_integration);
}


cur_frm.cscript["fluorine_site_type"] = function(doc){

	if(doc.fluorine_site_type === "Dedicated"){
		hide_field(["fluorine_site_depends_of_name"]);
		unhide_field(["ip_address", "fluorine_ddp_conn_url", "fluorine_desk_site_root_prefix", "fluorine_dependents_section"]);
		//doc.fluor_dev_mode = 0;
	}else{
		unhide_field(["fluorine_site_depends_of_name"]);
		hide_field(["ip_address", "fluorine_ddp_conn_url", "fluorine_desk_site_root_prefix", "fluorine_dependents_section"]);
	}
}

web_integration = function(integrate){

	if (integrate){
		unhide_field(["fluorine_web_site_root_prefix", "fluorine_web_ddp_conn_url"]);
	}else{
		hide_field(["fluorine_web_site_root_prefix", "fluorine_web_ddp_conn_url"]);
	}
}


cur_frm.cscript["fluorine_frappe_web_integration"] = function(doc){

	web_integration(doc.fluorine_frappe_web_integration);

}
