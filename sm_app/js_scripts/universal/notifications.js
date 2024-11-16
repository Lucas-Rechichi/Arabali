var username;

$(document).ready(function () {
    const csrfToken = $('meta[name="csrf-token"]').attr('content');
    username = $('meta[name="username"]').attr('content');
    
    $('.close-notification').click(function () {
        var notificationID = $(this).data('notification-id');

        $.ajax({
            type: 'POST',
            url: '/universal/remove-notification/',
            data: {
                'receiver': username,
                'type': 'notification-id',
                'csrfmiddlewaretoken': csrfToken,
                'notification_id': notificationID
            },
            success: function(response) {
                console.log(response.notification_count, response.notification_counter)
                var notification = $(".notification-" + notificationID)
                notification.remove();
                $('#notification-counter').text('');
                $('#notification-counter').text(response.notification_count);
                    if (response.notification_count == 0) {
                        $('#notification-counter').text(response.notification_count).hide();
                        $('#notification-counter').remove();
                        $('#bell-icon').removeClass('bi-bell-fill');
                        $('#bell-icon').addClass('bi-bell');
                    }
            }
        })
    })
    $('.read-notification').click(function () {
        var notificationID = $(this).data('notification-id');

        $.ajax({
            type: 'POST',
            url: '/universal/remove-notification/',
            data: {
                'receiver': username,
                'type': 'notification-id',
                'csrfmiddlewaretoken': csrfToken,
                'notification_id': notificationID
            },
            success: function(response) {
                console.log(response.message)
            }
        })
    })
})