let notificationSocket;

var username;
var notificationCount;
var csrfToken;

$(document).ready(function () {
    username = $('meta[name="username"]').attr('content');
    notificationCount = $('meta[name="notification-count"]').attr('content');
    csrfToken = $('meta[name="csrf-token"]').attr('content');

    if (notificationCount == '0') {
        var notification_counter = $('#notification-counter');
        notification_counter.text('').hide();
        var notification_bell = $('#bell-icon');
        notification_bell.removeClass('bi-bell-fill').addClass('bi-bell');
    } else {
        var notificationCounter = $('#notification-counter');
        notificationCounter.text(notificationCount).show();
        $('#bell-icon').removeClass('bi-bell').addClass('bi-bell-fill');
    }
})

function connectNotificationSocket() { // function for connecting to the websocket.
    notificationSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/brodcast-message/'
    ); // connect to the relevant consumer class: NotificationConsumer

    notificationSocket.onopen = function(e) {
        console.log('connected', e);
    };

    notificationSocket.onmessage = function(e) { // when the consumer class sends a message through
        console.log('Message coming through!');
        const data = JSON.parse(e.data); // reconfigures the data so that it can be used within our function.

        if (data.receiver === username) { // if the data belongs to this specific user
            $('#inbox').append(data.html_notification_popup); // adds HTML to the inbox div, which stores notification toasts
            $('#notification-inbox').prepend(data.stored_html_notification); // adds HTML to the notification div that houses the notifications in the off-canvas
            
            // Update notification count
            var notificationCounter = $('#notification-counter');
            var newCount = parseInt(notificationCounter.text()) || 0;
            notificationCounter.text(newCount + 1).show();
            
            if ($('#bell-icon').hasClass('bi-bell')) { // if the bell looks like it has 0 notifications
                $('#bell-icon').removeClass('bi-bell');
                $('#bell-icon').addClass('bi-bell-fill');
            }

            var notificationElement = document.getElementById('popup-notification-' + data.notification_id); // gets the newly created popup notification toast

            if (notificationElement) {
                var notification = new bootstrap.Toast(notificationElement); // creates a bootstrap toast
                // Show the toast
                notification.show();
            } else {
                console.error('Notification element not found:', 'notification-' + data.notification_id);
            }

            // Attach event handlers to the newly added notification
            attachNotificationEventHandlers(data.notification_id, data.receiver);
        } else {
            console.log('incorrect user');
        }
    };

    notificationSocket.onerror = function(e) {
        console.error('WebSocket encountered an error:', e);
    };

    notificationSocket.onclose = function(e) {
        console.error('WebSocket closed unexpectedly:', e);
        setTimeout(connectNotificationSocket, 5000); // attempt a reconnection to this websocket
    };
}

function attachNotificationEventHandlers(notificationId, receiver) {
    $(`#close-notification-${notificationId}`).click(function() {
        $.ajax({
            type: 'POST',
            url: '/universal/remove-notification/',
            data: {
                'receiver': receiver,
                'type': 'notification-id',
                'csrfmiddlewaretoken': csrfToken,
                'notification_id': notificationId,
            },
            success: function(response) {
                console.log(response.message);
                var notification = $(`#stored-notification-${notificationId}`);
                notification.remove();
                var notificationCounter = $('#notification-counter');
                var newCount = parseInt(notificationCounter.text()) - 1;

                if (newCount <= 0) {
                    notificationCounter.text('').hide();
                    $('#bell-icon').removeClass('bi-bell-fill').addClass('bi-bell');
                } else {
                    notificationCounter.text(newCount);
                }
            }
        });
    });

    $(`#read-notification-${notificationId}`).click(function() {
        $.ajax({
            type: 'POST',
            url: '/universal/remove-notification/',
            data: {
                'receiver': receiver,
                'type': 'notification-id',
                'csrfmiddlewaretoken': csrfToken,
                'notification_id': notificationId,
            },
            success: function(response) {
                console.log(response.message);
            }
        });
    });
}

connectNotificationSocket(); // connect to the relevant websocket