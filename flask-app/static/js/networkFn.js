function bindActions(cy, ur){
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


    $('.analyze').on('click', function () {
        console.log("analyze clicked");
        var which_network = $(this).attr('data-network');
        complex_shit(which_network);
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
                    ur.do('add', {
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
        if(event.target.isEdge()){
            var edge = event.target.id();
            var collection = cy.elements("edge[id = '"+edge+"']");
            ur.do('remove', collection)
            // cy.remove(collection)
        }
    });


    $('.back-button').on('click', function () {
        ur.undo();
    });

    $('.redo-button').on('click', function () {
        ur.redo();
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
}

function complex_shit(id){
    const ipAPI = 'http://' + document.domain + ':' + location.port +"/score_network/1";
    console.log("trying");
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    var steps = [
            "Preparing to train variables",
            "Data loaded",
            "Build K-Context for data",
            "Finished training data",
            "Finished testing",
            "Preparing scoring",
            "Finished scoring",
            "Finished"
    ];


    var html_steps_text = "<ul id='status-checker'>";

    steps.forEach(function (item, index) {
        html_steps_text += "<li>" + item + "</li>";
    });

    html_steps_text += "</ul>";

    // console.log(html_steps_text);

    swal({
      title: 'Scoring model',
      html: html_steps_text+'<span class="current-status">Currently on: <span class="swal2-status"></span>void</span>',
      type: 'info',
      confirmButtonText: 'Score',
      showLoaderOnConfirm: true,
      preConfirm: function() {
        socket.emit('score_model', {which_network: 1});

        return new Promise(function(resolve, reject) {
          swal.showLoading();
          var $status = $('.swal2-status');

          socket.on('score_resp', function(data) {
            // console.log(">", data);
            $status.html(data.msg);
            var nth = data.step;

            $('#status-checker li:nth-child('+nth+')').addClass('done');

            // console.log(data.step, steps.length );
            if(data.step === steps.length){
                finish_steps(data.scores);
                resolve();
            }
          });
        });
      },
      allowOutsideClick: false
    });


}

function move_to_next() {
    var $active = $('.wizard .nav-tabs li.active');

    $active.next().removeClass('disabled');
    nextTab($active);
}

function calculateTraces(allTraces, option_score){
    var result = [];

    for(var trace in allTraces){
        var sum = allTraces[trace].reduce(function(a, b) { return a + b; }, 0);
        var length = allTraces[trace].length;
        var score = Math.log10(sum/length);

        result.push({key: trace, score: score});
    }

    return result;
}

function finish_steps(allTraces){
    move_to_next();

    var scoretraces = calculateTraces(allTraces);

    buildPlot(scoretraces, allTraces);
}

function buildTable(data, traces){
    const $table = $('#table');
    const $remove = $('#remove');
    let selections = [];

    var processedData = [];

    for(var i in traces[data.trace]){
        processedData.push({id: i, event: traces[data.trace][i]})
    }

    console.log(processedData);

  $table.bootstrapTable({
      data: processedData,
    columns: [
      [
        {
            title: 'ID',
          field: 'id',
          align: 'center',
          valign: 'middle'
        }, {
          title: 'Event Score',
          field: 'event',
          align: 'center',
          valign: 'middle',
          sortable: true
        }
      ]
    ]
  });


}


function buildPlot(scores, allTraces) {

    var xScale = new Plottable.Scales.Linear();
    var yScale = new Plottable.Scales.Linear();

    // make data
    var data = [];

    var cnt = 0;
    for(var s in scores){
        data.push({x:cnt, y: scores[s].score, trace: scores[s].key});
        cnt++;
    }

    // begin plotting
    var xAxis = new Plottable.Axes.Numeric(xScale, "bottom");
    var yAxis = new Plottable.Axes.Numeric(yScale, "left");

    var plot = new Plottable.Plots.Scatter()
      .addDataset(new Plottable.Dataset(data))
      .x(function(d) { return d.x; }, xScale)
      .y(function(d) { return d.y; }, yScale)
        .attr("fill", "#000");



    // plots
    var plots = new Plottable.Components.Group([plot]);
    var table = new Plottable.Components.Table([[null, null],
                                                 [yAxis, plots],
                                                 [null, xAxis]]);

    var interaction = new Plottable.Interactions.Pointer();

    interaction.onPointerMove(function(p) {
      plot.entities().forEach(function(entity) {
        entity.selection.attr("fill", "#5279C7");
      });

      var entity = plot.entityNearest(p);

      entity.selection.attr("fill", "red");
    });

    var clickInteraction = new Plottable.Interactions.Click();

    clickInteraction.onClick(function(point) {
      plot.selections().attr("fill", "#5279c7");
      var selection = plot.entitiesAt(point)[0];

      if(typeof selection !== 'undefined'){
          var pp = selection.selection;
          console.log(selection.datum);

            swal(
                'You clicked the point:',
                JSON.stringify(selection.datum),
                'info'
            );

            buildTable(selection.datum, allTraces);

          pp.attr("fill", "#F99D42");
      }
    });

    interaction.attachTo(plot);
    clickInteraction.attachTo(plot);


    var pzi = new Plottable.Interactions.PanZoom();
    pzi.addXScale(xScale);
    pzi.addYScale(yScale);
    pzi.attachTo(plot);

    window.addEventListener("resize", function() {
      plot.redraw();
    });

    table.renderTo("svg#example");
}

function initializeCY(nodes, CD, FD) {
    /*
    * INITIALIZATION
    * */
    var cy = cytoscape({
        container: document.getElementById('cy'),

        boxSelectionEnabled: false,
        autounselectify: true,

        style: cytoscape.stylesheet()
            .selector('node')
            .css({
                'content': 'data(id)',
                'shape': 'ellipse'
            })
            .selector('edge')
            .css({
                'curve-style': 'bezier',
                'target-arrow-shape': 'triangle',
                'width': 3,
                'line-color': '#ddd',
                'target-arrow-color': '#ddd'
            })
            .selector('.highlighted')
            .css({
                'background-color': '#61bffc',
                'line-color': '#61bffc',
                'target-arrow-color': '#61bffc',
                'transition-property': 'background-color, line-color, target-arrow-color',
                'transition-duration': '0.1s'
            }),


        elements: {
            nodes: nodes,
            edges: CD,
        },

        layout: {
            name: 'grid',
            rows: 2
        },

    });

    // manually add the FD (now just a test it is CD)
    for(i in CD){
        cy.add({
            group: "edges", data: {
                id: CD[i]['data']['target'] + CD[i]['data']['source'],
                source: CD[i]['data']['target'], target: CD[i]['data']['source'],
                weight: 5,
            },
            style: {
                'width': 2,
                'line-style': 'dashed',
                'line-color': '#0071a7',
            }
        });
    }


    // ur is the handler for the
    // events that are done by the user
    var ur = cy.undoRedo({
        isDebug: true
    });

    /*
    * Create dynamically
    * */
    for(var i=1; i <= 6; i++) {
        $('#ex' + i).slider({
            formatter: function (value) {
                return 'Current value: ' + value;
            }
        });
    }


    bindActions(cy, ur)
}