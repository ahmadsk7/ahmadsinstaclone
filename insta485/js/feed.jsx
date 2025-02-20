import React, { StrictMode, useState, useEffect } from "react";
import Post from "./post";

export default function Feed() {
    const [posts, setPosts] = useState([]); 
    const [loading, setLoading] = useState(true);  
  
    useEffect(() => {
      fetch("/api/v1/posts/", { credentials: "same-origin" })
        .then((response) => {
          if (!response.ok) {
            throw Error(response.statusText);
          }
          return response.json();
        })
        .then((data) => {
          console.log("Fetched data:", data);
          console.log("Results:", data.results);
          setPosts(data.results);  // Simply set the posts without appending
          setLoading(false);  
        })
        .catch((error) => {
          console.error("Error fetching posts:", error);
          setLoading(false);  
        });
    }, []);  
  
    if (loading) {
      return <div>Loading...</div>;
    }
  
    return (
      <div>
        {posts.map((post) => (
          <Post 
            key={post.postid} 
            url={`/api/v1/posts/${post.postid}/`}  
          />
        ))}
      </div>
    );
  }