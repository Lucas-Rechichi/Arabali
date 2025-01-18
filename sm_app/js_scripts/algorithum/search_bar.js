import { correctApostrphe } from "../universal/extras.js"

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
                    // Response setup
                    var recommendationsLength = response.post_recommendations.length

                    var postRecomemndationsHtml = '';
                    var userRecommendationsHtml = '';
                    var categoryRecommendationsHtml = '';

                    var postRecomemndationHtml;
                    var userRecommendationHtml;
                    var categoryRecommendationHtml;

                    var postRecommendationSet;
                    var userRecommendationSet;
                    var categoryRecommendationSet;

                    // Loops though all recommendations, appending the HTML to it's respective variable above
                    for (let i=0; i < recommendationsLength; i++) {
                        // Getting recommendation
                        postRecommendationSet = response.post_recommendations[i];
                        userRecommendationSet = response.user_recommendations[i];
                        categoryRecommendationSet = response.category_recommendations[i];

                        // Creating HTML
                        postRecomemndationHtml = `
                            <div class="row d-flex justify-content-evenly">
                                <div class="col">
                                    <img class="post-icon" src="${postRecommendationSet['post_media_url']}" alt="${correctApostrphe(postRecommendationSet['post_title'])} Cover Slide Image">
                                </div>
                                <div class="col">
                                    <p class="m-0 p-0">Post: ${postRecommendationSet['post_title']}</p>
                                </div>
                            </div>
                        `;

                        userRecommendationHtml = `
                            <div class="row d-flex justify-content-evenly">
                                <div class="col">
                                    <img class="user-icon" src="${userRecommendationSet['user_pfp_url']}" alt="${correctApostrphe(userRecommendationSet['username'])} Profile Picture">
                                </div>
                                <div class="col">
                                    <p class="m-0 p-0">User: ${userRecommendationSet['username']}</p>
                                </div>
                            </div>
                        `;

                        categoryRecommendationHtml = `
                            <div class="row d-flex justify-content-evenly">
                                <div class="col">
                                    <p class="m-0 p-0">Category: ${categoryRecommendationSet['category_name']}</p>
                                </div>
                            </div>
                        `;

                        // Appending HTML
                        postRecomemndationsHtml += postRecomemndationHtml;
                        userRecommendationsHtml += userRecommendationHtml;
                        categoryRecommendationsHtml += categoryRecommendationHtml;
                    };

                    var suggestionsHtml = `
                        <div class="container">
                            <div class="row">
                                <div class="col">
                                    <p class="lead text-center">Posts</p>
                                </div>
                            </div>
                            ${postRecomemndationsHtml}
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