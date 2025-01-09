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
  addVideoToList(data);
  videoList.push(data);
  showNotification(getNotificationMessage(currentLink));
});

socket.on("update_list", function (data) {
  updatePlaylist(data);
  videoList = data;
  highlightCurrentVideo(currentVideoId);
});

socket.on("play_video", async function (data) {
  currentVideoId = data.video_id;
  showNotification("Playing");
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
  videoItem.className = "video-item";
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

function showNotification(message) {
  let notification = document.getElementById("notification-overlay");
  if (!notification) {
    notification = document.createElement("div");
    notification.id = "notification-overlay";
    document.body.appendChild(notification);
  }
  notification.textContent = message;
  notification.className = "show";

  notification.style.left = `50%`;
  notification.style.transform = `translateX(-50%)`;
  notification.style.bottom = `20px`;

  clearTimeout(currentNotificationTimeout);
  currentNotificationTimeout = setTimeout(() => {
    notification.className = notification.className.replace("show", "");
  }, 2000);
}

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
