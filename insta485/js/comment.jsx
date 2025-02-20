import React from "react";
import PropTypes from "prop-types";

export default function Comment({ comment, owned, handleDeleteComment }) {
  return (
    <div className="post-description-comment">
      <div className="post-description-comment-info">
        <a href={`/users/${comment.owner}/`}>{comment.owner}</a>
        <span data-testid="comment-text">{comment.text}</span>
      </div>
      {owned && (
        <button
          type="button"
          onClick={() => handleDeleteComment(comment.commentid)}
          className="post-description-comment-delete"
          data-testid="delete-comment-button"
        >
          Delete comment
        </button>
      )}
    </div>
  );
}

Comment.propTypes = {
  comment: PropTypes.string.isRequired,
  owned: PropTypes.bool.isRequired,
  handleDeleteComment: PropTypes.func.isRequired,
};
