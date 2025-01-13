let player;
let currentVideoId = null;
let videoList = [];
let suggestionOverlay = null;
let suggestionsEnabled = true;
let currentNotificationTimeout;
let currentLink = "";
let isSwiping = false;
let swipeStartX = 0;
let swipeStartY = 0;
let debounceTimer; // Timer for debounce
const swipeThreshold = 50;
let loopState = 0;
let currentLoopState = 0;

// --- Now defaulting to 20% volume. ---
let current_volume = 20;
let isSeeking = false;

const socket = io();
player = document.getElementById("player"); // <audio> element
let hasUserInteracted = false;

// Cache DOM elements
const inputField = document.getElementById("youtube-link");
const actionButton = document.getElementById("action-button");

//---------------------------------------------------------------------
// 1) Video Form & Suggestions
//---------------------------------------------------------------------
document.getElementById("youtube-link").addEventListener("input", function () {
  const query = this.value;
  if (suggestionsEnabled && query.length > 2) {
    debouncedFetchSuggestions(query);
  } else {
    hideSuggestions();
    // clearInput();
  }
});

// 1) PREVIOUS button
document.getElementById("prev-btn").addEventListener("click", () => {
  // We only try if there's some currentVideoId
  if (currentVideoId) {
    socket.emit("play_previous_video");
  }
});

document.getElementById("loop-btn").addEventListener("click", () => {
  const loopBtn = document.getElementById("loop-btn");
  const icon = loopBtn.querySelector("i");

  // Cycle through loop states
  loopState = (loopState + 1) % 3;

  // Update button appearance and functionality
  switch (loopState) {
    case 0: // Loop Off
      loopBtn.className = "";
      loopBtn.title = "Loop Off";
      icon.className = "fas fa-repeat";
      player.loop = false;
      showNotification(`Loop off`, "info");
      break;
    case 1: // Loop Once
      loopBtn.className = "loop-once";
      loopBtn.title = "Loop Once";
      icon.className = "fas fa-arrow-right";
      player.loop = false;
      showNotification(`Loop Once`, "info");
      break;
    case 2: // Loop Indefinitely
      loopBtn.className = "loop-indefinite";
      loopBtn.title = "Loop Indefinitely";
      icon.className = "fas fa-infinity";
      player.loop = true;
      showNotification(`Loop Indefinitely`, "info");
      break;
  }

  // Notify backend of the current loop state
  socket.emit("update_loop_state", { loopState });
});

// Receive loop state updates from frontend
socket.on("update_loop_state", (data) => {
  currentLoopState = data.loopState;
});

// Handle song playback logic
socket.on("play_next_video", (data) => {
  const { currentVideoId } = data;

  // Determine playback behavior based on loop state
  if (currentLoopState === 1) {
    // Loop Once: Replay current video once, then proceed
    socket.emit("play_video", { video_id: currentVideoId });
    currentLoopState = 0; // Reset loop state after one repeat
  } else if (currentLoopState === 2) {
    // Loop Indefinitely: Replay current video
    socket.emit("play_video", { video_id: currentVideoId });
  } else {
    // Loop Off: Play the next song as usual
    const nextVideoId = getNextVideoId(currentVideoId); // Implement this helper function
    if (nextVideoId) {
      socket.emit("play_video", { video_id: nextVideoId });
    } else {
      socket.emit("playlist_ended");
    }
  }

  // Sync frontend with the current playback state
  socket.emit("sync_play_state", { video_id: currentVideoId, loopState: currentLoopState });
});

function getNextVideoId(currentVideoId) {
  const currentIndex = videoList.findIndex((video) => video.video_id === currentVideoId);
  if (currentIndex === -1 || currentIndex >= videoList.length - 1) {
    return null; // End of playlist
  }
  return videoList[currentIndex + 1].video_id;
}


function playNextOnce() {
  player.loop = false;
  socket.emit("play_next_video");
  player.removeEventListener("ended", playNextOnce); // Ensure it doesn't keep looping
}

// 2) NEXT button
document.getElementById("next-btn").addEventListener("click", () => {
  // We only try if there's some currentVideoId
  if (currentVideoId) {
    socket.emit("play_next_video");
  }
});

