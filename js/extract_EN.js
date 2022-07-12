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
    for (var i = first + 1; i <= last && i < list.length; i++) {
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
    Array.from(list).forEach( ( rowElem ) => {
      let row = rowElem.querySelectorAll( 'td' );
      s += extract_entry( row, 0, 100000, '\n' );
    } );
    return s;
}

data = extract_entries(document.querySelectorAll('#candidate-list > tbody > tr'));

return data;
