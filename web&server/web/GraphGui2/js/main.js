var main = new autoComplete({
    selector: '#search',
    minChars: 0,

    source: function (term, suggest) {
        var query_tag = "match (p:FILE)-[r]->(m:Label) WHERE (toLower(m.name) contains $term) return DISTINCT m.name AS name, type(r) as rel order by name LIMIT 20";

        // var query_file = "match (p:Label)-[r]->(m:FILE) WHERE (toLower(m.name) contains $term) return DISTINCT m.name AS name, type(r) as rel order by name LIMIT 20";

        var res = [];

        // var statements = [
        //     {
        //         "statement": query_file,
        //         "parameters": {
        //             term: term.toLowerCase()
        //         },
        //         "resultDataContents": ["row"]
        //     }
        // ];

        // popoto.logger.info("AutoComplete ==> ");
        // popoto.rest.post(
        //     {
        //         "statements": statements
        //     })
        //     .done(function (data) {
        //         res = data.results[0].data.map(function (d) {
        //             var temp = d.row;
        //             temp[1] = "FILE";
        //             return temp
        //         });
        //     })
        //     .fail(function (xhr, textStatus, errorThrown) {
        //         console.error(xhr, textStatus, errorThrown);
        //         suggest([]);
        //     });

        statements = [
            {
                "statement": query_tag,
                "parameters": {
                    term: term.toLowerCase()
                },
                "resultDataContents": ["row"]
            }
        ];

        popoto.rest.post(
            {
                "statements": statements
            })
            .done(function (data) {
                res.push.apply(res, data.results[0].data.map(function (d) {
                    return d.row
                    })
                );
                suggest(res);
            })
            .fail(function (xhr, textStatus, errorThrown) {
                console.error(xhr, textStatus, errorThrown);
                suggest([]);
            });
    },
    renderItem: function (item, search) {
        search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&amp;');
        var re = new RegExp("(" + search.split(' ').join('|') + ")", "gi");
        var title = item[0];
        var rel = item[1];
        var label = "Label";
        
        var imagePath = popoto.provider.node.getImagePath({
            label: label,
            type: popoto.graph.node.NodeTypes.VALUE,
            attributes: {title: title}
        });

        return '<div class="autocomplete-suggestion" data-id="' + title + '" data-rel="' + rel + '" data-label="' + label + '" data-search="' + search + '"><img width="30px" height="45px" src="' + imagePath + '"> ' + rel + " "+ title.replace(re, "<b>$1</b>") + '</div>';
    },
    onSelect: function (e, term, item) {
        var id = item.getAttribute('data-id');
        var rel = item.getAttribute('data-rel');
        var label = item.getAttribute('data-label');

        document.getElementById('search').value = "";
        $("#search").blur();

        if (label != "FILE"){
            popoto.graph.node.addRelatedValues(popoto.graph.getRootNode(), [{
                id: id,
                rel: rel,
                label: label
            }]);
        }

    }
});
