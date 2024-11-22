$(document).ready(function () {
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    // Preview update functions for the post title and the contents
    $('#post-title').on('input', function () {
        var textInput = $('#post-title').val()
        console.log('Text: ' + textInput)
        console.log('Length: ' + textInput.length)

        if (textInput.length == 0) {
            var previewText = 'My Post'
        } else {
            var previewText = textInput
        }

        $('#post-title-preview').text(previewText)
    })

    $('#post-contents').on('input', function () {
        var textInput = $('#post-contents').val()
        console.log('Text: ' + textInput)
        console.log('Length: ' + textInput.length)

        if (textInput.length == 0) {
            var previewText = 'This post is about...'
        } else {
            var previewText = textInput
        }

        $('#post-contents-preview').text(previewText)
    })

    // Media preview: insert
    $('#media-input').on('input', function (event) {
        var mediaFiles = event.target.files[0]; // remove the '[0]' to have all media files in a list.
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
        var mediaFiles = event.originalEvent.dataTransfer.files[0]; // remove the '[0]' to have all media files in a list.
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
        $(this).removeClass('drag-over-state');
    })
})