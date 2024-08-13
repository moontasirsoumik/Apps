/* General Styles */
body, h1, p, input, button {
    margin: 0;
    padding: 0;
    font-family: 'Roboto', sans-serif;
    color: #333;
    box-sizing: border-box;
    transition: color 0.3s, background-color 0.3s;
}

body {
    background-color: #e0e0e0;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    width: 100vw;
    transition: background-color 0.3s;
}

.dark-mode {
    background-color: #2e2e2e;
    color: #ddd;
}

.container {
    width: 92%;
    max-width: 800px;
    max-height: 95vh;
    padding: 10px;
    border-radius: 20px;
    box-shadow: 20px 20px 60px #bebebe, -20px -20px 60px #ffffff;
    text-align: center;
    overflow-y: hidden;
}

h1 {
    font-size: 1.3rem;
    font-weight: 700;
    color: #333;
    padding: 5px;
    text-align: center;
    transition: color 0.3s;
}

.header {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 10px;
}

.header button {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.5rem;
    transition: color 0.3s;
}

.header button:hover {
    color: #ff9900;
}

.video-container, .controls-card, .video-form-card, .playlist {
    margin-bottom: 10px;
}

#player-container {
    position: relative;
    padding-top: 56.25%; /* 16:9 Aspect Ratio */
    margin-bottom: 10px;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: inset 10px 10px 20px #bebebe, inset -10px -10px 20px #ffffff;
}

#player {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}

.controls-card, .video-form-card, .video-item {
    padding: 15px;
    border-radius: 20px;
    box-shadow: 8px 8px 16px #bebebe, -8px -8px 16px #ffffff;
    background: #e0e0e0;
}

.dark-mode .controls-card, .dark-mode .video-form-card, .dark-mode .video-item {
    background: #2e2e2e;
    box-shadow: 8px 8px 16px #1b1b1b, -8px -8px 16px #404040;
}

.controls {
    display: flex;
    width: 100%;
    justify-content: space-between;
    align-items: center;
}

.controls .buttons {
    display: flex;
    gap: 10px;
}

.neomorphic-button {
    background: #e0e0e0;
    border: none;
    padding: 10px 20px;
    border-radius: 20px;
    box-shadow: 8px 8px 16px #bebebe, -8px -8px 16px #ffffff;
    cursor: pointer;
    transition: background 0.3s, box-shadow 0.3s;
}

.neomorphic-button:hover {
    background: #f0f0f0;
}

.neomorphic-slider {
    width: 100px;
    height: 5px;
    border-radius: 5px;
    -webkit-appearance: none;
    appearance: none;
    background: #e0e0e0;
    outline: none;
    opacity: 0.7;
    transition: opacity .15s ease-in-out;
    box-shadow: inset 8px 8px 16px #bebebe, inset -8px -8px 16px #ffffff;
}

.neomorphic-slider:hover {
    opacity: 1;
}

.neomorphic-input {
    padding: 10px;
    border-radius:
