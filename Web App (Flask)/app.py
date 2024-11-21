from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from pytube import YouTube, Playlist
import requests
import yt_dlp
import socket
from youtubesearchpython import VideosSearch
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
socketio = SocketIO(app, max_http_buffer_size=1000000)  # Adjust the size as needed


video_list = []
current_video_id = None
player_state = "paused"
current_volume = 10
YOUTUBE_API_KEY = "AIzaSyC-x1733bNl22rbecjJe6CNHhW62lIx_js"


@app.route("/")
def home():
    user_agent = request.headers.get("User-Agent")
    if "Mobi" in user_agent or request.args.get("view") == "mobile":
        return render_template("index_phone.html", videos=video_list)
    elif request.args.get("view") == "desktop":
        return render_template("index_pc.html", videos=video_list)
    else:
        return render_template("index_pc.html", videos=video_list)


@socketio.on("new_video")
def handle_new_video(data):
    try:
        if "list=" in data["link"]:
            # This is a playlist link
            playlist = Playlist(data["link"])
            for url in playlist.video_urls:
                add_video_to_list(url)
        else:
            # This is a single video link
            add_video_to_list(data["link"])
    except Exception as e:
        print(f"Error adding video: {e}")


def add_video_to_list(url):
    try:
        if "list=" in url:  # Check if it's a playlist
            playlist_id = extract_playlist_id(url)
            videos = fetch_videos_from_playlist(playlist_id)
            for video in videos:
                video_list.append(video)
                emit("update_playlist", video, broadcast=True)
        else:
            # For a single video
            video_id = extract_video_id(url)
            video_info = fetch_youtube_data(video_id)
            if video_info:
                video_info.update(
                    {
                        "id": len(video_list),
                        "video_id": video_id,
                    }
                )
                video_list.append(video_info)
                emit("update_playlist", video_info, broadcast=True)

    except Exception as e:
        print(f"Error adding video: {e}")


def extract_video_id(url):
    """Extract the video ID from a YouTube URL."""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None


def extract_playlist_id(url):
    """Extract the playlist ID from a YouTube URL."""
    if "list=" in url:
        return url.split("list=")[1].split("&")[0]
    return None


def fetch_youtube_data(video_id):
    """Fetch detailed information for a single video using the YouTube Data API."""
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={video_id}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "items" in data and data["items"]:
            item = data["items"][0]
            snippet = item["snippet"]
            content_details = item["contentDetails"]
            category_id = snippet.get("categoryId")
            tags = snippet.get("tags", [])
            length = parse_duration(content_details["duration"])

            # Ensure that title and thumbnail are retrieved correctly
            title = snippet.get("title", "Unknown Title")
            thumbnail = snippet.get("thumbnails", {}).get("high", {}).get("url", "")

            is_music = category_id == "10" or "music" in [tag.lower() for tag in tags]

            if is_music:
                return {
                    "title": title,
                    "thumbnail": thumbnail,
                    "artist": snippet["channelTitle"],
                    "album": snippet.get("album", "Unknown Album"),
                    "length": length,
                }
            else:
                return {
                    "title": title,
                    "thumbnail": thumbnail,
                    "creator": snippet["channelTitle"],
                    "length": length,
                }
    return {}


def fetch_videos_from_playlist(playlist_id):
    """Fetch all videos from a playlist using the YouTube Data API."""
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=50&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    video_list = []

    if response.status_code == 200:
        data = response.json()
        for item in data.get("items", []):
            video_id = item["snippet"]["resourceId"]["videoId"]
            video_info = fetch_youtube_data(video_id)
            if video_info:
                video_info.update(
                    {
                        "id": len(video_list),
                        "video_id": video_id,
                    }
                )
                video_list.append(video_info)

    return video_list


def parse_duration(duration):
    hours = minutes = seconds = 0
    duration = duration.replace("PT", "")
    if "H" in duration:
        hours, duration = duration.split("H")
        hours = int(hours)
    if "M" in duration:
        minutes, duration = duration.split("M")
        minutes = int(minutes)
    if "S" in duration:
        seconds = int(duration.replace("S", ""))
    return hours * 3600 + minutes * 60 + seconds


