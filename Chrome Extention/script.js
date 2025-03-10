// ---------------------------------------------------
// 1) Your keys
// ---------------------------------------------------
const PEXELS_API_KEY = "ZJRp2xVx5daOcfelDPWfYXonMkTi7BACE992fksYL1iuL3cXVpr4maSq"; // e.g. "ZJRp2xV..."
const WEATHERAPI_KEY = "9ccd43ea95ac4dbcada32426251003";

// 2) HTML elements
const bgVideoEl = document.getElementById("bg-video");
const greetingEl = document.getElementById("greeting");
const timeEl = document.getElementById("time");
const weatherEl = document.getElementById("weather");
const verseTextEl = document.getElementById("verse-text");
const verseRefEl = document.getElementById("verse-reference");
const searchBox = document.getElementById("search-box");

// 3) Fallback weather location (Dhaka)
const DEFAULT_LAT = 23.8103;
const DEFAULT_LON = 90.4125;

// Some typical non-animal Pexels search terms
const PEXELS_SEARCH_TERMS = [
  "abstract",
  "city",
  "tech",
  "space",
  "landscape",
  "timelapse",
  "rain",
  "clouds",
  "lights"
];

// ---------------------------------------------------
// Utility: localStorage for greeting
// ---------------------------------------------------
function getLocalStorage(key) {
  return localStorage.getItem(key);
}

function setLocalStorage(key, value) {
  localStorage.setItem(key, value);
}

// ---------------------------------------------------
// 1. Random Background Video (Pexels)
// ---------------------------------------------------
async function setRandomBackgroundVideo() {
  try {
    const randomTerm = PEXELS_SEARCH_TERMS[
      Math.floor(Math.random() * PEXELS_SEARCH_TERMS.length)
    ];
    const url = `https://api.pexels.com/videos/search?query=${randomTerm}&per_page=10&page=1`;
    const response = await fetch(url, {
      headers: { Authorization: PEXELS_API_KEY }
    });
    const data = await response.json();

    if (!data.videos || data.videos.length === 0) {
      console.error("No videos found for query:", randomTerm);
      return;
    }

    // Pick one random video from the returned array
    const videos = data.videos;
    const randomIndex = Math.floor(Math.random() * videos.length);
    const chosenVideo = videos[randomIndex];

    // Try to pick a "reasonable" resolution, e.g. <= 1080
    const suitableFile = chosenVideo.video_files.find(file => file.height <= 1080);
    const videoUrl = suitableFile
      ? suitableFile.link
      : chosenVideo.video_files[0].link;

    bgVideoEl.src = videoUrl;
  } catch (error) {
    console.error("Error fetching random Pexels video:", error);
  }
}

// ---------------------------------------------------
// 2. Local Time
// ---------------------------------------------------
function updateTime() {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
  const seconds = String(now.getSeconds()).padStart(2, "0");
  timeEl.textContent = `${hours}:${minutes}:${seconds}`;
}
setInterval(updateTime, 1000);
updateTime();

// ---------------------------------------------------
// 3. Weather (WeatherAPI)
// ---------------------------------------------------
function fetchWeather(lat, lon) {
  const url = `https://api.weatherapi.com/v1/current.json?key=${WEATHERAPI_KEY}&q=${lat},${lon}&aqi=no`;

  fetch(url)
    .then(resp => resp.json())
    .then(data => {
      if (!data || !data.current || !data.location) {
        weatherEl.textContent = "Weather data unavailable.";
        return;
      }
      const city = data.location.name;
      const temp = Math.round(data.current.temp_c);
      weatherEl.textContent = `Weather in ${city}: ${temp}°C`;
    })
    .catch(err => {
      console.error("Error fetching weather:", err);
      weatherEl.textContent = "Could not load weather.";
    });
}

function getLocationAndWeather() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      pos => {
        const { latitude, longitude } = pos.coords;
        fetchWeather(latitude, longitude);
      },
      err => {
        console.error("Geolocation denied or not available:", err);
        fetchWeather(DEFAULT_LAT, DEFAULT_LON);
      }
    );
  } else {
    fetchWeather(DEFAULT_LAT, DEFAULT_LON);
  }
}

