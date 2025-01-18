import { correctApostrophe } from "../universal/extras.js"

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
                            <div class="container d-flex flex-wrap justify-content-center">
                                <button type="button" class="btn d-flex flex-wrap" onclick="location.href='/posts/${postRecommendationSet['post_id']}'">
                                    <img class="post-icon" src="${postRecommendationSet['post_media_url']}" alt="${correctApostrophe(postRecommendationSet['post_title'])} Cover Slide Image">
                                    <p class="mt-2 ms-3 p-0">Post: ${postRecommendationSet['post_title']}</p>
                                </button>
                            </div>
                        `;

                        userRecommendationHtml = `
                            <div class="container d-flex flex-wrap justify-content-center" onclick="location.href='/profile/${userRecommendationSet['username']}'">
                                <button type="button" class="btn d-flex flex-wrap">
                                    <img class="user-icon align-self-start" src="${userRecommendationSet['user_pfp_url']}" alt="${correctApostrophe(userRecommendationSet['username'])} Profile Picture">
                                    <p class="mt-1 ms-3 p-0 align-self-start">User: ${userRecommendationSet['username']}</p>
                                </button>
                            </div>
                        `;

                        categoryRecommendationHtml = `
                            <div class="container d-flex flex-wrap justify-content-center">
                                <button type="button" class="btn d-flex flex-wrap" onclick="location.href='/page/recommended/${categoryRecommendationSet['category_name']}/1'">
                                    <i class="bi bi-filter-circle" style="font-size: 2vw; color: #198754;"></i>
                                    <p class="ms-3" style="margin-top: 12px;">Category: ${categoryRecommendationSet['category_name']}</p>
                                </button>
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
        suggestedCard.fadeOut(300)
    });

    // Event listener for realtime typing suggestions
    $('#search-bar').on('input', function () {
        var queryInput = $(this).val()

        $.ajax({
            type: 'POST',
            url: '/universal/search-suggestions/',
            data: {
                'query': queryInput,
                'csrfmiddlewaretoken': csrfToken
            },

            success: function(response) {

            }
        });

    });

    // Event lisner for pressing the search button
    $('#search-button').click(function () {

    });
});