// Update the button icon based on input type (query or link)
inputField.addEventListener("input", () => {
  const value = inputField.value.trim();
  if (isYouTubeLink(value)) {
    actionButton.innerHTML = '<i class="fas fa-plus"></i>'; // Add icon
    actionButton.title = "Add Link";
  } else {
    actionButton.innerHTML = '<i class="fas fa-search"></i>'; // Search icon
    actionButton.title = "Search Query";
  }
});



// Handle form submission
document.getElementById("video-form").addEventListener("submit", function (e) {
  e.preventDefault();
  const query = inputField.value.trim();

  if (!query) return; // Do nothing if the field is empty

  if (isYouTubeLink(query)) {
    // If it's a link, add it directly
    socket.emit("new_video", { link: query });
    clearInput();
  } else {
    // If it's a query, fetch suggestions
    debouncedFetchSuggestions(query);
  }
});

// Debounce function
function debounce(func, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => func.apply(this, args), delay);
  };
}

function fetchSuggestionsFallback(query) {
  fetch(`/search_suggestions?query=${encodeURIComponent(query)}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        showError("Error fetching suggestions: " + data.error);
        return;
      }

      const suggestions = data.suggestions || [];
      if (suggestions.length > 0) {
        showSuggestions(suggestions);
      } else {
        hideSuggestions();
      }
    })
    .catch((error) => {
      console.error("Error fetching suggestions:", error);
      showError("Failed to fetch suggestions. Please try again.");
      hideSuggestions();
    });
}

// Debounced function for suggestions
const debouncedFetchSuggestions = debounce((query) => {
  if (query.length > 2) {
    if (socket.connected) {
      // Use WebSocket if connected
      socket.emit("search_videos", { query });
      socket.once("suggestions", (data) => {
        if (data.error) {
          showError("Error fetching suggestions: " + data.error);
          return;
        }
        const suggestions = data.suggestions || [];
        if (suggestions.length > 0) {
          showSuggestions(suggestions);
        } else {
          hideSuggestions();
        }
      });
    } else {
      // Fallback to fetch if WebSocket is not available
      fetchSuggestionsFallback(query);
    }
  } else {
    hideSuggestions();
  }
}, 300);

// Determine if the input is a YouTube link
function isYouTubeLink(input) {
  const linkRegex =
    /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be|music\.youtube\.com)\/(watch\?v=|playlist\?list=|.+)/i;
  return linkRegex.test(input);
}

// Show suggestions overlay
function showSuggestions(suggestions) {
  if (!suggestionOverlay) {
    suggestionOverlay = document.createElement("div");
    suggestionOverlay.id = "suggestion-overlay";
    document.body.appendChild(suggestionOverlay);
  }
  suggestionOverlay.innerHTML = "";
  suggestions.forEach((item) => {
    const suggestionItem = document.createElement("div");
    suggestionItem.className = "suggestion-item";
    suggestionItem.innerHTML = `
      <div class="suggestion-thumbnail">
        <img src="${item.thumbnail}" alt="${item.title}">
      </div>
      <div class="suggestion-info">
        <p class="suggestion-title">${item.title}</p>
        <p class="suggestion-artist">${item.channel}</p>
      </div>
    `;
    suggestionItem.onclick = () => selectSuggestion(item.videoId, item.title);
    suggestionOverlay.appendChild(suggestionItem);
  });
  positionSuggestions();
  suggestionOverlay.style.display = "block";

  // Add event listeners to detect clicks or touches outside the overlay
  setTimeout(() => {
    document.addEventListener("click", handleOutsideClick);
    document.addEventListener("touchstart", handleOutsideTouch);
  }, 0);
}


function handleOutsideClick(event) {
  const contextMenu = document.getElementById("context-menu");
  const inputField = document.getElementById("youtube-link");

  // Check and hide context menu
  if (contextMenu && !contextMenu.contains(event.target)) {
    hideContextMenu();
  }

  // Check and hide suggestions overlay
  if (
    suggestionOverlay &&
    suggestionOverlay.style.display === "block" &&
    !suggestionOverlay.contains(event.target) &&
    event.target !== inputField
  ) {
    hideSuggestions();
  }
}

function handleOutsideTouch(event) {
  const contextMenu = document.getElementById("context-menu");
  const inputField = document.getElementById("youtube-link");

  // Check and hide context menu
  if (contextMenu && !contextMenu.contains(event.target)) {
    hideContextMenu();
  }

  // Check and hide suggestions overlay
  if (
    suggestionOverlay &&
    suggestionOverlay.style.display === "block" &&
    !suggestionOverlay.contains(event.target) &&
    event.target !== inputField
  ) {
    hideSuggestions();
  }
}

// Handle suggestion selection
function selectSuggestion(videoId, title) {
  inputField.value = ""; // Clear the input field
  hideSuggestions();
  clearInput();
  const link = `https://www.youtube.com/watch?v=${videoId}`;
  socket.emit("new_video", { link });
}

// Hide suggestions overlay (removes event listeners too)
function hideSuggestions() {
  if (suggestionOverlay) {
    suggestionOverlay.style.display = "none";
    document.removeEventListener("click", handleOutsideClick);
    document.removeEventListener("touchstart", handleOutsideTouch);
  }
}

// Position suggestions overlay
function positionSuggestions() {
  const rect = inputField.getBoundingClientRect();
  if (!suggestionOverlay) return;
  suggestionOverlay.style.left = `${rect.left}px`;
  suggestionOverlay.style.top = `${rect.bottom + window.scrollY}px`;
  suggestionOverlay.style.width = `${rect.width}px`;
}

function clearInput() {
  inputField.value = ""; // Clear the text in the field
  inputField.dispatchEvent(new Event("input")); // Trigger the input event to update the button icon
  hideSuggestions();
}

function showError(message) {
  if (!suggestionOverlay) {
    suggestionOverlay = document.createElement("div");
    suggestionOverlay.id = "suggestion-overlay";
    document.body.appendChild(suggestionOverlay);
  }
  suggestionOverlay.innerHTML = `<div class="error-message">${message}</div>`;
  positionSuggestions();
  suggestionOverlay.style.display = "block";
}

// function selectSuggestion(videoId, title) {
//   document.getElementById("youtube-link").value = title;
//   hideSuggestions();
//   currentLink = `https://www.youtube.com/watch?v=${videoId}`;
//   socket.emit("new_video", { link: currentLink });
// }

//---------------------------------------------------------------------
// 2) Socket.IO Event Handlers
//---------------------------------------------------------------------
socket.on("update_playlist", function (data) {
  console.log("Received data:", data);

  const alreadyExists = videoList.some((video) => video.video_id === data.video_id);

  if (alreadyExists) {
    // If it already exists, update its position in the list
    videoList = videoList.filter((video) => video.video_id !== data.video_id);
    videoList.push(data);
    updatePlaylist(videoList);

    // Notify if moved to the bottom
    showNotification(`'${data.title}' is already in the playlist. It has been moved to the bottom.`, "info");
  } else {
    // Add the new video
    videoList.push(data);
    addVideoToList(data);

    // Check if this was an undo action
    if (data.isUndo) {
      showNotification("Undo successful. Song added back to playlist.", "success");
    } else {
      showNotification(`'${data.title}' has been successfully added to the playlist.`, "success");
    }
  }
});

socket.on("update_list", function (data) {
  videoList = data;
  updatePlaylist(videoList); // Re-render the updated playlist
  highlightCurrentVideo(currentVideoId); // Highlight the currently playing song
});

socket.on("play_video", async function (data) {
  currentVideoId = data.video_id;

  // Find the song details based on the current video ID
  const songDetails = videoList.find((video) => video.video_id === currentVideoId);

  // Construct the notification message
  const songTitle = songDetails?.title || "Unknown Title";
  const artist = songDetails?.artist || songDetails?.creator || "Unknown Artist";
  const notificationMessage = `Playing: ${songTitle} by ${artist}`;

  // Show the notification
  showNotification(notificationMessage, "info");

  // Play the song
  await loadAndPlayVideo(currentVideoId);
});


socket.on("toggle_play_pause", (data) => {
  if (data.state === "playing") {
    player.play().catch((err) => {
      console.warn("Autoplay blocked or first interaction not done:", err);
      showNotification(
        "Please click on this page to allow audio, then press play again."
      );
    });
    showNotification("Playing");
  } else {
    player.pause();
    showNotification("Paused");
  }
  updatePlayPauseButton(data.state);
});

socket.on("sync_play_state", (data) => {
  currentVideoId = data.video_id;
  if (data.state === "playing") {
    player.play().catch((err) => {
      console.warn("Autoplay blocked or first interaction not done:", err);
      showNotification(
        "Please click on this page to allow audio, then press play again."
      );
    });
    showNotification("Playing");
  } else {
    player.pause();
    showNotification("Paused");
  }
  updatePlayPauseButton(data.state);
});

socket.on("update_volume", (data) => {
  if (player) {
    player.volume = data.volume / 100;
  }
  document.getElementById("volume-slider").value = data.volume;
  showVolumeOverlay(data.volume);
});

socket.on("current_video", (data) => {
  currentVideoId = data.video_id;
  updateCurrentTitle(currentVideoId);
  highlightCurrentVideo(currentVideoId);
  updatePlayPauseButton(data.state);
  if (player) {
    player.volume = data.volume / 100;
    document.getElementById("volume-slider").value = data.volume;
  }
});

socket.on("progress_update", function (data) {
  if (!isSeeking && player && !player.paused) {
    const { currentTime, duration } = data;
    const progressPercent = (currentTime / duration) * 100;
    document.getElementById(
      "progress-bar-inner"
    ).style.width = `${progressPercent}%`;
  }
});

socket.on("seek_video", function (data) {
  if (currentVideoId === data.video_id && player) {
    player.currentTime = data.time;
  }
});

socket.on("playlist_shuffled", () => {
  showNotification("Playlist Shuffled");
});

//---------------------------------------------------------------------
// 3) Audio Playback (HTML5 Audio)
//---------------------------------------------------------------------
async function loadAndPlayVideo(videoId) {
  const videoInfo = videoList.find((v) => v.video_id === videoId);
  if (!videoInfo) {
    console.log("Audio not found in playlist.");
    return;
  }

  let streamUrl = "";
  try {
    const response = await fetch("/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: `https://www.youtube.com/watch?v=${videoId}`,
      }),
    });
    const data = await response.json();

    if (data.error) {
      console.error("Error getting stream URL:", data.error);
      showNotification("Failed to load audio stream.");
      return;
    }
    streamUrl = data.stream_url;
  } catch (err) {
    console.error("Error fetching /stream:", err);
    showNotification("Failed to fetch stream.");
    return;
  }

  player.src = streamUrl;
  updateCurrentTitle(videoId);
  highlightCurrentVideo(videoId);

  try {
    await player.play();
    updatePlayPauseButton("playing");
  } catch (err) {
    console.warn("Autoplay blocked or first interaction required:", err);
    showNotification(
      "Please click on this page (e.g. press Play button here) to allow audio."
    );
    updatePlayPauseButton("paused");
  }
}

