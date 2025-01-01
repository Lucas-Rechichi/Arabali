export function previewMediaFiles(mediaFilesList, metadata) {

    // Preparing variables 
    var mediaURL;

    // Preview
    var carouselSlidesHtml = ``;
    var carouselIndicatorsHtml = ``;
    
    var carouselSlideHtml;
    var carouselCaptionHtml;
    var carouselIndicatiorHtml;

    // Carousel control and caption form
    var carouselPannelsHtml = ``;
    var carouselCaptionFormHtml = ``;

    var carouselPannelHtml;
    var carouselCaptionInputHtml;
    var captionTextHtml;
    var captionColourHtml;
    var captionFontHtml;

    var captionData;

    var type = metadata['type'];

    // Loops though all media within the media files list
    for (let i=0; i < mediaFilesList.length; i++) {
        // Creating the media URL object
        mediaURL = URL.createObjectURL(mediaFilesList[i]);

        // Check to see if images are used for media
        if (mediaFilesList[i].type.startsWith('image/')) {
            // Creating the carousel indicatiors
            if (i == 0) {
                carouselIndicatiorHtml = `
                    <button type="button" data-bs-target="#preview-media-carousel" data-bs-slide-to="${i}" class="active" aria-current="true" aria-label="Slide ${i + 1}"></button>
                `;
            } else {
                carouselIndicatiorHtml = `
                    <button type="button" data-bs-target="#preview-media-carousel" data-bs-slide-to="${i}" aria-label="Slide ${i + 1}"></button>
                `;
            }

            // Creating the carousel control elements
            if ( mediaFilesList.length != 1) {
                if (i == 0) { // cannot swap left
                    carouselPannelHtml = `
                        <div id="carousel-pannel-slide-${i}" class="col-2">
                            <div class="card p-1">
                                <p id="carousel-slide-indicator-${i}" class="lead text-center m-0">${i + 1}</p>
                                <img class="mb-1" src="${mediaURL}" alt="Previewing media with path: ${mediaURL}, for slide: ${i}" style="width: 70px; height: 40px;">
                                <div class="row">
                                    <div class="col-6">
                                        <button type="button" class="btn btn-outline-dark carousel-pannel-shuffle" data-slide-id="${i}" data-direction="left" disabled><i class="bi bi-arrow-left-short"></i></button>
                                    </div>
                                    <div class="col-6">
                                        <button type="button" class="btn btn-outline-dark carousel-pannel-shuffle" data-slide-id="${i}" data-direction="right"><i class="bi bi-arrow-right-short"></i></button>
                                    </div>
                                </div>
                                <div class="row mt-1">
                                    <div class="col d-flex justify-content-center">
                                        <button type="button" class="btn btn-outline-danger carousel-pannel-delete" data-slide-id="${i}"><i class="bi bi-trash3-fill"></i></button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                } else if (i == mediaFilesList.length - 1) { // cannot swap right
                    carouselPannelHtml = `
                        <div id="carousel-pannel-slide-${i}" class="col-2">
                            <div class="card p-1">
                                <p id="carousel-slide-indicator-${i}" class="lead text-center m-0">${i + 1}</p>
                                <img class="mb-1" src="${mediaURL}" alt="Previewing media with path: ${mediaURL}, for slide: ${i}" style="width: 70px; height: 40px;">
                                <div class="row">
                                    <div class="col-6">
                                        <button type="button" class="btn btn-outline-dark carousel-pannel-shuffle" data-slide-id="${i}" data-direction="left"><i class="bi bi-arrow-left-short"></i></button>
                                    </div>
                                    <div class="col-6">
                                        <button type="button" class="btn btn-outline-dark carousel-pannel-shuffle" data-slide-id="${i}" data-direction="right" disabled><i class="bi bi-arrow-right-short"></i></button>
                                    </div>
                                </div>
                                <div class="row mt-1">
                                    <div class="col d-flex justify-content-center">
                                        <button type="button" class="btn btn-outline-danger carousel-pannel-delete" data-slide-id="${i}"><i class="bi bi-trash3-fill"></i></button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                } else {  // can swap either way
                carouselPannelHtml = `
                    <div id="carousel-pannel-slide-${i}" class="col-2">
                        <div class="card p-1">
                            <p id="carousel-slide-indicator-${i}" class="lead text-center m-0">${i + 1}</p>
                            <img class="mb-1" src="${mediaURL}" alt="Previewing media with path: ${mediaURL}, for slide: ${i}" style="width: 70px; height: 40px;">
                            <div class="row">
                                <div class="col-6">
                                    <button type="button" class="btn btn-outline-dark carousel-pannel-shuffle" data-slide-id="${i}" data-direction="left"><i class="bi bi-arrow-left-short"></i></button>
                                </div>
                                <div class="col-6">
                                    <button type="button" class="btn btn-outline-dark carousel-pannel-shuffle" data-slide-id="${i}" data-direction="right"><i class="bi bi-arrow-right-short"></i></button>
                                </div>
                            </div>
                            <div class="row mt-1">
                                <div class="col d-flex justify-content-center">
                                    <button type="button" class="btn btn-outline-danger carousel-pannel-delete" data-slide-id="${i}"><i class="bi bi-trash3-fill"></i></button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                }
            } else { // cannot swap 
            carouselPannelHtml = `
                <div id="carousel-pannel-slide-${i}" class="col-2">
                    <div class="card p-1">
                        <p id="carousel-slide-indicator-${i}" class="lead text-center m-0">${i + 1}</p>
                        <img class="mb-1" src="${mediaURL}" alt="Previewing media with path: ${mediaURL}, for slide: ${i}" style="width: 70px; height: 40px;">
                        <div class="row">
                            <div class="col-6">
                                <button type="button" class="btn btn-outline-dark carousel-pannel-shuffle" data-slide-id="${i}" data-direction="left" disabled><i class="bi bi-arrow-left-short"></i></button>
                            </div>
                            <div class="col-6">
                                <button type="button" class="btn btn-outline-dark carousel-pannel-shuffle" data-slide-id="${i}" data-direction="right" disabled><i class="bi bi-arrow-right-short"></i></button>
                            </div>
                        </div>
                        <div class="row mt-1">
                            <div class="col d-flex justify-content-center">
                                <button type="button" class="btn btn-outline-danger carousel-pannel-delete" data-slide-id="${i}"><i class="bi bi-trash3-fill"></i></button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            }

            // Conditionals for different types of use cases for this function
            if (type === 'media-upload' || type === 'media-delete') {
                // For new media
                var inputIndexStart = metadata['input-index-start']

                // Conditional for if the index falls within the new range of media 
                if (i >= inputIndexStart && type === 'media-upload') { 
                    var captionText = 'This image represents...';
                    var captionColour = '#ffffffff';
                    var captionFont = 'default';
                    var captionFontClass = 'font-default';

                } else { // for both excluded indexes and when deleting media
                    var captionData = getCaptionData(i)

                    var captionText = captionData['text'];
                    var captionColour = captionData['colour'];
                    var captionFont = captionData['font'];
                    var captionFontClass = captionData['fontClass'];
                }

            } else { // type === 'media-shuffle' 

                // For the slide indexes that are affected by the shuffle
                var movingSlideID = metadata['moving-slide-id'];
                var affectedSlideID = metadata['affected-slide-id'];

                // Logic for what needs to be moved
                if (i === movingSlideID) {
                    captionData = getCaptionData(affectedSlideID);
                } else if (i === affectedSlideID) {
                    captionData = getCaptionData(movingSlideID);
                } else { // the index is not affected by the shuffle
                    captionData = getCaptionData(i)
                }

                var captionText = captionData['text'];
                var captionColour = captionData['colour'];
                var captionFont = captionData['font'];
                var captionFontClass = captionData['fontClass'];
            }
            
            // HTML for the caption form
            if (captionText === 'This image represents...') {
                captionTextHtml = `
                    <input type="text" id="caption-text-${i}" class="form-control caption-text" placeholder="Caption" aria-label="Caption" data-caption-id="${i}">
                `;
            } else {
                captionTextHtml = `
                    <input type="text" id="caption-text-${i}" class="form-control caption-text" placeholder="Caption" value="${captionText}" aria-label="Caption" data-caption-id="${i}">
                `;
            };

            captionColourHtml = `
                <div id="caption-text-colour-${i}" class="colour-picker-button" data-colour="${captionColour}" data-caption-id="${i}"></div> 
            `;

            // For the font selected
            switch (captionFont) {
                case 'default':
                    var optionsHtml = `
                        <option value="default" selected>Default Font</option>
                        <option value="strong">Strong</option>
                        <option value="italic">Italic</option>
                        <option value="corier-new">Corier New</option>
                        <option value="comic-sans-ms">Comic Sans MS</option>
                        <option value="impact">Impact</option>
                        <option value="palatino-linotype">Palatino Linotype</option>
                    `;
                    break;

                case 'strong':
                    var optionsHtml = `
                        <option value="default">Default Font</option>
                        <option value="strong" selected>Strong</option>
                        <option value="italic">Italic</option>
                        <option value="corier-new">Corier New</option>
                        <option value="comic-sans-ms">Comic Sans MS</option>
                        <option value="impact">Impact</option>
                        <option value="palatino-linotype">Palatino Linotype</option>
                    `;
                    break;

                case 'italic':
                    var optionsHtml = `
                        <option value="default">Default Font</option>
                        <option value="strong">Strong</option>
                        <option value="italic" selected>Italic</option>
                        <option value="corier-new">Corier New</option>
                        <option value="comic-sans-ms">Comic Sans MS</option>
                        <option value="impact">Impact</option>
                        <option value="palatino-linotype">Palatino Linotype</option>
                    `;
                    break;

                case 'corier-new':
                    var optionsHtml = `
                        <option value="default">Default Font</option>
                        <option value="strong">Strong</option>
                        <option value="italic">Italic</option>
                        <option value="corier-new" selected>Corier New</option>
                        <option value="comic-sans-ms">Comic Sans MS</option>
                        <option value="impact">Impact</option>
                        <option value="palatino-linotype">Palatino Linotype</option>
                    `;
                    break;

                case 'comic-sans-ms':
                    var optionsHtml = `
                        <option value="default">Default Font</option>
                        <option value="strong">Strong</option>
                        <option value="italic">Italic</option>
                        <option value="corier-new">Corier New</option>
                        <option value="comic-sans-ms" selected>Comic Sans MS</option>
                        <option value="impact">Impact</option>
                        <option value="palatino-linotype">Palatino Linotype</option>
                    `;
                    break;

                case 'impact':
                    var optionsHtml = `
                        <option value="default">Default Font</option>
                        <option value="strong">Strong</option>
                        <option value="italic">Italic</option>
                        <option value="corier-new">Corier New</option>
                        <option value="comic-sans-ms">Comic Sans MS</option>
                        <option value="impact" selected>Impact</option>
                        <option value="palatino-linotype">Palatino Linotype</option>
                    `;
                    break;

                case 'palatino-linotype':
                    var optionsHtml = `
                        <option value="default">Default Font</option>
                        <option value="strong">Strong</option>
                        <option value="italic">Italic</option>
                        <option value="corier-new">Corier New</option>
                        <option value="comic-sans-ms">Comic Sans MS</option>
                        <option value="impact">Impact</option>
                        <option value="palatino-linotype" selected>Palatino Linotype</option>
                    `;
                    break;
            }

            // HTML for the caption preview
            carouselCaptionHtml = `
                <p id="carousel-caption-text-${i}" class="${captionFontClass}" data-font="${captionFont}" data-colour="${captionColour}" style="color: ${captionColour}">${captionText}</p>
            `;

            // Adding in font option to select element
            captionFontHtml = `
                <select id="caption-text-font-${i}" class="form-select caption-text-font" aria-label="Font Selection" data-caption-id="${i}">
                    ${optionsHtml}
                </select>
            `;

            // Creating the carousel slides
            if (i == 0) {
                carouselSlideHtml = `
                    <div class="carousel-item active">
                        <img src="${mediaURL}" class="d-block w-100"  alt="Media preview with url: ${mediaURL} and for slide: ${i + 1}" aria-current="true" style="width: 365px; height: 200px;">
                        <div id="carousel-caption-${i}" class="carousel-caption d-block d-md-block">
                            ${carouselCaptionHtml}
                        </div>
                    </div>
                `;
            } else {
                carouselSlideHtml = `
                    <div class="carousel-item">
                        <img src="${mediaURL}" class="d-block w-100" alt="Media preview with url: ${mediaURL} and for slide: ${i + 1}" style="width: 365px; height: 200px;">
                        <div id="carousel-caption-${i}" class="carousel-caption d-block d-md-block">
                            ${carouselCaptionHtml}
                        </div>
                    </div>
                `;
            };

            // Create the carousel captions forms
            carouselCaptionInputHtml = `
                <div class="row">
                    <div class="col">
                        <div id="caption-input-${i}" class="card caption-inputs p-1 mb-1">
                            <div class="row">
                                <div class="col-2">
                                    <p class="lead text-center mt-3">${i + 1}</p>
                                </div>
                                <div class="col-4">
                                    <label for="caption-text-${i}" class="form-label">Caption:</label>
                                    ${captionTextHtml}
                                    <div id="carousel-caption-invalid-${i}" aria-describedby="carousel-caption" class="invalid-feedback ms-1">
                                        <strong>Caption text required</strong>
                                    </div>
                                </div>
                                <div class="col-2">
                                    <div class="dropdown">
                                        <label for="caption-text-colour-${i}" class="form-label">Colour:</label>
                                        <div class="colour-picker-button-outer-shell">
                                            <div id="colour-picker-button-background-${i}" class="colour-picker-button-background">
                                                ${captionColourHtml}
                                            </div>
                                        </div>
                                    </div>
                                    
                                </div>
                                <div class="col-4">
                                    <label for="text-font-${i}" class="form-label">Font:</label>
                                    ${captionFontHtml}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;


            // Append data to the plural variables
            carouselIndicatorsHtml += carouselIndicatiorHtml;
            carouselSlidesHtml += carouselSlideHtml;
            carouselPannelsHtml += carouselPannelHtml;
            carouselCaptionFormHtml += carouselCaptionInputHtml;
        };
    };

    var carouselPreviewHtml = `
        <div id="preview-media-carousel" class="carousel slide">
            <div class="carousel-indicators">
                ${carouselIndicatorsHtml}
            </div>
            <div class="carousel-inner">
                ${carouselSlidesHtml}
            </div>
            <button class="carousel-control-prev" type="button" data-bs-target="#preview-media-carousel" data-bs-slide="prev">
                <img class="carousel-button" src="/images/system/html_images/Carousel Arrow Left.png">
            </button>
            <button class="carousel-control-next" type="button" data-bs-target="#preview-media-carousel" data-bs-slide="next">
                <img class="carousel-button" src="/images/system/html_images/Carousel Arrow Right.png">
            </button>
        </div>
    `;

    var controlPannelHtml = `
        <div class="row">
            ${carouselPannelsHtml}
        </div>
    `;

    var previewHtml = {
        'carousel': carouselPreviewHtml,
        'controlPannel': controlPannelHtml,
        'captionForm': carouselCaptionFormHtml,
    };

    return previewHtml
};

// Function for adding new media files to the current media list
export function addMediaToList(mediaFiles, currentMediaList) {
    // Setup
    var limitReached;

    // File count cannot be greater than 6, extract the files that can be accepted only if they can fit.
    if (currentMediaList.length > 6) { // already full, no input, trigger on-screen error
        limitReached = true;
    } else {
        if (mediaFiles.length + currentMediaList.length > 6) { // the addition of the media files exceeds 6, input what can fit, starting by what was inputted first, trigger on-screen error
            limitReached = true;
            var maxInput = 6 - currentMediaList.length; // get how much files can fit inside the media list

            var inputIndexStart = 6 - maxInput; // where the input of new files starts within the list in terms of it's index

            for (let i=0; i < maxInput; i++ ) {
                currentMediaList.push(mediaFiles[i]) // append the first selected media to current list
            }

        } else { // input all files, no on-screen error
            limitReached = false;

            var inputIndexStart = currentMediaList.length

            for (let i=0; i < mediaFiles.length; i++ ) {
                currentMediaList.push(mediaFiles[i]) // append to current list
            }
        }
    }

    // Response set
    var response = {
        'updatedMediaList': currentMediaList,
        'limitReached': limitReached,
        'inputIndexStart': inputIndexStart,
    };

    return response
}

// For swapping two items in an array
export function shuffleArray(array, movingIndex, direction) {
    // Get the item in the list, removing it from the list
    var movingItem = array.splice(movingIndex, 1)[0];

    // Get the moving item, removing it from the list, and add in the list with it's new order
    if (direction === 'right') {
        var affectedIndex = movingIndex; // The function takes 1 item out of the list, therefore when moving right, the index of the affected item becomes the index of the moving item.
        var affectedItem = array.splice(affectedIndex, 1)[0]; 

        array.splice(movingIndex, 0, affectedItem);
        array.splice(movingIndex + 1, 0, movingItem);
    } else {
        var affectedIndex = movingIndex - 1;
        var affectedItem = array.splice(affectedIndex, 1)[0]; 
        
        array.splice(affectedIndex, 0, movingItem);
        array.splice(affectedIndex + 1, 0, affectedItem);
    }

    // Return the newly arranged array
    return array
}

// Function for getting the caption data from the caption preview
export function getCaptionData(captionID) {
    var caption = $('#carousel-caption-text-' + captionID);

    var captiontext = caption.text();
    var captionColour = caption.data('colour');
    var captionFont = caption.data('font');

    var fontClass = 'font-' +  captionFont;

    var captionData = {
        'text': captiontext,
        'colour': captionColour,
        'font': captionFont,
        'fontClass': fontClass
    };

    return captionData;
}