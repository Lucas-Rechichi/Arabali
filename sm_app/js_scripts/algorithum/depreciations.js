$(document).ready(function () {
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    var dateTime = new Date()
    var timeStamp = Math.floor(dateTime.getTime() / 1000)

    $.ajax({
        type: 'POST',
        url: '/universal/check-depreciation-time/',
        data: {
            'timestamp': timeStamp,
            'csrfmiddlewaretoken': csrfToken
        },
        success: function (response) {
            console.log(response.message)
        }
    })
});