if (player) {
  // If user manually interacts with the audio on PC, we consider that a user gesture
  player.addEventListener("play", () => {
    hasUserInteracted = true;
    socket.emit("sync_play_state", {
      video_id: currentVideoId,
      state: "playing",
    });
    updatePlayPauseButton("playing");
  });

  player.addEventListener("pause", () => {
    if (hasUserInteracted) {
      socket.emit("sync_play_state", {
        video_id: currentVideoId,
        state: "paused",
      });
    }
    updatePlayPauseButton("paused");
  });

  player.addEventListener("timeupdate", () => {
    if (!isSeeking) {
      const duration = player.duration || 0;
      const currentTime = player.currentTime;
      if (duration > 0) {
        const progressPercent = (currentTime / duration) * 100;
        document.getElementById(
          "progress-bar-inner"
        ).style.width = `${progressPercent}%`;
        socket.emit("progress_update", { currentTime, duration });
      }
    }
  });

  player.addEventListener("ended", () => {
    socket.emit("play_next_video");
  });
}

//---------------------------------------------------------------------
// 4) Playlist-Related
//---------------------------------------------------------------------
function addVideoToList(video) {
  const playlist = document.getElementById("playlist");
  const videoItem = document.createElement("div");
  videoItem.className = `video-item ${video.played ? "played" : ""}`;
  videoItem.setAttribute("data-id", video.id);
  videoItem.setAttribute("data-video-id", video.video_id);
  videoItem.innerHTML = `
    <img class="drag-area" src="${video.thumbnail}" alt="${video.title}">
    <div class="video-info">
      <p class="video-title"><strong>${video.title}</strong></p>
      <p class="video-artist">${
        video.artist ? video.artist : video.creator
      }</p>
      ${video.album ? `<p class="video-meta">Album: ${video.album}</p>` : ""}
    </div>
  `;
  playlist.appendChild(videoItem);
  attachClickListener(videoItem);
  attachSwipeListener(videoItem);
}

