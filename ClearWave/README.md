# ClearWave Noise Cancellation App

ClearWave is a web-based application for noise cancellation, allowing you to upload audio files, add noise, and filter the noise to get a cleaner version of your audio. The application provides a user-friendly interface for band-pass filtering using different filter types and visualizes both time-domain and frequency-domain analysis.

## Features

- Upload or record your own audio.
- Add random low/high frequency noise or use your own noisy audio.
- Filter out noise using different filter types, including Butterworth, FIR, IIR, Chebyshev Type I & II, Elliptic, and Bessel band-pass filters.
- Visualize time and frequency analysis before and after noise cancellation.
- Automatically suggest optimal low and high cutoff values based on the uploaded audio.
- Interactive plots to compare noisy and cleaned signals.
- Supports popular audio formats like WAV and MP3.

## Installation

### Step 1: Clone the Repository
```sh
$ git clone https://github.com/moontasirsoumik/Apps.git
$ cd Apps/ClearWave
```

### Step 2: Create a Virtual Environment (Optional but Recommended)
To create a virtual environment, use the following command:
```sh
$ python -m venv venv
$ source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Step 3: Install Dependencies
The following libraries are required to run the app:
- Streamlit
- Numpy
- Pandas
- Librosa
- Soundfile
- Matplotlib
- Altair
- Scipy

You can install the required libraries using:
```sh
$ pip install -r requirements.txt
```
Alternatively, install them manually using the following command:
```sh
$ pip install streamlit numpy pandas librosa soundfile matplotlib altair scipy
```

## Running the App
Once you have all the dependencies installed, you can run the app using Streamlit:
```sh
$ streamlit run app.py
```
This will start a local server, and you can open the app in your browser at `http://localhost:8501`.

## Usage
1. **Upload Audio**: Use the "Upload Audio" section to upload an audio file (WAV or MP3).
2. **Time and Frequency Analysis**: Visualize the time and frequency domains of the audio.
3. **Add Noise (Optional)**: Add low, high, or both types of noise to the audio.
4. **Apply Noise Cancellation**: Choose a filter type, set low and high cutoff frequencies, and filter the noisy audio.
5. **Compare Signals**: Compare original, noisy, and filtered audio visually through interactive plots.

## Code Structure
- **app.py**: The main application code.
- **requirements.txt**: Contains the list of dependencies for easy installation.

## Dependencies
- **[Streamlit](https://streamlit.io/)**: For building the interactive web app.
- **[Librosa](https://librosa.org/)**: For audio processing.
- **[Altair](https://altair-viz.github.io/)**: For plotting and visualization.
- **[Scipy](https://www.scipy.org/)**: For applying band-pass filters.
- **[Matplotlib](https://matplotlib.org/)**: For rendering plots.
- **[Soundfile](https://pysoundfile.readthedocs.io/en/latest/)**: For reading and writing audio files.

## Contributing
Contributions are welcome! If you have suggestions for improvements, please feel free to open an issue or create a pull request.

## License
This project does not currently have a specified license. If you are interested in contributing, please contact us for more details.

## Acknowledgements
- Inspired by the need for easy and intuitive noise cancellation tools.
- Thanks to the open-source community for providing the libraries used in this project.