// ---------------------------------------------------
// 4. Search Bar
// ---------------------------------------------------
function handleSearch(e) {
  if (e.key === "Enter") {
    const query = searchBox.value.trim();
    if (!query) return;

    // If it looks like a URL, open it directly
    if (query.includes(".") && !query.includes(" ")) {
      if (!query.startsWith("http://") && !query.startsWith("https://")) {
        window.location.href = "http://" + query;
      } else {
        window.location.href = query;
      }
    } else {
      // Otherwise, Google search
      window.location.href = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
    }
  }
}

// ---------------------------------------------------
// 5. Personalized Greeting
// ---------------------------------------------------
function setGreeting() {
  let userName = getLocalStorage("username");
  if (!userName) {
    userName = prompt("Assalamu alaikum! What's your name?") || "Friend";
    setLocalStorage("username", userName);
  }

  const hour = new Date().getHours();
  let greetingText = "Hello";
  if (hour < 12) {
    greetingText = "Good morning";
  } else if (hour < 18) {
    greetingText = "Good afternoon";
  } else {
    greetingText = "Good evening";
  }

  greetingEl.textContent = `${greetingText}, ${userName}!`;
}

// ---------------------------------------------------
// 6. Random Quran or Hadith (80%/20%)
// ---------------------------------------------------
function fetchRandomItem() {
  const chance = Math.random();
  if (chance < 0.99) {
    // 80% => Quran
    fetchRandomAyah();
  } else {
    // 20% => Hadith
    fetchRandomHadith();
  }
}

// (A) Random Quran Verse
async function fetchRandomAyah() {
  try {
    const totalAyahs = 6236;
    const randomAyahNumber = Math.floor(Math.random() * totalAyahs) + 1;
    // Use Sahih International English translation
    const url = `https://api.alquran.cloud/v1/ayah/${randomAyahNumber}/en.sahih`;

    const response = await fetch(url);
    const data = await response.json();

    if (!data || !data.data) {
      verseTextEl.textContent = "Could not load a verse right now.";
      verseRefEl.textContent = "";
      return;
    }

    const ayahText = data.data.text;
    const surahName = data.data.surah.englishName;
    const verseNum = data.data.numberInSurah;

    verseTextEl.textContent = ayahText;
    verseRefEl.textContent = `— Surah ${surahName}, Ayah ${verseNum}`;
  } catch (err) {
    console.error("Error fetching ayah:", err);
    verseTextEl.textContent = "Could not load a verse right now.";
    verseRefEl.textContent = "";
  }
}

// (B) Random Hadith (Sahih Bukhari, range 1-300)
async function fetchRandomHadith() {
  try {
    const url = "https://api.hadith.sutanlab.id/books/bukhari?range=1-300";
    const response = await fetch(url);
    const data = await response.json();

    if (!data || !data.data || !data.data.hadiths) {
      verseTextEl.textContent = "Could not load a hadith right now.";
      verseRefEl.textContent = "";
      return;
    }

    const hadiths = data.data.hadiths;
    if (!hadiths.length) {
      verseTextEl.textContent = "No hadith found in this range.";
      verseRefEl.textContent = "";
      return;
    }

    const randomIndex = Math.floor(Math.random() * hadiths.length);
    const randomHadith = hadiths[randomIndex];

    verseTextEl.textContent = randomHadith.en.trim();
    verseRefEl.textContent = `— Sahih Bukhari #${randomHadith.number}`;
  } catch (err) {
    console.error("Error fetching hadith:", err);
    verseTextEl.textContent = "Could not load a hadith right now.";
    verseRefEl.textContent = "";
  }
}

// ---------------------------------------------------
// 7. On Page Load
// ---------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  setRandomBackgroundVideo();  // Pexels videos
  getLocationAndWeather();     // Weather
  setGreeting();               // Greeting
  fetchRandomItem();           // 80% Quran, 20% Hadith
});

searchBox.addEventListener("keyup", handleSearch);
