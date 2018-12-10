$(document).ready(function () {
    //Initialize tooltips
    // $('.nav-tabs > li a[title]').tooltip();
    $('.nav-tabs > li a[title]').tooltip();

    //Wizard
    $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {
        var $target = $(e.target);


        if ($target.parent().hasClass('disabled')) {
            return false;
        }
    });

    $(".next-step").click(function (e) {
        // if($(this).attr('data-type') == 'log_file') return;

        var $active = $('.wizard .nav-tabs li.active');

        $active.next().removeClass('disabled');

        // collectFormInformation($($active.next()).find('a').attr('aria-controls'));
        // console.log();
        nextTab($active);
    });

    $(".prev-step").click(function (e) {
        var $active = $('.wizard .nav-tabs li.active');
        prevTab($active);
    });


});
//
// var form_information = [];
//
//
// function collectFormInformation(stepName) {
//     if(stepName == 'step2'){
//         var name = $('#name-input').val();
//         var notes = $('#notes-input').val();
//         var tags = $('#tags-input').tagsinput('items');
//         var authors = $('#author-input').tagsinput('items');
//
//         form_information.push({
//             'step1': {
//                 'name': name,
//                 'notes': notes,
//                 'tags': tags,
//                 'authors': authors
//             }
//         });
//
//         console.log(form_information);
//         console.log(form_information[0]['step1']);
//     }else if(stepName == 'step3'){
//         var alias = $('#alias-input').val();
//         var file = $('#datasetInputFile').prop('files')[0];
//
//         form_information.push({
//             'step2': {
//                 'alias': alias,
//                 'file': file
//             }
//         });
//         console.log(form_information);
//         console.log('step3')
//     }else if(stepName == 'complete'){
//         var parameters = [];
//
//         for(var i=0; i < 6; i++){
//             parameters.push($('#ex' + i).val());
//         }
//
//         form_information.push({
//             'step3': {
//                 'parameters': parameters
//             }
//         });
//
//         console.log(form_information);
//         console.log('completed');
//         showInformation();
//     }
// }
//
// function showInformation() {
//     console.log(form_information[0]['step1'])
//     console.log(form_information[2]['step3']['parameters'])
//     $('.name-show').text(form_information[0]['step1']['name']);
//     $('.author-show').text(form_information[0]['step1']['authors']);
//     $('.dataset-show').text(form_information[0]['step1']['alias']);
//     $('.alias-show').text(form_information[1]['step2']['alias']);
//     $('.note-show').text(form_information[0]['step1']['notes']);
//     $('.tags-show').text(form_information[0]['step1']['tags']);
//     $('.parameters-show').text(form_information[2]['step3']['parameters']);
// }

function nextTab(elem) {
    var tab = $(elem).next().find('a[data-toggle="tab"]');

    // if(tab.hasClass('networkModel')){
    //     console.log('test');
    //     createModel();
    // }

    tab.click();
}
function prevTab(elem) {
    $(elem).prev().find('a[data-toggle="tab"]').click();
}