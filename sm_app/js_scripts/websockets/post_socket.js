let postSocket;

function connectPostSocket() {
    postSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/posts/'
    );

    postSocket.onopen = function(e) {
        console.log('connected', e);
    };

    postSocket.onmessage = function(e) { // when the consumer class sends a message through
        console.log('Message coming through!');
        const data = JSON.parse(e.data); // reconfigures the data so that it can be used within our function.
        console.log(data)
        if (data.type == 'create_comment' || data.type == 'create_reply') {
            var username = data.data['username'];
            var userProfilePicture = data.data['user_pfp_url'];
            if (data.type == 'create_comment') {
                var postId = data.data['post_id'];
                var commentId = data.data['comment_id'];
                var commentText = data.data['text'];
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
                                <div class="col-8">
                                    <a href="#nested-comments-${commentId}" data-bs-toggle="collapse" class="link-secondary link-offset-2 link-underline-opacity-25 link-underline-opacity-100-hover">Replies</a>
                                </div>
                                <div class="col-4 d-flex justify-content-end">
                                    <button type="submit" id="like${commentId}" class="btn border border-success comment-like-button comment-like-button-${commentId} d-flex align-items-center p-0" data-comment-id="${commentId}" style="min-height: 30px; min-width: 50px">
                                        <p class="text-success mb-0 ms-2" id="comment-like-text-${commentId}" style="max-height: 20px;">0</p>
                                        <i class="bi bi-hand-thumbs-up ms-2" id="comment-like-icon-${commentId}" style="color: #198754;"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <div class="collapse" id="nested-comments-${commentId}">
                                        <div class="row">
                                            <div class="col-8">
                                                <div class="mb-3">
                                                    <label for="reply-text-${commentId}" class="form-label">Reply</label>
                                                    <input type="text" class="form-control" id="reply-text-${commentId}" placeholder="Add reply...">
                                                </div>   
                                            </div>
                                            <div class="col-4">
                                                <br>
                                                <button type="button" class="btn btn-success mt-2 ms-5 add-reply" data-comment-id="${commentId}">Reply</button>
                                            </div>
                                        </div>
                                        <br>
                                        <div id="replies-container-${commentId}">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                $('.comments-container-' + postId).append(newCommentHtml);
            }
            else { // 'create_reply'
                var commentId = data.data['comment_id'];
                var replyId = data.data['reply_id'];
                var replyText = data.data['text'];
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
                                <button type="submit" class="btn border border-success nested-comment-like-button nested-comment-like-button-${replyId} d-flex align-items-center pb-3 pt-2" data-comment-id="${replyId}" style="height: 25px;">
                                    <div class="row align-items-center">
                                        <div class="col mt-4">
                                            <p class="text-success" id="nested-comment-like-text-${replyId}">0</p>
                                        </div>
                                        <div class="col mt-1 d-flex justify-content-end">
                                            <i class="bi bi-hand-thumbs-up" id="nested-comment-like-icon-${replyId}" style="color: #198754;"></i>
                                        </div>
                                    </div>
                                </button>
                            </div>
                        </div>
                    </div>
                    <br>
                `;
                $('.replies-container-' + commentId).append(newReplyHtml);
            }
        }
        
    };

    postSocket.onerror = function(e) {
        console.error('WebSocket encountered an error:', e);
    };

    postSocket.onclose = function(e) {
        console.error('WebSocket closed unexpectedly:', e);
        setTimeout(connectPostSocket, reconnectionTime); // attempt a reconnection to this websocket
    };
}

connectPostSocket()