function updatePlaylist(videos) {
  const playlist = document.getElementById("playlist");
  playlist.innerHTML = "";
  videos.forEach((video) => addVideoToList(video));
  highlightCurrentVideo(currentVideoId);
}

function attachClickListener(videoItem) {
  videoItem.addEventListener("click", function () {
    const videoId = videoItem.getAttribute("data-video-id");
    socket.emit("play_video", { video_id: videoId });
  });
}

function attachSwipeListener(videoItem) {
  videoItem.addEventListener("touchstart", function (e) {
    if (videoItem.classList.contains("playing")) {
      isSwiping = false;
      return;
    }
    isSwiping = true;
    swipeStartX = e.touches[0].clientX;
    swipeStartY = e.touches[0].clientY;
    videoItem.style.transition = "none";
  });

  videoItem.addEventListener("touchmove", function (e) {
    if (!isSwiping) return;
    const swipeEndX = e.touches[0].clientX;
    const swipeEndY = e.touches[0].clientY;
    const deltaX = swipeEndX - swipeStartX;
    const deltaY = swipeEndY - swipeStartY;
    if (
      Math.abs(deltaX) > Math.abs(deltaY) &&
      Math.abs(deltaX) > swipeThreshold
    ) {
      e.preventDefault();
      videoItem.style.transform = `translateX(${deltaX}px)`;
    }
  });

  videoItem.addEventListener("touchend", function (e) {
    if (!isSwiping) return;
    const swipeEndX = e.changedTouches[0].clientX;
    const deltaX = swipeEndX - swipeStartX;
    isSwiping = false;
    if (Math.abs(deltaX) > swipeThreshold) {
      if (deltaX < 0) {
        videoItem.style.transition =
          "transform 0.3s ease-out, background-color 0.3s ease-out";
        videoItem.style.transform = "translateX(-100%)";
        videoItem.style.backgroundColor = "red";
        setTimeout(() => {
          socket.emit("remove_video", {
            id: parseInt(videoItem.getAttribute("data-id")),
          });
          videoItem.remove();
          showNotification("Audio Removed");
        }, 300);
      } else {
        videoItem.style.transition = "transform 0.3s ease-out";
        videoItem.style.transform = "translateX(0)";
      }
    } else {
      videoItem.style.transition = "transform 0.3s ease-out";
      videoItem.style.transform = "translateX(0)";
    }
  });

  videoItem.addEventListener("touchcancel", function () {
    isSwiping = false;
    videoItem.style.transform = "translateX(0)";
  });
}

