$(document).ready(function () {
    
    // FUNCTIONALITY

    // Setup
    let colourPickerActive = false;
    let captionID;

    // Opening colour picker
    $('#post-carousel-captions-form').on('click', '.colour-picker-button', function (event) {
        captionID = $(this).data('caption-id');
        if (colourPickerActive) {
            colourPickerActive = false
            $('.colour-picker').fadeOut(300);

        } else {
            colourPickerActive = true
            setTimeout(function () {
                $('.colour-picker').css({
                    display: "block",
                    position: "fixed",
                    zIndex: 10000,
                    left: event.pageX,
                    top: event.pageY,
                });
            }, 300)
        }
    })

    // For clicking outside of the colour picker
    $(document).click(function (event) {
        if (event.target.parentElement !== null) {
            if (!(event.target.parentElement.classList.contains('colour-picker-clickable')) && !(event.target.classList.contains('colour-picker-clickable'))) {
                if ($('.colour-picker').css('display') === 'block') {
                    colourPickerActive = false
                    $('.colour-picker').fadeOut(300);
                }
            }
        } else {
            if ($('.colour-picker').css('display') === 'block') {
                colourPickerActive = false
                $('.colour-picker').fadeOut(300);
            }
        }
    })


    // COLOUR PICKER
    // Setup variables
    const toHsl = culori.converter('hsl');

    // Initial hsl and opacity values (for black)
    let hue = 0;
    let saturation = 100;
    let lightness = 0;
    let opacity = 1;

    // Update the preview and input fields
    function updateColour (hueChange, usedSliders) {
        var hslaColour = `hsla(${hue}, ${saturation}%, ${lightness}%, ${opacity})`;
        $('#colour-preview').css('background', hslaColour)

        // Convert HSL to HEX and RGBA
        var rgb = culori.formatRgb(hslaColour)
        var hex = culori.formatHex(rgb)

        var isGreyscale = false;

        // Hue change logic
        if (hueChange) {
            // Get the rgb values
            if (rgb.includes('rgba')) {
                var rgbValuesString = rgb.slice(5, -1)
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
                var hueStyleRgb = `hsl(${hue}, 100%, 50%)`
                hue = 0 // default the hue to 0 for the rest of the range fields

            } else {
                // Change the display of the saturation and lightness sliders
                var displayRGB = culori.formatRgb(`hsl(${hue}, 100%, 50%)`) 

                $('#saturation-slider').css('background', `linear-gradient(to right, grey, ${displayRGB})`)
                $('#lightness-slider').css('background', `linear-gradient(to right, black, ${displayRGB}, white)`)
            }
        }

        // Slider use logic
        if (!usedSliders) {
            $('#hue-slider').val(hue);
            if (opacity == 1) {
                $('#saturation-slider').val(saturation);
            }
            $('#lightness-slider').val(lightness);
            $('#opacity-slider').val(opacity * 100);
        } 

        // Change the colour of the slider knobs to match the colour being represented
        var hslDisplay = `hsl(${hue}, 100%, 50%)`;
        var rgbDisplay = culori.formatRgb(hslDisplay);

        // for hue and saturation
        if (isGreyscale) {
            // Keep hue slider in it's original position
            $('#hue-slider')[0].style.setProperty('--hue-slider-thumb-bg', hueStyleRgb);

            if (opacity == 1) {
                var saturationStyleRgb = saturationOnRgb(rgbDisplay, saturation/100);
                $('#saturation-slider')[0].style.setProperty('--saturation-slider-thumb-bg', saturationStyleRgb);
            } 

        } else {
            var hueStyleRgb = rgbDisplay;
            $('#hue-slider')[0].style.setProperty('--hue-slider-thumb-bg', hueStyleRgb);

            var saturationStyleRgb = saturationOnRgb(rgbDisplay, saturation/100);
            $('#saturation-slider')[0].style.setProperty('--saturation-slider-thumb-bg', saturationStyleRgb);
        }
        
        // for lightness
        var lightnessStyleRgb = culori.formatRgb(`hsl(${hue}, 100%, ${lightness}%)`);
        $('#lightness-slider')[0].style.setProperty('--lightness-slider-thumb-bg', lightnessStyleRgb);

        // for opacity
        var opacityStyleRgb = `rgb(0, 0, 0, ${opacity})`;
        $('#opacity-slider')[0].style.setProperty('--opacity-slider-thumb-bg', opacityStyleRgb);

        // Change the input values to match the new colour
        $('#hex-input').val(hex);
        $('#rgba-input').val(rgb);
    };

    // Event listeners for sliders
    $('#hue-slider').on('input', function () {
        hue = $(this).val();
        updateColour(hueChange=true, usedSliders=true);
        
    });

    $('#saturation-slider').on('input', function () {
        saturation = $(this).val();
        updateColour(hueChange=false, usedSliders=true);
    });

    $('#lightness-slider').on('input', function () {
        lightness = $(this).val();
        updateColour(hueChange=false, usedSliders=true);
    });

    $('#opacity-slider').on('input', function () {
        opacity = $(this).val() / 100; // to make the opacity between 0 and 1
        updateColour(hueChange=false, usedSliders=true);
    });

    // For the input of the text fields
    $('#hex-input').on('blur', function (event) {
        var newHexValue = event.target.value;

        if (newHexValue.length == 7 && newHexValue.slice(0,1) == '#') {
            var colourHsl = toHsl(newHexValue)

            if (colourHsl['s'] === 0 || colourHsl['s'] === 1) {
                hue = 0
                saturation = colourHsl['s'] * 100;
                lightness = colourHsl['l'] * 100;

            } else {
                hue = colourHsl['h']
                saturation = colourHsl['s'] * 100;
                lightness = colourHsl['l'] * 100;
            }

            updateColour(hueChange=true, usedSliders=false);
        } 

    })

    $('#rgba-input').on('blur', function (event) {
        var newRgbValue = event.target.value;
        var validated;
        if (newRgbValue.includes('rgba')) {
            validated = rgbStringValidation(newRgbValue, alpha=true)
            if (validated) {
                var colourHsl = toHsl(newRgbValue)
                if (colourHsl['s'] === 0 || colourHsl['s'] === 1) {
                    hue = 0
                    saturation = colourHsl['s'] * 100
                    lightness = colourHsl['l'] * 100
                    opacity = colourHsl['alpha']
                } else {
                    hue = colourHsl['h']
                    saturation = colourHsl['s'] * 100
                    lightness = colourHsl['l'] * 100
                    opacity = colourHsl['alpha']
                }
                updateColour(hueChange=true, usedSliders=false);
            } else {
                // throw a validation error
            }

        } else {
            validated = rgbStringValidation(newRgbValue, alpha=false)
            if (validated) {
                var colourHsl = toHsl(newRgbValue)
                if (colourHsl['s'] === 0) {
                    hue = 0
                    saturation = colourHsl['s'] * 100
                    lightness = colourHsl['l'] * 100
                } else {
                    hue = colourHsl['h']
                    saturation = colourHsl['s'] * 100
                    lightness = colourHsl['l'] * 100
                }

                updateColour(hueChange=true, usedSliders=false)
            } else {
                // throw a validation error
            }
        }

    })

    // Save colour button
    $('#save-colour-selection').click(function () {

        // Gets the new colour and formats it in hex8 colour format
        var colourSelected = culori.formatHex8(`hsla(${hue}, ${saturation}%, ${lightness}%, ${opacity})`)
        var newColourHtml = `<div id="colour-picker-button-${captionID}" class="colour-picker-button" data-colour="${colourSelected}" data-caption-id="${captionID}"></div>`

        // Replaces the current button so that the new one can store the new colour
        $('#colour-picker-button-' + captionID).remove();
        $('#colour-picker-button-background' + captionID).html(newColourHtml);

        // Updates the new button visually with the new colour
        $('#colour-picker-button-' + captionID).css('background-color', colourSelected)

        // Close the colour picker menu
        $('.colour-picker').fadeOut(300);
    })

    // Cancel colour button
    $('#cancel-colour-selection').click(function () {
        colourPickerActive = false
        $('.colour-picker').fadeOut(300);
    })

    // Calculates the saturation effect on a RGB colour
    function saturationOnRgb (rgb, saturation) {
        var valuesString = rgb.replace('rgb(', '').replace(')', '')

        var rgbaList = getRgbaFromString(valuesString)

        var r = rgbaList[0];
        var g = rgbaList[1];
        var b = rgbaList[2];

        var greyscaleVal = Math.round((0.3 * r) + (0.59 * g) + (0.11 * b))

        var rPrime = Math.round(r + (greyscaleVal - r) * (1 - saturation))
        var gPrime = Math.round(g + (greyscaleVal - g) * (1 - saturation))
        var bPrime = Math.round(b + (greyscaleVal - b) * (1 - saturation))

        return `rgba(${rPrime}, ${gPrime}, ${bPrime}, 1)`

    }

    // Extracts the numbers from a string containg RGBA colours
    function getRgbaFromString (string) {
        string += ', ';
        let newString= '' ;
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
        var a = string.slice(9 + stringComp, string.length - 2)
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

    // Initialise the colour picker
    updateColour(hueChange=true, usedSliders=false);
    })
