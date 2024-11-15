$(document).ready(function () {
    $('.like-button').click(function() { // When the button is pressed
        console.log('clicked');
        var postId = $(this).data('post-id'); // Get Post ID
        console.log('Post ID:', postId);
    
        // Defining variables
        var clickedButton = $('.like-button-' + postId); 
        var isLiked
        var modalLikeCounter
        var pageLikeCounter
        var modalLikeIcon
        var pageLikeIcon
        console.log('defined');
        console.log(isLiked)

        // AJAX request
        $.ajax({
            type: 'POST',
            url: '/page/liked/',
            data: {
                'post_id': postId,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            
            // If the request was successful
            success: function(response) {
                console.log('success');

                // Getting relevent elements
                modalLikeCounter = $('#modal-like-text-' + postId);
                pageLikeCounter = $('#page-like-text-' + postId)
                modalLikeIcon = $('#modal-like-icon-' + postId);
                pageLikeIcon = $('#page-like-icon-' + postId)

                // Changing text
                modalLikeCounter.text(response.likes);
                pageLikeCounter.text(response.likes);
                
                // Different style changes for different like statuses
                if (response.isLiked) {
                    console.log('like');

                    
                    // Change classes for dislike state
                    modalLikeCounter.removeClass('text-success').addClass('text-white');
                    modalLikeIcon.removeClass('bi-hand-thumbs-up').addClass('bi-hand-thumbs-up-fill');
                    
                    pageLikeCounter.removeClass('text-success').addClass('text-white');
                    pageLikeIcon.removeClass('bi-hand-thumbs-up').addClass('bi-hand-thumbs-up-fill');

                    clickedButton.removeClass('liked-button').addClass('btn-success');

                    // Color change
                    modalLikeIcon = document.getElementById('modal-like-icon-' + postId)
                    modalLikeIcon.style.color = '#ffffff'
                    
                    pageLikeIcon = document.getElementById('page-like-icon-' + postId)
                    pageLikeIcon.style.color = '#ffffff'

                } else {
                    console.log('dislike');

                    // Change classes for like state
                    modalLikeCounter.removeClass('text-white').addClass('text-success');
                    modalLikeIcon.removeClass('bi-hand-thumbs-up-fill').addClass('bi-hand-thumbs-up');
                    
                    pageLikeCounter.removeClass('text-white').addClass('text-success');
                    pageLikeIcon.removeClass('bi-hand-thumbs-up-fill').addClass('bi-hand-thumbs-up');

                    clickedButton.removeClass('btn-success').addClass('liked-button');

                    // Color change
                    modalLikeIcon = document.getElementById('modal-like-icon-' + postId)
                    modalLikeIcon.style.color = '#198754'
                    pageLikeIcon = document.getElementById('page-like-icon-' + postId)
                    pageLikeIcon.style.color = '#198754'
                }
            },
            error: function(xhr, errmsg, err) {
                console.log('Error:', xhr.ststus, xhr.statusText);
            },
            beforeSend: function(xhr, settings) {
                console.log('Before send:', settings);
                console.log('i.hasContent:', settings.hasContent);
                console.log('i.data:', settings.data);
            }
        });
    });
    $(document).on('submit', '#post-form', function(e) {
        e.preventDefault(); // Prevents reloading of the website
        console.log('prevented');
    });
    $('.comments-container').on('click', '.comment-like-button', function() { // When the button is pressed
        console.log('clicked');
        var commentId = $(this).data('comment-id');
        console.log('Comment ID:', commentId)

        // Defining variables
        var button = $('.comment-like-button-' + commentId);
        var counter
        var icon

        // AJAX
        $.ajax({
            type: 'POST',
            url: '/page/comment-liked/',
            data: {
                'comment_id': commentId,
                'comment_type': 'comment',
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(response) {
                console.log('success');

                // Getting relevent elements
                counter = $('#comment-like-text-' + commentId);
                icon = $('#comment-like-icon-' + commentId);

                // Changing text
                counter.html(response.likes);

                // Different styles for in the comment was liked of not
                if (response.isLiked) {
                    console.log('like');

                    // Change classes for like state
                    counter.removeClass('text-success').addClass('text-white');
                    icon.removeClass('bi-hand-thumbs-up').addClass('bi-hand-thumbs-up-fill');
                    button.removeClass('liked-button').addClass('btn-success');

                    icon.css('color', '#ffffff');

                } else {
                    console.log('dislike');

                    // Change classes for dislike state
                    counter.removeClass('text-white').addClass('text-success');
                    icon.removeClass('bi-hand-thumbs-up-fill').addClass('bi-hand-thumbs-up');
                    button.removeClass('btn-success').addClass('liked-button');

                    icon.css('color', '#198754');                                                                     
                }
            },
            error: function(xhr, errmsg, err) {
                console.log('Error:', xhr.ststus, xhr.statusText);
            },
            beforeSend: function(xhr, settings) {
                console.log('Before send:', settings);
                console.log('i.hasContent:', settings.hasContent);
                console.log('i.data:', settings.data);
            }
        })
    });
    $('.comments-container').on('click', '.nested-comment-like-button', function() { // When the button is pressed
        console.log('clicked');
        var commentId = $(this).data('comment-id');
        console.log('Comment ID:', commentId);

        // Defining variables
        var button = $('.nested-comment-like-button-' + commentId);
        var counter;
        var icon;

        // AJAX
        $.ajax({
            type: 'POST',
            url: '/page/comment-liked/',
            data: {
                'comment_id': commentId,
                'comment_type': 'nested-comment',
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(response) {
                console.log('success');

                // Getting relevant elements
                counter = $('#nested-comment-like-text-' + commentId);
                icon = $('#nested-comment-like-icon-' + commentId);

                // Changing text
                counter.text(response.likes);

                // Different styles for if the comment was liked or not
                if (response.isLiked) {
                    console.log('like');

                    // Change classes for dislike state
                    counter.removeClass('text-success').addClass('text-white');
                    icon.removeClass('bi-hand-thumbs-up').addClass('bi-hand-thumbs-up-fill');
                    button.removeClass('liked-button').addClass('btn-success');

                    // Color change
                    icon.css('color', '#ffffff');

                } else {
                    console.log('dislike');

                    // Change classes for dislike state
                    counter.removeClass('text-white').addClass('text-success');
                    icon.removeClass('bi-hand-thumbs-up-fill').addClass('bi-hand-thumbs-up');
                    button.removeClass('btn-success').addClass('liked-button');

                    // Color change
                    icon.css('color', '#198754');                                                                      
                }
            },
            error: function(xhr, errmsg, err) {
                console.log('Error:', xhr.status, xhr.statusText);
            },
            beforeSend: function(xhr, settings) {
                console.log('Before send:', settings);
                console.log('i.hasContent:', settings.hasContent);
                console.log('i.data:', settings.data);
            }
        });
    });
    $('.add-comment').click(function () {
        var postId = $(this).data('post-id');
        var text = $('#comment-text-' + postId).val();
        console.log(postId, text)
        $.ajax({
            type: 'POST',
            url: '/page/new-comment/',
            data: {
                'post_id': postId,
                'text': text,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },

            success: function(response) {
                console.log('success', response)
                postSocket.send(JSON.stringify({
                    'request_type': 'create_comment',
                    'object_id': response.comment_id
                }));
            },
        })
    })
    $('.comments-container').on('click', '.add-reply', function () {
        var commentId = $(this).data('comment-id');
        var text = $('#reply-text-' + commentId).val();
        console.log(commentId, text);
        $.ajax({
            type: 'POST',
            url: '/page/new_reply/',
            data: {
                'comment_id': commentId,
                'text': text,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(response) {
                console.log('success')
                postSocket.send(JSON.stringify({
                    'request_type': 'create_reply',
                    'object_id': response.reply_id
                }));
            },
        },
        )
    });
})