export function previewMediaFiles(mediaFilesList, shuffle, captionID, affectedCaptionID, direction) {

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

    // Loops though all media within the media files list
    for (let i=0; i < mediaFilesList.length; i++) {
        // Creating the media URL object
        mediaURL = URL.createObjectURL(mediaFilesList[i]);

        // Check to see if images are used for media
        if (mediaFilesList[i].type.startsWith('image/')) {
            // Creating the carousal indicatiors
            if (i == 0) {
                carouselIndicatiorHtml = `
                    <button type="button" data-bs-target="#preview-media-carousal" data-bs-slide-to="${i}" class="active" aria-current="true" aria-label="Slide ${i + 1}"></button>
                `;
            } else {
                carouselIndicatiorHtml = `
                    <button type="button" data-bs-target="#preview-media-carousal" data-bs-slide-to="${i}" aria-label="Slide ${i + 1}"></button>
                `;
            }

            // Creating the carousel cotrol elements
            if (i == 0) {
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
                                <div class="col d-flex justify-content-center"">
                                    <button type="button" class="btn btn-outline-danger carousel-pannel-delete" data-slide-id="${i}"><i class="bi bi-trash3-fill"></i></button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            } else if (i == mediaFilesList.length - 1) {
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
                                <div class="col d-flex justify-content-center"">
                                    <button type="button" class="btn btn-outline-danger carousel-pannel-delete" data-slide-id="${i}"><i class="bi bi-trash3-fill"></i></button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            } else {
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
                                <div class="col d-flex justify-content-center"">
                                    <button type="button" class="btn btn-outline-danger carousel-pannel-delete" data-slide-id="${i}"><i class="bi bi-trash3-fill"></i></button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            };

            // For when shuffling of media occurs, change captions and caption preview.
            if (shuffle) {
                // If the index lines up with the indexes involved with the shuffle
                if (i === captionID || i === affectedCaptionID) {
                    // Logic for what needs to be moved
                    if (i === captionID) {
                        captionData = getCaptionData(affectedCaptionID);
                    } else {
                        captionData = getCaptionData(captionID);
                    }
                } else {
                    captionData =  getCaptionData(i);
                };

                // HTML for the caption form
                if (captionData['text'] === 'This image represents...') {
                    captionTextHtml = `
                        <input type="text" id="caption-text-${i}" class="form-control caption-text" placeholder="Caption" aria-label="Caption" data-caption-id="${i}">
                    `;
                } else {
                    captionTextHtml = `
                        <input type="text" id="caption-text-${i}" class="form-control caption-text" placeholder="Caption" value="${captionData['text']}" aria-label="Caption" data-caption-id="${i}">
                    `;
                };

                captionColourHtml = `
                    <div id="caption-text-colour-${i}" class="colour-picker-button" data-colour="${captionData['colour']}" data-caption-id="${i}"></div> 
                `;

                // For the font selected
                switch (captionData['font']) {
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
                    <p id="carousel-caption-text-${i}" class="${captionData['fontClass']}" data-font="${captionData['font']}" data-colour="${captionData['colour']}" style="color: ${captionData['colour']}">${captionData['text']}</p>
                `;

                // Adding in font option to select
                captionFontHtml = `
                    <select id="caption-text-font-${i}" class="form-select caption-text-font" aria-label="Font Selection" data-caption-id="${i}">
                        ${optionsHtml}
                    </select>
                `;
            };

            // No shuffle
            if (!shuffle) {
                // Caption form
                captionTextHtml = `
                    <input type="text" id="caption-text-${i}" class="form-control caption-text" placeholder="Caption" aria-label="Caption" data-caption-id="${i}">
                `;
                captionColourHtml = `
                    <div id="caption-text-colour-${i}" class="colour-picker-button" data-colour="#ffffffff" data-caption-id="${i}"></div> 
                `;
                captionFontHtml = `
                    <select id="caption-text-font-${i}" class="form-select caption-text-font" aria-label="Default select example" data-caption-id="${i}">
                        <option value="default" selected>Default Font</option>
                        <option value="strong">Strong</option>
                        <option value="italic">Italic</option>
                        <option value="corier-new">Corier New</option>
                        <option value="comic-sans-ms">Comic Sans MS</option>
                        <option value="impact">Impact</option>
                        <option value="palatino-linotype">Palatino Linotype</option>
                    </select>
                `;

                // Caption preview
                carouselCaptionHtml = `
                    <p id="carousel-caption-text-${i}" class="font-default" data-font="default" data-colour="#ffffffff" style="color: #ffffffff">This image represents...</p>
                `;
            };

            // Creating the carousal slides
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
                        <div id="caption-input-${i}" class="card caption-inputs p-1">
                            <div class="row">
                                <div class="col-2">
                                    <p class="lead text-center">${i + 1}</p>
                                </div>
                                <div class="col-4">
                                    <label for="caption-text-${i}" class="form-label">Caption:</label>
                                    ${captionTextHtml}
                                    <div id="carousel-caption-invalid-${i}" aria-describedby="carousel-caption" class="invalid-feedback ms-1">
                                        <strong>Caption Text Requred</strong>
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


            // Append data to the plural variable
            carouselIndicatorsHtml += carouselIndicatiorHtml;
            carouselSlidesHtml += carouselSlideHtml;
            carouselPannelsHtml += carouselPannelHtml;
            carouselCaptionFormHtml += carouselCaptionInputHtml;
        };
    };

    var carouselPreviewHtml = `
        <div id="preview-media-carousal" class="carousel slide">
            <div class="carousel-indicators">
                ${carouselIndicatorsHtml}
            </div>
            <div class="carousel-inner">
                ${carouselSlidesHtml}
            </div>
            <button class="carousel-control-prev" type="button" data-bs-target="#preview-media-carousal" data-bs-slide="prev">
                <img class="carousel-button" src="/images/system/html_images/Carousel Arrow Left.png">
            </button>
            <button class="carousel-control-next" type="button" data-bs-target="#preview-media-carousal" data-bs-slide="next">
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


export function addMediaToList(mediaFiles, currentMediaList) {
    // Setup
    var limitReached = false;

    // File count cannot be greater than 6, extract the files that can be accepted only if they can fit.
    if (currentMediaList.length > 6) { // already full, no input, trigger on-screen error
        limitReached = true;
    } else {
        if (mediaFiles.length + currentMediaList.length > 6) { // the addition of the media files exceeds 6, input what can fit, starting by what was inputted first, trigger on-screen error
            limitReached = true;
            var maxInput = 6 - currentMediaList.length; // get how much files can fit inside the files

            for (let i=0; i < maxInput; i++ ) {
                currentMediaList.push(mediaFiles[i]) // append to current list
            }
        } else { // input all files, no on-screen error
            limitReached = false

            for (let i=0; i < mediaFiles.length; i++ ) {
                currentMediaList.push(mediaFiles[i]) // append to current list
            }
        }
    }

    // Response set
    var response = {
        'updatedMediaList': currentMediaList,
        'limitReached': limitReached
    };

    return response
}

// For the shuffling of the 
export function shuffleArray(array, movingIndex, direction) {
    // Get the item in the list, removing it from the list
    var movingItem = array.splice(movingIndex, 1)[0]; // positoning?

    // Get the moving item, removing it from the list, and add in the list with it's new order
    if (direction === 'right') {
        var affectedIndex = movingIndex;
        var affectedItem = array.splice(affectedIndex, 1)[0]; // positoning?

        array.splice(movingIndex, 0, affectedItem);
        array.splice(movingIndex + 1, 0, movingItem);
    } else {
        var affectedIndex = movingIndex - 1;
        var affectedItem = array.splice(affectedIndex, 1)[0]; // positoning?
        
        array.splice(affectedIndex, 0, movingItem);
        array.splice(affectedIndex + 1, 0, affectedItem);
    }

    // Return the newly arranged array
    return array
}

export function getCaptionData(captionID) {
    var caption = $('#carousel-caption-text-' + captionID);

    var captiontext = caption.text();
    var captionColour = caption.data('colour');
    var captionFont = caption.data('font');

    var fontClass;
    switch (captionFont) {
        case 'default':
            fontClass = 'font-default';
            break;
        
        case 'strong':
            fontClass = 'font-strong';
            break;

        case 'italic':
            fontClass = 'font-italic';
            break;

        case 'corier-new':
            fontClass = 'font-corier-new';
            break;

        case 'comic-sans-ms':
            fontClass = 'font-comic-sans-ms';
            break;

        case 'impact':
            fontClass = 'font-impact';
            break;

        case 'palatino-linotype':
            fontClass = 'font-palatino-linotype';
            break;
    }


    var captionData = {
        'text': captiontext,
        'colour': captionColour,
        'font': captionFont,
        'fontClass': fontClass
    };

    return captionData;
}