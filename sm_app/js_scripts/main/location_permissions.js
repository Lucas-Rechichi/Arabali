$(document).ready(function () { 
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    var LPModal = new bootstrap.Modal(document.getElementById('LPModal'), {
        keyboard: false
    });
    var LPModalAllowed = new bootstrap.Modal(document.getElementById('LPModalAllow'), {
        keyboard: false
    });
    if (document.getElementById('locationModalActivation').dataset.location == 'allow') {
        LPModal.show();
    }
    else {
        // Check if Geolocation is supported
        if (navigator.geolocation) {
            // Get the current position
            navigator.geolocation.getCurrentPosition(position => {
                const {latitude, longitude} = position.coords;
                $.ajax({
                    type: 'POST',
                    url: '/page/save_location/',
                    data: {
                        'auto-request': 'true', // So that the modal will pop up every 2 hours and not reset every acessing of the location.
                        'latitude': latitude,
                        'longitude': longitude,
                        'csrfmiddlewaretoken': csrfToken
                    },
                    success: function (response) {
                        console.log('Location Accessed')
                    }
                })
            });
            
        }
        else {
            $.ajax({
                type: 'POST',
                url: '/page/error/',
                date: {
                    'issue': 'Geolocation API Not Supported On Your Browser',
                    'csrfmiddlewaretoken': csrfToken
                },
            })
        }
    }
    $('#allowedLP').click(function () {
        $('#allowedLP').remove()
        $('#deniedLP').before(
            '<button class="btn btn-success" type="button" disabled>' +
                '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span>' +
                '<span role="status"> Loading...</span>' +
                '</button>'
            )
        // Check if Geolocation is supported
        if (navigator.geolocation) {
            // Get the current position
            navigator.geolocation.getCurrentPosition(position => {
                const {latitude, longitude} = position.coords;
                $.ajax({
                    type: 'POST',
                    url: '/page/save_location/',
                    data: {
                        'auto-request': 'false',
                        'acessing-location': 'true',
                        'latitude': latitude,
                        'longitude': longitude,
                        'csrfmiddlewaretoken': csrfToken
                    },
                    success: function (response) {
                        console.log('Location Accessed')
                        LPModal.hide();
                        LPModalAllowed.show();
                    }
                })
            });
            
        }
        else {
            $.ajax({
                type: 'POST',
                url: '/page/error/',
                date: {
                    'issue': 'Geolocation API Not Supported On Your Browser',
                    'csrfmiddlewaretoken': csrfToken
                },
            })
        }
    });
    $('#deniedLP').click(function () {
        $.ajax({
            type: 'POST',
            url: '/page/save_location/',
            data: {
                'accessing-location': 'false',
                'csrfmiddlewaretoken': csrfToken
            },
            success: function (response) {
                console.log('location permission denied');
            }
        })
    })
});