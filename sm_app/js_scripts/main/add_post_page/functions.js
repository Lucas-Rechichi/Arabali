export function previewMediaFiles(mediaFilesList) {

    // Preparing variables 
    var mediaURL;

    // preview
    var carouselSlidesHtml = ``;
    var carouselIndicatorsHtml = ``;
    var carouselCaptionFormHtml = ``;

    var carouselSlideHtml;
    var carouselIndicatiorHtml;
    var carouselCaptionInputHtml;

    // carousel control
    var carouselPannelsHtml = ``;
    var carouselPannelHtml = ``;

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
                        <img src="${mediaURL}" class="d-block w-100"  alt="Media preview with url: ${mediaURL} and for slide: ${i + 1}" aria-current="true">
                        <div class="carousel-caption d-block d-md-block">
                            <p>This image represents...</p>
                        </div>
                    </div>
                `;
            } else {
                carouselSlideHtml = `
                    <div class="carousel-item">
                        <img src="${mediaURL}" class="d-block w-100" alt="Media preview with url: ${mediaURL} and for slide: ${i + 1}">
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
                        <img src="${mediaURL}" alt="Previewing media with path: ${mediaURL}, for slide: ${i}" style="width: 40px; height: 40px;">
                        <p class="lead text-center">${i}</p>
                        <div class="row">
                            <div class="col-6">
                                <button type="button" class="btn btn-outline-dark" disabled><i class="bi bi-arrow-left-short"></i></button>
                            </div>
                            <div class="col-6">
                                <button type="button" class="btn btn-outline-dark"><i class="bi bi-arrow-right-short"></i></button>
                            </div>
                        </div>
                    </div>
                `;
            } else if (i == 5) {
                carouselPannelHtml = `
                    <div class="col-2">
                        <img src="${mediaURL}" alt="Previewing media with path: ${mediaURL}, for slide: ${i}" style="width: 40px; height: 40px;">
                        <p class="lead text-center">${i}</p>
                        <div class="row">
                            <div class="col-6">
                                <button type="button" class="btn btn-outline-dark"><i class="bi bi-arrow-left-short"></i></button>
                            </div>
                            <div class="col-6">
                                <button type="button" class="btn btn-outline-dark" disabled><i class="bi bi-arrow-right-short"></i></button>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                carouselPannelHtml = `
                    <div class="col-2">
                        <img src="${mediaURL}" alt="Previewing media with path: ${mediaURL}, for slide: ${i}" style="width: 40px; height: 40px;">
                        <p class="lead text-center">${i}</p>
                        <div class="row">
                            <div class="col-6">
                                <button type="button" class="btn btn-outline-dark"><i class="bi bi-arrow-left-short"></i></button>
                            </div>
                            <div class="col-6">
                                <button type="button" class="btn btn-outline-dark"><i class="bi bi-arrow-right-short"></i></button>
                            </div>
                        </div>
                    </div>
                `;
            }

            // Create the carousel captions forms
            carouselCaptionInputHtml = `
                
            `;


            // Append data to the plural variable
            carouselIndicatorsHtml += carouselIndicatiorHtml;
            carouselSlidesHtml += carouselSlideHtml;
            carouselPannelsHtml += carouselPannelHtml;
        }
    }

    var carouselPreviewHtml = `
        <div id="preview-media-carousal" class="carousel slide">
            <div class="carousel-indicators">
                ${carouselIndicatorsHtml}
            </div>
            <div class="carousel-inner">
                ${carouselPannelsHtml}
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
    }

    return previewHtml
}


export function addMediaToList(mediaFiles, currentMediaList) {

    var mediaList;
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