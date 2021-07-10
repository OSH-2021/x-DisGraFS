
    // // Demo Neo4j database settings hosted on GrapheneDb

    popoto.rest.CYPHER_URL = "http://47.119.121.73:7474/db/data/transaction/commit";
    popoto.rest.AUTHORIZATION = "Basic " + btoa("neo4j:disgrafs");

    popoto.provider.node.Provider = {
        "FILE": {
            "returnAttributes": ["name", "ext","size"],
            "constraintAttribute": "name"
        },
        "Label": {
            "returnAttributes": ["name"],
            "constraintAttribute": "name"
        }
    };

    /**
     * Here a listener is used to retrieve the total results count and update the page accordingly.
     * This listener will be called on every graph modification.
     */
    popoto.result.onTotalResultCount(function (count) {
        document.getElementById("result-total-count").innerHTML = "(" + count + ")";
    });

    function changeQueryRoot() {

        // Get current graph schema
        var graph = popoto.graph.getSchema();

        // Change graph root to a random relation around actual root node
        if (graph.hasOwnProperty("rel") && graph.rel.length > 0) {

            // Remove a random branch from actual root node in graph
            var removedRandomBranch = graph.rel.splice(Math.floor(Math.random() * graph.rel.length), 1)[0];

            // Set the first target of thi branch as newRoot
            var newRoot = removedRandomBranch.target;

            // Add previously pruned graph as a branch and change the isReverse property if crossed in reverse order
            if (newRoot.rel === undefined) {
                newRoot.rel = []
            }
            newRoot.rel.push(
                {
                    label: removedRandomBranch.label,
                    isReverse: removedRandomBranch.isReverse !== true,
                    target: graph
                }
            );

            // Reset graph
            popoto.graph.mainLabel = newRoot;
            popoto.tools.reset();
        }
    }

    d3.select("#randomize").on("click", changeQueryRoot);

    popoto.start({
        "label": "FILE",
        "rel": [
            {"label": "tag1", "target": {"label": "Label"}},
            {"label": "tag2", "target": {"label": "Label"}},
            {"label": "tag3", "target": {"label": "Label"}},
            {"label": "tag4", "target": {"label": "Label"}},
            {"label": "tag5", "target": {"label": "Label"}},
            {"label": "tag6", "target": {"label": "Label"}}
            // ,{"label": "DIRECTED", "target": {"label": "Movie"}},
            // {"label": "PRODUCED", "target": {"label": "Movie"}},
            // {"label": "WROTE", "target": {"label": "Movie"}},
            // {"label": "REVIEWED", "target": {"label": "Movie"}},
            // {"label": "FOLLOWS", "target": {"label": "Person"}}
        ]
    });
    
    
    
    
    // Demo Neo4j database settings hosted on GrapheneDb
    // popoto.rest.CYPHER_URL = "https://db-kh9ct9ai1mqn6hz2itry.graphenedb.com:24780/db/data/transaction/commit";
    // popoto.rest.AUTHORIZATION = "Basic cG9wb3RvOmIuVlJZQVF2blZjV2tyLlRaYnpmTks5aHp6SHlTdXk=";

    // popoto.rest.CYPHER_URL = "http://47.119.121.73:7474/db/data/transaction/commit";
    // popoto.rest.AUTHORIZATION = "Basic " + btoa("neo4j:disgrafs");

    // popoto.graph.WHEEL_ZOOM_ENABLED = false;

    // popoto.provider.node.Provider = {
    //     "Person": {
    //         returnAttributes: ["name", "born"],
    //         constraintAttribute: "name",
    //         "resultOrderByAttribute": "name",
    //         "valueOrderByAttribute": "name",
    //         "isValueOrderAscending": true,
    //         getDisplayType: function (node) {
    //             return popoto.provider.node.DisplayTypes.IMAGE;
    //         },
    //         "getImagePath": function (node) {
    //             // if (node.type === popoto.graph.node.NodeTypes.VALUE) {
    //             //     return "../material/person/" + node.attributes['name'] + ".jpg"
    //             // } else if (node.hasOwnProperty("value") && node.value.length > 0) {
    //             //     return "../material/person/" + node.value[0].attributes['name'] + ".jpg"
    //             // }
    //             return 'image/node/person/person.svg';
    //         },
    //         "displayResults": function (pResultElmt) {

    //             var div1 = pResultElmt.append("div").attr("style", "display: flex;");
    //             div1.append("img")
    //                 .attr("height", "100px")
    //                 .attr("src", function (result) {
    //                     return 'image/node/person/person.svg';
    //                     // return "../material/person/" + result.attributes.name + ".jpg";
    //                 });

    //             var div = div1.append("div").attr("style", "margin-left: 20px;");
    //             // An <h3> element containing the person name
    //             div.append("h4")
    //                 .text(function (result) {
    //                     return result.attributes.name;
    //                 });

    //             // A <span> element with the computed age from born attribute
    //             div.filter(function (result) {
    //                 // Filter on attribute having born attribute value
    //                 return result.attributes.born;
    //             }).append("span").text(function (result) {
    //                 return "Born: " + result.attributes.born;
    //             });

    //         }
    //     },
    //     "Movie": {
    //         "returnAttributes": ["title", "tagline", "released"],
    //         "constraintAttribute": "title",
    //         "resultOrderByAttribute": "title",
    //         "valueOrderByAttribute": "title",
    //         "isValueOrderAscending": true,
    //         "getDisplayType": function (node) {
    //             return popoto.provider.node.DisplayTypes.IMAGE;
    //         },
    //         "getImagePath": function (node) {
    //             // if (node.type === popoto.graph.node.NodeTypes.VALUE) {
    //             //     return "../material/movie/" + node.attributes['title'] + ".jpg"
    //             // } else if (node.hasOwnProperty("value") && node.value.length > 0) {
    //             //     return "../material/movie/" + node.value[0].attributes['title'] + ".jpg"
    //             // }
    //             return 'image/node/movie/movie.svg';
    //         },
    //         "displayResults": function (pResultElmt) {

    //             var div1 = pResultElmt.append("div").attr("style", "display: flex;");
    //             div1.append("img")
    //                 .attr("height", "100px")
    //                 .attr("src", function (result) {
    //                     return 'image/node/movie/movie.svg';
    //                 });

    //             var div = div1.append("div").attr("style", "margin-left: 20px;");
    //             // An <h3> element containing the movie title
    //             div.append("h4")
    //                 .attr("style", "margin-top: 0;")
    //                 .text(function (result) {
    //                     return result.attributes.title;
    //                 });

    //             // A <span> element with the movie tagline
    //             div.append("div").filter(function (result) {
    //                 // Filter on attribute having born attribute value
    //                 return result.attributes.tagline;
    //             }).append("span").text(function (result) {
    //                 return result.attributes.tagline;
    //             });

    //             // A <span> element with the release date
    //             div.append("div").filter(function (result) {
    //                 // Filter on attribute having born attribute value
    //                 return result.attributes.released;
    //             }).append("span").text(function (result) {
    //                 return "Release date: " + result.attributes.released;
    //             });

    //         }
    //     }
    // };

    // popoto.provider.link.Provider = {

    //     // Customize the text displayed on links:
    //     "getTextValue": function (link) {
    //         if (link.type === popoto.graph.link.LinkTypes.RELATION || link.type === popoto.graph.link.LinkTypes.SEGMENT) {

    //             var targetName = "";
    //             if (link.type === popoto.graph.link.LinkTypes.SEGMENT) {
    //                 targetName = " " + popoto.provider.node.getTextValue(link.target);
    //             }

    //             switch (link.label) {
    //                 case "ACTED_IN":
    //                     return "Acted in" + targetName;
    //                 case "DIRECTED":
    //                     return "Directed" + targetName;
    //                 case "PRODUCED":
    //                     return "Produced" + targetName;
    //                 case "WROTE":
    //                     return "Wrote" + targetName;
    //                 case "FOLLOWS":
    //                     return "Follows" + targetName;
    //                 case "REVIEWED":
    //                     return "Reviewed" + targetName;
    //                 default :
    //                     return "Unexpected relation"
    //             }
    //         } else {
    //             return "";
    //         }
    //     }

    // };
    // popoto.result.onTotalResultCount(function (count) {
    //     document.getElementById("result-total-count").innerHTML = "(" + count + ")";
    // });


    // function initCollapsible() {

    //     var element = document.querySelector('#collapsible-components');
    //     var collapsible = new M.Collapsible(element,
    //         {
    //             accordion: false,
    //             onOpenEnd: function (el) {
    //                 var id = el.id;
    //                 if (id === "p-collapsible-popoto") {
    //                     if (popoto.graph.getRootNode() !== undefined) {
    //                         popoto.graph.getRootNode().px = $('#p-collapsible-popoto').width() / 2;
    //                         popoto.graph.getRootNode().py = 300;
    //                         popoto.updateGraph();
    //                     }
    //                 }
    //             },
    //             onCloseEnd: function (el) {
    //             }
    //         });
    // }

    // initCollapsible();

    // /**
    //  * Here a listener is used to retrieve the total results count and update the page accordingly.
    //  * This listener will be called on every graph modification.
    //  */
    // popoto.result.onTotalResultCount(function (count) {
    //     document.getElementById("result-total-count").innerHTML = "(" + count + ")";
    // });

    // function changeQueryRoot() {

    //     // Get current graph schema
    //     var graph = popoto.graph.getSchema();

    //     // Change graph root to a random relation around actual root node
    //     if (graph.hasOwnProperty("rel") && graph.rel.length > 0) {

    //         // Remove a random branch from actual root node in graph
    //         var removedRandomBranch = graph.rel.splice(Math.floor(Math.random() * graph.rel.length), 1)[0];

    //         // Set the first target of thi branch as newRoot
    //         var newRoot = removedRandomBranch.target;

    //         // Add previously pruned graph as a branch and change the isReverse property if crossed in reverse order
    //         if (newRoot.rel === undefined) {
    //             newRoot.rel = []
    //         }
    //         newRoot.rel.push(
    //             {
    //                 label: removedRandomBranch.label,
    //                 isReverse: removedRandomBranch.isReverse !== true,
    //                 target: graph
    //             }
    //         );

    //         // Reset graph
    //         popoto.graph.mainLabel = newRoot;
    //         popoto.tools.reset();
    //     }
    // }

    // d3.select("#randomize").on("click", changeQueryRoot);

    // popoto.start({
    //     "label": "Person",
    //     "rel": [
    //         {"label": "ACTED_IN", "target": {"label": "Movie"}},
    //         {"label": "DIRECTED", "target": {"label": "Movie"}},
    //         {"label": "PRODUCED", "target": {"label": "Movie"}},
    //         {"label": "WROTE", "target": {"label": "Movie"}},
    //         {"label": "REVIEWED", "target": {"label": "Movie"}},
    //         {"label": "FOLLOWS", "target": {"label": "Person"}}
    //     ]
    // });

