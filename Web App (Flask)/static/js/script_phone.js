let currentVideoId = null;
let isSeeking = false;
let videoDuration = 0;
let suggestionOverlay = null;
let suggestionsEnabled = true;
let currentNotificationTimeout;
let currentLink = ""; // Variable to store the full link
let isSwiping = false;
let swipeStartX = 0;
let swipeStartY = 0;
const swipeThreshold = 50; // Minimum distance in pixels to consider a swipe

const socket = io();
const YOUTUBE_API_KEY = "AIzaSyC-x1733bNl22rbecjJe6CNHhW62lIx_js"; // Ensure this matches your backend

document.getElementById("video-form").addEventListener("submit", function (e) {
  e.preventDefault();
  const link = document.getElementById("youtube-link").value;
  currentLink = link; // Store the full link
  socket.emit("new_video", { link });
  document.getElementById("youtube-link").value = "";
  hideSuggestions();
});

document.getElementById("youtube-link").addEventListener("input", function () {
  const query = this.value;
  if (suggestionsEnabled && query.length > 2) {
    fetchSuggestions(query);
  } else {
    hideSuggestions();
  }
});

function fetchSuggestions(query) {
  const suggestionsUrl = `https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&q=${query}&key=${YOUTUBE_API_KEY}&type=video`;
  fetch(suggestionsUrl)
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        showError("YouTube API error: " + data.error.message);
        return;
      }
      if (data.items && data.items.length > 0) {
        showSuggestions(data.items);
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
    suggestionItem.textContent = item.snippet.title;
    suggestionItem.onclick = () =>
      selectSuggestion(item.id.videoId, item.snippet.title);
    suggestionOverlay.appendChild(suggestionItem);
  });
  positionSuggestions();
  suggestionOverlay.style.display = "block";
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

function hideSuggestions() {
  if (suggestionOverlay) {
    suggestionOverlay.style.display = "none";
  }
}

function positionSuggestions() {
  const inputBox = document.getElementById("youtube-link");
  const rect = inputBox.getBoundingClientRect();
  const suggestionOverlay = document.getElementById("suggestion-overlay");
  suggestionOverlay.style.left = `${rect.left}px`;
  suggestionOverlay.style.top = `${rect.bottom + window.scrollY}px`;
  suggestionOverlay.style.width = `${rect.width}px`;
}

function selectSuggestion(videoId, title) {
  document.getElementById("youtube-link").value = title;
  hideSuggestions();
  currentLink = `https://www.youtube.com/watch?v=${videoId}`; // Store the full link
  socket.emit("new_video", { link: currentLink });
}

window.addEventListener("resize", positionSuggestions);

socket.on("update_playlist", function (data) {
  addVideoToList(data);
  highlightCurrentVideo(currentVideoId);
  showNotification(getNotificationMessage(currentLink));
});

socket.on("update_list", function (data) {
  updatePlaylist(data);
  highlightCurrentVideo(currentVideoId);
  // No notification needed here since individual video notifications will be handled by update_playlist
});

socket.on("play_video", function (data) {
  currentVideoId = data.video_id;
  highlightCurrentVideo(data.video_id);
  updateCurrentTitle(data.video_id);
  updatePlayPauseButton("playing");
  showNotification("Playing");
});

socket.on("toggle_play_pause", (data) => {
  updatePlayPauseButton(data.state);
  showNotification(data.state === "playing" ? "Playing" : "Paused");
});

socket.on("sync_play_state", (data) => {
  currentVideoId = data.video_id;
  updatePlayPauseButton(data.state);
  highlightCurrentVideo(data.video_id);
  updateCurrentTitle(data.video_id);
});

socket.on("update_volume", (data) => {
  document.getElementById("volume-slider").value = data.volume;
  showVolumeOverlay(data.volume);
});

socket.on("current_video", (data) => {
  currentVideoId = data.video_id;
  updateCurrentTitle(currentVideoId);
  highlightCurrentVideo(currentVideoId);
  updatePlayPauseButton(data.state === "playing" ? "playing" : "paused");
});

