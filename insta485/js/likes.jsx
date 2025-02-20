import React from "react";
import PropTypes from "prop-types";

export default function Likes({ numLikes, liked, handleLike }) {
  return (
    <div className="post-description-like">
      {numLikes} {numLikes === 1 ? "like" : "likes"}
      <button
        type="button"
        data-testid="like-unlike-button"
        onClick={handleLike}
      >
        {liked ? "unlike" : "like"}
      </button>
    </div>
  );
}

Likes.propTypes = {
  numLikes: PropTypes.number.isRequired,
  liked: PropTypes.bool.isRequired,
  handleLike: PropTypes.func.isRequired,
};
