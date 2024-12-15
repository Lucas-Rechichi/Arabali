export function previewMediaFiles(mediaFilesList, shuffle, movingSlideData, affectedSlideData, direction) {

    // Preparing variables 
    var mediaURL;

    // Preview
    var carouselSlidesHtml = ``;
    var carouselIndicatorsHtml = ``;
    
    var carouselSlideHtml;
    var carouselIndicatiorHtml;

    // Carousel control and caption form
    var carouselPannelsHtml = ``;
    var carouselCaptionFormHtml = ``;

    var carouselPannelHtml;
    var carouselCaptionInputHtml;
    var captionTextHtml;
    var captionColourHtml;
    var captionFontHtml;


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

            // Creating the carousal slides
            if (i == 0) {
                carouselSlideHtml = `
                    <div class="carousel-item active">
                        <img src="${mediaURL}" class="d-block w-100"  alt="Media preview with url: ${mediaURL} and for slide: ${i + 1}" aria-current="true" style="width: 365px; height: 200px;">
                        <div class="carousel-caption d-block d-md-block">
                            <p>This image represents...</p>
                        </div>
                    </div>
                `;
            } else {
                carouselSlideHtml = `
                    <div class="carousel-item">
                        <img src="${mediaURL}" class="d-block w-100" alt="Media preview with url: ${mediaURL} and for slide: ${i + 1}" style="width: 365px; height: 200px;">
                        <div class="carousel-caption d-block d-md-block">
                            <p>This image represents...</p>
                        </div>
                    </div>
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
            }
            // Getting data
            var movingCaptionID = movingSlideData['id'];
            var affectedCaptionID = affectedSlideData['id'];
            if (shuffle && (i === movingCaptionID || i === affectedCaptionID)) {

                // Logic for what needs to be moved
                if (i === movingCaptionID) {
                    if (direction === 'right') {
                        var relevantData = affectedSlideData
                    } else {
                        var relevantData = movingSlideData
                    }
                } else {
                    if (direction === 'right') {
                        var relevantData = movingSlideData
                    } else {
                        var relevantData = affectedSlideData
                    }
                }

                // Get the caption components from the relevant data
                var captionText = relevantData['text']
                var captionColour = relevantData['colourHex8']
                var captionFont = relevantData['font']

                captionTextHtml = `
                    <input type="text" id="caption-text-${i}" class="form-control caption-text" placeholder="Caption" value="${captionText}" aria-label="Caption" data-caption-id="${i}">
                `;

                // TODO: Update css colour when shuffled as well.
                captionColourHtml = `
                    <div id="caption-text-colour-${i}" class="colour-picker-button" data-colour="${captionColour}" data-caption-id="${i}"></div> 
                `;

                // For the font selected
                switch (captionFont) {
                    case 'default':
                        var optionsHtml = `
                            <option value="default" selected>Default Font</option>
                            <option value="strong"><Strong>Strong</Strong></option>
                            <option value="italic"><em>Italic</em></option>
                            <option value="corier-new"><p class="p-0 m-0">Corier New</p></option>
                            <option value="comic-sans-MS"><p class="p-0 m-0">Comic Sans MS</p></option>
                            <option value="impact"><p class="p-0 m-0">Impact</p></option>
                            <option value="palatino-linotype"><p class="p-0 m-0">Palatino Linotype</p></option>
                        `
                        break;

                    case 'strong':
                        var optionsHtml = `
                            <option value="default">Default Font</option>
                            <option value="strong" selected><Strong>Strong</Strong></option>
                            <option value="italic"><em>Italic</em></option>
                            <option value="corier-new"><p class="p-0 m-0">Corier New</p></option>
                            <option value="comic-sans-MS"><p class="p-0 m-0">Comic Sans MS</p></option>
                            <option value="impact"><p class="p-0 m-0">Impact</p></option>
                            <option value="palatino-linotype"><p class="p-0 m-0">Palatino Linotype</p></option>
                        `
                        break;

                    case 'italic':
                        var optionsHtml = `
                            <option value="default">Default Font</option>
                            <option value="strong"><Strong>Strong</Strong></option>
                            <option value="italic" selected><em>Italic</em></option>
                            <option value="corier-new"><p class="p-0 m-0">Corier New</p></option>
                            <option value="comic-sans-MS"><p class="p-0 m-0">Comic Sans MS</p></option>
                            <option value="impact"><p class="p-0 m-0">Impact</p></option>
                            <option value="palatino-linotype"><p class="p-0 m-0">Palatino Linotype</p></option>
                        `
                        break;

                    case 'corier-new':
                        var optionsHtml = `
                            <option value="default" selected>Default Font</option>
                            <option value="strong"><Strong>Strong</Strong></option>
                            <option value="italic"><em>Italic</em></option>
                            <option value="corier-new"><p class="p-0 m-0">Corier New</p></option>
                            <option value="comic-sans-MS"><p class="p-0 m-0">Comic Sans MS</p></option>
                            <option value="impact"><p class="p-0 m-0">Impact</p></option>
                            <option value="palatino-linotype"><p class="p-0 m-0">Palatino Linotype</p></option>
                        `
                        break;

                    case 'comic-sans-MS':
                        var optionsHtml = `
                            <option value="default">Default Font</option>
                            <option value="strong"><Strong>Strong</Strong></option>
                            <option value="italic"><em>Italic</em></option>
                            <option value="corier-new"><p class="p-0 m-0">Corier New</p></option>
                            <option value="comic-sans-MS selected"><p class="p-0 m-0">Comic Sans MS</p></option>
                            <option value="impact"><p class="p-0 m-0">Impact</p></option>
                            <option value="palatino-linotype"><p class="p-0 m-0">Palatino Linotype</p></option>
                        `
                        break;

                    case 'impact':
                        var optionsHtml = `
                            <option value="default">Default Font</option>
                            <option value="strong"><Strong>Strong</Strong></option>
                            <option value="italic"><em>Italic</em></option>
                            <option value="corier-new"><p class="p-0 m-0">Corier New</p></option>
                            <option value="comic-sans-MS"><p class="p-0 m-0">Comic Sans MS</p></option>
                            <option value="impact" selected><p class="p-0 m-0">Impact</p></option>
                            <option value="palatino-linotype"><p class="p-0 m-0">Palatino Linotype</p></option>
                        `
                        break;

                    case 'palatino-linotype':
                        var optionsHtml = `
                            <option value="default">Default Font</option>
                            <option value="strong"><Strong>Strong</Strong></option>
                            <option value="italic"><em>Italic</em></option>
                            <option value="corier-new"><p class="p-0 m-0">Corier New</p></option>
                            <option value="comic-sans-MS"><p class="p-0 m-0">Comic Sans MS</p></option>
                            <option value="impact"><p class="p-0 m-0">Impact</p></option>
                            <option value="palatino-linotype" seleced><p class="p-0 m-0">Palatino Linotype</p></option>
                        `
                        break;
                }

                // Adding in font option to select
                captionFontHtml = `
                    <select id="text-font-${i}" class="form-select font-select" aria-label="Default select example" data-caption-id="${i}">
                        ${optionsHtml}
                    </select>
                `;

                // TODO: Make the new caption layout
            } else {
                // Default to normal caption layout
            }
            
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
        }
    }

    var carouselPreviewHtml = `
        <div id="preview-media-carousal" class="carousel slide">
            <div class="carousel-indicators">
                ${carouselIndicatorsHtml}
            </div>
            <div class="carousel-inner">
                ${carouselSlidesHtml}
            </div>
            <button class="carousel-control-prev" type="button" data-bs-target="#preview-media-carousal" data-bs-slide="prev">
                <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Previous</span>
            </button>
            <button class="carousel-control-next" type="button" data-bs-target="#preview-media-carousal" data-bs-slide="next">
                <span class="carousel-control-next-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Next</span>
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
    }

    return previewHtml
}


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