$(document).ready(function () {
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    // Get the Unix timestamp of the current time in seconds
    var dateTime = new Date()
    var timeStamp = Math.floor(dateTime.getTime() / 1000)

    // Send over time
    $.ajax({
        type: 'POST',
        url: '/universal/check-modulation-time/',
        data: {
            'timestamp': timeStamp,
            'csrfmiddlewaretoken': csrfToken
        },
        success: function (response) {
            console.log(response.message)
        }
    })
});