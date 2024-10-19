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

Special thanks to ChatGPT 4.0 for adding detailed comments in the code and helping write this README file.

## License
This project does not currently have a specified license. If you are interested in contributing, please contact us for more details.

## Acknowledgements
- Inspired by the need for easy and intuitive noise cancellation tools.
- Thanks to the open-source community for providing the libraries used in this project.

## Contact
For questions or suggestions, feel free to contact us at [moontasir.soumik@helsinki.fi].

## Appendix: Filter Types Explained

### 1. Butterworth Band-pass Filter
The Butterworth filter is designed to have as flat a frequency response as possible in the passband. It is characterized by having no ripples in the passband or stopband. The frequency response \( H(s) \) of a Butterworth filter is given by:

\[
|H(j\omega)| = \frac{1}{\sqrt{1 + (\frac{\omega}{\omega_c})^{2n}}}
\]

where \( \omega_c \) is the cutoff frequency and \( n \) is the order of the filter. Higher-order filters have a steeper roll-off.

### 2. FIR Band-pass Filter
Finite Impulse Response (FIR) filters have a finite duration response to an impulse input. The FIR filter is represented by:

\[
y[n] = \sum_{k=0}^{N-1} b_k x[n-k]
\]

where \( b_k \) are the filter coefficients, \( N \) is the number of taps, and \( x[n] \) is the input signal. FIR filters are always stable and can provide a linear phase response, which is ideal for preserving the wave shape of signals.

### 3. IIR Band-pass Filter
Infinite Impulse Response (IIR) filters have an impulse response that lasts indefinitely. The general form of an IIR filter is:

\[
y[n] = \sum_{k=0}^{M} b_k x[n-k] - \sum_{k=1}^{N} a_k y[n-k]
\]

where \( b_k \) and \( a_k \) are the filter coefficients. IIR filters, such as the Butterworth type, provide a sharper cutoff with fewer coefficients compared to FIR filters but may introduce phase distortion.

### 4. Chebyshev Type I Band-pass Filter
The Chebyshev Type I filter has a steeper roll-off compared to the Butterworth filter by allowing ripples in the passband. The magnitude response is given by:

\[
|H(j\omega)| = \frac{1}{\sqrt{1 + \epsilon^2 T_n^2(\frac{\omega}{\omega_c})}}
\]

where \( T_n \) is the Chebyshev polynomial of the \( n \)-th order, \( \epsilon \) controls the passband ripple, and \( \omega_c \) is the cutoff frequency.

### 5. Chebyshev Type II Band-pass Filter
Chebyshev Type II filters allow ripples in the stopband instead of the passband, providing a flat passband response. The magnitude response is given by:

\[
|H(j\omega)| = \frac{1}{\sqrt{1 + \frac{1}{\epsilon^2} T_n^2(\frac{\omega_c}{\omega})}}
\]

where \( \epsilon \) controls the stopband attenuation and \( T_n \) is the Chebyshev polynomial of the \( n \)-th order. These filters provide a sharper transition compared to Type I filters.

### 6. Elliptic Band-pass Filter
The elliptic (or Cauer) filter offers the steepest roll-off for a given order by allowing ripples in both the passband and stopband. The magnitude response is given by:

\[
|H(j\omega)| = \frac{1}{\sqrt{1 + \epsilon_1^2 R_n^2(\omega)}}
\]

where \( R_n \) is the elliptic rational function, and \( \epsilon_1 \) and \( \epsilon_2 \) control the ripples in the passband and stopband, respectively. This filter is highly efficient but introduces variations in both passband and stopband.

### 7. Bessel Band-pass Filter
The Bessel filter is designed to provide a maximally flat group delay, which preserves the wave shape of filtered signals. The transfer function of a Bessel filter is derived from Bessel polynomials, ensuring a linear phase response in the passband. The group delay remains constant, which makes it suitable for audio applications where maintaining the shape of the signal is crucial.
