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


frappe.utils = {
	get_file_link: function(filename) {
		filename = cstr(filename);
		if(frappe.utils.is_url(filename)) {
			return filename;
		} else if(filename.indexOf("/")===-1) {
			return "files/" + filename;
		} else {
			return filename;
		}
	},
	is_html: function(txt) {
		if (!txt) return false;

		if(txt.indexOf("<br>")==-1 && txt.indexOf("<p")==-1
			&& txt.indexOf("<img")==-1 && txt.indexOf("<div")==-1) {
			return false;
		}
		return true;
	},
	strip_whitespace: function(html) {
		return (html || "").replace(/<p>\s*<\/p>/g, "").replace(/<br>(\s*<br>\s*)+/g, "<br><br>");
	},
	strip_original_content: function(txt) {
		var out = [],
			part = [],
			newline = txt.indexOf("<br>")===-1 ? "\n" : "<br>";

		_.each(txt.split(newline), function(t, i) {
			var tt = strip(t);
			if(tt && (tt.substr(0,1)===">" || tt.substr(0,4)==="&gt;")) {
				part.push(t);
			} else {
				out.concat(part);
				out.push(t);
				part = [];
			}
		});
		return out.join(newline);
	},
	is_url: function(txt) {
		return txt.toLowerCase().substr(0,7)=='http://'
			|| txt.toLowerCase().substr(0,8)=='https://'
	},
	filter_dict: function(dict, filters) {
		var ret = [];
		if(typeof filters=='string') {
			return [dict[filters]]
		}
		_.each(dict, function(d, i) {
			for(key in filters) {
				if(_.isArray(filters[key])) {
					if(filters[key][0]=="in") {
						if(filters[key][1].indexOf(d[key])==-1)
							return;
					} else if(filters[key][0]=="not in") {
						if(filters[key][1].indexOf(d[key])!=-1)
							return;
					} else if(filters[key][0]=="<") {
						if (!(d[key] < filters[key])) return;
					} else if(filters[key][0]=="<=") {
						if (!(d[key] <= filters[key])) return;
					} else if(filters[key][0]==">") {
						if (!(d[key] > filters[key])) return;
					} else if(filters[key][0]==">=") {
						if (!(d[key] >= filters[key])) return;
					}
				} else {
					if(d[key]!=filters[key]) return;
				}
			}
			ret.push(d);
		});
		return ret;
	},
	comma_or: function(list) {
		return frappe.utils.comma_sep(list, " " + __("or") + " ");
	},
	comma_and: function(list) {
		return frappe.utils.comma_sep(list, " " + __("and") + " ");
	},
	comma_sep: function(list, sep) {
		if(list instanceof Array) {
			if(list.length==0) {
				return "";
			} else if (list.length==1) {
				return list[0];
			} else {
				return list.slice(0, list.length-1).join(", ") + sep + list.slice(-1)[0];
			}
		} else {
			return list;
		}
	},
	validate_type: function ( val, type ) {
		// from https://github.com/guillaumepotier/Parsley.js/blob/master/parsley.js#L81
		var regExp;

		switch ( type ) {
			case "number":
				regExp = /^-?(?:\d+|\d{1,3}(?:,\d{3})+)?(?:\.\d+)?$/;
				break;
			case "digits":
				regExp = /^\d+$/;
				break;
			case "alphanum":
				regExp = /^\w+$/;
				break;
			case "email":
				regExp = /^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))$/i;
				break;
			case "url":
				regExp = /^(https?|s?ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i;
				break;
			case "dateIso":
				regExp = /^(\d{4})\D?(0[1-9]|1[0-2])\D?([12]\d|0[1-9]|3[01])$/;
				break;
			default:
				return false;
				break;
		}

		// test regExp if not null
		return '' !== val ? regExp.test( val ) : false;
	},
	guess_style: function(text, default_style, _colour) {
		var style = default_style || "default";
		var colour = "darkgrey";
		if(text) {
			if(has_words(["Pending", "Review", "Medium", "Not Approved", "Pending"], text)) {
				style = "warning";
				colour = "orange";
			} else if(has_words(["Open", "Urgent", "High"], text)) {
				style = "danger";
				colour = "red";
			} else if(has_words(["Closed", "Finished", "Converted", "Completed", "Confirmed",
				"Approved", "Yes", "Active", "Available", "Paid"], text)) {
				style = "success";
				colour = "green";
			} else if(has_words(["Submitted"], text)) {
				style = "info";
				colour = "blue";
			}
		}
		return _colour ? colour : style;
	},

	guess_colour: function(text) {
		return frappe.utils.guess_style(text, null, true);
	},

	sort: function(list, key, compare_type, reverse) {
		if(!list || list.length < 2)
			return list || [];

		var sort_fn = {
			"string": function(a, b) {
				return cstr(a[key]).localeCompare(cstr(b[key]));
			},
			"number": function(a, b) {
				return flt(a[key]) - flt(b[key]);
			}
		};

		if(!compare_type)
		 	compare_type = typeof list[0][key]==="string" ? "string" : "number";

		list.sort(sort_fn[compare_type]);

		if(reverse) { list.reverse(); }

		return list;
	},

	unique: function(list) {
		var dict = {},
			arr = [];
		for(var i=0, l=list.length; i < l; i++) {
			if(!dict.hasOwnProperty(list[i])) {
				dict[list[i]] = null;
				arr.push(list[i]);
			}
		}
		return arr;
	},

	remove_nulls: function(list) {
		var new_list = [];
		for (var i=0, l=list.length; i < l; i++) {
			if (!is_null(list[i])) {
				new_list.push(list[i]);
			}
		}
		return new_list;
	},

	all: function(lst) {
		for(var i=0, l=lst.length; i<l; i++) {
			if(!lst[i]) {
				return false;
			}
		}
		return true;
	},

	dict: function(keys,values) {
		// make dictionaries from keys and values
		var out = [];
		_.each(values, function(row, row_idx) {
			var new_row = {};
			_.each(keys, function(key, key_idx) {
				new_row[key] = row[key_idx];
			})
			out.push(new_row);
		});
		return out;
	},

	sum: function(list) {
		return list.reduce(function(previous_value, current_value) { return flt(previous_value) + flt(current_value); }, 0.0);
	},

	intersection: function(a, b) {
		// from stackoverflow: http://stackoverflow.com/questions/1885557/simplest-code-for-array-intersection-in-javascript
		/* finds the intersection of
		 * two arrays in a simple fashion.
		 *
		 * PARAMS
		 *  a - first array, must already be sorted
		 *  b - second array, must already be sorted
		 *
		 * NOTES
		 *
		 *  Should have O(n) operations, where n is
		 *    n = MIN(a.length(), b.length())
		 */
		var ai=0, bi=0;
		var result = new Array();

		// sorted copies
		a = ([].concat(a)).sort();
		b = ([].concat(b)).sort();

		while( ai < a.length && bi < b.length ) {
			if (a[ai] < b[bi] ) { ai++; }
			else if (a[ai] > b[bi] ) { bi++; }
			else {
				/* they're equal */
				result.push(a[ai]);
				ai++;
				bi++;
			}
		}

		return result;
	},
    csv_to_array: function (strData, strDelimiter) {
        // Check to see if the delimiter is defined. If not,
        // then default to comma.
        strDelimiter = (strDelimiter || ",");

        // Create a regular expression to parse the CSV values.
        var objPattern = new RegExp(
            (
                // Delimiters.
                "(\\" + strDelimiter + "|\\r?\\n|\\r|^)" +

                // Quoted fields.
                "(?:\"([^\"]*(?:\"\"[^\"]*)*)\"|" +

                // Standard fields.
                "([^\"\\" + strDelimiter + "\\r\\n]*))"
            ),
            "gi"
            );


        // Create an array to hold our data. Give the array
        // a default empty first row.
        var arrData = [[]];

        // Create an array to hold our individual pattern
        // matching groups.
        var arrMatches = null;


        // Keep looping over the regular expression matches
        // until we can no longer find a match.
        while (arrMatches = objPattern.exec( strData )){

            // Get the delimiter that was found.
            var strMatchedDelimiter = arrMatches[ 1 ];

            // Check to see if the given delimiter has a length
            // (is not the start of string) and if it matches
            // field delimiter. If id does not, then we know
            // that this delimiter is a row delimiter.
            if (
                strMatchedDelimiter.length &&
                strMatchedDelimiter !== strDelimiter
                ){

                // Since we have reached a new row of data,
                // add an empty row to our data array.
                arrData.push( [] );

            }

            var strMatchedValue;

            // Now that we have our delimiter out of the way,
            // let's check to see which kind of value we
            // captured (quoted or unquoted).
            if (arrMatches[ 2 ]){

                // We found a quoted value. When we capture
                // this value, unescape any double quotes.
                strMatchedValue = arrMatches[ 2 ].replace(
                    new RegExp( "\"\"", "g" ),
                    "\""
                    );

            } else {

                // We found a non-quoted value.
                strMatchedValue = arrMatches[ 3 ];

            }


            // Now that we have our value string, let's add
            // it to the data array.
            arrData[ arrData.length - 1 ].push( strMatchedValue );
        }

        // Return the parsed data.
        return( arrData );
    },
    full_name: function(fn, ln) {
        return fn + (ln ? ' ' : '') + (ln ? ln : '')
    }
};


if (Meteor.isServer){

    frappe.get_frappe_cookie = function(userId, keys){
	var res = "";
	var userinfo = Meteor.users.find(userId).fetch()[0];
	if (userinfo){
		var cookies = userinfo.profile.cookies.join(";");
		_.each(keys, function(key){
			var val = frappe.get_cookie(key, cookies);
			res = res + repl("%(key)s=%(sid)s;", {key: key, sid: val});
		});
	}

	return res;
}

}