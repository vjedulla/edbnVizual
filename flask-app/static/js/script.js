(function() {

    /*
    * Upload file...wait...process network
    * */
    $('#add_to_queue').on('click', function (e) {
        swal({
            position: 'top-end',
            backdrop: true,
            type: 'success',
            title: 'Your work has sent to the queue!',
            showConfirmButton: false,
            timer: 1500,
            onClose: function () {
                console.log("sending the form");
                $('#queueing_form').submit();
            }
        })
    });

}).call(this);

