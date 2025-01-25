from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import yt_dlp
import socket
import random
from youtubesearchpython.extras import Video
from youtubesearchpython import Playlist as YTPlaylist, VideosSearch
from ytmusicapi import YTMusic

played_songs = set()

app = Flask(__name__)
app.config["SECRET_KEY"] = "my_secret_key"
socketio = SocketIO(app, max_http_buffer_size=1000000)

video_list = []
current_video_id = None
player_state = "paused"
current_volume = 10
ytmusic = YTMusic()


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
        undo = data["undo"]
    except:
        undo = False
    print("Hnadle: ", undo)
    try:
        if "list=" in data["link"]:
            # Fetch playlist videos using youtubesearchpython
            videos = fetch_videos_from_playlist(data["link"])
            for video in videos:
                video_list.append(video)
                emit("update_playlist", video, broadcast=True)
        else:
            add_video_to_list(data["link"], undo)
    except Exception as e:
        print(f"Error adding video: {e}")
        print(data)


def extract_video_id(url):
    """Extracts video ID from YouTube URLs."""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None


def add_video_to_list(url, undo=False):
    print("Add video: ", undo)
    try:
        # Extract video ID from URL
        video_id = extract_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        # Check if the video is already in the playlist
        global video_list
        for video in video_list:
            if video["video_id"] == video_id:
                # Move the existing video to the bottom
                video_list.remove(video)
                video_list.append(video)
                emit("update_list", video_list, broadcast=True)
                emit(
                    "notification",
                    {
                        "message": f"'{video['title']}' is already in the playlist. It has been moved to the bottom."
                    },
                    broadcast=True,
                )
                return  # Exit early as the video is already in the playlist

        # Attempt to fetch the YouTube Music version
        music_url = f"https://music.youtube.com/watch?v={video_id}"
        try:
            video_info = fetch_youtube_music_data(music_url)
            if video_info:
                video_info.update(
                    {
                        "id": len(video_list),
                        "video_id": video_id,
                        "isUndo": undo,  # Add this flag
                    }
                )
                video_list.append(video_info)
                emit("update_playlist", video_info, broadcast=True)
                if not undo:
                    print(undo)
                    emit(
                        "notification",
                        {
                            "message": f"'{video_info['title']}' has been added to the playlist."
                        },
                        broadcast=True,
                    )
                return  # Success: Exit function
        except Exception as e:
            print(f"Failed to fetch from YouTube Music: {e}")

        # Fallback to the original YouTube version
        video_info = fetch_youtube_data(url)
        if video_info:
            video_info.update(
                {
                    "id": len(video_list),
                    "video_id": video_id,
                    "isUndo": undo,  # Add this flag
                }
            )
            video_list.append(video_info)
            emit("update_playlist", video_info, broadcast=True)
            if not undo:
                emit(
                    "notification",
                    {
                        "message": f"'{video_info['title']}' has been added to the playlist."
                    },
                    broadcast=True,
                )
    except Exception as e:
        print(f"Error adding video: {e}")


def fetch_youtube_music_data(url):
    """Fetch video information from YouTube Music using ytmusicapi."""
    try:
        video_id = extract_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube Music URL")

        # Get detailed video info
        video_info = ytmusic.get_song(video_id)
        if not video_info:
            raise ValueError("Video not found on YouTube Music")

        # Clean up artist name
        artist_name = (
            video_info["videoDetails"]["author"].replace(" - Topic", "").strip()
        )

        # Extract relevant data
        return {
            "title": video_info["videoDetails"]["title"],
            "thumbnail": video_info["videoDetails"]["thumbnail"]["thumbnails"][-1][
                "url"
            ],
            "artist": artist_name,
            "length": video_info["videoDetails"]["lengthSeconds"],
        }
    except Exception as e:
        print(f"Error fetching YouTube Music data: {e}")
        return None


def extract_playlist_id(url):
    if "list=" in url:
        return url.split("list=")[1].split("&")[0]
    return None


