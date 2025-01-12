$(document).ready(function () {
    // const csrfToken = $('meta[name="csrf-token"]').attr('content');

    // var postEndMarker = $('.end-of-posts');
    // var triggered = false

    // $(window).on('scroll', function () {
    //     // Getting the increment and catergory from the end of posts marker
    //     let increment = postEndMarker.data('increment');
    //     let catergory = postEndMarker.data('catergory');

    //     // Getting the scroll position, window height, element offset top and element height
    //     var scrollTop = $(window).scrollTop();
    //     var windowHeight = window.innerHeight;
    //     var elementOffsetTop = postEndMarker.offset().top;
    //     var elementHeight = postEndMarker.outerHeight();

    //     // Checking if the target element is in view
    //     if (!triggered) {
    //         if ((scrollTop + windowHeight) >= elementOffsetTop && scrollTop <= (elementOffsetTop + elementHeight)) {
    //             // Your JavaScript code to execute
    //             console.log('Target element is in view!');
    //             console.log('Conditional 1: ' + scrollTop + '+' +  windowHeight + '(' + (scrollTop + windowHeight) + ')' + '>='  + elementOffsetTop);
    //             console.log('Conditional 2: ' + scrollTop + '<='  + elementOffsetTop + '+' + elementHeight + '(' + (scrollTop + windowHeight) + ')' );
    //             // Perform other actions here

    //             triggered = true
    //             $.ajax({
    //                 type: 'POST',
    //                 url: '/page/load-posts/',
    //                 data: {
    //                     'increment': increment,
    //                     'catergory': catergory,
    //                     'csrfmiddlewaretoken': csrfToken
    //                 },
    //                 success: function(response) {

    //                     // Adding in the fetched posts
    //                     var postsToAppend = response.posts_to_append;
    //                     var fetchedPostsHtml = ``;
    //                     var fetchedPostHtml;
    //                     for (let i=0; i <= postsToAppend.length; i++) {

    //                         // for liked_by
    //                         var likedByDict = postsToAppend[i]['post_liked_by'];
    //                         var likedBysHtml = ``;
    //                         var likedByHtml;
    //                         for (let j=0; j <= likedByDict.length; j++) {
    //                             likedByHtml = `
    //                                 <button type="button" class="btn mb-2 d-inline-flex">
    //                                     <!-- adding profile pictures -->
    //                                     <img src="${likedByDict[j]['user_pfp_url']}"  style="width: 30px; height: 30px;">
    //                                     <p class="p-0 m-0 ms-2">${likedByDict[j]['username']}</p>
    //                                 </button>
    //                             `;
    //                             likedBysHtml += likedByHtml
    //                         }
    //                         // for comments
    //                         var commentsDict = postsToAppend[i]['post_comments'];
    //                         var commentsHtml = ``;
    //                         var commentHtml;
    //                         for (let k=0; k <= commentsDict.length; k++) {

    //                             // for replies
    //                             var repliesDict = commentsDict[k]['comment_replies'];
    //                             var repliesHtml = ``;
    //                             var replyHtml;
    //                             for (let l=0; l <= repliesDict.length; l++) {

    //                                 // different like button for replies that have been liked or not
    //                                 var replyLikeButtonHtml;
    //                                 if (repliesDict[l]['has_liked']) { // yes
    //                                     replyLikeButtonHtml = `
    //                                         <button type="button" class="btn btn-success border border-success nested-comment-like-button nested-comment-like-button-${repliesDict[l]['reply_id']} d-flex align-items-center pb-3 pt-2" data-comment-id="${repliesDict[l]['reply_id']}" style="height: 25px;">
    //                                             <div class="row align-items-center">
    //                                                 <div class="col mt-1 d-flex justify-content-end">
    //                                                     <i class="bi bi-hand-thumbs-up-fill" id="nested-comment-like-icon-${repliesDict[l]['reply_id']}" style="color: #ffffff;"></i>
    //                                                 </div>
    //                                                 <div class="col mt-4">
    //                                                     <p class="text-white" id="nested-comment-like-text-${repliesDict[l]['reply_id']}">${repliesDict[l]['reply_likes']}</p>
    //                                                 </div>
    //                                             </div>
    //                                         </button>
    //                                     `;
    //                                 } else { // no
    //                                     replyLikeButtonHtml = `
    //                                     <button type="button" class="btn border border-success nested-comment-like-button nested-comment-like-button-${repliesDict[l]['reply_id']} d-flex align-items-center pb-3 pt-2" data-comment-id="${repliesDict[l]['reply_id']}" style="height: 25px;">
    //                                         <div class="row align-items-center">
    //                                             <div class="col mt-1 d-flex justify-content-end">
    //                                                 <i class="bi bi-hand-thumbs-up" id="nested-comment-like-icon-${repliesDict[l]['reply_id']}" style="color: #198754;"></i>
    //                                             </div>
    //                                             <div class="col mt-4">
    //                                                 <p class="text-success" id="nested-comment-like-text-${repliesDict[l]['reply_id']}">${repliesDict[l]['reply_likes']}</p>
    //                                             </div>
    //                                         </div>
    //                                     </button>
    //                                     `;
    //                                 }
    //                                 // HTML for replies
    //                                 replyHtml = `
    //                                     <div class="card p-1">
    //                                         <div class="row">
    //                                             <div class="col">
    //                                                 <img class="border border-success" src="${repliesDict[l]['reply-user_pfp_url']}" alt="${repliesDict[l]['reply_username']}'s Profine Picture" style="height:20px; width: 20px; border-radius: 10px;">
    //                                                 <em>${repliesDict[l]['reply_username']}</em>
    //                                             </div>
    //                                         </div>
    //                                         <div class="row">
    //                                             <div class="col">
    //                                                 ${repliesDict[l]['reply_text']}
    //                                             </div>
    //                                             <div class="col d-flex justify-content-end">
    //                                                 ${replyLikeButtonHtml}
    //                                             </div>
    //                                         </div>
    //                                     </div>
    //                                 `;
    //                                 repliesHtml += replyHtml;
    //                             }
    //                             // different like button for comments that have been liked or not
    //                             var commentLikeButtonHtml;
    //                             if (commentsDict[l]['has_liked']) { // yes
    //                                 commentLikeButtonHtml = `
    //                                     <button type="button" class="btn btn-success border border-success comment-like-button comment-like-button-${commentsDict[k]['comment_id']} d-flex align-items-center pb-3 pt-2" data-comment-id="${commentsDict[k]['comment_id']}" style="height: 25px;">
    //                                         <div class="row align-items-center">
    //                                             <div class="col mt-1 d-flex justify-content-end">
    //                                                 <i class="bi bi-hand-thumbs-up-fill" id="comment-like-icon-${commentsDict[k]['comment_id']}" style="color: #ffffff;"></i>
    //                                             </div>
    //                                             <div class="col mt-4">
    //                                                 <p class="text-white" id="comment-like-text-${commentsDict[k]['comment_id']}">{${commentsDict[k]['comment_likes']}</p>
    //                                             </div>
    //                                         </div>
    //                                     </button>
    //                                 `;
    //                             } else { // no
    //                                 commentLikeButtonHtml = `
    //                                     <button type="button" class="btn border border-success comment-like-button comment-like-button-${commentsDict[k]['comment_id']} d-flex align-items-center pb-3 pt-2" data-comment-id="${commentsDict[k]['comment_id']}" style="height: 25px;">
    //                                         <div class="row align-items-center">
    //                                             <div class="col mt-1 d-flex justify-content-end">
    //                                                 <i class="bi bi-hand-thumbs-up" id="comment-like-icon-${commentsDict[k]['comment_id']} style="color: #198754;"></i>
    //                                             </div>
    //                                             <div class="col mt-4">
    //                                                 <p class="text-success" id="comment-like-text-${commentsDict[k]['comment_id']}">${commentsDict[k]['comment_likes']}</p>
    //                                             </div>
    //                                         </div>
    //                                     </button>
    //                                 `;
    //                             }
    //                             // put the commentsHtml into the comments container
    //                             commentHtml = `
    //                                 <div class="row">
    //                                     <div class="col">
    //                                         <div class="card p-3 m-2">
    //                                             <div class="row">
    //                                                 <div class="col">
    //                                                     <img class="border border-success" src="${commentsDict[k]['comment_user_pfp_url']}" alt="${commentsDict[k]['comment_username']}'s Profile Picture" style="height:20px; width: 20px; border-radius: 10px;">
    //                                                     <strong>${commentsDict[k]['comment_username']}</strong>
    //                                                 </div>
    //                                             </div>
    //                                             <div class="row">
    //                                                 <div class="col">
    //                                                     ${commentsDict[k]['comment_text']}
    //                                                 </div>
    //                                             </div>
    //                                             <div class="row">
    //                                                 <div class="col-10">
    //                                                     <a href="#nested-comments-${commentsDict[k]['comment_id']}" data-bs-toggle="collapse" class="link-secondary link-offset-2 link-underline-opacity-25 link-underline-opacity-100-hover">Replies</a>
    //                                                 </div>
    //                                                 <div class="col d-flex justify-content-end">
    //                                                     ${commentLikeButtonHtml}
    //                                                 </div>
    //                                             </div>
    //                                             <div class="row">
    //                                                 <div class="col">
    //                                                     <div class="collapse" id="nested-comments-${commentsDict[k]['comment_id']}">
    //                                                         <div class="row">
    //                                                             <div class="col">
    //                                                                 <div class="row">
    //                                                                     <div class="col-8">
    //                                                                         <div class="mb-3">
    //                                                                             <label for="reply-text-${commentsDict[k]['comment_id']}" class="form-label">Reply</label>
    //                                                                             <input type="text" class="form-control" id="reply-text-${commentsDict[k]['comment_id']}" placeholder="Add reply...">
    //                                                                         </div>   
    //                                                                     </div>
    //                                                                     <div class="col-4">
    //                                                                         <br>
    //                                                                         <button type="button" class="btn btn-success mt-2 ms-5 add-reply" data-comment-id="${commentsDict[k]['comment_id']}">Reply</button>
    //                                                                     </div>
    //                                                                 </div>
    //                                                             </div>
    //                                                         </div>
    //                                                         <br>
    //                                                         <div id="replies-container-${commentsDict[k]['comment_id']}">
    //                                                             ${repliesHtml}
    //                                                         </div>
    //                                                     </div>
    //                                                 </div>
    //                                             </div>
    //                                         </div>
    //                                     </div>   
    //                                 </div>
    //                             `;

    //                             commentsHtml += commentHtml
    //                         }
    //                         // different like button for comments that have been liked or not
    //                         var pageLikeButtonHtml;
    //                         var modalLikeButtonHtml;
    //                         if (postsToAppend[i]['has_liked']) { // yes
    //                             pageLikeButtonHtml = `
    //                                 <button type="submit" class="btn btn-success border border-success like-button like-button-${postsToAppend[i]['post_id']} d-flex align-items-center pb-3 pt-2" data-post-id="${postsToAppend[i]['post_id']}" style="height: 25px;">
    //                                     <div class="row align-items-center">
    //                                         <div class="col mt-1 d-flex justify-content-end">
    //                                             <i class="bi bi-hand-thumbs-up-fill" id="page-like-icon-${postsToAppend[i]['post_id']}" style="color: #ffffff;"></i>
    //                                         </div>
    //                                         <div class="col mt-4">
    //                                             <p class="text-white" id="page-like-text-${postsToAppend[i]['post_id']}">${postsToAppend[i]['post_likes']}</p>
    //                                         </div>
    //                                     </div>
    //                                 </button>
    //                             `;
    //                             modalLikeButtonHtml = `
    //                                 <button type="button" class="btn btn-success border border-success like-button like-button-${postsToAppend[i]['post_id']} d-flex align-items-center pb-3 pt-2" data-post-id="${postsToAppend[i]['post_id']}" style="height: 25px;">
    //                                     <div class="row align-items-center">
    //                                         <div class="col mt-1 d-flex justify-content-end">
    //                                             <i class="bi bi-hand-thumbs-up-fill" id="modal-like-icon-${postsToAppend[i]['post_id']}" style="color: #ffffff;"></i>
    //                                         </div>
    //                                         <div class="col mt-4">
    //                                             <p class="text-white" id="modal-like-text-${postsToAppend[i]['post_id']}">${postsToAppend[i]['post_likes']}</p>
    //                                         </div>
    //                                     </div>
    //                                 </button>
    //                             `;
    //                         } else { // no
    //                             pageLikeButtonHtml = `
    //                                 <button type="submit" class="btn border border-success like-button like-button-${postsToAppend[i]['post_id']} d-flex align-items-center pb-3 pt-2" data-post-id="${postsToAppend[i]['post_id']}" style="height: 25px;">
    //                                     <div class="row align-items-center">
    //                                         <div class="col mt-1 d-flex justify-content-end">
    //                                             <i class="bi bi-hand-thumbs-up" id="page-like-icon-${postsToAppend[i]['post_id']}" style="color: #198754;"></i>
    //                                         </div>
    //                                         <div class="col mt-4">
    //                                             <p class="text-success" id="page-like-text-${postsToAppend[i]['post_id']}">${postsToAppend[i]['post_likes']}</p>
    //                                         </div>
    //                                     </div>
    //                                 </button>
    //                             `;
    //                             modalLikeButtonHtml = `
    //                                 <button type="button" class="btn border border-success like-button like-button-${postsToAppend[i]['post_id']} d-flex align-items-center pb-3 pt-2" data-post-id="${postsToAppend[i]['post_id']}" style="height: 25px;">
    //                                     <div class="row align-items-center">
    //                                         <div class="col mt-1 d-flex justify-content-end">
    //                                             <i class="bi bi-hand-thumbs-up" id="modal-like-icon-${postsToAppend[i]['post_id']}" style="color: #198754;"></i>
    //                                         </div>
    //                                         <div class="col mt-4">
    //                                             <p class="text-success" id="modal-like-text-${postsToAppend[i]['post_id']}">${postsToAppend[i]['post_likes']}</p>
    //                                         </div>
    //                                     </div>
    //                                 </button>
    //                             `;
    //                         }

    //                         // post HTML
    //                         fetchedPostHtml = `
    //                             <div class="col-12">
    //                                 <div class="card m-5">
    //                                     <div class="row">
    //                                         <div class="col m-2">
    //                                             <button class="btn btn-light"><img src="${postsToAppend[i]['post_user_pfp_url']}", onclick='location.href = "/profile/${postsToAppend[i]['post_user_pfp_url']}"' style="width: 30px; height: 30px;"></button>
    //                                         </div>
    //                                     </div>
    //                                     <div class="row">
    //                                         <div class="col m-2">
    //                                             <h6 class="display-6">${postsToAppend[i]['post_username']}</h6>
    //                                         </div>
    //                                     </div>
    //                                     <div class="row">
    //                                         <div class="col m-2">
    //                                             <img src="${postsToAppend[i]['post_media_url']}" alt="Post: ${postsToAppend[i]['post_title']}'s Media" class="post-checkpoint post-no-${postsToAppend[i]['post_id']}" style="height: 248px; width: 100%;" data-post-id="${postsToAppend[i]['post_media_url']}">
    //                                         </div>
    //                                     </div>
    //                                     <div class="row m-2">
    //                                         <div class="col">
    //                                             <h3 class="display-6">${postsToAppend[i]['post_title']}</h3>
    //                                         </div>
    //                                     </div>
    //                                     <div class="row m-1">
    //                                         <div class="col">
    //                                             <p class="lead">${postsToAppend[i]['post_contents']}</p>
    //                                         </div>
    //                                     </div>
    //                                     <div class="row m-1">
    //                                         <div class="col-6 d-flex justify-content-start">
    //                                             <button type="button" class="btn" data-bs-target="#expand-${postsToAppend[i]['post_id']}" data-bs-toggle="modal"><i class="bi bi-three-dots"></i></button>
    //                                         </div>
    //                                         <div class="col-6 d-flex justify-content-end">
    //                                             ${pageLikeButtonHtml}
    //                                         </div>
    //                                     </div>    
    //                                 </div>
    //                                 <div id="expand-${postsToAppend[i]['post_id']}" class="modal fade">
    //                                     <div class="modal-dialog" style="max-width: 56%;">
    //                                         <div class="modal-content">
    //                                             <div class="modal-header">
    //                                                 Post
    //                                                 <button class="btn btn-close" data-bs-dismiss="modal" data-bs-target="#expand-${postsToAppend[i]['post_id']}"></button>
    //                                             </div>
    //                                             <div class="modal-body">
    //                                                 <div class="row">
    //                                                     <div class="col m-2">
    //                                                         <button class="btn btn-light" style="border-radius: 15px; width: fit-content; height: fit-content;"><img src="${postsToAppend[i]['post_user_pfp_url']}", onclick='location.href = "/profile/${postsToAppend[i]['post_username']}"' style="width: 30px; height: 30px;"></button>
    //                                                     </div>
    //                                                 </div>
    //                                                 <div class="row">
    //                                                     <div class="col m-2">
    //                                                         <h6 class="display-6">${postsToAppend[i]['post_username']}</h6>
    //                                                     </div>
    //                                                 </div>
    //                                                 <div class="row">
    //                                                     <div class="col m-2">
    //                                                         <img src="${postsToAppend[i]['post_media_url']}" alt="Post: ${postsToAppend[i]['post_title']}'s Media" style="height: 248px; width: 100%;">
    //                                                     </div>
    //                                                 </div>
    //                                                 <div class="row m-2">
    //                                                     <div class="col">
    //                                                         <h3 class="display-6">${postsToAppend[i]['post_title']}</h3>
    //                                                     </div>
    //                                                 </div>
    //                                                 <div class="row m-1">
    //                                                     <div class="col">
    //                                                         <p class="lead">${postsToAppend[i]['post_id']}</p>
    //                                                     </div>
    //                                                 </div>
    //                                                 <div class="row">
    //                                                     <div class="col-4">
    //                                                         <a class="btn btn-success" data-bs-toggle="collapse" href="#liked-by-${postsToAppend[i]['post_id']}" role="button" aria-expanded="false" aria-controls="liked-by-${postsToAppend[i]['post_id']}">Liked By</a> 
    //                                                     </div>
    //                                                     <div class="col-8 d-flex justify-content-end">
    //                                                         ${modalLikeButtonHtml}
    //                                                     </div>
    //                                                 </div>
    //                                                 <div class="row">
    //                                                     <div class="col">
    //                                                         <div class="collapse card m-1" id="liked-by-${postsToAppend[i]['post_id']}">
    //                                                             <ul class="list-group list-group-flush">
    //                                                                 ${likedBysHtml}
    //                                                             </ul>
    //                                                         </div>
    //                                                     </div>
    //                                                 </div>
    //                                                 <div class="row">
    //                                                     <div class="col text-center">
    //                                                         <p class="lead">Date Created: ${postsToAppend[i]['post_date_created']}</p>
    //                                                     </div>
    //                                                 </div>
    //                                                 <br>
    //                                                 <div class="row">
    //                                                     <div class="col">
    //                                                         <p class="lead text-center">Comments:</p>
    //                                                     </div>
    //                                                 </div>
    //                                                 <div class="row">
    //                                                     <div class="col d-flex justify-content-center">
    //                                                         <!-- Comments form -->
    //                                                         <div class="row">
    //                                                             <div class="col-8">
    //                                                                 <div class="mb-3">
    //                                                                     <label for="comment-text-${postsToAppend[i]['post_id']}" class="form-label">Comment</label>
    //                                                                     <input type="text" class="form-control" id="comment-text-${postsToAppend[i]['post_id']}" placeholder="Add Comment...">
    //                                                                 </div>   
    //                                                             </div>
    //                                                             <div class="col-4">
    //                                                                 <br>
    //                                                                 <button type="button" class="btn btn-success mt-2 ms-5 add-comment" data-post-id="${postsToAppend[i]['post_id']}">Add</button>
    //                                                             </div>
    //                                                         </div>
    //                                                     </div>
    //                                                 </div>
    //                                             </div>
    //                                             <div id="comments-container-{{posts.id}}">
    //                                                 ${commentsHtml}
    //                                             </div>
    //                                         </div>
    //                                     </div> 
    //                                 </div>
    //                             </div>
    //                         `;
    //                         fetchedPostsHtml += fetchedPostHtml
    //                     }

    //                     // Add in the fetched posts
    //                     $('#post-card').append(fetchedPostsHtml)
                        
    //                     // Changing the increment tag for the next triggering of the function
    //                     var newIncrement = response.new_increment
    //                     var catergory = response.catergory
    //                     var newEndMarkerHtml = `
    //                         <div class="end-of-posts" data-increment="${newIncrement}" data-catergory="${catergory}"></div>
    //                     `;

    //                     // Add in the new end of posts marker into the HTML document
    //                     postEndMarker.remove();
    //                     $('#post-card').append(newEndMarkerHtml);

    //                     // Delay the next trigger
    //                     setTimeout(function () {
    //                         triggered = false
    //                     }, 400)
    //                 }
    //             });
    //         }
    //     }
    // })
});