const sortable = new Sortable(document.getElementById("playlist"), {
  animation: 150,
  handle: ".drag-area",
  onStart: function (evt) {
    evt.item.classList.add("dragging");
  },
  onEnd: function (evt) {
    evt.item.classList.remove("dragging");
    const order = Array.from(evt.to.children).map((item) =>
      parseInt(item.getAttribute("data-id"))
    );
    socket.emit("reorder_videos", { order });
    highlightCurrentVideo(currentVideoId);
  },
});

//---------------------------------------------------------------------
// 5) Progress, Play/Pause, Shuffle, Volume
//---------------------------------------------------------------------
document.getElementById("play-pause-btn").addEventListener("click", () => {
  if (player) {
    if (player.paused) {
      player.play().catch((err) => {
        console.warn("Autoplay blocked or no user gesture yet:", err);
        showNotification(
          "Click on this page to allow playback, then play again."
        );
      });
      showNotification("Playing");
      socket.emit("play_pause");
      socket.emit("request_current_video");
    } else {
      player.pause();
      showNotification("Paused");
      socket.emit("play_pause");
      socket.emit("request_current_video");
    }
  } else {
    socket.emit("play_pause");
    socket.emit("request_current_video");
  }
});

document.getElementById("shuffle-btn").addEventListener("click", () => {
  socket.emit("shuffle_playlist");
});

