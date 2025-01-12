import { previewMediaFiles, addMediaToList, shuffleArray, getCaptionData } from './functions.js';

$(document).ready(function () {

    // Getting csrf token from the HTML document
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    // Preview update functions for the post title and the contents
    $('#post-title').on('input', function () {
        var textInput = $('#post-title').val()

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
    let mediaFiles;
    let mediaList = [];

    // Media preview: Insert
    $('#media-input').on('input', function (event) {
        mediaFiles = Array.from(event.target.files); 

        if (mediaFiles) {

            // Add new media to the list
            var mediaListData = addMediaToList(mediaFiles, mediaList)
            mediaList = mediaListData['updatedMediaList'];

            // Visual indicatiors for when the media input limit is reached
            if (mediaListData['limitReached']) {
                $('#post-media-limit-message').css('display', 'block');
            }

            // Prepare previewMediaFiles metadata
            var metadata = {
                'type': 'media-upload',
                'input-index-start': mediaListData['inputIndexStart'],
            }

            // Get the preview HTML, replace controls/preview HTML or placeholders
            var carouselObjects = previewMediaFiles(mediaList, metadata);
            $('#post-media-preview-container').html(carouselObjects['carousel']); 
            $('#post-carousel-control-pannel').html(carouselObjects['controlPannel']);
            $('#post-carousel-captions-form').html(carouselObjects['captionForm']);

            // Change the state of the field if validation has occured
            if ( ( $('#post-media-card').hasClass('is-invalid') || $('#post-media-invalid').css('display') === 'block' ) && ( $('#create-post').hasClass('validated') ) ) {
                $('#post-media-card').removeClass('invalid-media').addClass('valid-media');
                $('#post-media-invalid').css('display', 'none');
            }
            // Change the css of the colour picker buttons for the caption form
            var colourPickerButtons = $('#post-carousel-captions-form .colour-picker-button');
            colourPickerButtons.each(function () {
                $(this).css('background-color', `${$(this).data('colour')}`);
            })
        }
    })

    // Media preview: drag and drop
    $('#post-media-card').on('dragover', function (event) {
        event.preventDefault(); // prevents the opening of another tab to view the image.

        // For seeing the dragover state
        if ( $('#create-post').hasClass('validated') && ( $('#post-media-invalid').css('display') === 'block' || $('#file-drop-input').hasClass('invalid-media') ) ) {
            $('#post-media-card').removeClass('invalid-media');
        }

        $(this).addClass('drag-over-state');
    });

    $('#post-media-card').on('dragleave', function () {

        // For validation
        if ( $('#create-post').hasClass('validated') && $('#post-media-invalid').css('display') === 'block' ) {
            $('#post-media-card').addClass('invalid-media');
        };

        $(this).removeClass('drag-over-state');
    });

    $('#post-media-card').on('drop', function (event) {
        event.preventDefault(); // prevents the opening of another tab to view the image.

        // Getting media files from drop input
        mediaFiles = Array.from(event.originalEvent.dataTransfer.files);

        // Processing files
        if (mediaFiles) {

            // Add new media to the list
            var mediaListData = addMediaToList(mediaFiles, mediaList)
            mediaList = mediaListData['updatedMediaList'];

            // Visual indicatiors for when the media input limit is reached
            if (mediaListData['limitReached']) {
                $('#post-media-limit-message').css('display', 'block');
            }

            // Prepare previewMediaFiles metadata
            var metadata = {
                'type': 'media-upload',
                'input-index-start': mediaListData['inputIndexStart'],
            }

            // Get the preview HTML, replace controls/preview HTML or placehonders
            var carouselObjects = previewMediaFiles(mediaList, metadata);
            $('#post-media-preview-container').html(carouselObjects['carousel']);
            $('#post-carousel-control-pannel').html(carouselObjects['controlPannel']);
            $('#post-carousel-captions-form').html(carouselObjects['captionForm']);
            
            // Change the state of the field if validation has occured
            if ( ( $('#post-media-card').hasClass('is-invalid') || $('#post-media-invalid').css('display') === 'block' ) && ( $('#create-post').hasClass('validated') ) ) {
                $('#post-media-card').removeClass('invalid-media').addClass('valid-media');
                $('#post-media-invalid').css('display', 'none');
            }

            // Change the css of the colour picker buttons for the caption form
            var colourPickerButtons = $('#post-carousel-captions-form .colour-picker-button');
            colourPickerButtons.each(function () {
                $(this).css('background-color', `${$(this).data('colour')}`);
            })

            // Visual indicators for the dropover box
            $(this).removeClass('drag-over-state');

        }
    })

    // Carousel control pannel: Shuffle
    $('#post-carousel-control-pannel').on('click', '.carousel-pannel-shuffle', function () {

        // Get relevant data
        var slideID = $(this).data('slide-id');
        var direction = $(this).data('direction');

        // Logic for moving slides
        if (direction === 'left') {
            // Compute the id pf the affected slide, shuffle the position of the media inside of the mediaFiles array
            var affectedSlideID = slideID - 1;
            mediaList = shuffleArray(mediaList, slideID, direction)

        } else { // direction === 'right'
            // Compute the id pf the affected slide, shuffle the position of the media inside of the mediaFiles array
            var affectedSlideID = slideID + 1;
            mediaList = shuffleArray(mediaList, slideID, direction)
        }

        // Prepare previewMediaFiles metadata
        var metadata = {
            'type': 'media-shuffle',
            'moving-slide-id': slideID,
            'affected-slide-id': affectedSlideID
        }

        // Recall previewMediaFiles function with the newly ordered files
        var carouselObjects = previewMediaFiles(mediaList, metadata);
        $('#post-media-preview-container').html(carouselObjects['carousel']);
        $('#post-carousel-control-pannel').html(carouselObjects['controlPannel']);
        $('#post-carousel-captions-form').html(carouselObjects['captionForm']);

        // Change the css of the colour picker buttons for the caption form
        var colourPickerButtons = $('#post-carousel-captions-form .colour-picker-button');
        colourPickerButtons.each(function () {
            $(this).css('background-color', `${$(this).data('colour')}`);
        })
    })

    // Carousel control pannel: Delete
    $('#post-carousel-control-pannel').on('click', '.carousel-pannel-delete', function () {
        // Get slide id
        var slideID = $(this).data('slide-id');

        // Delete from media list, redo previews
        mediaList.splice(slideID, 1)

        if (mediaList.length > 0) {

            // Prepare previewMediaFiles metadata
            var metadata = {
                'type': 'media-delete',
            }

            // Recall previewMediaFiles function with the newly ordered files
            var carouselObjects = previewMediaFiles(mediaList, metadata);
            $('#post-media-preview-container').html(carouselObjects['carousel']);
            $('#post-carousel-control-pannel').html(carouselObjects['controlPannel']);
            $('#post-carousel-captions-form').html(carouselObjects['captionForm']);
        } else {
            // Replace data with defaults
            var emptyPannelMessageHtml = `
                <div class="row">
                    <div class="col">
                        <p class="lead text-center m-0 pt-2 pb-2">No media to sort.</p>
                    </div>
                </div>
            `;
            var emptyCaptionContainerMessageHtml = `
                <div class="row">
                    <div class="col">
                        <p class="lead text-center m-0 pt-2 pb-2">No media to caption.</p>
                    </div>
                </div>
            `;
            var imagePlaceholderHtml = `
                <i class="bi bi-card-image d-flex justify-content-center" style="font-size: 15rem; color: #198754;"></i>
            `;

            $('#post-carousel-control-pannel').html(emptyPannelMessageHtml);
            $('#post-carousel-captions-form').html(emptyCaptionContainerMessageHtml);
            $('#post-media-preview-container').html(imagePlaceholderHtml);

            // Change the state of the field if validation has occured
            if ( ( $('#post-media-card').hasClass('valid-media') || $('#post-media-invalid').css('display') === 'none' ) && ( $('#create-post').hasClass('validated') ) ) {
                $('#post-media-card').removeClass('valid-media').addClass('invalid-media');
                $('#post-media-invalid').css('display', 'block');
            }
        }

        // Change the css of the colour picker buttons for the caption form
        var colourPickerButtons = $('#post-carousel-captions-form .colour-picker-button');
        colourPickerButtons.each(function () {
            $(this).css('background-color', `${$(this).data('colour')}`);
        })

        // Hide the limit message
        $('#post-media-limit-message').css('display', 'none');
    });

    // Caption form input previews
    $('#post-carousel-captions-form').on('input', '.caption-text', function () {
        var captionID = $(this).data('caption-id');
        var textInput = $(this).val();

        var captionData = getCaptionData(captionID);

        if (textInput.length === 0) {
            var captionHtml = `<p id="carousel-caption-text-${captionID}" class="${captionData['fontClass']}" data-font="${captionData['font']}" data-colour="${captionData['colour']}" style="color: ${captionData['colour']}">This image represents...</p>`

            if ( $('#create-post').hasClass('validated') ) {
                $('#caption-text-' + captionID).removeClass('is-valid').addClass('is-invalid');
                $('#carousel-caption-invalid-' + captionID).css('display', 'block');
            }

        } else {
            var captionHtml = `<p id="carousel-caption-text-${captionID}" class="${captionData['fontClass']}" data-font="${captionData['font']}" data-colour="${captionData['colour']}" style="color: ${captionData['colour']}">${textInput}</p>`

            if ( ( $('#caption-text-' + captionID).hasClass('is-invalid') || $('#carousel-caption-invalid-' + captionID).css('display') === 'block' ) && ( $('#create-post').hasClass('validated') ) ) {
                $('#caption-text-' + captionID).removeClass('is-invalid').addClass('is-valid');
                $('#carousel-caption-invalid-' + captionID).css('display', 'none');
            }
        }

        $('#carousel-caption-' + captionID).html(captionHtml)
        
    })

    // Colour picker preview event listener is within colour-picker.js, triggered by the save button

    $('#post-carousel-captions-form').on('change', '.caption-text-font', function () {
        var captionID = $(this).data('caption-id');
        var option = $(this).val();
        var captionData = getCaptionData(captionID);

        var captionHtml = `<p id="carousel-caption-text-${captionID}" class="${'font-' + option}" data-font="${option}" data-colour="${captionData['colour']}" style="color: ${captionData['colour']}">${captionData['text']}</p>`

        $('#carousel-caption-' + captionID).html(captionHtml);
    })


    // Visual modals 
    var creatingPostModal = new bootstrap.Modal(document.getElementById('creating-post-modal'), {
        keyboard: false
    })
    var postCreatedModal = new bootstrap.Modal(document.getElementById('post-created-modal'), {
        keyboard: false
    })

    // Button for visual modal
    $('#make-another-post').click(function () {
        postCreatedModal.hide();
    })

    // Post submission
    $('#create-post').click(function () {
        $(this).addClass('validated')

        // Defining key input fields 
        var titleField = $('#post-title');
        var contentsField = $('#post-contents');
        var mediaDropField = $('.file-drop-input');

        // For the captions
        var captionsAreValid = true;
        var captionData;
        var captionDataList = [];
        for (let i=0; i < mediaList.length; i++) {
            if ( !($('#caption-text-' + i).val()) ) {
                captionsAreValid = false
            } else {
                captionData = getCaptionData(i)
                captionDataList.push({
                    'text': captionData['text'],
                    'colour': captionData['colour'],
                    'font': captionData['font'] 
                })
            }
        }

        // Form validation
        if (titleField.val().length == 0 || contentsField.val().length == 0 || mediaList.length == 0 || !captionsAreValid) {

            // For the title
            if (titleField.val().length == 0) {
                titleField.removeClass('is-valid').addClass('is-invalid');
                $('#post-title-invalid').css('display', 'block');
            } else {
                titleField.removeClass('is-invalid').addClass('is-valid');
                $('#post-title-invalid').css('display', 'none');
            }

            // For the contents of the post
            if (contentsField.val().length == 0) {
                contentsField.removeClass('is-valid').addClass('is-invalid');
                $('#post-contents-invalid').css('display', 'block');
            } else {
                contentsField.removeClass('is-invalid').addClass('is-valid');
                $('#post-contetns-invalid').css('display', 'none');
            }   

            // For the media of the post
            if (mediaList.length == 0) {
                mediaDropField.removeClass('valid-media').addClass('invalid-media');
                $('#post-media-invalid').css('display', 'block');
            } else {
                mediaDropField.removeClass('invalid-media').addClass('valid-media');
                $('#post-media-invalid').css('display', 'none');
            }

            for (let i=0; i < mediaList.length; i++) {
                if ( !($('#caption-text-' + i).val()) ) {
                    $('#caption-text-' + i).removeClass('is-valid').addClass('is-invalid');
                    $('#carousel-caption-invalid-' + i).css('display', 'block');
                } else {
                    $('#caption-text-' + i).removeClass('is-invalid').addClass('is-valid');
                    $('#carousel-caption-invalid-' + i).css('display', 'none');
                }
            }

        } else {
            // Getting relevant data
            var titleInput = $('#post-title').val();
            var contentsInput = $('#post-contents').val();

            // Caption data is gotten within first for loop

            // Show the creating post modal
            creatingPostModal.show()

            // Formatting data into FormData object
            var formData = new FormData()

            // For media files
            for (let i=0; i < mediaList.length; i++) {
                formData.append('media', mediaList[i])
            }

            formData.append('title', titleInput)
            formData.append('contents', contentsInput)
            formData.append('captions', JSON.stringify(captionDataList))
            formData.append('csrfmiddlewaretoken', csrfToken)

            // AJAX request
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
                    }, 500)
                }
            })
        }
    })

})