frappe.pages['fluorine-admin'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Fluorine Administrator',
		single_column: true
	});

	page.main.html(frappe.render_template("fluorine_admin_page", {}));
}