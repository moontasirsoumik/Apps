import streamlit as st
import numpy as np
import pandas as pd
import librosa
import soundfile as sf
import matplotlib.patheffects as path_effects
from scipy import signal
from scipy.signal import (
    butter,
    lfilter,
    firwin,
    freqz,
    iirfilter,
    cheby1,
    cheby2,
    ellip,
    bessel,
)
import io
import altair as alt

all_filters = [
    "Butterworth Band-pass",
    "FIR Band-pass",
    "IIR Band-pass",
    "Chebyshev Type I Band-pass",
    "Chebyshev Type II Band-pass",
    "Elliptic Band-pass",
    "Bessel Band-pass",
]


def butter_bandpass(lowcut, highcut, fs, order=5):
    """
    Design a Butterworth band-pass filter, which provides a smooth frequency response.

    Parameters:
    - lowcut: Low cutoff frequency (Hz).
    - highcut: High cutoff frequency (Hz).
    - fs: Sampling frequency (Hz).
    - order: Filter order, which defines the steepness of the filter transition.

    Returns:
    - b, a: Numerator (b) and denominator (a) polynomials of the IIR filter.
    """
    nyquist = 0.5 * fs  # Nyquist frequency, half the sampling rate
    low = lowcut / nyquist  # Normalize the low cutoff frequency
    high = highcut / nyquist  # Normalize the high cutoff frequency
    b, a = butter(
        order, [low, high], btype="band"
    )  # Design Butterworth band-pass filter
    return b, a


def fir_bandpass(lowcut, highcut, fs, numtaps=101):
    """
    Design a FIR band-pass filter with a specified number of taps.

    Parameters:
    - lowcut: Low cutoff frequency (Hz).
    - highcut: High cutoff frequency (Hz).
    - fs: Sampling frequency (Hz).
    - numtaps: Number of filter taps, controlling the filter order.

    Returns:
    - taps: FIR filter coefficients, defining the filter's impulse response.
    """
    nyquist = 0.5 * fs  # Nyquist frequency
    taps = firwin(
        numtaps, [lowcut / nyquist, highcut / nyquist], pass_zero=False
    )  # Design FIR band-pass filter
    return taps


def iir_bandpass(lowcut, highcut, fs, order=5):
    """
    Design a general IIR band-pass filter (Butterworth by default).

    Parameters:
    - lowcut: Low cutoff frequency (Hz).
    - highcut: High cutoff frequency (Hz).
    - fs: Sampling frequency (Hz).
    - order: Filter order.

    Returns:
    - b, a: Numerator (b) and denominator (a) polynomials of the IIR filter.
    """
    nyquist = 0.5 * fs  # Nyquist frequency
    low = lowcut / nyquist  # Normalize low cutoff frequency
    high = highcut / nyquist  # Normalize high cutoff frequency
    b, a = iirfilter(
        order, [low, high], btype="band", ftype="butter"
    )  # Design IIR filter with Butterworth characteristics
    return b, a


def cheby1_bandpass(lowcut, highcut, fs, order=5, rp=0.5):
    """
    Design a Chebyshev Type I band-pass filter with ripple in the passband.

    Parameters:
    - lowcut: Low cutoff frequency (Hz).
    - highcut: High cutoff frequency (Hz).
    - fs: Sampling frequency (Hz).
    - order: Filter order.
    - rp: Maximum ripple allowed in the passband (in dB).

    Returns:
    - b, a: Numerator (b) and denominator (a) polynomials of the IIR filter.
    """
    nyquist = 0.5 * fs  # Nyquist frequency
    low = lowcut / nyquist  # Normalize low cutoff frequency
    high = highcut / nyquist  # Normalize high cutoff frequency
    b, a = cheby1(
        order, rp, [low, high], btype="band"
    )  # Design Chebyshev Type I band-pass filter
    return b, a


def cheby2_bandpass(lowcut, highcut, fs, order=5, rs=20):
    """
    Design a Chebyshev Type II band-pass filter with attenuation in the stopband.

    Parameters:
    - lowcut: Low cutoff frequency (Hz).
    - highcut: High cutoff frequency (Hz).
    - fs: Sampling frequency (Hz).
    - order: Filter order.
    - rs: Minimum attenuation required in the stopband (in dB).

    Returns:
    - b, a: Numerator (b) and denominator (a) polynomials of the IIR filter.
    """
    nyquist = 0.5 * fs  # Nyquist frequency
    low = lowcut / nyquist  # Normalize low cutoff frequency
    high = highcut / nyquist  # Normalize high cutoff frequency
    b, a = cheby2(
        order, rs, [low, high], btype="band"
    )  # Design Chebyshev Type II band-pass filter
    return b, a


def ellip_bandpass(lowcut, highcut, fs, order=5, rp=0.5, rs=20):
    """
    Design an elliptic (Cauer) band-pass filter with ripple in the passband and stopband.

    Parameters:
    - lowcut: Low cutoff frequency (Hz).
    - highcut: High cutoff frequency (Hz).
    - fs: Sampling frequency (Hz).
    - order: Filter order.
    - rp: Maximum ripple allowed in the passband (in dB).
    - rs: Minimum attenuation required in the stopband (in dB).

    Returns:
    - b, a: Numerator (b) and denominator (a) polynomials of the IIR filter.
    """
    nyquist = 0.5 * fs  # Nyquist frequency
    low = lowcut / nyquist  # Normalize low cutoff frequency
    high = highcut / nyquist  # Normalize high cutoff frequency
    b, a = ellip(
        order, rp, rs, [low, high], btype="band"
    )  # Design elliptic band-pass filter
    return b, a


def bessel_bandpass(lowcut, highcut, fs, order=5):
    """
    Design a Bessel band-pass filter with a maximally flat group delay.

    Parameters:
    - lowcut: Low cutoff frequency (Hz).
    - highcut: High cutoff frequency (Hz).
    - fs: Sampling frequency (Hz).
    - order: Filter order.

    Returns:
    - b, a: Numerator (b) and denominator (a) polynomials of the IIR filter.
    """
    nyquist = 0.5 * fs  # Nyquist frequency
    low = lowcut / nyquist  # Normalize low cutoff frequency
    high = highcut / nyquist  # Normalize high cutoff frequency
    b, a = bessel(order, [low, high], btype="band")  # Design Bessel band-pass filter
    return b, a


