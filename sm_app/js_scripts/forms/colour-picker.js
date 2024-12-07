document.addEventListener("DOMContentLoaded", () => {
    // Setup variables
    const toHSL = culori.converter('hsl');

    // Initial hsl and opacity values
    let hue = 0;
    let saturation = 100;
    let lightness = 50;
    let opacity = 1;

    // Update the preview and input fields
    function updateColour (hueChange, usedSliders) {
        var hslaColour = `hsla(${hue}, ${saturation}%, ${lightness}%, ${opacity})`;
        $('colour-preview').css('background-colour', hslaColour)

        // Convert HSL to HEX and RGBA
        var rgb = culori.formatRgb(hslaColour)
        var hex = culori.formatHex(rgb)

        // Hue change logic
        if (hueChange) {
            // Get the rgb values
            if (rgb.includes('rgba')) {
                var rgbValuesString = rgb.slice(5, -1)
                var rgbValues = getRgbaFromString(rgbValuesString, alpha=false)
            } else {
                var rgbValuesString = rgb.slice(4, -1)
                var rgbValues = getRgbaFromString(rgbValuesString, alpha=false)
            }

            var r = rgbValues[0]
            var g = rgbValues[1]
            var b = rgbValues[2]

            if (r == g && r == b && g == b) { // if it is a greyscale colour
                hue = 0 // default the hue to 0
            }

            else {
                // Change the display of the saturation and lightness sliders
                var displayRGB = culori.formatRgb(`hsl(${hue}, 100%, 50%)`) 
                
                $('#saturation-slider').css('background', `linear-gradient(to right, grey, ${displayRGB})`)
                $('#lightness-slider').css('background', `linear-gradient(to right, black, ${displayRGB}, white)`)
            }
        }

        // Slider use logic
        if (!usedSliders) {
            $('#hue-slider').val() = hue;
            $('#saturation-slider').val() = saturation;
            $('#lightness-slider').val() = lightness;
        } 

        // Change the colour of the slider knobs to match the colour being represented
        var hslDisplay = `hsl(${hue}, 100%, 50%)`;
        var rgbDisplay = culori.formatRgb(hslDisplay);

        // for hue
        var hueStyleRgb = rgbDisplay;
        $('#hue-slider')[0].style.setProperty('--hue-slider-thumb-bg', hueStyleRgb);

        // for saturation
        var saturationStyleRgb = saturationOnRgb(rgbDisplay, saturation/100);
        $('#saturation-slider')[0].style.setProperty('--saturation-slider-thumb-bg', saturationStyleRgb);

        // for lightness
        var lightnessStyleRgb = culori.formatRgb(`hsl(${hue}, 100%, ${lightness}%)`);
        $('#lightness-slider')[0].style.setProperty('--lightness-slider-thumb-bg', lightnessStyleRgb);

        // for opacity
        var opacityStyleRgb = `rgb(0, 0, 0, ${opacity})`;
        $('#opacity-slider')[0].style.setProperty('--opacity-slider-thumb-bg', opacityStyleRgb);

        // Change the input values to match the new colour
        $('#hex-input').val() = hex;
        $('#rgba-input').val() = rgb;
    };

    // Event listeners for sliders
    $('#hue-slider').input(function () {
        hue = $(this).val();
        updateColour(hueChange=true, usedSliders=true);
        
    });

    $('#saturation-slider').input(function (event) {
        saturation = $(this).val();
        updateColour(hueChange=false, usedSliders=true);
    });

    $('#lightness-slider').input(function (event) {
        lightness = $(this).val();
        updateColour(hueChange=false, usedSliders=true);
    });

    $('#opacity-slider').input(function (event) {
        opacity = $(this).val() / 100; // to make the opacity between 0 and 1
        updateColour(hueChange=false, usedSliders=true);
    });

    // For the input of the text fields
    $('#hex-input').on('blur', function (event) {
        var newHexValue = event.target.value;
        console.log(newHexValue.slice(0,1))

        if (newHexValue.length == 7 && newHexValue.slice(0,1) == '#') {
            var colourHSL = toHSL(newHexValue)
            console.log(colourHSL)

            if (colourHSL['s'] === 0) {
                hue = 0
                saturation = colourHSL['s'] * 100;
                lightness = colourHSL['l'] * 100;

            } else {
                hue = colourHSL['h']
                saturation = colourHSL['s'] * 100;
                lightness = colourHSL['l'] * 100;
            }

            updateColour(hueChange=true), usedSliders=false;
        } 

    })

    $('#rgba-input').on('blur', function (event) {
        var newRgbValue = e.target.value;
        var validated;
        if (newRgbValue.includes('rgba')) {
            validated = rgbStringValidation(newRgbValue, alpha=true)
            if (validated) {
                var colourHsl = culori.formatHsl(newRgbValue)
                if (colourHsl['s'] === 0) {
                    hue = 0
                    saturation = colourHsl['s'] * 100
                    lightness = colourHsl['l'] * 100
                    opacity = colourHsl['a']
                } else {
                    hue = colourHsl['h']
                    saturation = colourHsl['s'] * 100
                    lightness = colourHsl['l'] * 100
                    opacity = colourHsl['a']
                }

            } else {
                // throw a validation error
            }

        } else {
            validated = rgbStringValidation(newRgbValue, alpha=false)
            if (validated) {
                var colourHsl = toHSL(newRgbValue)
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

    })

    // Calculates the saturation effect on a RGB colour
    function saturationOnRgb (rgb, saturation) {
        var valuesString = rgb.replace('rgb(', '').replace(')', '')


        var rgbaList = getRgbaFromString(valuesString, alpha=false)

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
    function getRgbaFromString (string, alpha) {
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

        // Return values
        if (alpha) {
            var a = string.slice(21, -1)
            if (a === '') {
                a = 1;
            }
            return [r, g, b, a]
        } else {
            return [r, g, b]
        }
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
            var rgbaValues = getRgbaFromString(stringValues, alpha=true) 

            if (rgbaValues === false) {
                checkTwo = false
            } else {
                var r = rgbaValues[0];
                var g = rgbaValues[1];
                var b = rgbaValues[2];
                var a = rgbaValues[3];
                
                if (0 <= r <= 255 && 0 <= g <= 255 && 0 <= b <= 255 && 0 <= a <= 1) {
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
            var stringValues = rgbString.slice(5, -1)
            var rgbValues = getRgbaFromString(stringValues, alpha=true) 

            if (rgbValues === false) {
                checkTwo = false
            } else {
                var r = rgbValues[0];
                var g = rgbValues[1];
                var b = rgbValues[2];
                var a = rgbValues[3];
                
                if (0 <= r <= 255 && 0 <= g <= 255 && 0 <= b <= 255 && 0 <= a <= 1) {
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

});
