$(document).ready(function () {
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    var postEndMarker = $('#end-of-posts');
    var increment = postEndMarker.data('increment');
    var catergory = postEndMarker.data('catergory');
    var triggered = false

    $(window).on('scroll', function () {
        var scrollTop = $(window).scrollTop();
        var windowHeight = window.innerHeight;
        var elementOffsetTop = postEndMarker.offset().top;
        var elementHeight = postEndMarker.outerHeight();
        if (!triggered) {
            if ((scrollTop + windowHeight) >= elementOffsetTop && scrollTop <= (elementOffsetTop + elementHeight)) {
                triggered = true
                $.ajax({
                    type: 'POST',
                    url: '/page/load-posts/',
                    data: {
                        'increment': increment,
                        'catergory': catergory,
                        'csrfmiddlewaretoken': csrfToken
                    },
                    success: function(response) {

                        // Changing the increment tag for the next triggering of the function
                        var newIncrement = response.new_increment
                        var catergory = response.catergory
                        var newEndMarkerHtml = `
                            <div id="end-of-posts" data-increment="${newIncrement}" data-catergory="${catergory}"></div>
                        `;
                        postEndMarker.replaceWith(newEndMarkerHtml);

                        // Adding in the fetched posts
                        var postsToAppend = response.posts_to_append;
                        var fetchedPostsHtml = ``;
                        for (let i=0; i <= postsToAppend.length; i++) {
                            // if conditional for if the user las liked the post
                                // yes, have it green with white text and logo
                                // no, have it outlined in green with green text and green outlined icon

                            // for liked_by
                            var likedByDict = postsToAppend[i]['post_liked_by'];
                            for (let j=0; j <= likedByDict.length; j++) {

                            }
                            // for comments
                            var commentsDict = postsToAppend[i]['post_comments'];
                            for (let k=0; k <= commentsDict.length; k++) {
                                // if conditional for if the user las liked the comment
                                    // yes, have it green with white text and logo
                                    // no, have it outlined in green with green text and green outlined icon

                                // for replies
                                var repliesDict = commentsDict[k]['comment_replies'];
                                var repliesHtml = ``;
                                var replyHtml;
                                for (let l=0; l <= repliesDict.length; l++) {
                                    // if conditional for if the user las liked the reply
                                        // yes, have it green with white text and logo
                                        // no, have it outlined in green with green text and green outlined icon
                                    replyHtml = `
                                        <div class="card p-1">
                                            <div class="row">
                                                <div class="col">
                                                    <img class="border border-success" src="${repliesDict[l]['reply-user_pfp_url']}" alt="${repliesDict[l]['reply_username']}'s Profine Picture" style="height:20px; width: 20px; border-radius: 10px;">
                                                    <em>${repliesDict[l]['reply_username']}</em>
                                                </div>
                                            </div>
                                            <div class="row">
                                                <div class="col">
                                                    ${repliesDict[l]['reply_text']}
                                                </div>
                                                <div class="col d-flex justify-content-end">
                                                    {% if user_liked_by in subCommentData.liked__by.all %}
                                                        <button type="button" class="btn btn-success border border-success nested-comment-like-button-{{subCommentPk}} d-flex align-items-center pb-3 pt-2" data-comment-id="{{subCommentPk}}" style="height: 25px;">
                                                            <div class="row align-items-center">
                                                                <div class="col mt-1 d-flex justify-content-end">
                                                                    <i class="bi bi-hand-thumbs-up-fill" id="nested-comment-like-icon-{{subCommentPk}}" style="color: #ffffff;"></i>
                                                                </div>
                                                                <div class="col mt-4">
                                                                    <p class="text-white" id="nested-comment-like-text-{{subCommentPk}}">{{subCommentData.likes}}</p>
                                                                </div>
                                                            </div>
                                                        </button>
                                                    {% else %}
                                                        <button type="button" class="btn border border-success nested-comment-like-button-{{subCommentPk}} d-flex align-items-center pb-3 pt-2" data-comment-id="{{subCommentPk}}" style="height: 25px;">
                                                            <div class="row align-items-center">
                                                                <div class="col mt-1 d-flex justify-content-end">
                                                                    <i class="bi bi-hand-thumbs-up" id="nested-comment-like-icon-{{subCommentPk}}" style="color: #198754;"></i>
                                                                </div>
                                                                <div class="col mt-4">
                                                                    <p class="text-success" id="nested-comment-like-text-{{subCommentPk}}">{{subCommentData.likes}}</p>
                                                                </div>
                                                            </div>
                                                        </button>
                                                    {% endif %}
                                                </div>
                                            </div>
                                        </div>
                                    `;
                                }
                            }
                                
                        }
                    }
                });
            }
        }
    })
});