def apply_filter(data, lowcut, highcut, fs, filter_type, order=5, rp=None, rs=None):
    """
    Apply the selected filter type to the input audio data.

    Parameters:
    - data: Input audio data (numpy array).
    - lowcut: Low cutoff frequency (Hz).
    - highcut: High cutoff frequency (Hz).
    - fs: Sampling frequency (Hz).
    - filter_type: Type of filter to apply (e.g., 'Butterworth', 'FIR').
    - order: Filter order (applicable to IIR filters).
    - rp: Passband ripple (dB) for Chebyshev I and Elliptic filters (optional).
    - rs: Stopband attenuation (dB) for Chebyshev II and Elliptic filters (optional).

    Returns:
    - Filtered audio data (numpy array).
    """
    if filter_type == "Butterworth Band-pass":
        b, a = butter_bandpass(lowcut, highcut, fs, order)  # Design Butterworth filter
        return lfilter(b, a, data)  # Apply filter to the input data
    elif filter_type == "FIR Band-pass":
        taps = fir_bandpass(lowcut, highcut, fs)  # Design FIR filter
        return lfilter(taps, 1.0, data)  # Apply FIR filter
    elif filter_type == "IIR Band-pass":
        b, a = iir_bandpass(lowcut, highcut, fs, order)  # Design general IIR filter
        return lfilter(b, a, data)  # Apply IIR filter
    elif filter_type == "Chebyshev Type I Band-pass":
        # Use the provided rp, or fall back to a default if not provided
        rp = rp if rp is not None else 0.5
        b, a = cheby1_bandpass(
            lowcut, highcut, fs, order, rp
        )  # Design Chebyshev Type I filter
        return lfilter(b, a, data)  # Apply Chebyshev Type I filter
    elif filter_type == "Chebyshev Type II Band-pass":
        # Use the provided rs, or fall back to a default if not provided
        rs = rs if rs is not None else 20
        b, a = cheby2_bandpass(
            lowcut, highcut, fs, order, rs
        )  # Design Chebyshev Type II filter
        return lfilter(b, a, data)  # Apply Chebyshev Type II filter
    elif filter_type == "Elliptic Band-pass":
        # Use the provided rp and rs, or fall back to defaults if not provided
        rp = rp if rp is not None else 0.5
        rs = rs if rs is not None else 20
        b, a = ellip_bandpass(
            lowcut, highcut, fs, order, rp, rs
        )  # Design elliptic filter
        return lfilter(b, a, data)  # Apply elliptic filter
    elif filter_type == "Bessel Band-pass":
        b, a = bessel_bandpass(lowcut, highcut, fs, order)  # Design Bessel filter
        return lfilter(b, a, data)  # Apply Bessel filter


