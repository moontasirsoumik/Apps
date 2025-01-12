let currentVideoId = null;
let isSeeking = false;
let videoDuration = 0; // We'll store the duration from the PC's updates
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
const socket = io();
let lastDeletedSongLink = null;

// Cache DOM elements
const inputField = document.getElementById("youtube-link");
const actionButton = document.getElementById("action-button");

//--------------------------------------------------------------------------
// 1) Form Handling & Suggestions
//--------------------------------------------------------------------------
document.getElementById("youtube-link").addEventListener("input", function () {
  const query = this.value;
  if (suggestionsEnabled && query.length > 2) {
    debouncedFetchSuggestions(query);
  } else {
    hideSuggestions();
  }
});

function scrollToPlayingSong() {
  if (currentVideoId) {
    const currentVideoElement = document.querySelector(
      `.video-item[data-video-id="${currentVideoId}"]`
    );
    if (currentVideoElement) {
      currentVideoElement.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  }
}

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


// Handle suggestion selection
function selectSuggestion(videoId, title) {
  inputField.value = ""; // Clear the input field
  hideSuggestions();
  clearInput();
  const link = `https://www.youtube.com/watch?v=${videoId}`;
  socket.emit("new_video", { link });
}

// Hide suggestions overlay
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

window.addEventListener("resize", positionSuggestions);

//--------------------------------------------------------------------------
// 2) Socket.IO Event Handlers (Phone as Remote)
//--------------------------------------------------------------------------
socket.on("update_playlist", function (data) {
  // Check if the song already exists in the playlist
  const alreadyExists = videoList.some((video) => video.video_id === data.video_id);

  if (alreadyExists) {
    // If it already exists, update its position in the list
    videoList = videoList.filter((video) => video.video_id !== data.video_id);
    videoList.push(data); // Move it to the bottom
    updatePlaylist(videoList);
    showNotification(
      `'${data.title}' is already in the playlist. It has been moved to the bottom.`,
      "info"
    );
  } else {
    // Add the new song
    videoList.push(data);
    addVideoToList(data);
    showNotification(`'${data.title}' has been successfully added to the playlist.`, "success");
  }
});




socket.on("update_list", function (data) {
  videoList = data;
  updatePlaylist(data);
  highlightCurrentVideo(currentVideoId);
});

/**
 * The PC says "play_video with this ID".
 * Phone just updates local UI to show it's playing.
 */
socket.on("play_video", function (data) {
  currentVideoId = data.video_id;

  // Find the song details based on the current video ID
  const songDetails = videoList.find((video) => video.video_id === currentVideoId);

  // Construct the notification message
  const songTitle = songDetails?.title || "Unknown Title";
  const artist = songDetails?.artist || songDetails?.creator || "Unknown Artist";
  const notificationMessage = `Playing: ${songTitle} by ${artist}`;

  // Highlight the current video
  highlightCurrentVideo(data.video_id);

  // Update the current title
  updateCurrentTitle(data.video_id);

  // Update play/pause button
  updatePlayPauseButton("playing");

  // Show the notification
  showNotification(notificationMessage, "info");
});


/**
 * The server toggled global play/pause.
 * Update phone UI only.
 */
socket.on("toggle_play_pause", (data) => {
  updatePlayPauseButton(data.state);
  showNotification(data.state === "playing" ? "Playing" : "Paused");
});

/**
 * Another user changed the play state.
 * Phone updates UI.
 */
socket.on("sync_play_state", (data) => {
  currentVideoId = data.video_id;
  updatePlayPauseButton(data.state);
  highlightCurrentVideo(data.video_id);
  updateCurrentTitle(data.video_id);
  showNotification(data.state === "playing" ? "Playing" : "Paused");
});

/**
 * Global volume changed. Phone updates its slider only.
 */
socket.on("update_volume", (data) => {
  const volume = data.volume;
  document.getElementById("volume-slider").value = volume;
  showVolumeOverlay(volume);
});

/**
 * The server is telling phone the current video details.
 */
socket.on("current_video", (data) => {
  currentVideoId = data.video_id;
  updateCurrentTitle(data.video_id);
  highlightCurrentVideo(data.video_id);
  updatePlayPauseButton(data.state === "playing" ? "playing" : "paused");
  const vol = parseInt(data.volume) || 10;
  document.getElementById("volume-slider").value = vol;
  scrollToPlayingSong();
});

/**
 * The PC sends progress updates, which we use to set phone's seek slider.
 */
socket.on("progress_update", function (data) {
  if (!isSeeking) {
    const { currentTime, duration } = data;
    videoDuration = duration;
    const progressPercent = (currentTime / duration) * 100;
    document.getElementById("seek-slider").value = progressPercent;
  }
});

/**
 * A global "seek_video" event. If not seeking locally, update phone slider.
 */
socket.on("seek_video", function (data) {
  if (!isSeeking && data.video_id === currentVideoId) {
    const { time } = data;
    const duration = videoDuration;
    if (duration > 0) {
      const progressPercent = (time / duration) * 100;
      document.getElementById("seek-slider").value = progressPercent;
    }
  }
});

socket.on("playlist_shuffled", () => {
  showNotification("Playlist Shuffled");
});

//--------------------------------------------------------------------------
// 3) No local playback on phone, so no loadAndPlayVideo or <video> usage
//--------------------------------------------------------------------------

//--------------------------------------------------------------------------
// 4) Seek Bar Handling (remote style)
//--------------------------------------------------------------------------
const seekSlider = document.getElementById("seek-slider");
seekSlider.addEventListener("input", function (e) {
  isSeeking = true;
  const value = parseFloat(e.target.value);
  if (videoDuration > 0) {
    const seekTime = (value / 100) * videoDuration;
    const formattedSeekTime = formatTime(seekTime);
    const formattedDuration = formatTime(videoDuration);
    const seekTimeOverlay = document.getElementById("seek-time");
    seekTimeOverlay.textContent = `${formattedSeekTime} / ${formattedDuration}`;
    seekTimeOverlay.style.display = "block";
  }
});

seekSlider.addEventListener("change", function (e) {
  isSeeking = false;
  document.getElementById("seek-time").style.display = "none";
  if (videoDuration > 0) {
    const value = parseFloat(e.target.value);
    socket.emit("seek_video", { percent: value });
  }
});

//--------------------------------------------------------------------------
// 5) Controls: Play/Pause, Shuffle, Volume => just emit to server
//--------------------------------------------------------------------------
document.getElementById("play-pause-btn").addEventListener("click", () => {
  socket.emit("play_pause");
  socket.emit("request_current_video");
});

document.getElementById("shuffle-btn").addEventListener("click", () => {
  socket.emit("shuffle_playlist");
});

document.getElementById("volume-slider").addEventListener("input", function () {
  const volume = this.value;
  socket.emit("change_volume", { volume });
  showVolumeOverlay(volume);
});

//--------------------------------------------------------------------------
// 6) Playlist, Swiping, Sorting
//--------------------------------------------------------------------------
function addVideoToList(video) {
  const playlist = document.getElementById("playlist");
  const videoItem = document.createElement("div");
  videoItem.className = "video-item unselectable";
  videoItem.setAttribute("data-id", video.id);
  videoItem.setAttribute("data-video-id", video.video_id);
  videoItem.setAttribute(
    "data-url",
    `https://www.youtube.com/watch?v=${video.video_id}`
  ); // Set the correct video URL
  videoItem.innerHTML = `
    <img class="drag-area" src="${video.thumbnail}" alt="${video.title}">
    <div class="video-info">
      <p class="video-title"><strong>${video.title}</strong></p>
      <p class="video-artist">${
        video.artist ? video.artist : video.creator
      }</p>
      ${video.album ? `<p class=".suggestion-item">Album: ${video.album}</p>` : ""}
    </div>
  `;
  playlist.appendChild(videoItem);
  attachClickListener(videoItem);
  attachSwipeListener(videoItem);
  attachLongPressListener(videoItem);
  updateContainerSize();  
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
    if (videoId === currentVideoId) {
      // If same video tapped, toggle play/pause
      socket.emit("play_pause");
    } else {
      // A new video -> ask server to play it on PC
      socket.emit("play_video", { video_id: videoId });
    }
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
              // Save the deleted song's link
              lastDeletedSongLink = videoItem.getAttribute("data-url");

              // Swipe left => remove
              videoItem.style.transition =
                  "transform 0.3s ease-out, background-color 0.3s ease-out";
              videoItem.style.transform = "translateX(-100%)";
              videoItem.style.backgroundColor = "red";
              setTimeout(() => {
                  socket.emit("remove_video", {
                      id: parseInt(videoItem.getAttribute("data-id")),
                  });
                  videoItem.remove();
                  showNotification("Song removed.", "info", true); // Show undo option
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


// Fetch the playlist from the backend on page load
window.addEventListener("load", () => {
  fetch("/fetch_playlist")
    .then((response) => response.json())
    .then((data) => {
      videoList = data;
      updatePlaylist(data); // Update the frontend playlist
    })
    .catch((err) => console.error("Error fetching playlist:", err));
});

// Swipe functionality to remove a song and delete it permanently
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

    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > swipeThreshold) {
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
        // Swipe left => remove video
        videoItem.style.transition = "transform 0.3s ease-out, background-color 0.3s ease-out";
        videoItem.style.transform = "translateX(-100%)";
        videoItem.style.backgroundColor = "red";
        setTimeout(() => {
          const videoId = videoItem.getAttribute("data-video-id");
          socket.emit("remove_video", { video_id: videoId }); // Notify server
          videoItem.remove(); // Remove from UI
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

//--------------------------------------------------------------------------
// 7) Dark Mode & Suggestions Toggle
//--------------------------------------------------------------------------
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

window.addEventListener("load", () => {
  const isDarkMode = localStorage.getItem("darkMode") === "true";
  suggestionsEnabled = true; // Force suggestions to be enabled on load

  // Ensure volume slider starts at 20%
  document.getElementById("volume-slider").value = 20;

  if (isDarkMode) {
    document.body.classList.add("dark-mode");
    document
      .getElementById("dark-mode-toggle")
      .querySelector("i")
      .classList.replace("fa-moon", "fa-sun");
  }

  document.getElementById("suggestions-toggle").checked = true; // Always checked
  localStorage.setItem("suggestionsEnabled", true); // Always save as enabled

  socket.emit("request_current_video");
});

//--------------------------------------------------------------------------
// 8) Utility Functions
//--------------------------------------------------------------------------
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
  const btn = document.getElementById("play-pause-btn");
  if (state === "playing") {
    btn.innerHTML = '<i class="fas fa-pause"></i>';
  } else {
    btn.innerHTML = '<i class="fas fa-play"></i>';
  }
}

function formatDuration(seconds) {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hrs ? hrs + ":" : ""}${mins}:${secs < 10 ? "0" : ""}${secs}`;
}

function formatTime(time) {
  const hrs = Math.floor(time / 3600);
  const mins = Math.floor((time % 3600) / 60);
  const secs = Math.floor(time % 60);
  return hrs > 0
    ? `${hrs}:${mins.toString().padStart(2, "0")}:${secs
        .toString()
        .padStart(2, "0")}`
    : `${mins}:${secs.toString().padStart(2, "0")}`;
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
          socket.emit("new_video", { link: link });
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
  }, 5000); // Adjust the duration as needed
}


// Listen for notification events emitted from the server
socket.on("notification", function (data) {
  const { message, type = "info", undo = false, video_id, link } = data;
  showNotification(message, type, undo, link);
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
    return "Video Added";
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

// If you still want the long-press context menu for "Copy Link," keep it:
function attachLongPressListener(videoItem) {
  let longPressTimeout;
  videoItem.addEventListener("touchstart", function (e) {
    longPressTimeout = setTimeout(() => {
      e.preventDefault();
      showContextMenu(videoItem, e.touches[0].clientX, e.touches[0].clientY);
    }, 500);
  });
  videoItem.addEventListener("touchend", () => clearTimeout(longPressTimeout));
  videoItem.addEventListener("touchmove", () => clearTimeout(longPressTimeout));
  videoItem.addEventListener("touchcancel", () =>
    clearTimeout(longPressTimeout)
  );
}

function showContextMenu(videoItem, x, y) {
  const existingMenu = document.getElementById("context-menu");
  if (existingMenu) existingMenu.remove();

  const contextMenu = document.createElement("div");
  contextMenu.id = "context-menu";
  contextMenu.className = "context-menu";
  contextMenu.innerHTML = `
      <div class="context-menu-item" onclick="copyToClipboard('${videoItem.getAttribute(
        "data-url"
      )}')">Copy Link</div>
  `;
  document.body.appendChild(contextMenu);

  const menuHeight = contextMenu.offsetHeight;
  contextMenu.style.left = `${x - 50}px`;
  contextMenu.style.top = `${y - 70 - menuHeight}px`;
  contextMenu.style.display = "block";

  setTimeout(() => {
    document.addEventListener("touchstart", handleOutsideTouch, { once: true });
    document.addEventListener("click", handleOutsideClick, { once: true });
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

function hideContextMenu() {
  const contextMenu = document.getElementById("context-menu");
  if (contextMenu) contextMenu.remove();
}

function copyToClipboard(text) {
  if (!text || text === "null") {
    showNotification("Failed to copy: Invalid link");
    return;
  }

  if (navigator.clipboard) {
    navigator.clipboard
      .writeText(text)
      .then(() => {
        showNotification("Link copied to clipboard");
        hideContextMenu();
      })
      .catch((err) => {
        showNotification("Failed to copy link");
        console.error("Error copying link: ", err);
      });
  } else {
    showFallbackCopy(text);
  }
}

function showFallbackCopy(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.focus();
  textarea.select();

  try {
    const successful = document.execCommand("copy");
    if (successful) {
      showNotification("Link copied to clipboard");
    } else {
      showNotification("Failed to copy link");
    }
  } catch (err) {
    console.error("Fallback copy error:", err);
    showNotification("Failed to copy link");
  }
  document.body.removeChild(textarea);
  hideContextMenu();
}