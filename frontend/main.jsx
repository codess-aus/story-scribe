/**
 * main.jsx
 * WHAT: Entry point for StoryScribe SPA (no auth mode).
 * WHY: Keeps bootstrap minimal; easy to layer auth later.
 * HOW: Renders story list + prompt fetch demo components.
 */

import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";

createRoot(document.getElementById("root")).render(<App />);