@st.cache_data
def suggest_bandpass_values(audio_data, sr):
    """
    Suggest advanced band-pass filter cutoff values based on multiple audio characteristics,
    including spectral centroid, rolloff, flatness, and bandwidth.

    Parameters:
    - audio_data: Input audio data.
    - sr: Sampling rate.

    Returns:
    - lowcut_suggested: Suggested low cutoff frequency.
    - highcut_suggested: Suggested high cutoff frequency.
    """
    # Perform Fast Fourier Transform (FFT) on the audio data
    fft = np.fft.fft(audio_data)
    freqs = np.fft.fftfreq(len(fft), 1 / sr)
    magnitude = np.abs(fft)

    # Focus on positive frequencies (first half of the FFT output)
    positive_freqs = freqs[: len(freqs) // 2]
    positive_magnitude = magnitude[: len(magnitude) // 2]

    # Calculate the total energy of the positive frequencies
    total_energy = np.sum(positive_magnitude)

    # Calculate the spectral centroid (center of mass of the spectrum)
    spectral_centroid = np.sum(positive_freqs * positive_magnitude) / total_energy

    # Compute the cumulative energy for spectral rolloff calculation
    cumulative_energy = np.cumsum(positive_magnitude) / total_energy

    # Spectral rolloff: frequency below which 85% of the energy is concentrated
    spectral_rolloff = positive_freqs[np.searchsorted(cumulative_energy, 0.85)]

    # Compute spectral flatness (a measure of noisiness) and spectral bandwidth (spread of energy)
    spectral_flatness = librosa.feature.spectral_flatness(y=audio_data)[0]
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sr)[0]

    # Estimate low and high cutoff based on the 10th and 90th percentile of the energy distribution
    lowcut_suggested = positive_freqs[np.searchsorted(cumulative_energy, 0.1)]
    highcut_suggested = positive_freqs[np.searchsorted(cumulative_energy, 0.9)]

    # Adjust the low and high cutoff based on spectral centroid and rolloff
    lowcut_suggested = (lowcut_suggested + spectral_centroid * 0.2) / 2
    highcut_suggested = (highcut_suggested + spectral_rolloff * 0.8) / 2

    # If spectral flatness suggests high noise, reduce the high cutoff
    if (
        np.mean(spectral_flatness) > 0.3
    ):  # Higher flatness indicates more noise-like signal
        highcut_suggested = (
            highcut_suggested * 0.8
        )  # Lower the high cutoff to filter noise

    # Further adjust the low and high cutoff based on spectral bandwidth
    lowcut_suggested = min(lowcut_suggested, np.mean(spectral_bandwidth) * 0.2)
    highcut_suggested = max(highcut_suggested, np.mean(spectral_bandwidth) * 1.2)

    return int(lowcut_suggested), int(highcut_suggested)


@st.cache_data
def load_audio(audio_file):
    """
    Load the uploaded audio file into memory.

    Parameters:
    - audio_file: The uploaded audio file.

    Returns:
    - audio_data: The audio data as a numpy array.
    - sr: Sampling rate of the audio.
    """
    audio_data, sr = librosa.load(audio_file, sr=None)
    return audio_data, sr


primary_color = "#00CC66"  # Matte green used for cleaned signals
secondary_color = "#FF4B4B"  # Matte red used for noisy signals
tertiary_color = "#3399FF"  # Matte blue used for neutral signals


def apply_text_effects():
    """
    Apply text effects for plot labels to enhance visibility.

    Returns:
    - List of path_effects for text styling.
    """
    return [path_effects.Stroke(linewidth=3, foreground="white"), path_effects.Normal()]


def filter_customization_panel(
    audio_data,
    lowcut,
    highcut,
    sr,
    filter_type,
    default_order=5,
    default_rp=0.5,
    default_rs=20,
):
    """
    Create an interactive filter customization panel where users can modify filter parameters and visualize the result.

    Parameters:
    - audio_data: Input audio signal.
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - sr: Sampling rate.
    - filter_type: Type of filter (e.g., Butterworth, Chebyshev, Elliptic).
    - default_order: Default filter order.
    - default_rp: Default passband ripple (for Chebyshev I and Elliptic filters).
    - default_rs: Default stopband ripple (for Chebyshev II and Elliptic filters).

    Returns:
    - filter_order: The selected filter order.
    - rp: The passband ripple value (if applicable).
    - rs: The stopband ripple value (if applicable).
    """

    # General Filter Customization Controls
    st.write("**Filter Customization**")

    # Slider for Filter Order (applies to most filters), with a unique key
    filter_order = st.slider(
        "Filter Order",
        min_value=1,
        max_value=10,
        value=default_order,
        key="filter_order_slider",
    )

    # Additional controls for ripple parameters (for Chebyshev I, II and Elliptic filters), with unique keys
    if filter_type in ["Chebyshev Type I Band-pass", "Elliptic Band-pass"]:
        rp = st.slider(
            "Passband Ripple (dB)",
            min_value=0.1,
            max_value=5.0,
            value=default_rp,
            step=0.1,
            key="passband_ripple_slider",
        )
    else:
        rp = None

    if filter_type in ["Chebyshev Type II Band-pass", "Elliptic Band-pass"]:
        rs = st.slider(
            "Stopband Ripple (dB)",
            min_value=5,
            max_value=40,
            value=default_rs,
            step=1,
            key="stopband_ripple_slider",
        )
    else:
        rs = None

    # Apply the filter with customized parameters
    if filter_type == "Butterworth Band-pass":
        b, a = butter_bandpass(lowcut, highcut, sr, filter_order)
    elif filter_type == "FIR Band-pass":
        b, a = fir_bandpass(lowcut, highcut, sr), 1.0
    elif filter_type == "IIR Band-pass":
        b, a = iir_bandpass(lowcut, highcut, sr, filter_order)
    elif filter_type == "Chebyshev Type I Band-pass":
        b, a = cheby1_bandpass(lowcut, highcut, sr, filter_order, rp)
    elif filter_type == "Chebyshev Type II Band-pass":
        b, a = cheby2_bandpass(lowcut, highcut, sr, filter_order, rs)
    elif filter_type == "Elliptic Band-pass":
        b, a = ellip_bandpass(lowcut, highcut, sr, filter_order, rp, rs)
    elif filter_type == "Bessel Band-pass":
        b, a = bessel_bandpass(lowcut, highcut, sr, filter_order)

    # Plot the frequency response of the customized filter
    w, h = freqz(b, a, worN=2000)
    freqs = (sr * 0.5 / np.pi) * w

    # Apply a small epsilon to avoid log of zero
    epsilon = 1e-10
    gain = 20 * np.log10(np.abs(h) + epsilon)  # Avoid log(0) by adding epsilon

    # Prepare the data for plotting
    df = pd.DataFrame({"Frequency (Hz)": freqs, "Gain (dB)": gain})

    # Create an Altair plot for the filter response
    chart = (
        alt.Chart(df)
        .mark_line(opacity=0.7, color=primary_color)
        .encode(
            x=alt.X(
                "Frequency (Hz)",
                title="Frequency (Hz)",
                scale=alt.Scale(domain=[0, sr / 2]),
            ),
            y=alt.Y("Gain (dB)", title="Gain (dB)", scale=alt.Scale(domain=[-60, 5])),
            color=alt.value(tertiary_color),
            tooltip=["Frequency (Hz)", "Gain (dB)"],
        )
        .properties(
            title=f"{filter_type} - Frequency Response (Order: {filter_order})",
            width=600,
            autosize=alt.AutoSizeParams(type="fit", contains="padding"),
        )
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)

    # Return the necessary parameters
    return filter_order, rp, rs


def plot_time_domain(
    noisy_audio,
    cleaned_audio=None,
    sr=44100,
    noisy="Noisy",
    cleaned="Cleaned",
    max_points=5000,
):
    """
    Plot the time-domain signal of noisy and cleaned audio data.

    Parameters:
    - noisy_audio: Noisy audio signal.
    - cleaned_audio: Cleaned audio signal (optional).
    - sr: Sampling rate.
    - noisy: Label for noisy audio.
    - cleaned: Label for cleaned audio.
    - max_points: Maximum number of points to plot.
    """
    time = np.linspace(0, len(noisy_audio) / sr, len(noisy_audio))
    step = max(1, len(noisy_audio) // max_points)
    time_downsampled = time[::step]
    noisy_downsampled = noisy_audio[::step]

    # Noisy audio plot only
    if cleaned_audio is None:
        df = pd.DataFrame(
            {"Time (s)": time_downsampled, "Amplitude": noisy_downsampled}
        )
        chart = (
            alt.Chart(df)
            .mark_line(opacity=0.5, color=tertiary_color)
            .encode(
                x="Time (s)",
                y=alt.Y("Amplitude", title="Amplitude"),
                tooltip=["Time (s)", "Amplitude"],
            )
            .properties(
                title="Time-Domain Signal",
                width=500,
                autosize=alt.AutoSizeParams(type="fit", contains="padding"),
            )
            .interactive()
        )

    # Both noisy and cleaned audio plots
    else:
        cleaned_downsampled = cleaned_audio[::step]
        df = pd.DataFrame(
            {
                "Time (s)": time_downsampled,
                noisy: noisy_downsampled,
                cleaned: cleaned_downsampled,
            }
        )
        df_melted = df.melt("Time (s)", var_name="Signal", value_name="Amplitude")
        signal_color = tertiary_color if cleaned == "Original" else primary_color
        chart = (
            alt.Chart(df_melted)
            .mark_line(opacity=0.5)
            .encode(
                x="Time (s)",
                y=alt.Y("Amplitude", title="Amplitude"),
                color=alt.Color(
                    "Signal",
                    scale=alt.Scale(
                        domain=[noisy, cleaned], range=[secondary_color, signal_color]
                    ),
                ),
                tooltip=["Time (s)", "Amplitude", "Signal"],
            )
            .properties(
                title="Time-Domain Signal",
                width=500,
                autosize=alt.AutoSizeParams(type="fit", contains="padding"),
            )
            .interactive()
        )

    st.altair_chart(chart, use_container_width=True)


@st.cache_data
def plot_frequency_domain(
    noisy_audio,
    cleaned_audio=None,
    sr=44100,
    lowcut=None,
    highcut=None,
    max_points=5000,
):
    """
    Plot the frequency-domain signal of noisy and cleaned audio data.

    Parameters:
    - noisy_audio: Noisy audio signal.
    - cleaned_audio: Cleaned audio signal (optional).
    - sr: Sampling rate.
    - lowcut: Low cutoff frequency (for marking on the plot).
    - highcut: High cutoff frequency (for marking on the plot).
    - max_points: Maximum number of points to plot.
    """
    noisy_fft = np.fft.fft(noisy_audio)
    freqs = np.fft.fftfreq(len(noisy_fft), 1 / sr)

    # Positive frequency components
    positive_freqs = freqs[: len(freqs) // 2]
    noisy_magnitude = np.abs(noisy_fft[: len(freqs) // 2])

    # Downsample for plot clarity
    step = max(1, len(positive_freqs) // max_points)
    freqs_downsampled = positive_freqs[::step]
    noisy_magnitude_downsampled = noisy_magnitude[::step]

    # Plot only noisy signal
    if cleaned_audio is None:
        df = pd.DataFrame(
            {
                "Frequency (Hz)": freqs_downsampled,
                "Magnitude": noisy_magnitude_downsampled,
            }
        )
        chart = (
            alt.Chart(df)
            .mark_area(opacity=0.5)
            .encode(
                x=alt.X(
                    "Frequency (Hz):Q",
                    scale=alt.Scale(type="log", domain=[1, sr / 2]),
                    title="Frequency (Hz, log scale)",
                ),
                y=alt.Y("Magnitude", title="Magnitude"),
                color=alt.value(tertiary_color),
                tooltip=["Frequency (Hz)", "Magnitude"],
            )
            .properties(title="Frequency-Domain Magnitude Spectrum", width=500)
            .interactive()
        )

    # Plot both noisy and cleaned signals
    else:
        cleaned_fft = np.fft.fft(cleaned_audio)
        cleaned_magnitude = np.abs(cleaned_fft[: len(freqs) // 2])
        cleaned_magnitude_downsampled = cleaned_magnitude[::step]
        df = pd.DataFrame(
            {
                "Frequency (Hz)": freqs_downsampled,
                "Noisy Magnitude": noisy_magnitude_downsampled,
                "Cleaned Magnitude": cleaned_magnitude_downsampled,
            }
        )
        df_melted = df.melt("Frequency (Hz)", var_name="Signal", value_name="Magnitude")
        chart = (
            alt.Chart(df_melted)
            .mark_area(opacity=0.5)
            .encode(
                x=alt.X(
                    "Frequency (Hz):Q",
                    scale=alt.Scale(type="log", domain=[1, sr / 2]),
                    title="Frequency (Hz, log scale)",
                ),
                y=alt.Y("Magnitude", title="Magnitude"),
                color=alt.Color(
                    "Signal",
                    scale=alt.Scale(
                        domain=["Noisy Magnitude", "Cleaned Magnitude"],
                        range=[secondary_color, primary_color],
                    ),
                ),
                tooltip=["Frequency (Hz)", "Magnitude", "Signal"],
            )
            .properties(title="Frequency-Domain Magnitude Spectrum", width=500)
            .interactive()
        )

        # Plot cutoff frequencies as vertical lines
        if lowcut is not None and highcut is not None:
            cutoff_df = pd.DataFrame(
                {
                    "Frequency (Hz)": [lowcut, highcut],
                    "Magnitude": [0, 0],
                    "Cutoff Frequency": ["Low Cutoff", "High Cutoff"],
                }
            )
            cutoff_lines = (
                alt.Chart(cutoff_df)
                .mark_rule(strokeDash=[5, 5])
                .encode(
                    x=alt.X(
                        "Frequency (Hz):Q",
                        scale=alt.Scale(type="log", domain=[1, sr / 2]),
                    ),
                    color=alt.Color(
                        "Cutoff Frequency",
                        scale=alt.Scale(
                            domain=["Low Cutoff", "High Cutoff"],
                            range=["#1f77b4", "#ff7f0e"],
                        ),
                    ),
                    size=alt.value(1),
                    tooltip=["Cutoff Frequency"],
                )
            )
            chart = alt.layer(chart, cutoff_lines).properties(
                autosize=alt.AutoSizeParams(type="fit", contains="padding")
            )

    st.altair_chart(chart, use_container_width=True)


@st.cache_data
def plot_filter_response(lowcut, highcut, sr, filter_type=None, filters=None, order=5):
    """
    Plot the frequency response for multiple filters, allowing for comparison of different filter types.

    Parameters:
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - sr: Sampling rate.
    - filter_type: Single filter type to plot if filters list is not provided.
    - filters: List of filter types to plot if multiple filters are to be compared.
    - order: Filter order (applicable to IIR filters).

    Returns:
    - None: Displays an interactive Altair plot of the frequency responses.
    """

    # Function to compute the frequency response of the selected filter
    def get_filter_response(filter_type, lowcut, highcut, sr, order):
        if filter_type == "Butterworth Band-pass":
            b, a = butter_bandpass(lowcut, highcut, sr, order)
        elif filter_type == "FIR Band-pass":
            taps = fir_bandpass(lowcut, highcut, sr)
            b, a = taps, 1.0
        elif filter_type == "IIR Band-pass":
            b, a = iir_bandpass(lowcut, highcut, sr, order)
        elif filter_type == "Chebyshev Type I Band-pass":
            b, a = cheby1_bandpass(lowcut, highcut, sr, order)
        elif filter_type == "Chebyshev Type II Band-pass":
            b, a = cheby2_bandpass(lowcut, highcut, sr, order)
        elif filter_type == "Elliptic Band-pass":
            b, a = ellip_bandpass(lowcut, highcut, sr, order)
        elif filter_type == "Bessel Band-pass":
            b, a = bessel_bandpass(lowcut, highcut, sr, order)
        # Calculate the frequency response (w = frequencies, h = frequency response values)
        return freqz(b, a, worN=2000)

    # If no list of filters is provided, use the single filter type
    if filters is None:
        filters = [filter_type]

    combined_df = pd.DataFrame()  # DataFrame to store all the filter responses

    # Loop over each filter type in the list and compute its frequency response
    for filt in filters:
        w, h = get_filter_response(filt, lowcut, highcut, sr, order)
        # Create a DataFrame to store frequency and gain for the current filter
        df = pd.DataFrame(
            {"Frequency (Hz)": (sr * 0.5 / np.pi) * w, "Gain": abs(h), "Filter": filt}
        )
        # Append the current filter's response to the combined DataFrame
        combined_df = pd.concat([combined_df, df])

    # Plot the frequency response using Altair
    chart = (
        alt.Chart(combined_df)
        .mark_line(opacity=0.5)  # Set opacity for the lines
        .encode(
            x=alt.X(
                "Frequency (Hz)", scale=alt.Scale(domain=(0, sr / 2))
            ),  # X-axis represents frequency
            y=alt.Y("Gain", title="Gain"),  # Y-axis represents gain
            color="Filter",  # Color by filter type
            tooltip=[
                "Frequency (Hz)",
                "Gain",
                "Filter",
            ],  # Show tooltips for data points
        )
        .properties(
            title="Frequency Response",  # Title of the plot
            width=500,  # Set plot width
            autosize=alt.AutoSizeParams(
                type="fit", contains="padding"
            ),  # Auto-size to fit
        )
        .interactive()  # Enable interactive features
    )

    # Display the Altair chart in Streamlit
    st.altair_chart(chart, use_container_width=True)


@st.cache_data
def plot_spectral_centroid(audio_data, sr):
    """
    Plot the spectral centroid over time, which indicates the 'center of mass' of the spectrum.

    Parameters:
    - audio_data: Input audio signal.
    - sr: Sampling rate.

    Returns:
    - None: Displays an interactive Altair plot of the spectral centroid.
    """

    # Compute the spectral centroid of the audio signal
    spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sr)[0]

    # Convert the frames to time for plotting
    frames = range(len(spectral_centroid))
    t = librosa.frames_to_time(frames)

    # Prepare the data for plotting
    df = pd.DataFrame({"Time (s)": t, "Spectral Centroid (Hz)": spectral_centroid})

    # Create an Altair line chart to plot the spectral centroid over time
    chart = (
        alt.Chart(df)
        .mark_line(opacity=0.5, color=primary_color)  # Set the color and opacity
        .encode(
            x=alt.X("Time (s)", title="Time (s)"),  # X-axis represents time
            y=alt.Y(
                "Spectral Centroid (Hz)", title="Spectral Centroid (Hz)"
            ),  # Y-axis represents spectral centroid
            tooltip=["Time (s)", "Spectral Centroid (Hz)"],  # Tooltips for the plot
        )
        .properties(
            title="Spectral Centroid Over Time",  # Title of the plot
            width=500,  # Set plot width
            autosize=alt.AutoSizeParams(
                type="fit", contains="padding"
            ),  # Auto-size to fit
        )
        .interactive()  # Enable interactivity for the plot
    )

    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)


@st.cache_data
def plot_phase_response(lowcut, highcut, sr, filter_type=None, filters=None, order=5):
    """
    Plot the phase response for multiple filters, allowing for comparison of different filter types.

    Parameters:
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - sr: Sampling rate.
    - filter_type: Single filter type to plot if filters list is not provided.
    - filters: List of filter types to plot if multiple filters are to be compared.
    - order: Filter order (applicable to IIR filters).

    Returns:
    - None: Displays an interactive Altair plot of the phase responses.
    """

    # Function to compute the phase response of the selected filter
    def get_phase_response(filter_type, lowcut, highcut, sr, order):
        if filter_type == "Butterworth Band-pass":
            b, a = butter_bandpass(lowcut, highcut, sr, order)
        elif filter_type == "FIR Band-pass":
            taps = fir_bandpass(lowcut, highcut, sr)
            b, a = taps, 1.0
        elif filter_type == "IIR Band-pass":
            b, a = iir_bandpass(lowcut, highcut, sr, order)
        elif filter_type == "Chebyshev Type I Band-pass":
            b, a = cheby1_bandpass(lowcut, highcut, sr, order)
        elif filter_type == "Chebyshev Type II Band-pass":
            b, a = cheby2_bandpass(lowcut, highcut, sr, order)
        elif filter_type == "Elliptic Band-pass":
            b, a = ellip_bandpass(lowcut, highcut, sr, order)
        elif filter_type == "Bessel Band-pass":
            b, a = bessel_bandpass(lowcut, highcut, sr, order)
        w, h = freqz(b, a, worN=2000)  # Get frequency and phase response
        return w, np.angle(h)  # Return the frequencies and phase values

    # If no list of filters is provided, use the single filter type
    if filters is None:
        filters = [filter_type]

    combined_df = pd.DataFrame()  # DataFrame to store phase responses for all filters

    # Loop over each filter type and compute its phase response
    for filt in filters:
        w, phase = get_phase_response(filt, lowcut, highcut, sr, order)
        df = pd.DataFrame(
            {
                "Frequency (Hz)": (sr * 0.5 / np.pi) * w,  # Convert to Hz
                "Phase (radians)": phase,  # Phase values in radians
                "Filter": filt,  # Filter type
            }
        )
        combined_df = pd.concat([combined_df, df])

    # Plot the phase response using Altair
    chart = (
        alt.Chart(combined_df)
        .mark_line(opacity=0.5)  # Set line opacity
        .encode(
            x=alt.X(
                "Frequency (Hz)", scale=alt.Scale(domain=(0, sr / 2))
            ),  # X-axis represents frequency
            y=alt.Y(
                "Phase (radians)", title="Phase (radians)"
            ),  # Y-axis represents phase
            color="Filter",  # Color by filter type
            tooltip=[
                "Frequency (Hz)",
                "Phase (radians)",
                "Filter",
            ],  # Tooltip for interactive plot
        )
        .properties(
            title="Phase Response",  # Title of the plot
            width=500,  # Set plot width
            autosize=alt.AutoSizeParams(
                type="fit", contains="padding"
            ),  # Auto-size to fit
        )
        .interactive()  # Enable interactivity for the plot
    )

    # Display the Altair chart in Streamlit
    st.altair_chart(chart, use_container_width=True)


@st.cache_data
def plot_group_delay(lowcut, highcut, sr, filter_type=None, filters=None, order=5):
    """
    Plot the group delay for multiple filters, allowing for comparison of different filter types.

    Parameters:
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - sr: Sampling rate.
    - filter_type: Single filter type to plot if filters list is not provided.
    - filters: List of filter types to plot if multiple filters are to be compared.
    - order: Filter order (applicable to IIR filters).

    Returns:
    - None: Displays an interactive Altair plot of the group delays.
    """

    # Function to compute the group delay of the selected filter
    def get_group_delay(filter_type, lowcut, highcut, sr, order):
        if filter_type == "Butterworth Band-pass":
            b, a = butter_bandpass(lowcut, highcut, sr, order)
        elif filter_type == "FIR Band-pass":
            taps = fir_bandpass(lowcut, highcut, sr)
            b, a = taps, 1.0
        elif filter_type == "IIR Band-pass":
            b, a = iir_bandpass(lowcut, highcut, sr, order)
        elif filter_type == "Chebyshev Type I Band-pass":
            b, a = cheby1_bandpass(lowcut, highcut, sr, order)
        elif filter_type == "Chebyshev Type II Band-pass":
            b, a = cheby2_bandpass(lowcut, highcut, sr, order)
        elif filter_type == "Elliptic Band-pass":
            b, a = ellip_bandpass(lowcut, highcut, sr, order)
        elif filter_type == "Bessel Band-pass":
            b, a = bessel_bandpass(lowcut, highcut, sr, order)
        w, h = freqz(b, a, worN=2000)  # Get the frequency and phase response
        unwrapped_phase = np.unwrap(
            np.angle(h)
        )  # Unwrap phase to avoid discontinuities
        group_delay = -np.diff(unwrapped_phase) / np.diff(w)  # Calculate group delay
        return w[1:], group_delay  # Ignore the first frequency bin

    # If no list of filters is provided, use the single filter type
    if filters is None:
        filters = [filter_type]

    combined_df = pd.DataFrame()  # DataFrame to store group delays for all filters

    # Loop over each filter type and compute its group delay
    for filt in filters:
        w, group_delay = get_group_delay(filt, lowcut, highcut, sr, order)
        df = pd.DataFrame(
            {
                "Frequency (Hz)": (sr * 0.5 / np.pi) * w,  # Convert to Hz
                "Group Delay (samples)": group_delay,  # Group delay values in samples
                "Filter": filt,  # Filter type
            }
        )
        combined_df = pd.concat([combined_df, df])

    # Plot the group delay using Altair
    chart = (
        alt.Chart(combined_df)
        .mark_line(opacity=0.5)  # Set line opacity
        .encode(
            x=alt.X(
                "Frequency (Hz)", scale=alt.Scale(domain=(0, sr / 2))
            ),  # X-axis represents frequency
            y=alt.Y(
                "Group Delay (samples)", title="Group Delay (samples)"
            ),  # Y-axis represents group delay
            color="Filter",  # Color by filter type
            tooltip=[
                "Frequency (Hz)",
                "Group Delay (samples)",
                "Filter",
            ],  # Tooltip for interactive plot
        )
        .properties(
            title="Group Delay",  # Title of the plot
            width=500,  # Set plot width
            autosize=alt.AutoSizeParams(
                type="fit", contains="padding"
            ),  # Auto-size to fit
        )
        .interactive()  # Enable interactivity for the plot
    )

    # Display the Altair chart in Streamlit
    st.altair_chart(chart, use_container_width=True)


@st.cache_data
def calculate_snr(original_audio, cleaned_audio):
    """
    Calculate the Signal-to-Noise Ratio (SNR) between the original and cleaned audio.

    Parameters:
    - original_audio: Original audio signal.
    - cleaned_audio: Cleaned audio signal after noise cancellation.

    Returns:
    - snr: Calculated SNR in decibels (dB).
    """

    # Ensure both arrays are of float64 type to avoid overflow issues
    original_audio = original_audio.astype(np.float64)
    cleaned_audio = cleaned_audio.astype(np.float64)

    # Clip extreme differences to prevent overflow during squaring
    diff = np.clip(original_audio - cleaned_audio, -1e6, 1e6)

    # Calculate the power of the original and noise signals
    signal_power = np.mean(np.square(original_audio))  # Power of the original signal
    noise_power = np.mean(np.square(diff))  # Power of the noise signal

    # Avoid divide-by-zero errors
    if noise_power == 0:
        return np.inf  # Infinite SNR if there's no noise

    # Calculate SNR in decibels (dB)
    snr = 10 * np.log10(signal_power / noise_power)
    return snr


@st.cache_data
def plot_snr_vs_frequency(original_audio, cleaned_audio, sr, max_points=5000):
    """
    Plot the Signal-to-Noise Ratio (SNR) across the frequency spectrum.

    Parameters:
    - original_audio: Original audio signal.
    - cleaned_audio: Cleaned audio signal after noise cancellation.
    - sr: Sampling rate.
    - max_points: Maximum number of points to plot.

    Returns:
    - None: Displays an interactive Altair plot of the SNR across frequency.
    """

    # Perform FFT on the original and cleaned audio signals
    original_fft = np.fft.fft(original_audio)
    cleaned_fft = np.fft.fft(cleaned_audio)
    freqs = np.fft.fftfreq(len(original_fft), 1 / sr)  # Get the frequencies

    # Extract positive frequencies and their magnitudes
    positive_freqs = freqs[: len(freqs) // 2]
    original_magnitude = np.abs(original_fft[: len(freqs) // 2])
    cleaned_magnitude = np.abs(cleaned_fft[: len(freqs) // 2])

    # Calculate the SNR in the frequency domain
    snr_values = 10 * np.log10(
        (original_magnitude**2)
        / (np.abs(original_magnitude - cleaned_magnitude) ** 2 + 1e-10)
    )

    # Downsample the data for better plotting performance
    step = max(1, len(positive_freqs) // max_points)
    freqs_downsampled = positive_freqs[::step]
    snr_downsampled = snr_values[::step]

    # Prepare the data for plotting
    df = pd.DataFrame(
        {"Frequency (Hz)": freqs_downsampled, "SNR (dB)": snr_downsampled}
    )

    # Plot the SNR vs frequency using Altair
    chart = (
        alt.Chart(df)
        .mark_line(opacity=0.7, color=tertiary_color)  # Set line opacity and color
        .encode(
            x=alt.X(
                "Frequency (Hz)",
                scale=alt.Scale(
                    type="log", domain=[1, sr / 2]
                ),  # Logarithmic scale for frequency
                title="Frequency (Hz, log scale)",
            ),
            y=alt.Y("SNR (dB)", title="SNR (dB)"),  # Y-axis represents SNR
            tooltip=["Frequency (Hz)", "SNR (dB)"],  # Tooltip for interactive plot
        )
        .properties(title="SNR vs Frequency", width=500)  # Set plot title and width
        .interactive()  # Enable interactivity for the plot
    )

    # Display the Altair chart in Streamlit
    st.altair_chart(chart, use_container_width=True)


@st.cache_data
def plot_impulse_response(lowcut, highcut, sr, filter_type=None, filters=None, order=5):
    """
    Plot the impulse response for multiple filters, allowing for comparison of different filter types.

    Parameters:
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - sr: Sampling rate.
    - filter_type: Single filter type to plot if filters list is not provided.
    - filters: List of filter types to plot if multiple filters are to be compared.
    - order: Filter order (applicable to IIR filters).

    Returns:
    - None: Displays an interactive Altair plot of the impulse responses.
    """

    # Function to compute the filtered impulse response of the selected filter
    def get_filtered_impulse(filter_type, lowcut, highcut, sr, order):
        impulse = np.zeros(100)  # Create an impulse signal
        impulse[0] = 1  # Set the first sample to 1 (impulse)
        return apply_filter(impulse, lowcut, highcut, sr, filter_type, order)

    # If no list of filters is provided, use the single filter type
    if filters is None:
        filters = [filter_type]

    combined_df = pd.DataFrame()  # DataFrame to store impulse responses for all filters
    time = np.arange(0, 100) / sr  # Generate time values for the impulse response

    # Loop over each filter type and compute its impulse response
    for filt in filters:
        filtered_impulse = get_filtered_impulse(filt, lowcut, highcut, sr, order)
        df = pd.DataFrame(
            {
                "Time (s)": time,  # Time axis
                "Filtered Impulse Response": filtered_impulse,  # Amplitude of the impulse response
                "Filter": filt,  # Filter type
            }
        )
        combined_df = pd.concat([combined_df, df])

    # Plot the impulse response using Altair
    chart = (
        alt.Chart(combined_df)
        .mark_line(opacity=0.5)  # Set line opacity
        .encode(
            x=alt.X("Time (s)", title="Time (s)"),  # X-axis represents time
            y=alt.Y(
                "Filtered Impulse Response", title="Amplitude"
            ),  # Y-axis represents amplitude
            color="Filter",  # Color by filter type
            tooltip=[
                "Time (s)",
                "Filtered Impulse Response",
                "Filter",
            ],  # Tooltip for interactive plot
        )
        .properties(title="Impulse Response", width=500)  # Set plot title and width
        .interactive()  # Enable interactivity for the plot
    )

    # Display the Altair chart in Streamlit
    st.altair_chart(chart, use_container_width=True)


@st.cache_data
def plot_step_response(lowcut, highcut, sr, filter_type=None, filters=None, order=5):
    """
    Plot the step response for multiple filters, allowing for comparison of different filter types.

    Parameters:
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - sr: Sampling rate.
    - filter_type: Single filter type to plot if filters list is not provided.
    - filters: List of filter types to plot if multiple filters are to be compared.
    - order: Filter order (applicable to IIR filters).

    Returns:
    - None: Displays an interactive Altair plot of the step responses.
    """

    # Function to compute the filtered step response of the selected filter
    def get_filtered_step(filter_type, lowcut, highcut, sr, order):
        step_signal = np.ones(100)  # Create a step signal (all ones)
        return apply_filter(step_signal, lowcut, highcut, sr, filter_type, order)

    # If no list of filters is provided, use the single filter type
    if filters is None:
        filters = [filter_type]

    combined_df = pd.DataFrame()  # DataFrame to store step responses for all filters
    time = np.arange(0, 100) / sr  # Generate time values for the step response

    # Loop over each filter type and compute its step response
    for filt in filters:
        filtered_step = get_filtered_step(filt, lowcut, highcut, sr, order)
        df = pd.DataFrame(
            {"Time (s)": time, "Filtered Step Response": filtered_step, "Filter": filt}
        )
        combined_df = pd.concat([combined_df, df])

    # Plot the step response using Altair
    chart = (
        alt.Chart(combined_df)
        .mark_line(opacity=0.5)  # Set line opacity
        .encode(
            x=alt.X("Time (s)", title="Time (s)"),  # X-axis represents time
            y=alt.Y(
                "Filtered Step Response", title="Amplitude"
            ),  # Y-axis represents amplitude
            color="Filter",  # Color by filter type
            tooltip=[
                "Time (s)",
                "Filtered Step Response",
                "Filter",
            ],  # Tooltip for interactive plot
        )
        .properties(title="Step Response", width=500)  # Set plot title and width
        .interactive()  # Enable interactivity for the plot
    )

    # Display the Altair chart in Streamlit
    st.altair_chart(chart, use_container_width=True)


@st.cache_data
def plot_time_domain_comparison(
    audio_data, lowcut, highcut, sr, filters, order=5, max_points=5000
):
    """
    Plot the time-domain comparison of multiple filtered signals with downsampling to avoid large data sizes.

    Parameters:
    - audio_data: Input audio signal.
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - sr: Sampling rate.
    - filters: List of filter types to compare.
    - order: Filter order (applicable to IIR filters).
    - max_points: Maximum number of points to plot (downsampling to prevent large data).
    """
    time = np.linspace(0, len(audio_data) / sr, len(audio_data))

    # Downsample the time-domain signal to reduce data size
    step = max(1, len(audio_data) // max_points)
    time_downsampled = time[::step]

    combined_df = pd.DataFrame({"Time (s)": time_downsampled})

    # Loop through each filter type and apply the filter
    for filt in filters:
        filtered_signal = apply_filter(audio_data, lowcut, highcut, sr, filt, order)
        filtered_downsampled = filtered_signal[::step]
        combined_df[filt] = filtered_downsampled

    # Melt the DataFrame for plotting
    df_melted = combined_df.melt("Time (s)", var_name="Filter", value_name="Amplitude")

    # Create an Altair line chart to plot the time-domain comparison
    chart = (
        alt.Chart(df_melted)
        .mark_line(opacity=0.5)
        .encode(
            x=alt.X("Time (s)", title="Time (s)"),
            y=alt.Y("Amplitude", title="Amplitude"),
            color="Filter",
            tooltip=["Time (s)", "Amplitude", "Filter"],
        )
        .properties(
            title="Time-Domain Comparison of Filters",
            width=500,
            autosize=alt.AutoSizeParams(type="fit", contains="padding"),
        )
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)


@st.cache_data
def plot_poles_zeros(filter_type, lowcut, highcut, sr, order=5):
    """
    Plot the poles and zeros of the designed filter in the z-plane for filter stability analysis.

    Parameters:
    - filter_type: Type of filter to analyze (e.g., Butterworth, Chebyshev, etc.).
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - sr: Sampling rate.
    - order: Filter order (for IIR filters).

    Returns:
    - None: Displays the poles and zeros plot in Streamlit.
    """
    # Get the filter coefficients based on the filter type
    if filter_type == "Butterworth Band-pass":
        b, a = butter_bandpass(lowcut, highcut, sr, order)
    elif filter_type == "FIR Band-pass":
        b, a = fir_bandpass(lowcut, highcut, sr), 1.0
    elif filter_type == "IIR Band-pass":
        b, a = iir_bandpass(lowcut, highcut, sr, order)
    elif filter_type == "Chebyshev Type I Band-pass":
        b, a = cheby1_bandpass(lowcut, highcut, sr, order)
    elif filter_type == "Chebyshev Type II Band-pass":
        b, a = cheby2_bandpass(lowcut, highcut, sr, order)
    elif filter_type == "Elliptic Band-pass":
        b, a = ellip_bandpass(lowcut, highcut, sr, order)
    elif filter_type == "Bessel Band-pass":
        b, a = bessel_bandpass(lowcut, highcut, sr, order)

    # Calculate poles and zeros
    z, p, k = signal.tf2zpk(b, a)

    # Convert to real and imaginary components
    zeros_real, zeros_imag = np.real(z), np.imag(z)
    poles_real, poles_imag = np.real(p), np.imag(p)

    # Create DataFrames for poles and zeros
    df_zeros = pd.DataFrame(
        {"Real": zeros_real, "Imaginary": zeros_imag, "Type": "Zero"}
    )
    df_poles = pd.DataFrame(
        {"Real": poles_real, "Imaginary": poles_imag, "Type": "Pole"}
    )
    df_combined = pd.concat([df_zeros, df_poles])

    # Create an Altair plot for poles and zeros
    chart = (
        alt.Chart(df_combined)
        .mark_point(filled=True, size=100)
        .encode(
            x=alt.X("Real", scale=alt.Scale(domain=(-2, 2)), title="Real"),
            y=alt.Y("Imaginary", scale=alt.Scale(domain=(-2, 2)), title="Imaginary"),
            shape="Type:N",
            color="Type:N",
            tooltip=["Real", "Imaginary", "Type"],
        )
        .properties(
            title=f"Filter Design (Poles and Zeros): {filter_type}",
            width=400,
            height=400,
        )
    )

    # Add unit circle to the plot (for z-plane)
    unit_circle = (
        alt.Chart(pd.DataFrame({"theta": np.linspace(0, 2 * np.pi, 500)}))
        .transform_calculate("Real", "cos(datum.theta)")
        .transform_calculate("Imaginary", "sin(datum.theta)")
        .mark_line(strokeDash=[5, 5], color="black")
        .encode(x="Real:Q", y="Imaginary:Q")
    )

    chart = chart + unit_circle

    st.altair_chart(chart, use_container_width=True)


# Title and Header for the App in a non-collapsible section for uniformity
with st.container():
    st.markdown(
        "<div style='background-color: #f0f0f5; padding: 10px; border-radius: 10px;'>"
        "<h1 style='text-align: center; color: #333333; font-family: Arial;'>ClearWave</h1>"
        "</div>",
        unsafe_allow_html=True,
    )

# Add a gap between the title container and the first expander
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# 1. Upload Audio Section with improved feedback and layout
with st.expander("1. Upload Audio", expanded=True):
    st.write("**Upload an audio file to begin.**")
    audio_file = st.file_uploader("Upload your audio file", type=["wav", "mp3"])

    if audio_file is not None:
        # Make the audio player as wide as in section 2 and 3
        st.audio(audio_file, format="audio/wav")

        # Load the audio data
        audio_data, sr = load_audio(audio_file)
        st.success("**Audio loaded successfully!**")

        # Automatically suggest bandpass filter cutoff frequencies
        lowcut_suggested, highcut_suggested = suggest_bandpass_values(audio_data, sr)

        # Push high cutoff to the far right using 3 columns with a uniform gap
        col1, col2, col3, col4, col5 = st.columns([0.5, 1, 1, 1, 0.5])
        col2.metric("Suggested Low Cutoff", f"{lowcut_suggested} Hz")
        col4.metric("Suggested High Cutoff", f"{highcut_suggested} Hz")

        # Display time-domain and frequency-domain analyses of the original audio
        plot_time_domain(audio_data, None, sr)  # Time-domain representation
        plot_frequency_domain(audio_data, None, sr)  # Frequency-domain representation

# 2. Add Noise Section with refined controls
if audio_file is not None:
    with st.expander("2. Add Noise (Optional)", expanded=False):
        st.write("You can add **synthetic noise** to the audio for testing purposes.")

        # Checkbox for adding noise
        add_noise = st.checkbox("Add Noise to Audio")

        if add_noise:
            # Better control elements with better UI text
            noise_type = st.selectbox(
                "Select Noise Type", ["Low Frequency", "High Frequency", "Both"]
            )
            noise_level = st.slider("Select Noise Level", 0.0, 1.0, 0.05)

            # Generate and add noise based on user selection
            duration = len(audio_data) / sr
            time = np.linspace(0.0, duration, len(audio_data))
            low_freq_noise = (
                np.sin(2 * np.pi * 50 * time)
                if noise_type in ["Low Frequency", "Both"]
                else np.zeros_like(audio_data)
            )
            high_freq_noise = (
                np.sin(2 * np.pi * 8000 * time)
                if noise_type in ["High Frequency", "Both"]
                else np.zeros_like(audio_data)
            )
            noise = noise_level * (low_freq_noise + high_freq_noise)

            noisy_audio = audio_data + noise

            # Play the noisy audio for preview
            noisy_audio_buffer = io.BytesIO()
            sf.write(noisy_audio_buffer, noisy_audio, sr, format="WAV")
            noisy_audio_buffer.seek(0)

            st.success("Noise added successfully!")
            st.audio(noisy_audio_buffer, format="audio/wav")

            # Plot noisy vs original audio
            st.subheader("Noisy Audio Analysis")
            plot_time_domain(
                noisy_audio, audio_data, sr, noisy="Noisy", cleaned="Original"
            )
            plot_frequency_domain(noisy_audio, None, sr)

            # Display suggested cutoff frequencies for noisy audio
            lowcut_suggested, highcut_suggested = suggest_bandpass_values(
                noisy_audio, sr
            )
            # Push high cutoff to the far right using 3 columns with a uniform gap
            col1, col2, col3, col4, col5 = st.columns([0.5, 1, 1, 1, 0.5])
            col2.metric("Suggested Low Cutoff", f"{lowcut_suggested} Hz")
            col4.metric("Suggested High Cutoff", f"{highcut_suggested} Hz")
        else:
            noisy_audio = audio_data

# 3. Apply Noise Cancellation Section with better layout and feedback
if audio_file is not None and noisy_audio is not None:
    with st.expander("3. Apply Noise Cancellation", expanded=False):
        st.write("Apply a **noise cancellation filter** to the noisy audio.")

        # Filter settings in a cleaner layout
        filter_type = st.selectbox(
            "Select Filter Type",
            all_filters,
        )

        col1, col2 = st.columns(2)
        lowcut = col1.slider(
            "Low Frequency Cutoff", 50, 8000, lowcut_suggested, key="lowcut_slider"
        )
        highcut = col2.slider(
            "High Frequency Cutoff", 50, 8000, highcut_suggested, key="highcut_slider"
        )

        filter_order, rp, rs = filter_customization_panel(
            noisy_audio, lowcut, highcut, sr, filter_type
        )

        # Apply the filter and display audio
        if lowcut > 0 and highcut > lowcut:
            cleaned_audio = apply_filter(
                noisy_audio, lowcut, highcut, sr, filter_type, filter_order, rp, rs
            )

            # Play the cleaned (filtered) audio for preview
            cleaned_audio_buffer = io.BytesIO()
            sf.write(cleaned_audio_buffer, cleaned_audio, sr, format="WAV")
            cleaned_audio_buffer.seek(0)

            st.success("Noise cancellation applied successfully!")
            st.audio(cleaned_audio_buffer, format="audio/wav")

            # Plot noisy vs cleaned audio
            plot_time_domain(noisy_audio, cleaned_audio, sr)
            plot_frequency_domain(noisy_audio, cleaned_audio, sr, lowcut, highcut)

# 4. Analysis and Comparison Section with cleaner analysis layout
if audio_file is not None and noisy_audio is not None:
    with st.expander("4. Analysis & Comparison", expanded=False):
        st.write(
            "Analyze the **results of noise cancellation** using advanced metrics and plots."
        )

        # Spectral centroid, filter response, and SNR comparison
        plot_spectral_centroid(audio_data, sr)
        plot_filter_response(lowcut, highcut, sr, filter_type, order=filter_order)
        plot_phase_response(lowcut, highcut, sr, filter_type, order=filter_order)
        plot_group_delay(lowcut, highcut, sr, filter_type, order=filter_order)

        # Display SNR after filtering with a metric
        snr = calculate_snr(noisy_audio, cleaned_audio)
        st.metric("Signal-to-Noise Ratio (SNR)", f"{snr:.2f} dB")

        # Plot SNR across the frequency spectrum
        plot_snr_vs_frequency(noisy_audio, cleaned_audio, sr)

        # Plot the impulse response of the filter
        plot_impulse_response(lowcut, highcut, sr, filter_type, order=filter_order)

        # Plot the step response of the filter
        plot_step_response(lowcut, highcut, sr, filter_type, order=filter_order)

        # Filter design display (poles and zeros plot)
        # st.write("**Filter Design: Poles and Zeros Plot**")
        plot_poles_zeros(filter_type, lowcut, highcut, sr, order=filter_order)

    with st.expander("5. Compare Filters", expanded=False):
        st.write(
            "Click the button below to compare the responses of different filters."
        )
        if st.button("Generate Comparison Plots"):
            filters_to_compare = all_filters
            # Spectral centroid, filter response, and SNR comparison
            plot_filter_response(
                lowcut, highcut, sr, filter_type, filters=filters_to_compare
            )
            plot_phase_response(
                lowcut,
                highcut,
                sr,
                filter_type,
                filters=filters_to_compare,
                order=filter_order,
            )
            plot_group_delay(
                lowcut,
                highcut,
                sr,
                filter_type,
                filters=filters_to_compare,
                order=filter_order,
            )

            # Plot the impulse response of the filter
            plot_impulse_response(
                lowcut, highcut, sr, filter_type, filters=filters_to_compare
            )

            # Plot the step response of the filter
            plot_step_response(
                lowcut, highcut, sr, filter_type, filters=filters_to_compare
            )

            # Time-domain comparison of filtered signals
            plot_time_domain_comparison(
                audio_data, lowcut, highcut, sr, filters_to_compare, order=filter_order
            )
