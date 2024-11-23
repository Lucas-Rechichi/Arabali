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

            $('#post-title').removeClass('is-valid').addClass('is-invalid')
            $('.post-title-invalid').css('display', 'block')
        } else {
            var previewText = textInput

            $('#post-title').removeClass('is-invalid').addClass('is-valid')
            $('.post-title-invalid').css('display', 'none')
        }   

        $('#post-title-preview').text(previewText)
    })

    $('#post-contents').on('input', function () {
        var textInput = $('#post-contents').val()
        console.log('Text: ' + textInput)
        console.log('Length: ' + textInput.length)

        if (textInput.length == 0) {
            var previewText = 'This post is about...'

            $('#post-contents').removeClass('is-valid').addClass('is-invalid')
            $('.post-contetns-invalid').css('display', 'block')
        } else {
            var previewText = textInput

            $('#post-contents').removeClass('is-invalid').addClass('is-valid')
            $('.post-contetns-invalid').css('display', 'none')
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
                var mediaURL = URL.createObjectURL(mediaFiles);
                var mediaPreviewHtml = `
                    <img src="${mediaURL}" alt="Preview of selected media" style="height: 248px; width: 100%; border-radius: 20px;">
                `;
                $('#post-media-preview-container').html(mediaPreviewHtml)
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
                var mediaURL = URL.createObjectURL(mediaFiles);
                var mediaPreviewHtml = `
                    <img src="${mediaURL}" alt="Preview of selected media" style="height: 248px; width: 100%; border-radius: 20px;">
                `;
                $('#post-media-preview-container').html(mediaPreviewHtml)
            }   
        }
        $(this).removeClass('drag-over-state');
        $(this).addClass('valid-media');
    })

    // Post submission
    $('#create-post').click(function () {
        // defining key input fields 
        var titleField = $('#post-title');
        var contentsField = $('#post-contents');
        var mediaDropField = $('.file-drop-input');

        console.log(mediaDropField)

        // form validation
        if (titleField.val().length == 0 || contentsField.val().length == 0) {

            // for the title
            if (titleField.val().length == 0) {
                titleField.removeClass('is-valid').addClass('is-invalid');
                $('.post-title-invalid').css('display', 'block');
            } else {
                titleField.removeClass('is-invalid').addClass('is-valid');
                $('.post-title-invalid').css('display', 'none');
            }

            // for the contents of the post
            if (contentsField.val().length == 0) {
                contentsField.removeClass('is-valid').addClass('is-invalid');
                $('.post-contents-invalid').css('display', 'block');
            } else {
                contentsField.removeClass('is-invalid').addClass('is-valid');
                $('.post-contetns-invalid').css('display', 'none');
            }   

            // for the media of the post
            if (!mediaFiles) {
                mediaDropField.removeClass('valid-media').addClass('invalid-media');
            } else {
                mediaDropField.removeClass('invalid-media').addClass('valid-media');
            }
        }
    })
})