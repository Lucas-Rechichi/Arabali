let postSocket;

function connectPostSocket() {
    postSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/posts/'
    );

    postSocket.onopen = function(e) {
        console.log('connected', e);
    };

    postSocket.onmessage = function(e) { // when the consumer class sends a message through

        // Setup
        const data = JSON.parse(e.data); // reconfigures the data so that it can be used within our function.
        console.log(data)

        // Websocket logic
        if (data['type'] == 'create_comment' || data['type'] == 'create_reply') {

            // Getting data
            var username = data['username'];
            var userProfilePicture = data['user_pfp_url'];
            
            if (data.type == 'create_comment') {

                // Getting data
                var postID = data['post_id'];
                var commentID = data['comment_id'];
                var commentText = data['text'];

                // Package data into HTML for the new comment
                var newCommentHtml = `
                    <div class="col">
                        <div class="card p-3 m-2">
                            <div class="row">
                                <div class="col">
                                    <img class="border border-success" src="${userProfilePicture}" alt="" style="height:20px; width: 20px; border-radius: 10px;">
                                    <strong>${username}</strong>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col">
                                    ${commentText}
                                </div>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <button type="button" class="btn btn-success border border-success comment-like-button comment-like-button-${commentID} d-flex align-items-center pb-3 pt-2" data-comment-id="${commentID}" style="height: 25px;">
                                        <div class="row align-items-center">
                                            <div class="col mt-1 d-flex justify-content-end">
                                                <i class="bi bi-hand-thumbs-up-fill" id="comment-like-icon-${commentID}" style="color: #ffffff;"></i>
                                            </div>
                                            <div class="col mt-4">
                                                <p class="text-white" id="comment-like-text-${commentID}">{{comment.comment_likes}}</p>
                                            </div>
                                        </div>
                                    </button>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <div class="collapse" id="nested-comments-${commentID}">
                                        <div class="row">
                                            <div class="col-8">
                                                <div class="mb-3">
                                                    <label for="reply-text-${commentID}" class="form-label">Reply</label>
                                                    <input type="text" class="form-control" id="reply-text-${commentID}" placeholder="Add reply...">
                                                </div>   
                                            </div>
                                            <div class="col-4">
                                                <br>
                                                <button type="button" class="btn btn-success mt-2 ms-5 add-reply" data-comment-id="${commentID}">Reply</button>
                                            </div>
                                        </div>
                                        <br>
                                        <div id="replies-container-${commentID}">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                // Append to HTML
                $('#comments-container-' + postID).append(newCommentHtml);
            }
            else { // 'create_reply'

                // Getting data
                var commentID = data['comment_id'];
                var replyID = data['reply_id'];
                var replyText = data['text'];

                // Packaging data into HTML for the new reply
                var newReplyHtml = `
                    <div class="card p-1">
                        <div class="row">
                            <div class="col">
                                <img class="border border-success" src="${userProfilePicture}" alt="" style="height:20px; width: 20px; border-radius: 10px;">
                                <em>${username}</em>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col">
                                ${replyText}
                            </div>
                            <div class="col d-flex justify-content-end">
                                <button type="button" class="btn btn-success border border-success nested-comment-like-button nested-comment-like-button-${replyID} d-flex align-items-center pb-3 pt-2" data-comment-id="${replyID}" style="height: 25px;">
                                    <div class="row align-items-center">
                                        <div class="col mt-1 d-flex justify-content-end">
                                            <i class="bi bi-hand-thumbs-up-fill" id="nested-comment-like-icon-${replyID}" style="color: #ffffff;"></i>
                                        </div>
                                        <div class="col mt-4">
                                            <p class="text-white" id="nested-comment-like-text-${replyID}">{{reply.reply_likes}}</p>
                                        </div>
                                    </div>
                                </button>
                            </div>
                        </div>
                    </div>
                    <br>
                `;

                // Append to HTML
                $('#replies-container-' + commentID).append(newReplyHtml);
            }
        }
        
    };

    postSocket.onerror = function(e) {
        console.error('WebSocket encountered an error:', e);
    };

    postSocket.onclose = function(e) {
        console.error('WebSocket closed unexpectedly:', e);
        setTimeout(connectPostSocket, 5000); // attempt a reconnection to this websocket
    };
}

connectPostSocket()