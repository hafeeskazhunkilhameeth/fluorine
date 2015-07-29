if (typeof frappe === 'undefined')
	frappe = {};

frappe.provide = function(namespace) {
    var nsl = namespace.split('.');
    var parent;
    if (Meteor.isClient)
        parent = window;
    else
        parent = frappe;
    for (var i = 0; i < nsl.length; i++) {
        var n = nsl[i];
        if (!parent[n]) {
            parent[n] = {}
        }
        parent = parent[n];
    }
    return parent;
}

if (Meteor.isClient)
    frappe.provide('frappe.utils');
else
    frappe.provide('utils');


frappe.utils.full_name = function(fn, ln) {
    return fn + (ln ? ' ' : '') + (ln ? ln : '')
}

inList = in_list = function in_list(list, item) {
    if (!list)
        return false;
    for (var i = 0, j = list.length; i < j; i++)
        if (list[i] == item)
            return true;
    return false;
};

strip = function(s, chars) {
    if (s) {
        var s = lstrip(s, chars)
        s = rstrip(s, chars);
        return s;
    }
}
rstrip = function(s, chars) {
    if (!chars)
        chars = ['\n', '\t', ' '];
    var last_char = s.substr(s.length - 1);
    while (in_list(chars, last_char)) {
        var s = s.substr(0, s.length - 1);
        last_char = s.substr(s.length - 1);
    }
    return s;
}

lstrip = function (s, chars){
    if(!chars) chars=['\n','\t',' '];
    var first_char=s.substr(0,1);
    while(in_list(chars,first_char)){
        var s=s.substr(1);first_char=s.substr(0,1);
    }
    return s;
}

cstr = function cstr(s) {
    if (s == null)
        return '';
    return s + '';
}
nth = function nth(number) {
    number = cint(number);
    var s = 'th';
    if ((number + '').substr( - 1) == '1')
        s = 'st';
    if ((number + '').substr( - 1) == '2')
        s = 'nd';
    if ((number + '').substr( - 1) == '3')
        s = 'rd';
    return number + s;
}
esc_quotes = function esc_quotes(s) {
    if (s == null)
        s = '';
    return s.replace(/'/, "\'");
}
crop = function(s, len) {
    if (s.length > len)
        return s.substr(0, len - 3) + '...';
    else
        return s;
}

is_null = function is_null(v) {
    if (v === null || v === undefined || cstr(v).trim() === "")
        return true;
}

copy_dict = function copy_dict(d) {
    var n = {};
    for (var k in d)
        n[k] = d[k];
    return n;
}

replace_newlines = function replace_newlines(t) {
    return t ? t.replace(/\n/g, '<br>') : '';
}
validate_email = function validate_email(txt) {
    return frappe.utils.validate_type(txt, "email");
}

toTitle = function toTitle(str) {
    var word_in = str.split(" ");
    var word_out = [];
    for (w in word_in) {
        word_out[w] = word_in[w].charAt(0).toUpperCase() + word_in[w].slice(1);
    }
    return word_out.join(" ");
}

repl = function repl(s, dict) {
    if (s == null)
        return '';
    for (key in dict) {
        s = s.split("%(" + key + ")s").join(dict[key]);
    }
    return s;
}

replace_all = function replace_all(s, t1, t2) {
    return s.split(t1).join(t2);
}

dkeys = function keys(obj) {
    var mykeys = [];
    for (var key in obj)
        mykeys[mykeys.length] = key;
    return mykeys;
}

dvalues = function values(obj) {
    var myvalues = [];
    for (var key in obj)
        myvalues[myvalues.length] = obj[key];
    return myvalues;
}

has_words = function has_words(list, item) {
    if (!item)
        return true;
    if (!list)
        return false;
    for (var i = 0, j = list.length; i < j; i++) {
        if (item.indexOf(list[i])!=-1)
            return true;
    }
    return false;
}

has_common = function has_common(list1, list2) {
    if (!list1 ||!list2)
        return false;
    for (var i = 0, j = list1.length; i < j; i++) {
        if (in_list(list2, list1[i]))
            return true;
    }
    return false;
}

function add_lists(l1, l2) {
    return [].concat(l1).concat(l2);
}

add_lists = function docstring(obj) {
    return JSON.stringify(obj);
}


remove_from_list = function remove_from_list(list, val) {
    if (list.indexOf(val)!==-1) {
        list.splice(list.indexOf(val), 1);
    }
    return list
}

if (Meteor.isClient){
    frappe.urllib = {
        get_arg: function(name) {
            name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
            var regexS = "[\\?&]" + name + "=([^&#]*)";
            var regex = new RegExp(regexS);
            var results = regex.exec(window.location.href);
            if (results == null)
                return "";
            else
                return decodeURIComponent(results[1]);
        },
        get_dict: function() {
            var d = {}
            var t = window.location.href.split('?')[1];
            if (!t)
                return d;
            if (t.indexOf('#')!=-1)
                t = t.split('#')[0];
            if (!t)
                return d;
            t = t.split('&');
            for (var i = 0; i < t.length; i++) {
                var a = t[i].split('=');
                d[decodeURIComponent(a[0])] = decodeURIComponent(a[1]);
            }
            return d;
        },
        get_base_url: function() {
            var url = (frappe.base_url || window.location.href).split('#')[0].split('?')[0].split('desk')[0];
            if (url.substr(url.length - 1, 1) == '/')
                url = url.substr(0, url.length - 1)
            return url
        },
        get_full_url: function(url) {
            if (url.indexOf("http://") === 0 || url.indexOf("https://") === 0) {
                return url;
            }
            return url.substr(0, 1) === "/" ? (frappe.urllib.get_base_url() + url) : (frappe.urllib.get_base_url() + "/" + url);
        }
    }
get_url_arg = frappe.urllib.get_arg;
get_url_dict = frappe.urllib.get_dict;
}

format = function format(str, args) {
    if (str == undefined)
        return str;
    this.unkeyed_index = 0;
    return str.replace(/\{(\w*)\}/g, function(match, key) {
        if (key === '') {
            key = this.unkeyed_index;
            this.unkeyed_index++
        }
        if (key ==+ key) {
            return args[key] !== undefined ? args[key] : match;
        }
    }.bind(this));
}
if (typeof jQuery !== 'undefined') {
    jQuery.format = format
}
