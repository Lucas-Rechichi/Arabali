$(document).ready(function () {
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    var postEndMarker = $('.end-of-posts');
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
                // Your JavaScript code to execute
                console.log('Target element is in view!');
                console.log('Conditional 1: ' + scrollTop + '+' +  windowHeight + '(' + (scrollTop + windowHeight) + ')' + '>='  + elementOffsetTop);
                console.log('Conditional 2: ' + scrollTop + '<='  + elementOffsetTop + '+' + elementHeight + '(' + (scrollTop + windowHeight) + ')' );
                // Perform other actions here
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
                            <div class="end-of-posts" data-increment="${newIncrement}" data-catergory="${catergory}"></div>
                        `;

                        // Add in the new end of posts marker into the HTML document
                        postEndMarker.html('')
                        $('#post-card').append(newEndMarkerHtml)

                        // Adding in the fetched posts
                        var postsToAppend = response.posts_to_append;
                        var fetchedPostsHtml = ``;
                        for (let i=0; i <= postsToAppend.length; i++) {
                            // if conditional for if the user las liked the post
                                // yes, have it green with white text and logo
                                // no, have it outlined in green with green text and green outlined icon

                            // for liked_by
                            var likedByDict = postsToAppend[i]['post_liked_by'];
                            var likedBysHtml = ``;
                            var likedByHtml;
                            for (let j=0; j <= likedByDict.length; j++) {
                                likedByHtml = `
                                    <button type="button" class="btn mb-2 d-inline-flex">
                                        <!-- adding profile pictures -->
                                        <img src="${likedByDict[j]['user_pfp_url']}"  style="width: 30px; height: 30px;">
                                        <p class="p-0 m-0 ms-2">${likedByDict[j]['username']}</p>
                                    </button>
                                `;
                                likedBysHtml += likedByHtml
                            }
                            // for comments
                            var commentsDict = postsToAppend[i]['post_comments'];
                            var commentsHtml = ``;
                            var commentHtml;
                            for (let k=0; k <= commentsDict.length; k++) {

                                // for replies
                                var repliesDict = commentsDict[k]['comment_replies'];
                                var repliesHtml = ``;
                                var replyHtml;
                                for (let l=0; l <= repliesDict.length; l++) {

                                    // different like button for replies that have been liked or not
                                    var replyLikeButtonHtml;
                                    if (repliesDict[l]['has_liked']) { // yes
                                        replyLikeButtonHtml = `
                                            <button type="button" class="btn btn-success border border-success nested-comment-like-button nested-comment-like-button-${repliesDict[l]['reply_id']} d-flex align-items-center pb-3 pt-2" data-comment-id="${repliesDict[l]['reply_id']}" style="height: 25px;">
                                                <div class="row align-items-center">
                                                    <div class="col mt-1 d-flex justify-content-end">
                                                        <i class="bi bi-hand-thumbs-up-fill" id="nested-comment-like-icon-${repliesDict[l]['reply_id']}" style="color: #ffffff;"></i>
                                                    </div>
                                                    <div class="col mt-4">
                                                        <p class="text-white" id="nested-comment-like-text-${repliesDict[l]['reply_id']}">${repliesDict[l]['reply_likes']}</p>
                                                    </div>
                                                </div>
                                            </button>
                                        `;
                                    } else { // no
                                        replyLikeButtonHtml = `
                                        <button type="button" class="btn border border-success nested-comment-like-button nested-comment-like-button-${repliesDict[l]['reply_id']} d-flex align-items-center pb-3 pt-2" data-comment-id="${repliesDict[l]['reply_id']}" style="height: 25px;">
                                            <div class="row align-items-center">
                                                <div class="col mt-1 d-flex justify-content-end">
                                                    <i class="bi bi-hand-thumbs-up" id="nested-comment-like-icon-${repliesDict[l]['reply_id']}" style="color: #198754;"></i>
                                                </div>
                                                <div class="col mt-4">
                                                    <p class="text-success" id="nested-comment-like-text-${repliesDict[l]['reply_id']}">${repliesDict[l]['reply_likes']}</p>
                                                </div>
                                            </div>
                                        </button>
                                        `;
                                    }
                                    // HTML for replies
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
                                                    ${replyLikeButtonHtml}
                                                </div>
                                            </div>
                                        </div>
                                    `;
                                    repliesHtml += replyHtml;
                                }
                                // different like button for comments that have been liked or not
                                var commentLikeButtonHtml;
                                if (commentsDict[l]['has_liked']) { // yes
                                    commentLikeButtonHtml = `
                                        <button type="button" class="btn btn-success border border-success comment-like-button comment-like-button-${commentsDict[k]['comment_id']} d-flex align-items-center pb-3 pt-2" data-comment-id="${commentsDict[k]['comment_id']}" style="height: 25px;">
                                            <div class="row align-items-center">
                                                <div class="col mt-1 d-flex justify-content-end">
                                                    <i class="bi bi-hand-thumbs-up-fill" id="comment-like-icon-${commentsDict[k]['comment_id']}" style="color: #ffffff;"></i>
                                                </div>
                                                <div class="col mt-4">
                                                    <p class="text-white" id="comment-like-text-${commentsDict[k]['comment_id']}">{${commentsDict[k]['comment_likes']}</p>
                                                </div>
                                            </div>
                                        </button>
                                    `;
                                } else { // no
                                    commentLikeButtonHtml = `
                                        <button type="button" class="btn border border-success comment-like-button comment-like-button-${commentsDict[k]['comment_id']} d-flex align-items-center pb-3 pt-2" data-comment-id="${commentsDict[k]['comment_id']}" style="height: 25px;">
                                            <div class="row align-items-center">
                                                <div class="col mt-1 d-flex justify-content-end">
                                                    <i class="bi bi-hand-thumbs-up" id="comment-like-icon-${commentsDict[k]['comment_id']} style="color: #198754;"></i>
                                                </div>
                                                <div class="col mt-4">
                                                    <p class="text-success" id="comment-like-text-${commentsDict[k]['comment_id']}">${commentsDict[k]['comment_likes']}</p>
                                                </div>
                                            </div>
                                        </button>
                                    `;
                                }
                                // put the commentsHtml into the comments container
                                commentHtml = `
                                    <div class="row">
                                        <div class="col">
                                            <div class="card p-3 m-2">
                                                <div class="row">
                                                    <div class="col">
                                                        <img class="border border-success" src="${commentsDict[k]['comment_user_pfp_url']}" alt="${commentsDict[k]['comment_username']}'s Profile Picture" style="height:20px; width: 20px; border-radius: 10px;">
                                                        <strong>${commentsDict[k]['comment_username']}</strong>
                                                    </div>
                                                </div>
                                                <div class="row">
                                                    <div class="col">
                                                        ${commentsDict[k]['comment_text']}
                                                    </div>
                                                </div>
                                                <div class="row">
                                                    <div class="col-10">
                                                        <a href="#nested-comments-${commentsDict[k]['comment_id']}" data-bs-toggle="collapse" class="link-secondary link-offset-2 link-underline-opacity-25 link-underline-opacity-100-hover">Replies</a>
                                                    </div>
                                                    <div class="col d-flex justify-content-end">
                                                        ${commentLikeButtonHtml}
                                                    </div>
                                                </div>
                                                <div class="row">
                                                    <div class="col">
                                                        <div class="collapse" id="nested-comments-${commentsDict[k]['comment_id']}">
                                                            <div class="row">
                                                                <div class="col">
                                                                    <div class="row">
                                                                        <div class="col-8">
                                                                            <div class="mb-3">
                                                                                <label for="reply-text-${commentsDict[k]['comment_id']}" class="form-label">Reply</label>
                                                                                <input type="text" class="form-control" id="reply-text-${commentsDict[k]['comment_id']}" placeholder="Add reply...">
                                                                            </div>   
                                                                        </div>
                                                                        <div class="col-4">
                                                                            <br>
                                                                            <button type="button" class="btn btn-success mt-2 ms-5 add-reply" data-comment-id="${commentsDict[k]['comment_id']}">Reply</button>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                            <br>
                                                            <div id="replies-container-${commentsDict[k]['comment_id']}">
                                                                ${repliesHtml}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>   
                                    </div>
                                `;

                                commentsHtml += commentHtml
                            }

                        }
                        setTimeout(function () {
                            triggered = false
                        }, 400)
                    }
                });
            }
        }
    })
});