def fetch_youtube_data(video_url):
    """Fetches video information using youtubesearchpython"""
    try:
        # Clean the URL to extract the video ID
        video_id = extract_video_id(video_url)
        if not video_id:
            print("Invalid video URL.")
            return {}

        # Rebuild the clean URL
        clean_url = f"https://youtu.be/{video_id}"

        # Fetch video information
        video_info = Video.getInfo(clean_url, mode="json")
        if video_info:
            title = video_info.get("title", "Unknown Title")
            thumbnails = video_info.get("thumbnails", [{}])
            thumbnail = thumbnails[-1].get("url", "") if thumbnails else ""
            channel_name = video_info.get("channel", {}).get("name", "Unknown Channel")
            duration_seconds = int(
                video_info.get("duration", {}).get("secondsText", 0) or 0
            )
            category = video_info.get("category", "Unknown")

            # Clean up artist name
            channel_name = channel_name.replace(" - Topic", "").strip()

            # Determine if it's music-related
            is_music = category.lower() == "music"

            if is_music:
                return {
                    "title": title,
                    "thumbnail": thumbnail,
                    "artist": channel_name,
                    "length": duration_seconds,
                }
            else:
                return {
                    "title": title,
                    "thumbnail": thumbnail,
                    "creator": channel_name,
                    "length": duration_seconds,
                }
        return {}
    except Exception as e:
        print(f"Error fetching video info: {e}")
        return {}


def fetch_videos_from_playlist(playlist_url):
    """Fetches videos from a playlist using youtubesearchpython"""
    try:
        playlist = YTPlaylist.getVideos(playlist_url, mode="json")
        video_list_local = []
        for video in playlist.get("videos", []):
            video_url = video.get("link", "")
            if video_url:
                video_info = fetch_youtube_data(video_url)
                if video_info:
                    video_info.update(
                        {"id": len(video_list_local), "video_id": video["id"]}
                    )
                    video_list_local.append(video_info)
        return video_list_local
    except Exception as e:
        print(f"Error fetching playlist videos: {e}")
        return []


@socketio.on("remove_video")
def handle_remove_video(data):
    global video_list
    try:
        video_id = data.get("video_id")
        if video_id is None:
            emit("error", {"message": "Invalid video ID"})
            return

        # Find the video to be removed
        video_to_remove = next(
            (video for video in video_list if video["video_id"] == video_id), None
        )

        if video_to_remove:
            # Remove video from in-memory list
            video_list = [
                video for video in video_list if video["video_id"] != video_id
            ]

            # Broadcast the updated list to all clients
            emit("update_list", video_list, broadcast=True)

            # Send a notification with undo data
            emit(
                "notification",
                {
                    "message": f"Removed: {video_to_remove['title']}",
                    "type": "info",
                    "undo": True,
                    "video_id": video_id,
                    "link": f"https://www.youtube.com/watch?v={video_id}",
                },
            )
            print(f"Video '{video_to_remove['title']}' removed successfully.")
        else:
            emit("error", {"message": "Video not found"})
    except Exception as e:
        print(f"Error removing video: {e}")
        emit("error", {"message": str(e)})


@app.route("/fetch_playlist", methods=["GET"])
def fetch_playlist():
    # Send the current playlist (can load from persistent storage if needed)
    return jsonify(video_list)


@socketio.on("search_videos")
def search_videos(data):
    query = data.get("query", "")
    if not query:
        emit("suggestions", {"error": "Query is missing"})
        return

    try:
        # Perform the search on YouTube Music
        results = ytmusic.search(query, filter="songs", limit=5)
        suggestions = [
            {
                "videoId": result["videoId"],
                "title": result["title"],
                "thumbnail": result["thumbnails"][-1]["url"],
                "channel": (
                    result["artists"][0]["name"]
                    if "artists" in result
                    else "Unknown Artist"
                ),
                "duration": result.get("duration", "Unknown"),
            }
            for result in results
            if result["resultType"] == "song"
        ]
        emit("suggestions", {"suggestions": suggestions})
    except Exception as e:
        print(f"Error fetching YouTube Music suggestions: {e}")
        emit("suggestions", {"error": str(e)})


