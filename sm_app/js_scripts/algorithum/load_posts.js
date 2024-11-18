$(document).ready(function () {
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    var postEndMarker = $('#end-of-posts');
    var increment = postEndMarker.data('increment');
    var catergory = postEndMarker.data('catergory');
    var triggered = false

    $(window).on('scroll', function () {
        var scrollTop = $(window).scrollTop();
        var windowHeight = window.innerHeight;
        var elementOffsetTop = postEndMarker.offset().top;
        var elementHeight = postEndMarker.outerHeight();
        if (!triggered) {
            if ((scrollTop + windowHeight) >= elementOffsetTop && scrollTop <= (elementOffsetTop + elementHeight)) {
                triggered = true
                $.ajax({
                    type: 'POST',
                    url: '/page/load-posts/',
                    data: {
                        'increment': increment,
                        'catergory': catergory,
                        'csrfmiddlewaretoken': csrfToken
                    },
                    success: function(response) {
                        var newIncrement = response.new_increment
                        var catergory = response.catergory
                        var newEndMarkerHtml = `
                            <div id="end-of-posts" data-increment="${newIncrement}" data-catergory="${catergory}"></div>
                        `;
                        postEndMarker.replaceWith(newEndMarkerHtml);
                        
                    }
                });
            }
        }
    })
});