@socketio.on("remove_video")
def handle_remove_video(data):
    video_id = data["id"]
    global video_list, current_video_id
    video_list = [video for video in video_list if video["id"] != video_id]

    if current_video_id and any(video["id"] == video_id for video in video_list):
        current_video_id = None
        emit(
            "current_video",
            {
                "video_id": None,
                "title": "None",
                "state": "paused",
                "volume": current_volume,
            },
            broadcast=True,
        )
    else:
        current_video = next(
            (video for video in video_list if video["video_id"] == current_video_id),
            None,
        )
        if current_video:
            emit(
                "current_video",
                {
                    "video_id": current_video["video_id"],
                    "title": current_video["title"],
                    "state": player_state,
                    "volume": current_volume,
                },
                broadcast=True,
            )

    emit("update_list", video_list, broadcast=True)


@socketio.on("shuffle_playlist")
def handle_shuffle_playlist():
    global video_list, current_video_id

    if current_video_id:
        current_index = next(
            (
                index
                for index, video in enumerate(video_list)
                if video["video_id"] == current_video_id
            ),
            -1,
        )

        if current_index != -1:
            played_videos = video_list[: current_index + 1]
            unplayed_videos = video_list[current_index + 1 :]
            random.shuffle(unplayed_videos)
            video_list = played_videos + unplayed_videos
    else:
        random.shuffle(video_list)

    emit("update_list", video_list, broadcast=True)
    emit("playlist_shuffled", broadcast=True)  # Emit the shuffle notification event


@socketio.on("reorder_videos")
def handle_reorder_videos(data):
    global video_list
    new_order = data["order"]
    reordered_list = [
        next(video for video in video_list if video["id"] == vid_id)
        for vid_id in new_order
    ]
    video_list = reordered_list
    emit("update_list", video_list, broadcast=True)


@socketio.on("request_current_video")
def handle_request_current_video():
    global current_video_id, player_state, current_volume
    if current_video_id is not None:
        current_video = next(
            (video for video in video_list if video["video_id"] == current_video_id),
            None,
        )
        if current_video:
            emit(
                "current_video",
                {
                    "video_id": current_video["video_id"],
                    "title": current_video["title"],
                    "state": player_state,
                    "volume": current_volume,
                },
                broadcast=True,
            )
    emit("update_list", video_list, broadcast=True)


@socketio.on("sync_play_state")
def handle_sync_play_state(data):
    global current_video_id, player_state
    current_video_id = data["video_id"]
    player_state = data["state"]
    emit(
        "sync_play_state",
        {"video_id": current_video_id, "state": player_state},
        broadcast=True,
    )


@socketio.on("play_video")
def handle_play_video(data):
    global current_video_id, player_state
    current_video_id = data["video_id"]
    player_state = "playing"
    emit("play_video", data, broadcast=True)


@socketio.on("play_pause")
def handle_play_pause():
    global player_state
    player_state = "paused" if player_state == "playing" else "playing"
    emit("toggle_play_pause", {"state": player_state}, broadcast=True)


@socketio.on("change_volume")
def handle_change_volume(data):
    global current_volume
    current_volume = data["volume"]
    emit("update_volume", data, broadcast=True)


@socketio.on("progress_update")
def handle_progress_update(data):
    emit("progress_update", data, broadcast=True)


@socketio.on("play_next_video")
def handle_play_next_video():
    play_next_video()


def play_next_video():
    global current_video_id, player_state
    current_index = next(
        (
            index
            for index, video in enumerate(video_list)
            if video["video_id"] == current_video_id
        ),
        -1,
    )
    if current_index != -1 and current_index < len(video_list) - 1:
        next_video = video_list[current_index + 1]
        current_video_id = next_video["video_id"]
        player_state = "playing"
        emit(
            "play_video",
            {"video_id": current_video_id, "title": next_video["title"]},
            broadcast=True,
        )


@socketio.on("seek_video")
def handle_seek_video(data):
    global current_video_id
    video_id = current_video_id
    if video_id:
        duration = next(
            (video["length"] for video in video_list if video["video_id"] == video_id),
            None,
        )
        if duration:
            try:
                percent = float(data["percent"])
                duration = float(duration)
                seek_time = (percent / 100) * duration
                emit(
                    "seek_video",
                    {"video_id": video_id, "time": seek_time},
                    broadcast=True,
                )
            except ValueError as e:
                print(f"Error converting seek data: {e}")


if __name__ == "__main__":
    local_ip = socket.gethostbyname(socket.gethostname())
    print(
        f"Server is running at http://{local_ip}:5000/ (or http://0.0.0.0:5000/ for all interfaces)"
    )
    socketio.run(app, host="0.0.0.0", port=5000)