// Update the player progress and handle seeking
socket.on("progress_update", function (data) {
  if (!isSeeking) {
    const { currentTime, duration } = data;
    videoDuration = duration;
    const progressPercent = (currentTime / duration) * 100;
    document.getElementById("seek-slider").value = progressPercent;
  }
});

socket.on("seek_video", function (data) {
  if (!isSeeking) {
    const progressPercent = (data.time / videoDuration) * 100;
    document.getElementById("seek-slider").value = progressPercent;
  }
});

// Handle the slider input for seeking
document.getElementById("seek-slider").addEventListener("input", function (e) {
  isSeeking = true;
  const value = e.target.value;
  const seekTime = (value / 100) * videoDuration;

  // Format the seek time and display it as an overlay
  const formattedSeekTime = formatTime(seekTime);
  const formattedDuration = formatTime(videoDuration);
  const seekTimeOverlay = document.getElementById("seek-time");
  seekTimeOverlay.textContent = `${formattedSeekTime} / ${formattedDuration}`;
  seekTimeOverlay.style.display = "block";

  // Emit the seek event to the server
  socket.emit("seek_video", { percent: value });
});

document.getElementById("seek-slider").addEventListener("change", function () {
  isSeeking = false;
  document.getElementById("seek-time").style.display = "none";
});

function formatTime(seconds) {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  return hrs > 0
    ? `${hrs}:${mins.toString().padStart(2, "0")}:${secs
        .toString()
        .padStart(2, "0")}`
    : `${mins}:${secs.toString().padStart(2, "0")}`;
}

// Suggestions toggle
document
  .getElementById("suggestions-toggle")
  .addEventListener("change", (event) => {
    suggestionsEnabled = event.target.checked;
    localStorage.setItem("suggestionsEnabled", suggestionsEnabled);
    showNotification(suggestionsEnabled ? "Suggestions On" : "Suggestions Off");
  });

// Initialize state
window.addEventListener("load", () => {
  const isDarkMode = localStorage.getItem("darkMode") === "true";
  suggestionsEnabled = localStorage.getItem("suggestionsEnabled") === "true";
  if (isDarkMode) {
    document.body.classList.add("dark-mode");
    document
      .getElementById("dark-mode-toggle")
      .querySelector("i")
      .classList.replace("fa-moon", "fa-sun");
  }
  document.getElementById("suggestions-toggle").checked = suggestionsEnabled;
  socket.emit("request_current_video");
});

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
            <p class="video-meta">${
              video.artist
                ? "Artist: " + video.artist
                : "Creator: " + video.creator
            }</p>
            ${
              video.album
                ? `<p class="video-meta">Album: ${video.album}</p>`
                : ""
            }
            <p class="video-meta">Length: ${formatDuration(video.length)}</p>
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

    // Check if the movement is primarily horizontal and significant enough
    if (
      Math.abs(deltaX) > Math.abs(deltaY) &&
      Math.abs(deltaX) > swipeThreshold
    ) {
      e.preventDefault(); // Prevent vertical scroll
      videoItem.style.transform = `translateX(${deltaX}px)`;
    }
  });

  videoItem.addEventListener("touchend", function (e) {
    if (!isSwiping) return;

    const swipeEndX = e.changedTouches[0].clientX;
    const deltaX = swipeEndX - swipeStartX;
    isSwiping = false; // Reset swiping state

    if (Math.abs(deltaX) > swipeThreshold) {
      if (deltaX < 0) {
        // Swipe left to delete
        videoItem.style.transition =
          "transform 0.3s ease-out, background-color 0.3s ease-out";
        videoItem.style.transform = "translateX(-100%)";
        videoItem.style.backgroundColor = "red";
        setTimeout(() => {
          const videoId = videoItem.getAttribute("data-video-id");
          videoItem.remove();
          socket.emit("remove_video", {
            id: parseInt(videoItem.getAttribute("data-id")),
          });
          showNotification("Video Removed");
        }, 300);
      } else {
        // Swipe right - reset position or add custom action if needed
        videoItem.style.transition = "transform 0.3s ease-out";
        videoItem.style.transform = "translateX(0)";
      }
    } else {
      // Not enough swipe distance, reset position
      videoItem.style.transition = "transform 0.3s ease-out";
      videoItem.style.transform = "translateX(0)";
    }
  });

  videoItem.addEventListener("touchcancel", function () {
    isSwiping = false;
    videoItem.style.transform = "translateX(0)"; // Reset position
  });
}