/**
 *  Setting the player volume to 0.2 initially to match the UI slider,
 *  which we will also set to 20 on load.
 */
// document.getElementById("volume-slider").addEventListener("input", function () {
//   const volume = this.value;
//   current_volume = volume;
//   if (player) {
//     player.volume = volume / 100;
//   }
//   socket.emit("change_volume", { volume });
//   showVolumeOverlay(volume);
// });

//---------------------------------------------------------------------
// 6) Seek Handling
//---------------------------------------------------------------------
function updateProgressBar() {
  if (player) {
    const currentTime = player.currentTime;
    const duration = player.duration;
    if (!isNaN(duration) && duration > 0) {
      socket.emit("progress_update", { currentTime, duration });
    }
  }
}
setInterval(updateProgressBar, 1000);

//---------------------------------------------------------------------
// 7) Dark Mode & Suggestions Toggle
//---------------------------------------------------------------------
document.getElementById("dark-mode-toggle").addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");
  const icon = document.getElementById("dark-mode-toggle").querySelector("i");
  if (document.body.classList.contains("dark-mode")) {
    icon.classList.remove("fa-moon");
    icon.classList.add("fa-sun");
    showNotification("Dark Mode Enabled");
  } else {
    icon.classList.remove("fa-sun");
    icon.classList.add("fa-moon");
    showNotification("Light Mode Enabled");
  }
  localStorage.setItem(
    "darkMode",
    document.body.classList.contains("dark-mode")
  );
});

document
  .getElementById("suggestions-toggle")
  .addEventListener("change", (event) => {
    suggestionsEnabled = event.target.checked;
    localStorage.setItem("suggestionsEnabled", suggestionsEnabled);
    showNotification(suggestionsEnabled ? "Suggestions On" : "Suggestions Off");
  });

window.addEventListener("load", () => {
  const isDarkMode = localStorage.getItem("darkMode") === "true";
  suggestionsEnabled = localStorage.getItem("suggestionsEnabled") === "true";

  // Set the UI slider to 20% and the player volume to 0.2 on load
  document.getElementById("volume-slider").value = 20;
  if (player) {
    player.volume = 0.2;
  }

  if (isDarkMode) {
    document.body.classList.add("dark-mode");
    document
      .getElementById("dark-mode-toggle")
      .querySelector("i")
      .classList.replace("fa-moon", "fa-sun");
  }
  document
    .getElementById("suggestions-toggle")
    .addEventListener("change", (event) => {
      // Ensure suggestions are always enabled
      if (!event.target.checked) {
        event.target.checked = true; // Force the toggle to stay on
        suggestionsEnabled = true;
        showNotification("Suggestions cannot be disabled.");
      } else {
        suggestionsEnabled = true;
        showNotification("Suggestions are enabled.");
      }
      localStorage.setItem("suggestionsEnabled", true); // Always save as enabled
    });
  socket.emit("request_current_video");
});

//---------------------------------------------------------------------
// 8) Utility Functions
//---------------------------------------------------------------------
function highlightCurrentVideo(videoId) {
  document.querySelectorAll(".video-item").forEach((item) => {
    item.classList.toggle(
      "playing",
      item.getAttribute("data-video-id") === videoId
    );
  });
}

function updateCurrentTitle(videoId) {
  const currentItem = Array.from(document.querySelectorAll(".video-item")).find(
    (item) => item.getAttribute("data-video-id") === videoId
  );
  if (currentItem) {
    const currentTitle = currentItem.querySelector(".video-info p").innerText;
    document.getElementById("current-title").innerText = currentTitle;
  } else {
    document.getElementById("current-title").innerText = "Now Playing: None";
  }
}

function updatePlayPauseButton(state) {
  const playPauseBtn = document.getElementById("play-pause-btn");
  if (state === "playing") {
    playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
  } else {
    playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
  }
}

