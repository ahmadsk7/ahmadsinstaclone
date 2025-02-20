import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import Likes from "./likes";
import Comment from "./comment";

dayjs.extend(relativeTime);
dayjs.extend(utc);

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [created, setCreated] = useState();
  const [postid, setPostid] = useState("");
  const [likes, setLikes] = useState(0);
  const [comments, setComments] = useState([]);
  const [lognameLikesThis, setLognameLikesThis] = useState(false);
  const [commentText, setCommentText] = useState("");

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          console.log(data);
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setOwnerImgUrl(data.ownerImgUrl);
          setCreated(data.created);
          setPostid(data.postid);
          setLikes(data.likes.numLikes);
          setComments((prevComments) => [...prevComments, ...data.comments]);
          setLognameLikesThis(data.likes.lognameLikesThis);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  const handleLike = () => {
    fetch(`/api/v1/likes/?postid=${postid}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "same-origin",
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        if (lognameLikesThis && data.likeid) {
          console.log("DELETE");
          fetch(`/api/v1/likes/${data.likeid}/`, {
            method: "DELETE",
            credentials: "same-origin",
          }).then((response) => {
            if (!response.ok) throw Error(response.statusText);
            if (response.status === 204) {
              setLikes(likes - 1);
              setLognameLikesThis(false);
              return null;
            }
            return response.json();
          });
        } else {
          console.log("CREATE LIKE");
          if (!lognameLikesThis) {
            setLikes(likes + 1);
            setLognameLikesThis(true);
          }
        }
      });
  };

  const addComment = (event) => {
    event.preventDefault();
    fetch(`/api/v1/comments/?postid=${postid}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "same-origin",
      body: JSON.stringify({ text: commentText }),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        console.log("commentid:", data.commentid);
        if (data.commentid) {
          setComments((prevComments) => [...prevComments, data]);
          console.log(data);
          setCommentText("");
        }
      });
  };

  const handleCommentText = (event) => {
    event.preventDefault();
    setCommentText(event.target.value);
  };

  const deleteComment = (commentid) => {
    console.log("deleted comment");
    console.log(commentid);
    fetch(`/api/v1/comments/${commentid}`, {
      method: "DELETE",
      credentials: "same-origin",
    }).then((response) => {
      if (!response.ok) throw Error(response.statusText);
      if (response.status === 204) {
        setComments((prevComments) =>
          prevComments.filter((comment) => comment.commentid !== commentid),
        );
        return null;
      }
      return response.json();
    });
  };

  // Render post image and post owner
  return (
    <div className="post">
      <div className="post-header">
        <div className="post-header-user">
          <a href={`/users/${owner}`}>
            <img className="post-avatar" src={ownerImgUrl} alt="Owner avatar" />
          </a>
          <a href={`/users/${owner}`}>{owner}</a>
        </div>
        <a href={`/posts/${postid}/`}>{dayjs.utc(created).local().fromNow()}</a>
      </div>
      <div className="post-image">
        <img src={imgUrl} alt="post_image" />
      </div>
      <div className="post-description">
        <div className="post-description-likes">
          <Likes
            numLikes={likes}
            liked={lognameLikesThis}
            handleLike={handleLike}
          />
        </div>
        <div className="post-description-comments">
          {comments.map((comment) => (
            <Comment
              key={comment.commentid}
              comment={comment}
              owned={comment.lognameOwnsThis}
              handleDeleteComment={deleteComment}
            />
          ))}
        </div>
        <div>
          <form data-testid="comment-form" onSubmit={addComment}>
            <input
              type="text"
              onChange={handleCommentText}
              value={commentText}
            />
          </form>
        </div>
      </div>
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};
