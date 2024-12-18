# ClearWave

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
- Altair
- Scipy

Create a `requirements.txt` file with the following content:
```
streamlit
numpy
pandas
librosa
soundfile
altair
scipy
```

You can install the required libraries using:
```sh
$ pip install -r requirements.txt
```
Alternatively, install them manually using the following command:
```sh
$ pip install streamlit numpy pandas librosa soundfile altair scipy
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
6. **Advanced Analysis**: Use advanced metrics and plots, such as spectral centroid, phase response, group delay, impulse response, and step response, to analyze the effects of the applied filter.

## Code Structure
- **app.py**: The main application code.
- **requirements.txt**: Contains the list of dependencies for easy installation.

## Dependencies
- **[Streamlit](https://streamlit.io/)**: For building the interactive web app.
- **[Librosa](https://librosa.org/)**: For audio processing.
- **[Altair](https://altair-viz.github.io/)**: For plotting and visualization.
- **[Scipy](https://www.scipy.org/)**: For applying band-pass filters.
- **[Soundfile](https://pysoundfile.readthedocs.io/en/latest/)**: For reading and writing audio files.

## Contributing
Contributions are welcome! If you have suggestions for improvements, please feel free to open an issue or create a pull request.

Special thanks to ChatGPT 4o for adding detailed comments in the code and helping write this README file.

## License
This project does not currently have a specified license. If you are interested in contributing, please contact us for more details.

## Acknowledgements
- Inspired by the need for easy and intuitive noise cancellation tools.
- Thanks to the open-source community for providing the libraries used in this project.

## Contact
For questions or suggestions, feel free to contact us at [moontasir.soumik@helsinki.fi].

## Appendix: Filter Types Explained

### 1. Butterworth Band-pass Filter
The Butterworth filter is designed to have as flat a frequency response as possible in the passband. It has no ripples in either the passband or the stopband, making it ideal for applications requiring a smooth frequency response. The Butterworth filter is often used in audio processing because it provides a balance between simplicity and performance, offering a relatively gradual roll-off without introducing much distortion.

### 2. FIR Band-pass Filter
Finite Impulse Response (FIR) filters have a finite response to an impulse input, meaning that the filter output eventually settles to zero. FIR filters are inherently stable and can provide a linear phase response, which preserves the shape of the input signal. This makes FIR filters suitable for applications where maintaining the phase integrity of the signal is important, such as in audio and communication systems.

### 3. IIR Band-pass Filter
Infinite Impulse Response (IIR) filters have an impulse response that theoretically continues indefinitely. IIR filters can achieve a sharper cutoff with fewer coefficients compared to FIR filters, making them more efficient for certain applications. However, they may introduce phase distortion, which can affect the shape of the filtered signal. IIR filters, like the Butterworth type, are commonly used when computational efficiency is crucial.

### 4. Chebyshev Type I Band-pass Filter
The Chebyshev Type I filter provides a steeper roll-off compared to the Butterworth filter by allowing ripples in the passband. The amount of ripple is determined by a parameter that can be adjusted to control the trade-off between passband flatness and roll-off steepness. Chebyshev Type I filters are used in applications where a sharper transition between passband and stopband is required, and some variation in the passband can be tolerated.

### 5. Chebyshev Type II Band-pass Filter
Chebyshev Type II filters have a steeper roll-off by allowing ripples in the stopband rather than the passband, resulting in a flat passband response. This type of filter is useful when the passband must remain flat, but some attenuation in the stopband is acceptable. Chebyshev Type II filters provide a good balance between roll-off steepness and passband performance, making them suitable for applications where maintaining a clean passband is important.

### 6. Elliptic Band-pass Filter
The elliptic (or Cauer) filter provides the steepest roll-off for a given filter order by allowing ripples in both the passband and stopband. This makes the elliptic filter highly efficient in terms of achieving a narrow transition band. However, the presence of ripples in both the passband and stopband means that this filter may introduce more distortion compared to other filter types. Elliptic filters are often used in applications that require the most efficient use of filter order, such as in communication systems.

### 7. Bessel Band-pass Filter
The Bessel filter is designed to provide a maximally flat group delay, which helps preserve the wave shape of filtered signals, particularly in the time domain. This makes Bessel filters ideal for audio applications and other situations where maintaining the temporal characteristics of the signal is crucial. The Bessel filter sacrifices some roll-off sharpness to achieve a constant group delay, which ensures minimal phase distortion.

### Suggested Cutoff Frequencies
The suggested cutoff frequencies for the band-pass filters are determined based on the spectral characteristics of the uploaded audio. Specifically, the algorithm calculates the spectral centroid (which represents the center of mass of the frequency spectrum) and the cumulative energy distribution to identify where most of the audio's energy is concentrated. The lower cutoff frequency is typically suggested based on the point where 10% of the total energy is reached, and the higher cutoff frequency is based on the point where 90% of the total energy is reached. This approach ensures that the majority of the signal's meaningful content is preserved while filtering out noise.

### Plots Explained
- **Time-Domain Plot**: This plot represents the variation in amplitude of the audio signal over time. It helps visualize the overall structure of the audio, including loud and quiet sections, and allows comparison between the original, noisy, and cleaned signals.

- **Frequency-Domain Plot**: This plot shows the magnitude of different frequency components present in the audio signal. It helps identify which frequencies are prominent in the audio and how the filter affects these frequencies. The plot is particularly useful for understanding the effect of noise and the efficiency of the noise cancellation process.

- **Spectral Centroid Plot**: The spectral centroid represents the "center of mass" of the audio spectrum and provides a measure of the brightness of the sound. A higher spectral centroid indicates that higher frequencies are more prominent. This plot helps visualize how the filtering process affects the distribution of energy across the frequency spectrum.

- **Filter Response Plot**: This plot shows the frequency response of the selected filter, illustrating how the filter attenuates or passes different frequency components. It helps understand the characteristics of the filter and how it will affect the audio signal.

- **Phase Response Plot**: The phase response plot shows how the phase of different frequency components is affected by the filter. This is particularly important for understanding any potential phase distortion introduced by the filter.

- **Group Delay Plot**: Group delay represents the time delay experienced by different frequency components as they pass through the filter. The Bessel filter, for instance, is designed to have a flat group delay to preserve the time-domain characteristics of the signal.

- **Impulse Response Plot**: The impulse response represents how the filter reacts to an impulse input (a single spike). It provides insight into the filter's behavior and stability.

- **Step Response Plot**: The step response represents how the filter reacts to a step input (a sudden change from zero to one). It helps in understanding the transient behavior of the filter and how quickly it stabilizes.

- **Poles and Zeros Plot**: The poles and zeros plot is used for analyzing the stability and frequency response of the filter. The positions of poles and zeros in the complex plane provide insight into how the filter behaves and whether it is stable.

- **SNR vs Frequency Plot**: This plot represents the Signal-to-Noise Ratio (SNR) across different frequencies, providing insight into how effectively noise has been reduced across the frequency spectrum.

- **Time-Domain Comparison Plot**: This plot compares the time-domain signals of multiple filtered versions of the audio, allowing for a visual comparison of the effects of different filters.
