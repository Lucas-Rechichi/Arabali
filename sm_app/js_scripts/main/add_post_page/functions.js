export function previewMediaFiles(mediaFilesList) {

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
                    <div class="col-2">
                        <div class="card p-1">
                            <p class="lead text-center m-0">${i + 1}</p>
                            <img class="mb-1" src="${mediaURL}" alt="Previewing media with path: ${mediaURL}, for slide: ${i}" style="width: 70px; height: 40px;">
                            <div class="row">
                                <div class="col-6">
                                    <button type="button" class="btn btn-outline-dark carousel-control-button" disabled><i class="bi bi-arrow-left-short"></i></button>
                                </div>
                                <div class="col-6">
                                    <button type="button" class="btn btn-outline-dark carousel-control-button"><i class="bi bi-arrow-right-short"></i></button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            } else if (i == 5) {
                carouselPannelHtml = `
                    <div class="col-2">
                        <div class="card p-1">
                            <p class="lead text-center m-0">${i + 1}</p>
                            <img class="mb-1" src="${mediaURL}" alt="Previewing media with path: ${mediaURL}, for slide: ${i}" style="width: 70px; height: 40px;">
                            <div class="row">
                                <div class="col-6">
                                    <button type="button" class="btn btn-outline-dark carousel-control-button"><i class="bi bi-arrow-left-short"></i></button>
                                </div>
                                <div class="col-6">
                                    <button type="button" class="btn btn-outline-dark carousel-control-button" disabled><i class="bi bi-arrow-right-short"></i></button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                carouselPannelHtml = `
                    <div class="col-2">
                        <div class="card p-1">
                            <p class="lead text-center m-0">${i + 1}</p>
                            <img class="mb-1" src="${mediaURL}" alt="Previewing media with path: ${mediaURL}, for slide: ${i}" style="width: 70px; height: 40px;">
                            <div class="row">
                                <div class="col-6">
                                    <button type="button" class="btn btn-outline-dark carousel-control-button"><i class="bi bi-arrow-left-short"></i></button>
                                </div>
                                <div class="col-6">
                                    <button type="button" class="btn btn-outline-dark carousel-control-button"><i class="bi bi-arrow-right-short"></i></button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
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
                                    <label for="caption-text" class="form-label">Caption:</label>
                                    <input type="text" id="caption-text" class="form-control" placeholder="Caption" aria-label="Caption">
                                </div>
                                <div class="col-2">
                                    <label for="caption-colour" class="form-label">Colour:</label>
                                    <div class="colour-picker-button-outer-shell">
                                        <div id="colour-picker-button-background-${i}" class="colour-picker-button-background">
                                            <div id="colour-picker-button-${i}" class="colour-picker-button" data-colour="#000000" data-caption-id="${i}"></div> 
                                        </div>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <label for="font-select-${i}" class="form-label">Font:</label>
                                    <select id="font-select-${i}" class="form-select font-select" aria-label="Default select example" data-caption-id="${i}">
                                        <option selected>Default Font</option>
                                        <option value="strong"><Strong>Strong</Strong></option>
                                        <option value="italic"><em>Italic</em></option>
                                        <option value="corier-new"><p class="p-0 m-0">Corier New</p></option>
                                        <option value="comic-sans-MS"><p class="p-0 m-0">Comic Sans MS</p></option>
                                        <option value="impact"><p class="p-0 m-0">Impact</p></option>
                                        <option value="palatino-linotype"><p class="p-0 m-0">Palatino Linotype</p></option>
                                    </select>
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

    var limitReached = false;
    // File count cannot be greater than 6, extract the files that can be accepted.
    if (mediaFiles.length > 6) {
        // Get the maximum amount of files that can be accepted
        var acceptableFilesLength = 6 - currentMediaList.length;

        for (let i=0; i < acceptableFilesLength; i++) {
            currentMediaList.push(mediaFiles[i])
            limitReached = true
        }

    } else {
        for (let i=0; i < mediaFiles.length; i++) {
            currentMediaList.push(mediaFiles[i])
            limitReached = false
        }
    }

    var response = {
        'updatedMediaList': currentMediaList,
        'limitReached': limitReached
    }

    return response
}