@app.route("/search_suggestions")
def search_suggestions():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "Query is empty"}), 400
    try:
        search = VideosSearch(query, limit=5)
        results = search.result()["result"]
        suggestions = [
            {
                "title": result["title"],
                "thumbnail": result["thumbnails"][0]["url"],
                "videoId": result["id"],
            }
            for result in results
        ]
        return jsonify({"suggestions": suggestions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@socketio.on("shuffle_playlist")
def handle_shuffle_playlist():
    global video_list, current_video_id

    if current_video_id:
        # Find the index of the currently playing song
        current_index = next(
            (
                index
                for index, video in enumerate(video_list)
                if video["video_id"] == current_video_id
            ),
            -1,
        )

        if current_index != -1:
            # Separate played and unplayed songs
            played_videos = [
                video for video in video_list if video.get("played", False)
            ]
            unplayed_videos = [
                video for video in video_list if not video.get("played", False)
            ]

            # Shuffle unplayed videos
            random.shuffle(unplayed_videos)

            # Remove the current playing song from played_videos if it exists
            current_song = video_list[current_index]
            if current_song in played_videos:
                played_videos.remove(current_song)

            # Reassemble the playlist: played above, current playing, unplayed below
            video_list = (
                played_videos
                + [current_song]  # Add current playing song
                + [
                    video
                    for video in unplayed_videos
                    if video["video_id"] != current_video_id
                ]
            )
    else:
        # If no current playing song, shuffle everything
        random.shuffle(video_list)

    emit("update_list", video_list, broadcast=True)
    emit("playlist_shuffled", broadcast=True)


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
    global current_video_id, player_state, played_songs
    current_video_id = data["video_id"]
    player_state = "playing"

    # Mark the video as played
    played_songs.add(current_video_id)
    for video in video_list:
        video["played"] = video["video_id"] in played_songs

    emit("play_video", data, broadcast=True)
    emit("update_list", video_list, broadcast=True)


@socketio.on("play_pause")
def handle_play_pause():
    global player_state, current_video_id

    if current_video_id is None:  # No song is currently playing
        if video_list:  # Check if there are videos in the playlist
            current_video = video_list[0]  # Select the first song
            current_video_id = current_video["video_id"]
            player_state = "playing"  # Set state to playing
            emit(
                "play_video",
                {"video_id": current_video_id, "title": current_video["title"]},
                broadcast=True,
            )
        else:
            # No songs in the playlist; send notification or ignore
            emit("notification", {"message": "No songs in the playlist to play."})
    else:
        # Toggle play/pause state for the currently playing song
        player_state = "paused" if player_state == "playing" else "playing"
        emit("toggle_play_pause", {"state": player_state}, broadcast=True)


@socketio.on("change_volume")
def handle_change_volume(data):
    global current_volume
    current_volume = data["volume"]
    emit("update_volume", data, broadcast=True)


@socketio.on("progress_update")
def handle_progress_update(data):
    # Forward progress data so all clients (including phone) see it
    emit("progress_update", data, broadcast=True)


@socketio.on("play_next_video")
def handle_play_next_video():
    play_next_video()


@socketio.on("play_previous_video")
def handle_play_previous_video():
    play_previous_video()


def play_previous_video():
    global current_video_id, player_state

    # If there's no current song, do nothing
    current_index = next(
        (
            index
            for index, v in enumerate(video_list)
            if v["video_id"] == current_video_id
        ),
        -1,
    )
    # If we are not at the first song, move one step back
    if current_index > 0:
        prev_video = video_list[current_index - 1]
        current_video_id = prev_video["video_id"]
        player_state = "playing"
        emit(
            "play_video",
            {"video_id": current_video_id, "title": prev_video["title"]},
            broadcast=True,
        )
    # Otherwise, do nothing if current_index <= 0


def play_next_video():
    global current_video_id, player_state
    current_index = next(
        (
            index
            for index, v in enumerate(video_list)
            if v["video_id"] == current_video_id
        ),
        -1,
    )
    # If we're not at the last song, move one step forward
    if current_index != -1 and current_index < len(video_list) - 1:
        next_video = video_list[current_index + 1]
        current_video_id = next_video["video_id"]
        player_state = "playing"
        emit(
            "play_video",
            {"video_id": current_video_id, "title": next_video["title"]},
            broadcast=True,
        )
    # Otherwise, do nothing if at the last song or no current


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


@app.route("/stream", methods=["POST"])
def stream():
    try:
        data = request.get_json()
        url = data.get("url")
        if not url:
            return jsonify({"error": "Invalid URL"}), 400

        ydl_opts_audio = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            stream_url = info_dict["url"]
            return jsonify({"stream_url": stream_url, "type": "audio"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    local_ip = socket.gethostbyname(socket.gethostname())
    port = 5000
    print(
        f"Server is running at http://{local_ip}:{port}/ "
        f"(or http://0.0.0.0:{port}/ for all interfaces)"
    )
    socketio.run(app, host="0.0.0.0", port=port)