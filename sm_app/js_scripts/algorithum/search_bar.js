$(document).ready(function () {

    // Setup
    const csrfToken = $('meta[name="csrf-token"]').attr('content');
    var suggestedCard = $('#search-suggestions-card');
    var searchSuggestions = $('#search-suggestions');


    // Event listener for recommendations
    $('#search-bar').on('focus', function () {
        
        if (suggestedCard.css('display') === 'none') {
            // Present suggestions via ajax and DOM manipulation

            $.ajax({
                type: 'POST',
                url: '/universal/search-recommendations/',
                data: {
                    'csrfmiddlewaretoken': csrfToken
                },

                success: function(response) {
                    var suggestionsHtml = `
                        <div class="container">
                            <div class="row">
                                <div class="col">
                                    <p class="lead text-center">Posts</p>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <p class="lead text-center">Users</p>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <p class="lead text-center">Categories</p>
                                </div>
                            </div>
                        </div>
                    `;

                    searchSuggestions.html(suggestionsHtml);

                }
            })

            suggestedCard.css('display', 'block')
        } 
    });

    $('#search-bar').on('blur', function () {
        // TODO: Add functionality for if the user clicks on a recomendation presented so that the popup doesn't close before the event lisener is triggered
        suggestedCard.fadeOut(300)
    });

    // Event listener for realtime typing suggestions
    $('#search-bar').input(function () {

    });

    // Event lisner for pressing the search button
    $('#search-button').click(function () {

    });
});