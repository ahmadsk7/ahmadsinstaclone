import React, { StrictMode, useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import Feed from "./feed";

const root = createRoot(document.getElementById("reactEntry"));

root.render(
  <StrictMode>
    <Feed />
  </StrictMode>
);
