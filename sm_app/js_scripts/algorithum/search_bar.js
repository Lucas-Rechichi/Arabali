import { correctApostrophe } from "../universal/extras.js"

$(document).ready(function () {

    // Setup
    const csrfToken = $('meta[name="csrf-token"]').attr('content');
    var suggestedCard = $('#search-suggestions-card');
    var searchSuggestions = $('#search-suggestions');


    // Event listener for recommendations
    $('#search-bar').on('focus', function () {
        if (suggestedCard.css('display') === 'none') {
            recommendations()
            suggestedCard.css('display', 'block')
        } 
    });

    $('#search-bar').on('blur', function () {
        suggestedCard.fadeOut(300)
    });

    // Event listener for realtime typing suggestions
    $('#search-bar').on('input', function () {
        var queryInput = $(this).val();

        // Logic for query input
        if (queryInput.length === 0) {

            recommendations() // show the recommendations when the input is empty
            suggestedCard.css('display', 'block')

        } else {
            $.ajax({
                type: 'POST',
                url: '/universal/search-suggestions/',
                data: {
                    'query': queryInput,
                    'csrfmiddlewaretoken': csrfToken
                },
    
                success: function(response) {
                    // Setup
                    var userSuggestionsLength = response.results_data['users'].length;
                    var categorySuggestionsLength = response.results_data['categories'].length;
    
                    var userSuggestionsHtml = '';
                    var categorySuggestionsHtml = '';
    
                    var userSuggestionHtml;
                    var categorySuggestionHtml;
    
                    var userSuggestionSet;
                    var categorySuggestionSet;
    
                    // Loops though all user suggestions, processes it into HTML
                    for (let i=0; i < userSuggestionsLength; i++) {
                        userSuggestionSet = response.results_data['users'][i];
    
                        userSuggestionHtml = `
                            <div class="container d-flex flex-wrap justify-content-center">
                                <button type="button" class="btn d-flex flex-wrap" onclick="location.href=\'/profile/${userSuggestionSet['username']}\'">
                                    <img class="user-icon align-self-start" src="${userSuggestionSet['user_pfp_url']}" alt="${correctApostrophe(userSuggestionSet['username'])} Profile Picture">
                                    <p class="mt-1 ms-3 p-0 align-self-start">User: ${userSuggestionSet['username']}</p>
                                </button>
                            </div>
                        `;
    
                        userSuggestionsHtml += userSuggestionHtml;;
                    };
    
                    // Loops though all category suggestions, processes it into HTML
                    for (let i=0; i < categorySuggestionsLength; i++) {
                        categorySuggestionSet = response.results_data['categories'][i];
    
                        categorySuggestionHtml = `
                            <div class="container d-flex flex-wrap justify-content-center">
                                <button type="button" class="btn d-flex flex-wrap" onclick="location.href=\'/page/recommended/${categorySuggestionSet['category_name']}/1\'">
                                    <i class="bi bi-filter-circle" style="font-size: 2vw; color: #198754;"></i>
                                    <p class="ms-3" style="margin-top: 12px;">Category: ${categorySuggestionSet['category_name']}</p>
                                </button>
                            </div>
                        `;
    
                        categorySuggestionsHtml += categorySuggestionHtml;
                    };

                    // Constructing the suggestions
                    var suggestionsHtml = `
                        <div class="container">
                            <div class="row">
                                <div class="col">
                                    <p class="lead text-center">Users</p>
                                </div>
                            </div>
                            ${userSuggestionsHtml}
                            <div class="row">
                                <div class="col">
                                    <p class="lead text-center">Categories</p>
                                </div>
                            </div>
                            ${categorySuggestionsHtml}
                        </div>
                    `;
    
                    searchSuggestions.html('');
                    searchSuggestions.html(suggestionsHtml);
    
                }
            });
        }

    });

    // Event lisner for pressing the search button
    $('#search-button').click(function () {
        var searchForm = $('#search-bar-form');
        var queryInput = $('#search-bar').val();

        // Query input logic
        if (queryInput.length === 0) {
            // Throw an error?
        } else {
            searchForm.attr('action', `/search/${queryInput}/1/1/1`); // For a get request to the search page

            searchForm[0].submit();
        }

    });

    // Function for presenting recommendations via ajax and DOM manipulation
    function recommendations() {
        $.ajax({
            type: 'POST',
            url: '/universal/search-recommendations/',
            data: {
                'csrfmiddlewaretoken': csrfToken
            },

            success: function(response) {
                // Response setup
                var userRecommendationsLength = response.user_recommendations.length;
                var categoryRecommendationsLength = response.category_recommendations.length;

                var userRecommendationsHtml = '';
                var categoryRecommendationsHtml = '';

                var userRecommendationHtml;
                var categoryRecommendationHtml;

                var userRecommendationSet;
                var categoryRecommendationSet;

                // Loops though all user recommendations, appending the HTML to it's respective variable above
                for (let i=0; i < userRecommendationsLength; i++) {

                    // Getting recommendation
                    userRecommendationSet = response.user_recommendations[i];

                    userRecommendationHtml = `
                        <div class="container d-flex flex-wrap justify-content-center">
                            <button type="button" class="btn d-flex flex-wrap" onclick="location.href=\'/profile/${userRecommendationSet['username']}\'">
                                <img class="user-icon align-self-start" src="${userRecommendationSet['user_pfp_url']}" alt="${correctApostrophe(userRecommendationSet['username'])} Profile Picture">
                                <p class="mt-1 ms-3 p-0 align-self-start">User: ${userRecommendationSet['username']}</p>
                            </button>
                        </div>
                    `;

                    userRecommendationsHtml += userRecommendationHtml;
                };

                // Loops though all category recommendations, appending the HTML to it's respective variable above
                for (let i=0; i < categoryRecommendationsLength; i++) {

                    // Getting recommendation
                    categoryRecommendationSet = response.category_recommendations[i];

                    categoryRecommendationHtml = `
                        <div class="container d-flex flex-wrap justify-content-center">
                            <button type="button" class="btn d-flex flex-wrap" onclick="location.href=\'/page/recommended/${categoryRecommendationSet['category_name']}/1\'">
                                <i class="bi bi-filter-circle" style="font-size: 2vw; color: #198754;"></i>
                                <p class="ms-3" style="margin-top: 12px;">Category: ${categoryRecommendationSet['category_name']}</p>
                            </button>
                        </div>
                    `;

                    categoryRecommendationsHtml += categoryRecommendationHtml;
                };

                // Constructing the recommentations
                var recommendationsHtml = `
                    <div class="container">
                        <div class="row">
                            <div class="col">
                                <p class="lead text-center">Users</p>
                            </div>
                        </div>
                        ${userRecommendationsHtml}
                        <div class="row">
                            <div class="col">
                                <p class="lead text-center">Categories</p>
                            </div>
                        </div>
                        ${categoryRecommendationsHtml}
                    </div>
                `;

                searchSuggestions.html('');
                searchSuggestions.html(recommendationsHtml);

            }
        })
    }
});