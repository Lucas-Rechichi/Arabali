$(document).ready(function() {
    const csrfToken = $('meta[name="csrf-token"]').attr('content');
    
    var triggerPoints = $('.post-checkpoint'); // Assuming all posts have a class 'post'
    var hasTriggered = {};

    triggerPoints.each(function() {
        var triggerPoint = $(this);
        var postId = triggerPoint.data('post-id');
        hasTriggered[postId] = false; // Initialize the trigger flag for each post

        $(window).on('scroll', function() {
            if (!hasTriggered[postId]){
                var scrollTop = $(window).scrollTop();
                var windowHeight = window.innerHeight;
                var elementOffsetTop = triggerPoint.offset().top;
                var elementHeight = triggerPoint.outerHeight();

                // Check if the element is in the viewport
                if ((scrollTop + windowHeight) >= elementOffsetTop && scrollTop <= (elementOffsetTop + elementHeight)) {
                    console.log('Target element is in view!');
                    console.log('Conditional 1: ' + scrollTop + '+' +  windowHeight + '(' + (scrollTop + windowHeight) + ')' + '>='  + elementOffsetTop);
                    console.log('Conditional 2: ' + scrollTop + '<='  + elementOffsetTop + '+' + elementHeight + '(' + (scrollTop + windowHeight) + ')' );

                    // Set the flag to true to prevent further triggering
                    hasTriggered[postId] = true;

                    $.ajax({
                        type: 'POST',
                        url: '/page/scrolled-by/',
                        data: {
                            'post_id': postId,
                            'csrfmiddlewaretoken': csrfToken
                        },
                        success: function(response) {
                            console.log(response.post_id + ' was passed successfully!')
                        }
                    });
                }
            } 
        });
    });
});