function formatDuration(seconds) {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hrs ? hrs + ":" : ""}${mins}:${secs < 10 ? "0" : ""}${secs}`;
}

function showNotification(message, type = "info", undo = false, link = null) {
  let notification = document.getElementById("notification-overlay");
  if (!notification) {
      notification = document.createElement("div");
      notification.id = "notification-overlay";
      document.body.appendChild(notification);
  }

  // Style notification based on type
  const typeStyles = {
      info: { backgroundColor: "#007bff", color: "#fff" },
      success: { backgroundColor: "#28a745", color: "#fff" },
      warning: { backgroundColor: "#ffc107", color: "#212529" },
      error: { backgroundColor: "#dc3545", color: "#fff" },
  };
  const styles = typeStyles[type] || typeStyles.info;
  notification.style.backgroundColor = styles.backgroundColor;
  notification.style.color = styles.color;

  // Add message and undo button if applicable
  notification.innerHTML = `
      <span style="font-size: 16px; margin-right: 10px;">${message}</span>
  `;
  if (undo && link) {
      const undoButton = document.createElement("button");
      undoButton.textContent = "Undo";
      undoButton.style.cssText = `
          font-size: 16px;
          font-weight: bold;
          color: #fff;
          background-color: #f44336;
          border: none;
          border-radius: 5px;
          padding: 8px 16px;
          cursor: pointer;
          transition: transform 0.2s, background-color 0.2s;
          margin-left: 10px;
      `;
      undoButton.addEventListener("mouseover", () => {
          undoButton.style.backgroundColor = "#d32f2f";
      });
      undoButton.addEventListener("mouseout", () => {
          undoButton.style.backgroundColor = "#f44336";
      });
      undoButton.addEventListener("click", () => { 
        socket.emit("new_video", { link: link, undo: true }); 
        showNotification("Undo successful. Song added back to playlist.", "success"); 
      });      
      notification.appendChild(undoButton);
  }

  notification.className = "show";
  notification.style.left = "50%";
  notification.style.transform = "translateX(-50%)";
  notification.style.bottom = "20px";
  notification.style.padding = "12px 20px";
  notification.style.borderRadius = "10px";
  notification.style.boxShadow = "0px 4px 10px rgba(0, 0, 0, 0.2)";

  // Set timeout to hide the notification
  clearTimeout(currentNotificationTimeout);
  currentNotificationTimeout = setTimeout(() => {
      notification.className = notification.className.replace("show", "");
  }, 2000); // Adjust the duration as needed
}

// Listen for notification events emitted from the server
socket.on("notification", function (data) {
  const message = data.message || "Notification received";
  const type = data.type || "info"; // Default type is "info"
  showNotification(message, type); // Use your showNotification function to display it
});

function getNotificationMessage(link) {
  if (!link) {
    return "Content Added";
  }
  if (link.includes("list=")) {
    return "Playlist Added";
  } else if (link.includes("music.youtube.com")) {
    return "Music Added";
  } else if (link.includes("youtube.com") || link.includes("youtu.be")) {
    return "Audio Added";
  }
  return "Content Added";
}

function showVolumeOverlay(volume) {
  let volumeOverlay = document.getElementById("volume-overlay");
  if (!volumeOverlay) {
    volumeOverlay = document.createElement("div");
    volumeOverlay.id = "volume-overlay";
    document.body.appendChild(volumeOverlay);
  }
  volumeOverlay.textContent = `Volume: ${volume}%`;
  volumeOverlay.className = "show";

  const volumeSlider = document.getElementById("volume-slider");
  const rect = volumeSlider.getBoundingClientRect();
  const overlayRect = volumeOverlay.getBoundingClientRect();

  volumeOverlay.style.left = `${
    rect.left + rect.width / 2 - overlayRect.width / 2
  }px`;
  volumeOverlay.style.top = `${rect.top - overlayRect.height - 10}px`;

  setTimeout(() => {
    volumeOverlay.className = volumeOverlay.className.replace("show", "");
  }, 1000);
}

function updateContainerSize() {
  const container = document.querySelector(".container");
  const playlist = document.querySelector(".playlist");
  const items = playlist.children;
  if (items.length === 0) {
    container.classList.add("empty-container");
    container.classList.remove("full-container");
  } else {
    container.classList.remove("empty-container");
    container.classList.add("full-container");
  }
}
updateContainerSize();
window.addEventListener("resize", updateContainerSize);


