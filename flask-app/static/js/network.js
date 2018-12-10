(function () {
   // /*
    // * INITIALIZATION
    // * */
    // var cy = cytoscape({
    //     container: document.getElementById('cy'),
    //
    //     boxSelectionEnabled: false,
    //     autounselectify: true,
    //
    //     style: cytoscape.stylesheet()
    //         .selector('node')
    //         .css({
    //             'content': 'data(id)',
    //             'shape': 'ellipse'
    //         })
    //         .selector('edge')
    //         .css({
    //             'curve-style': 'bezier',
    //             'target-arrow-shape': 'triangle',
    //             'width': 2,
    //             'line-color': '#ddd',
    //             'target-arrow-color': '#ddd'
    //         })
    //         .selector('.highlighted')
    //         .css({
    //             'background-color': '#61bffc',
    //             'line-color': '#61bffc',
    //             'target-arrow-color': '#61bffc',
    //             'transition-property': 'background-color, line-color, target-arrow-color',
    //             'transition-duration': '0.1s'
    //         }),
    //
    //     elements: {
    //         nodes: [
    //             { data: { id: 'a', weight: 30 } },
    //             { data: { id: 'b' } },
    //             { data: { id: 'c' } },
    //             { data: { id: 'd' } },
    //             { data: { id: 'e' } }
    //         ],
    //
    //         edges: [
    //             { data: { id: 'ae', weight: 1, source: 'a', target: 'e' } },
    //             { data: { id: 'ab', weight: 3, source: 'a', target: 'b' } },
    //             { data: { id: 'be', weight: 4, source: 'b', target: 'e' } },
    //             { data: { id: 'bc', weight: 5, source: 'b', target: 'c' } },
    //             { data: { id: 'ce', weight: 6, source: 'c', target: 'e' } },
    //             { data: { id: 'cd', weight: 2, source: 'c', target: 'd' } },
    //             { data: { id: 'de', weight: 7, source: 'd', target: 'e' } }
    //         ]
    //     },
    //
    //     layout: {
    //         name: 'breadthfirst',
    //         directed: true,
    //         animate: false,
    //         roots: '#a',
    //         padding: 20,
    //         fit: true,
    //         animationDuration: 100
    //     }
    // });


    /*
    * RESIZE PROBLEM FIX
    * */
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        cy.resize();
        cy.center();
    });

    $('.resize-button').on('click', function () {
        cy.reset();
        cy.center();
    });

    $('.helper-button').on('click', function () {
        $('.helper-box').toggle('can_see');
    });



    /*
    * EMIT doubletap event
    * */
    var doubleClickDelayMs = 350;
    var previousTapStamp;

    cy.on('tap', function(e) {
        var currentTapStamp = e.timeStamp;
        var msFromLastTap = currentTapStamp - previousTapStamp;

        if (msFromLastTap < doubleClickDelayMs && isEditMode()) {
            e.target.trigger('doubleTap', e);
        }
        previousTapStamp = currentTapStamp;
    });


    /*
    * Highlight a node
    * */
    cy.on('click', 'node', function (evt) {
        if (evt.target.isNode()) {
            cy.$('#' + evt.target.id()).toggleClass('highlighted');
        }
    });

    var conectivity_state = [];

    /*
    * Remove Highlight when clicking background
    * */
    cy.on('tap', function (event) {

        if (event.target === cy) {
            clearSelectedNodes();
            return;
        }

        if(! isEditMode()) return;

        if (event.target.isNode()) {
            var currElement = event.target.id();

            var idNum = cy.edges().size(),
                setID = idNum.toString();


            if (conectivity_state.length === 0) {
                conectivity_state.push(
                    currElement
                );
                // console.log(conectivity_state);
            } else {
                var prevElement = conectivity_state.pop();
                var valid = cy.edges("[id = '" + prevElement + currElement + "']").length === 0;

                if (valid) {
                    cy.add({
                        group: "edges", data: {
                            id: prevElement + currElement,
                            source: prevElement, target: currElement
                        }
                    });
                }


                clearSelectedNodes();
            }
        }

    });



    /*
    * Create new node on double click
    * */
    cy.on('doubleTap', function(event, originalTapEvent) {
        if(! isEditMode()) return;

        // Create a node on double tap
        //
        // if(event.target === cy){
        //     // console.log(event);
        //     // console.log(originalTapEvent);
        //     // var pos = {x: event.offsetX, y: event.offsetY};
        //
        //     var idNum = cy.nodes().size(),
        //         setID = idNum.toString();
        //
        //
        //     cy.add([{
        //         group : "nodes",
        //         data : {
        //             id : "n" + setID
        //         },
        //         renderedPosition :
        //                 originalTapEvent.renderedPosition,
        //         style: cytoscape.stylesheet()
        //                 .selector('node')
        //                 .css({
        //                     'content': 'data(id)',
        //                     'shape': 'square'
        //                 })
        //
        //     }]);
        //
        //     return;
        // }

        if(event.target.isEdge()){
            var edge = event.target.id();
            var collection = cy.elements("edge[id = '"+edge+"']");
            cy.remove(collection)
        }
    });


    function clearSelectedNodes() {
        cy.nodes().forEach(function (ele) {
                cy.$('#' + ele.id()).removeClass('highlighted');
        });

        conectivity_state.splice(0, conectivity_state.length);
    }

    function isEditMode() {
        return $('#switch-button-checkbox').is(":checked");
    }

});