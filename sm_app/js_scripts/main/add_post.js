$(document).ready(function () {

    // Getting csrf token from the HTML document
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    // Preview update functions for the post title and the contents
    $('#post-title').on('input', function () {
        var textInput = $('#post-title').val()
        console.log('Text: ' + textInput)
        console.log('Length: ' + textInput.length)

        if (textInput.length == 0) {
            var previewText = 'My Post'
            if ( $('#create-post').hasClass('validated') ) {
                $('#post-title').removeClass('is-valid').addClass('is-invalid');
                $('#post-title-invalid').css('display', 'block');
            }
        } else {
            var previewText = textInput
            if ( ( $('#post-title').hasClass('is-invalid') || $('#post-title-invaid').css('display') === 'block' ) && ( $('#create-post').hasClass('validated') ) ) {
                $('#post-title').removeClass('is-invalid').addClass('is-valid');
                $('#post-title-invalid').css('display', 'none');
            }
        }
        $('#post-title-preview').text(previewText)
    })

    $('#post-contents').on('input', function () {
        var textInput = $('#post-contents').val()
        console.log('Text: ' + textInput)
        console.log('Length: ' + textInput.length)

        if (textInput.length == 0) {
            var previewText = 'This post is about...'

            if ( $('#create-post').hasClass('validated') ) {
                $('#post-contents').removeClass('is-valid').addClass('is-invalid');
                $('#post-contents-invalid').css('display', 'block');
            }
        } else {
            var previewText = textInput

            if ( ( $('#post-contents').hasClass('is-invalid') || $('#post-contents-invalid').css('display') === 'block' ) && ( $('#create-post').hasClass('validated') ) ) {
                $('#post-contents').removeClass('is-invalid').addClass('is-valid');
                $('#post-contents-invalid').css('display', 'none');
            }
        }
        $('#post-contents-preview').text(previewText)
    })
    // Media setup
    var mediaFiles;

    // Media preview: insert
    $('#media-input').on('input', function (event) {
        mediaFiles = event.target.files[0]; // remove the '[0]' to have all media files in a list.
        if (mediaFiles) {
            console.log(mediaFiles.type)
            if (mediaFiles.type.startsWith('image/')) {
                // preview the media
                var mediaURL = URL.createObjectURL(mediaFiles);
                var mediaPreviewHtml = `
                    <img src="${mediaURL}" alt="Preview of selected media" style="height: 248px; width: 100%; border-radius: 20px;">
                `;
                $('#post-media-preview-container').html(mediaPreviewHtml)

                // change the state of the field if validation has occured
                if ( ( $('#post-media-card').hasClass('is-invalid') || $('#post-media-invalid').css('display') === 'block' ) && ( $('#create-post').hasClass('validated') ) ) {
                    $('#post-media-card').removeClass('invalid-media').addClass('valid-media');
                    $('#post-media-invalid').css('display', 'none');
                }
            }   
        }
    })

    // Media preview: drag and drop
    $('#post-media-card').on('dragover', function (event) {
        event.preventDefault();
        $(this).addClass('drag-over-state');
    });

    $('#post-media-card').on('dragleave', function () {
        $(this).removeClass('drag-over-state');
    });

    $('#post-media-card').on('drop', function (event) {
        event.preventDefault();
        mediaFiles = event.originalEvent.dataTransfer.files[0]; // remove the '[0]' to have all media files in a list.
        if (mediaFiles) {
            if (mediaFiles.type.startsWith('image/')) {
                // preview the media
                var mediaURL = URL.createObjectURL(mediaFiles);
                var mediaPreviewHtml = `
                    <img src="${mediaURL}" alt="Preview of selected media" style="height: 248px; width: 100%; border-radius: 20px;">
                `;
                $('#post-media-preview-container').html(mediaPreviewHtml)

                // change the state of the field if validation has occured
                if ( ( $('#post-media-card').hasClass('is-invalid') || $('#post-media-invalid').css('display') === 'block' ) && ( $('#create-post').hasClass('validated') ) ) {
                    $('#post-media-card').removeClass('invalid-media').addClass('valid-media');
                    $('#post-media-invalid').css('display', 'none');
                }
            }   
        }
        $(this).removeClass('drag-over-state');
        $(this).addClass('valid-media');
    })

    // Visual modals 
    var creatingPostModal = new bootstrap.Modal(document.getElementById('creating-post-modal'), {
        keyboard: false
    })
    var postCreatedModal = new bootstrap.Modal(document.getElementById('post-created-modal'), {
        keyboard: false
    })

    // Post submission
    $('#create-post').click(function () {
        $(this).addClass('validated')

        // defining key input fields 
        var titleField = $('#post-title');
        var contentsField = $('#post-contents');
        var mediaDropField = $('.file-drop-input');

        // form validation
        if (titleField.val().length == 0 || contentsField.val().length == 0 || !mediaFiles) {

            // for the title
            if (titleField.val().length == 0) {
                titleField.removeClass('is-valid').addClass('is-invalid');
                $('#post-title-invalid').css('display', 'block');
            } else {
                titleField.removeClass('is-invalid').addClass('is-valid');
                $('#post-title-invalid').css('display', 'none');
            }

            // for the contents of the post
            if (contentsField.val().length == 0) {
                contentsField.removeClass('is-valid').addClass('is-invalid');
                $('#post-contents-invalid').css('display', 'block');
            } else {
                contentsField.removeClass('is-invalid').addClass('is-valid');
                $('#post-contetns-invalid').css('display', 'none');
            }   

            // for the media of the post
            if (!mediaFiles) {
                mediaDropField.removeClass('valid-media').addClass('invalid-media');
                $('#post-media-invalid').css('display', 'block');
            } else {
                mediaDropField.removeClass('invalid-media').addClass('valid-media');
                $('#post-media-invalid').css('display', 'none');
            }
        } else {
            // getting relevant data
            var titleInput = $('#post-title').val();
            var contentsInput = $('#post-contents').val();
            var mediaInput = mediaFiles

            creatingPostModal.show()

            formData = new FormData()
            formData.append('title', titleInput)
            formData.append('contents', contentsInput)
            formData.append('media', mediaInput)
            formData.append('csrfmiddlewaretoken', csrfToken)

            $.ajax({
                type: 'POST',
                url: '/add/add-post/',
                processData: false,
                contentType: false, 
                data: formData,
                success: function (response) {
                    creatingPostModal.hide()
                    setTimeout(function () {
                        postCreatedModal.show()
                    }, 300)
                }
            })
        }
    })

})