function purify(s) {
		if (!s.length)
				return s;

		if (!s[0].trim().length)
				return purify(s.substring(1));

		if (!s[s.length - 1].trim().length)
				return purify(s.slice(0, -1));

		return s;
}

		

function extract_entry(list, first, last, ending = "\t") {
    s = purify(list[first].innerText);
    for (var i = first + 1; i <= last; i++) {
				if (list[i].innerText.indexOf("\n") == -1)
						s += '\t' + purify(list[i].innerText);
				else {
						var v = list[i].innerText.split("\n");
						s += '\t' + purify(v[0]);
				}
		}
		return s + ending;
}

function extract_entries(list) {
		var s = "";
		for (var i = 0; i + 1 < list.length; i += 2) {
				var l1 = list[i].querySelectorAll('td'), l2 = list[i + 1].querySelectorAll('td');
				let p = l1.length - 19; // skip ranking columns if present
				s += extract_entry(l1, 0, 1);
				s += extract_entry(l1, p + 2, p + 11);
				s += extract_entry(l2, 0, 3);
				s += extract_entry(l1, p + 12, p + 14);
				s += extract_entry(l2, 4, 6);
				s += extract_entry(l1, p + 15, p + 15);
				s += extract_entry(l2, 7, 9);
				s += extract_entry(l1, p + 16, p + 18, '\n');
		}
		return s;
}

data = extract_entries(document.getElementsByClassName("tr1"));
data += extract_entries(document.getElementsByClassName("tr2"));
return data;