function handleSwipe(videoItem) {
  const swipeDistance = swipeStartX - swipeEndX;

  if (swipeDistance > swipeThreshold) {
    // Swipe left detected
    const videoId = videoItem.getAttribute("data-video-id");
    if (videoId !== currentVideoId) {
      videoItem.style.transition =
        "transform 0.3s ease-out, background-color 0.3s ease-out";
      videoItem.style.transform = "translateX(-100%)";
      videoItem.style.backgroundColor = "red";
      setTimeout(() => {
        videoItem.remove();
        socket.emit("remove_video", {
          id: parseInt(videoItem.getAttribute("data-id")),
        });
        showNotification("Video Removed");
      }, 300);
    } else {
      showNotification("Cannot remove the playing video");
    }
  }
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

function highlightCurrentVideo(videoId) {
  document.querySelectorAll(".video-item").forEach((item) => {
    item.classList.toggle(
      "playing",
      item.getAttribute("data-video-id") === videoId
    );
  });
}

document.getElementById("play-pause-btn").addEventListener("click", () => {
  socket.emit("play_pause");
});

document.getElementById("volume-slider").addEventListener("input", function () {
  const volume = this.value;
  socket.emit("change_volume", { volume });
  showVolumeOverlay(volume);
});

document
  .getElementById("volume-slider")
  .addEventListener("touchstart", function () {
    isTouchingVolumeSlider = true;
  });

// Volume slider handling
document
  .getElementById("volume-slider")
  .addEventListener("touchend", function () {
    isTouchingVolumeSlider = false;
    hideVolumeOverlay();
  });

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
}

function hideVolumeOverlay() {
  if (!isTouchingVolumeSlider) {
    const volumeOverlay = document.getElementById("volume-overlay");
    if (volumeOverlay) {
      volumeOverlay.className = volumeOverlay.className.replace("show", "");
    }
  }
}

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
  if (isDarkMode) {
    document.body.classList.add("dark-mode");
    document
      .getElementById("dark-mode-toggle")
      .querySelector("i")
      .classList.replace("fa-moon", "fa-sun");
  }
  document.getElementById("suggestions-toggle").checked = suggestionsEnabled;
  socket.emit("request_current_video");
});

function updateCurrentTitle(videoId) {
  const currentItem = Array.from(document.querySelectorAll(".video-item")).find(
    (item) => item.getAttribute("data-video-id") === videoId
  );
  if (currentItem) {
    const currentTitle = currentItem.querySelector(".video-info p").innerText;
    document.getElementById("current-title").innerText = currentTitle;
  } else {
    document.getElementById("current-title").innerText = "None";
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

  const overlayRect = notification.getBoundingClientRect();
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
    console.log("No link provided, defaulting to 'Content Added'");
    return "Content Added";
  }

  console.log("Determining message for link:", link);

  if (link.includes("list=")) {
    console.log("Playlist detected");
    return "Playlist Added";
  } else if (link.includes("music.youtube.com")) {
    console.log("Music detected");
    return "Music Added";
  } else if (link.includes("youtube.com") || link.includes("youtu.be")) {
    console.log("Video detected");
    return "Video Added";
  }

  console.log("Fallback content added");
  return "Content Added";
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

// Initial call to set the size based on the current state
updateContainerSize();

// Example function to add video to the playlist
function addVideo(videoElement) {
  const playlist = document.querySelector(".playlist");
  playlist.appendChild(videoElement);
  updateContainerSize();
}

// Attach resize event listener if needed for dynamic adjustments
window.addEventListener("resize", updateContainerSize);
