frappe.pages['fluorine-admin'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Fluorine Administrator',
		single_column: true
	});

	page.main.html(frappe.render_template("fluorine_admin_page", {}));
	console.log("BlazeLayout.setRoot");
	$( "#fluorine_admin_enter" ).parent().removeClass("layout-main-section");
	FlowRouter.initialize();
    BlazeLayout.setRoot('#fluorine_admin_enter');
    //Session.set("pillState", "panel_home");
    BlazeLayout.render("Layout", {content: "panel_home", panel_home:true});
}


frappe.pages['fluorine-admin'].refresh = function(wrapper) {
	console.log("flowrouter init");

}