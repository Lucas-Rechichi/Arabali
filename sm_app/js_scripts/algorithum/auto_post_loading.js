$(document).ready(function () {
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    var postEndMarker = $('#end-of-posts');
    var increment = postEndMarker.data('increment');
    var triggered = false

    $(window).on('scroll', function () {
        var scrollTop = $(window).scrollTop();
        var windowHeight = window.innerHeight;
        var elementOffsetTop = postEndMarker.offset().top;
        var elementHeight = postEndMarker.outerHeight();
        if (!triggered) {
            if ((scrollTop + windowHeight) >= elementOffsetTop && scrollTop <= (elementOffsetTop + elementHeight)) {
                console.log('end of posts?')
                triggered = true
                $.ajax({
                    type: 'POST',
                    url: '',
                    data: {
                        'increment': increment,
                        'csrfmiddlewaretoken': csrfToken
                    },
                    success: function(response) {
                    }
                });
            }
        }
    })
});