frappe.provide("fluorine");

cur_frm.cscript.refresh = function(doc){
	var cs = cur_frm.cscript;
	console.log("fluorine_site_names ", doc);
	if(doc.fluorine_site_type === "Dedicated"){
		hide_field(["fluorine_site_depends_of"]);
		unhide_field(["ip_address", "fluorine_ddp_conn_url", "fluorine_site_root_prefix"]);
		//doc.fluor_dev_mode = 0;
	}else{
		unhide_field(["fluorine_site_depends_of"]);
		hide_field(["ip_address", "fluorine_ddp_conn_url", "fluorine_site_root_prefix"]);
	}

}


cur_frm.cscript["fluorine_site_type"] = function(doc){

	if(doc.fluorine_site_type === "Dedicated"){
		hide_field(["fluorine_site_depends_of"]);
		unhide_field(["ip_address", "fluorine_ddp_conn_url", "fluorine_site_root_prefix"]);
		//doc.fluor_dev_mode = 0;
	}else{
		unhide_field(["fluorine_site_depends_of"]);
		hide_field(["ip_address", "fluorine_ddp_conn_url", "fluorine_site_root_prefix"]);
	}
}