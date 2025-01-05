import { getCaptionData } from "../main/add_post_page/functions.js";

$(document).ready(function () {
    // FUNCTIONALITY

    // Setup
    let colourPickerActive = false;
    let captionID;

    // Setup variables
    const toHsl = culori.converter('hsl');

    // Initial hsl and opacity values (for white)
    let hue = 0;
    let saturation = 0;
    let lightness = 255;
    let opacity = 100;

    // Opening colour picker
    $('#post-carousel-captions-form').on('click', '.colour-picker-button', function (event) {

        // Fetch caption ID
        captionID = $(this).data('caption-id')

        // Get the colour picker popup, and display it
        var colourPicker = $('#colour-picker');

        if (colourPickerActive) {
            colourPickerActive = false
            colourPicker.fadeOut(300);

        } else {
            colourPickerActive = true

            // Get the current colour of the colour picker button, send that over to the colour picker popup
            var colourPickerButton = $('#caption-text-colour-' + captionID);
            var currentColourHsl = toHsl(colourPickerButton.data('colour'));

            if (currentColourHsl['s'] === 0 || currentColourHsl['s'] === 1) {
                hue = 0;
                saturation = scale(currentColourHsl['s'], '0-1', '0-255');
                lightness = scale(currentColourHsl['l'], '0-1', '0-255');

            } else {
                hue = currentColourHsl['h'];
                saturation = scale(currentColourHsl['s'], '0-1', '0-255');
                lightness = scale(currentColourHsl['l'], '0-1', '0-255');
            }

            updateColour(true, false);

            // Display the colour picker
            setTimeout(function () {
                colourPicker.css({
                    display: "block",
                    zIndex: 9000,
                    left: event.pageX,
                    top: event.pageY,
                });
            }, 300);
            
        }
    })

    // Function for hiding colour picker
    $(document).on('click', function (event) {
        if (!$(event.target).closest('#colour-picker, .colour-picker-button').length) { // if there is distance between the element and where you clicked
            $('#colour-picker').fadeOut(300);
            colourPickerActive = false;
        }
    });

    // COLOUR PICKER

    // Event listeners for sliders
    $('#hue-slider').on('input', function () {
        hue = $(this).val();
        updateColour(true, true);
        
    });

    $('#saturation-slider').on('input', function () {
        saturation = $(this).val();
        updateColour(false, true);
    });

    $('#lightness-slider').on('input', function () {
        lightness = $(this).val();
        updateColour(false, true);
    });

    $('#opacity-slider').on('input', function () {
        opacity = $(this).val(); // to make the opacity between 0 and 1
        updateColour(false, true);
    });

    // For the input of the text fields
    $('#hex-input').on('blur', function (event) {
        var newHexValue = event.target.value;

        if (newHexValue.length == 7 && newHexValue.slice(0,1) == '#') {
            var colourHsl = toHsl(newHexValue)

            if (colourHsl['s'] === 0 || colourHsl['s'] === 1) {
                hue = 0
                saturation = scale(colourHsl['s'], '0-1', '0-255');
                lightness = scale(colourHsl['l'], '0-1', '0-255');

            } else {
                hue = colourHsl['h'];
                saturation = scale(colourHsl['s'], '0-1', '0-255');
                lightness = scale(colourHsl['l'], '0-1', '0-255');
            }

            updateColour(true, false);

            // Validation for the input
            $(this).removeClass('is-invalid')
            $('#hex-input-invalid').css('display', 'none')
        } else {

            // Validation for the input
            $(this).addClass('is-invalid')
            $('#hex-input-invalid').css('display', 'block')
        }

    })

    $('#rgba-input').on('blur', function (event) {
        var newRgbValue = event.target.value;
        var validated;
        if (newRgbValue.includes('rgba')) {
            validated = rgbStringValidation(newRgbValue, true)
            if (validated) {
                var colourHsl = toHsl(newRgbValue)
                if (colourHsl['s'] === 0 || colourHsl['s'] === 1) {
                    hue = 0
                    saturation = scale(colourHsl['s'], '0-1', '0-255');
                    lightness = scale(colourHsl['l'], '0-1', '0-255');
                    opacity = scale(colourHsl['alpha'], '0-1', '0-100');
                } else {
                    hue = colourHsl['h']
                    saturation = scale(colourHsl['s'], '0-1', '0-255');
                    lightness = scale(colourHsl['l'], '0-1', '0-255');
                    opacity = scale(colourHsl['alpha'], '0-1', '0-100');
                }
                updateColour(true, false);

                // Validation for the input
                $(this).removeClass('is-invalid')
                $('#rgba-input-invalid').css('display', 'none')
            } else {

                // Validation for the input
                $(this).addClass('is-invalid')
                $('#rgba-input-invalid').css('display', 'block')
            }

        } else {
            validated = rgbStringValidation(newRgbValue, false)
            if (validated) {
                var colourHsl = toHsl(newRgbValue)
                if (colourHsl['s'] === 0) {
                    hue = 0
                    saturation = scale(colourHsl['s'], '0-1', '0-255');
                    lightness = scale(colourHsl['l'], '0-1', '0-255');
                } else {
                    hue = colourHsl['h']
                    saturation = scale(colourHsl['s'], '0-1', '0-255');
                    lightness = scale(colourHsl['l'], '0-1', '0-255');
                }

                updateColour(true, false)

                // Validation for the input
                $(this).removeClass('is-invalid')
                $('#rgba-input-invalid').css('display', 'none')
            } else {

                // Validation for the input
                $(this).addClass('is-invalid')
                $('#rgba-input-invalid').css('display', 'block')
            }
        }

    })

    // Save colour button
    $('#save-colour-selection').click(function () {

        // Gets the new colour and formats it in hex8 colour format
        var hslaColour = `hsla(${hue}, ${scale(saturation, '0-255', '0-100')}%, ${scale(lightness, '0-255', '0-100')}%, ${scale(opacity, '0-100', '0-1')})`;
        var colourSelected = culori.formatHex8(hslaColour)
        var newColourHtml = `<div id="caption-text-colour-${captionID}" class="colour-picker-button" data-colour="${colourSelected}" data-caption-id="${captionID}"></div>`

        // Replaces the current button so that the new one can store the new colour
        $('#caption-text-colour-' + captionID).remove();
        $('#colour-picker-button-background-' + captionID).html(newColourHtml);

        // Updates the new button visually with the new colour
        $('#caption-text-colour-' + captionID).css('background-color', colourSelected)

        // Updates the caption colour
        var captionData = getCaptionData(captionID);
        var newCaptionHtml = `
            <p id="carousel-caption-text-${captionID}" class="${captionData['fontClass']}" data-font="${captionData['font']}" data-colour="${colourSelected}" style="color: ${colourSelected}">${captionData['text']}</p>
        `;
        $('#carousel-caption-' + captionID).html(newCaptionHtml);

        // Close the colour picker menu
        $('#colour-picker').fadeOut(300);
    })

    // Cancel colour button
    $('#cancel-colour-selection').click(function () {
        colourPickerActive = false
        $('#colour-picker').fadeOut(300);
    })

    // Update the preview and input fields
    function updateColour (hueChange, usedSliders) {
        var hslaColour = `hsla(${hue}, ${scale(saturation, '0-255', '0-100')}%, ${scale(lightness, '0-255', '0-100')}%, ${scale(opacity, '0-100', '0-1')})`;
        $('#colour-preview').css('background', hslaColour)

        // Convert HSL to HEX and RGBA
        var rgb = culori.formatRgb(hslaColour)
        var hex = culori.formatHex(rgb)

        var isGreyscale = false;

        // Hue change logic
        if (hueChange) {
            // Get the rgb values
            if (rgb.includes('rgba')) {
                var rgbValuesString = rgb.slice(5, -1) // extra character
                var rgbValues = getRgbaFromString(rgbValuesString)
            } else {
                var rgbValuesString = rgb.slice(4, -1)
                var rgbValues = getRgbaFromString(rgbValuesString)
            }

            var r = rgbValues[0]
            var g = rgbValues[1]
            var b = rgbValues[2]

            if (r == g && r == b && g == b) { // if it is a greyscale colour
                isGreyscale = true
                var hueStyleColour = `hsl(${hue}, 100%, 50%)` // so that the hue slider knob can remain with it's colour dispite the saturation and lightness sliders retaining it's colour.
                hue = 0 // default the hue to 0 for the rest of the range fields

            } else {
                // Change the display of the saturation and lightness sliders
                var displayRGB = culori.formatRgb(`hsl(${hue}, 100%, 50%)`) 

                // Change the look of the saturation slider and lightness sliders to non-grayscale colours
                $('#saturation-slider').css('background', `linear-gradient(to right, grey, ${displayRGB})`)
                $('#lightness-slider').css('background', `linear-gradient(to right, black, ${displayRGB}, white)`)
            }
        }

        // Slider use logic
        if (!usedSliders) {
            $('#hue-slider').val(hue);
            $('#saturation-slider').val(saturation); 
            $('#lightness-slider').val(lightness);
            $('#opacity-slider').val(opacity);
        } 

        // Change the colour of the slider knobs to match the colour being represented
        var hslDisplayColour = `hsl(${hue}, 100%, 50%)`;
        var rgbDisplayColour = culori.formatRgb(hslDisplayColour);

        // For hue and saturation
        if (isGreyscale) {

            $('#hue-slider')[0].style.setProperty('--hue-slider-thumb-bg', hueStyleColour); // retains it's set hue

            var saturationStyleRgb = saturationOnRgb(rgbDisplayColour, scale(saturation, '0-255', '0-1'));
            $('#saturation-slider')[0].style.setProperty('--saturation-slider-thumb-bg', saturationStyleRgb); // saturation is for red colour only

        } else {
            var hueStyleColour = rgbDisplayColour;
            $('#hue-slider')[0].style.setProperty('--hue-slider-thumb-bg', hueStyleColour);

            var saturationStyleRgb = saturationOnRgb(rgbDisplayColour, scale(saturation, '0-255', '0-1'));
            $('#saturation-slider')[0].style.setProperty('--saturation-slider-thumb-bg', saturationStyleRgb);
        }

        // For lightness
        var lightnessStyleRgb = culori.formatRgb(`hsl(${hue}, 100%, ${scale(lightness, '0-255', '0-100')}%)`);
        $('#lightness-slider')[0].style.setProperty('--lightness-slider-thumb-bg', lightnessStyleRgb);

        // For opacity
        var opacityStyleRgb = `rgb(0, 0, 0, ${scale(opacity, '0-100', '0-1')})`;
        $('#opacity-slider')[0].style.setProperty('--opacity-slider-thumb-bg', opacityStyleRgb);

        // Change the input values to match the new colour
        $('#hex-input').val(hex);
        $('#rgba-input').val(rgb);
    };

    // Calculates the saturation effect on a RGB colour
    function saturationOnRgb (rgb, saturation) {

        // Get the RGB colour values
        var valuesString = rgb.replace('rgb(', '').replace(')', '')
        var rgbaList = getRgbaFromString(valuesString)

        var r = rgbaList[0];
        var g = rgbaList[1];
        var b = rgbaList[2];

        // Get the greyscale value
        var greyscaleVal = Math.round((0.3 * r) + (0.59 * g) + (0.11 * b))

        // Compute the saturated colour when the saturation has been applied
        var rPrime = Math.round(r + (greyscaleVal - r) * (1 - saturation))
        var gPrime = Math.round(g + (greyscaleVal - g) * (1 - saturation))
        var bPrime = Math.round(b + (greyscaleVal - b) * (1 - saturation))

        return `rgba(${rPrime}, ${gPrime}, ${bPrime}, 1)`

    }

    // Extracts the numbers from a string containg RGBA colours
    function getRgbaFromString (string) {
        let newString = '';
        let stringComp = 0;

        // Standadize string
        for (let i=0; i < 9; i+=3) {
            let slice = string.slice(i + stringComp, i + 3 + stringComp)
            var numbers

            if (slice.includes('  ') || slice.includes(',,') || slice.includes(', ,')) {
                return false

            } else {
                if (slice.includes(', ')) { // one digit (1)
                    numbers = slice.slice(0, 1);
                    newString += `${numbers}.000, `
                    stringComp += 0
    
                } else if (slice.includes(',')) { // two digits (11)
                    numbers = slice.slice(0, 2);
                    newString += `${numbers}.00, `
                    stringComp += 1
    
                } else { // three digits (111)
                    numbers = slice.slice(0, 3);
                    newString += `${numbers}.0, `
                    stringComp += 2
                }
            }
        }

        // Get rgb values
        var r = parseInt(newString.slice(0, 5));
        var g = parseInt(newString.slice(7, 12));
        var b = parseInt(newString.slice(14, 19));

        // For alpha
        var a = string.slice(9 + stringComp, string.length)
        if (a === '') {
            a = 1; // default alpha to 1
            var hasAlpha = false
        } else {
            var hasAlpha = true
        }

        // Return rgba values
        return [r, g, b, a, hasAlpha]
        
    }

    // Validates the string depicting RGB/RGBA values
    function rgbStringValidation (rgbString, alpha) {
        var checkOne = false;
        var checkTwo = false;
            
        // Different validation for opacity vs no opacity (alpha)
        if (alpha) {

            // Check one: to see if the wrappers are correct
            var prefix = rgbString.slice(0, 5);
            var suffix = rgbString[rgbString.length - 1]

            if (prefix === 'rgba(' && suffix === ')') {
                checkOne = true
            } else {
                checkOne = false
            }

            // Check two: to see if the values are valid
            var stringValues = rgbString.slice(5, -1)
            var rgbaValues = getRgbaFromString(stringValues) 

            if (rgbaValues === false) {
                checkTwo = false
            } else {
                var r = rgbaValues[0];
                var g = rgbaValues[1];
                var b = rgbaValues[2];
                var a = rgbaValues[3];
                var hasAlpha = rgbaValues[4];

                if (0 <= r <= 255 && 0 <= g <= 255 && 0 <= b <= 255 && 0 <= a <= 1 && hasAlpha == true) {
                    checkTwo = true
                } else {
                    checkTwo = false
                }
            }

        } else {

            // Check one: to see if the wrappers are correct
            var prefix = rgbString.slice(0, 4);
            var suffix = rgbString[rgbString.length - 1]

            if (prefix === 'rgb(' && suffix === ')') {
                checkOne = true
            } else {
                checkOne = false
            }

            // Check two: to see if the values are valid
            var stringValues = rgbString.slice(4, -1)
            var rgbValues = getRgbaFromString(stringValues) 

            if (rgbValues === false) {
                checkTwo = false
            } else {
                var r = rgbValues[0];
                var g = rgbValues[1];
                var b = rgbValues[2];
                var hasAlpha = rgbValues[4];
                
                if (0 <= r <= 255 && 0 <= g <= 255 && 0 <= b <= 255 && hasAlpha == false) {
                    checkTwo = true
                } else {
                    checkTwo = false
                }
            }

        }

        if (checkOne && checkTwo) {
            return true
        } else {
            return false
        }

    }

    // Function for scaling colour values
    function scale(colourValue, inputIntervalType, outputIntervalType) {
        if (inputIntervalType === '0-1') {
            if (outputIntervalType === '0-100') {
                var scaledColourValue = colourValue * 100
            } else if (outputIntervalType === '0-255') {  
                var scaledColourValue = colourValue * 255
            } else { // '0-359'
                var scaledColourValue = colourValue * 359
            }
        } else if (inputIntervalType === '0-100') {
            if (outputIntervalType === '0-1') {
                var scaledColourValue = colourValue / 100
            } else if (outputIntervalType === '0-255') {  
                var scaledColourValue = colourValue * 2.55 
            } else { // '0-359'
                var scaledColourValue = colourValue * 3.59
            }
        } else if (inputIntervalType === '0-255') {
            if (outputIntervalType === '0-100') {
                var scaledColourValue = colourValue / 2.55
            } else if (outputIntervalType === '0-1') {  
                var scaledColourValue = colourValue / 255 
            } else { // '0-359'
                var scaledColourValue = colourValue * 1.408
            }
        } else { // '0-359'
            if (outputIntervalType === '0-100') {
                var scaledColourValue = colourValue / 3.59
            } else if (outputIntervalType === '0-255') {  
                var scaledColourValue = colourValue / 1.408
            } else { // '0-1'
                var scaledColourValue = colourValue / 359
            }
        }

        return scaledColourValue

    
    }
})
