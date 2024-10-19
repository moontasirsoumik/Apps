import streamlit as st
import numpy as np
import pandas as pd
import librosa
import soundfile as sf
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from scipy.signal import butter, lfilter, firwin, freqz, iirfilter, cheby1, cheby2, ellip, bessel
import io
import altair as alt

def butter_bandpass(lowcut, highcut, fs, order=5):
    """
    Design a Butterworth band-pass filter.

    Parameters:
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - fs: Sampling frequency.
    - order: Filter order.

    Returns:
    - b, a: Numerator (b) and denominator (a) polynomials of the IIR filter.
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def fir_bandpass(lowcut, highcut, fs, numtaps=101):
    """
    Design a FIR band-pass filter.

    Parameters:
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - fs: Sampling frequency.
    - numtaps: Number of filter taps (filter order).

    Returns:
    - taps: FIR filter coefficients.
    """
    nyquist = 0.5 * fs
    taps = firwin(numtaps, [lowcut / nyquist, highcut / nyquist], pass_zero=False)
    return taps

def iir_bandpass(lowcut, highcut, fs, order=5):
    """
    Design a general IIR band-pass filter (Butterworth by default).

    Parameters:
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - fs: Sampling frequency.
    - order: Filter order.

    Returns:
    - b, a: Numerator (b) and denominator (a) polynomials of the IIR filter.
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = iirfilter(order, [low, high], btype='band', ftype='butter')
    return b, a

def cheby1_bandpass(lowcut, highcut, fs, order=5, rp=0.5):
    """
    Design a Chebyshev Type I band-pass filter.

    Parameters:
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - fs: Sampling frequency.
    - order: Filter order.
    - rp: Maximum ripple allowed in the passband (in dB).

    Returns:
    - b, a: Numerator (b) and denominator (a) polynomials of the IIR filter.
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = cheby1(order, rp, [low, high], btype='band')
    return b, a

def cheby2_bandpass(lowcut, highcut, fs, order=5, rs=20):
    """
    Design a Chebyshev Type II band-pass filter.

    Parameters:
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - fs: Sampling frequency.
    - order: Filter order.
    - rs: Minimum attenuation required in the stopband (in dB).

    Returns:
    - b, a: Numerator (b) and denominator (a) polynomials of the IIR filter.
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = cheby2(order, rs, [low, high], btype='band')
    return b, a

def ellip_bandpass(lowcut, highcut, fs, order=5, rp=0.5, rs=20):
    """
    Design an elliptic (Cauer) band-pass filter.

    Parameters:
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - fs: Sampling frequency.
    - order: Filter order.
    - rp: Maximum ripple allowed in the passband (in dB).
    - rs: Minimum attenuation required in the stopband (in dB).

    Returns:
    - b, a: Numerator (b) and denominator (a) polynomials of the IIR filter.
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = ellip(order, rp, rs, [low, high], btype='band')
    return b, a

def bessel_bandpass(lowcut, highcut, fs, order=5):
    """
    Design a Bessel band-pass filter.

    Parameters:
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - fs: Sampling frequency.
    - order: Filter order.

    Returns:
    - b, a: Numerator (b) and denominator (a) polynomials of the IIR filter.
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = bessel(order, [low, high], btype='band')
    return b, a

def apply_filter(data, lowcut, highcut, fs, filter_type, order=5):
    """
    Apply the selected filter type to the audio data.

    Parameters:
    - data: Input audio data.
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - fs: Sampling frequency.
    - filter_type: Type of filter to apply.
    - order: Filter order (applicable to IIR filters).

    Returns:
    - Filtered audio data.
    """
    if filter_type == 'Butterworth Band-pass':
        b, a = butter_bandpass(lowcut, highcut, fs, order)
        return lfilter(b, a, data)
    elif filter_type == 'FIR Band-pass':
        taps = fir_bandpass(lowcut, highcut, fs)
        return lfilter(taps, 1.0, data)
    elif filter_type == 'IIR Band-pass':
        b, a = iir_bandpass(lowcut, highcut, fs, order)
        return lfilter(b, a, data)
    elif filter_type == 'Chebyshev Type I Band-pass':
        b, a = cheby1_bandpass(lowcut, highcut, fs, order)
        return lfilter(b, a, data)
    elif filter_type == 'Chebyshev Type II Band-pass':
        b, a = cheby2_bandpass(lowcut, highcut, fs, order)
        return lfilter(b, a, data)
    elif filter_type == 'Elliptic Band-pass':
        b, a = ellip_bandpass(lowcut, highcut, fs, order)
        return lfilter(b, a, data)
    elif filter_type == 'Bessel Band-pass':
        b, a = bessel_bandpass(lowcut, highcut, fs, order)
        return lfilter(b, a, data)

@st.cache_data
def suggest_bandpass_values(audio_data, sr):
    """
    Suggest band-pass filter cutoff values based on the audio's frequency distribution.

    Parameters:
    - audio_data: Input audio data.
    - sr: Sampling rate.

    Returns:
    - lowcut_suggested: Suggested low cutoff frequency.
    - highcut_suggested: Suggested high cutoff frequency.
    """
    fft = np.fft.fft(audio_data)
    freqs = np.fft.fftfreq(len(fft), 1/sr)
    magnitude = np.abs(fft)
    
    # Consider only positive frequencies
    positive_freqs = freqs[:len(freqs)//2]
    positive_magnitude = magnitude[:len(magnitude)//2]
    
    # Calculate total energy and cumulative energy
    total_energy = np.sum(positive_magnitude)
    cumulative_energy = np.cumsum(positive_magnitude) / total_energy
    
    # Find frequencies where cumulative energy crosses 10% and 90%
    lowcut_suggested = positive_freqs[np.searchsorted(cumulative_energy, 0.1)]
    highcut_suggested = positive_freqs[np.searchsorted(cumulative_energy, 0.9)]
    
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

primary_color = '#00CC66' # Matte green used for cleaned signals
secondary_color = '#FF4B4B'   # Matte red used for noisy signals
tertiary_color = '#3399FF' # Matte blue used for neutral signals

def apply_text_effects():
    """
    Apply text effects for plot labels to enhance visibility.
    
    Returns:
    - List of path_effects for text styling.
    """
    return [path_effects.Stroke(linewidth=3, foreground='white'), path_effects.Normal()]

def plot_time_domain(noisy_audio, cleaned_audio=None, sr=44100, noisy="Noisy", cleaned="Cleaned", max_points=5000):
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
        df = pd.DataFrame({
            'Time (s)': time_downsampled,
            'Amplitude': noisy_downsampled
        })
        chart = alt.Chart(df).mark_line(opacity=0.5, color=tertiary_color).encode(
            x='Time (s)',
            y=alt.Y('Amplitude', title='Amplitude'),
            tooltip=['Time (s)', 'Amplitude']
        ).properties(
            title="Time-Domain Signal",
            width=500,
            autosize=alt.AutoSizeParams(type="fit", contains="padding")
        ).interactive()
    
    # Both noisy and cleaned audio plots
    else:
        cleaned_downsampled = cleaned_audio[::step]
        df = pd.DataFrame({
            'Time (s)': time_downsampled,
            noisy: noisy_downsampled,
            cleaned: cleaned_downsampled
        })
        df_melted = df.melt('Time (s)', var_name='Signal', value_name='Amplitude')
        signal_color = tertiary_color if cleaned == "Original" else primary_color
        chart = alt.Chart(df_melted).mark_line(opacity=0.5).encode(
            x='Time (s)',
            y=alt.Y('Amplitude', title='Amplitude'),
            color=alt.Color('Signal', scale=alt.Scale(domain=[noisy, cleaned], range=[secondary_color, signal_color])),
            tooltip=['Time (s)', 'Amplitude', 'Signal']
        ).properties(
            title="Time-Domain Signal",
            width=500,
            autosize=alt.AutoSizeParams(type="fit", contains="padding")
        ).interactive()

    st.altair_chart(chart, use_container_width=True)

@st.cache_data
def plot_frequency_domain(noisy_audio, cleaned_audio=None, sr=44100, lowcut=None, highcut=None, max_points=5000):
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
    freqs = np.fft.fftfreq(len(noisy_fft), 1/sr)
    
    # Positive frequency components
    positive_freqs = freqs[:len(freqs)//2]
    noisy_magnitude = np.abs(noisy_fft[:len(freqs)//2])
    
    # Downsample for plot clarity
    step = max(1, len(positive_freqs) // max_points)
    freqs_downsampled = positive_freqs[::step]
    noisy_magnitude_downsampled = noisy_magnitude[::step]

    # Plot only noisy signal
    if cleaned_audio is None:
        df = pd.DataFrame({
            'Frequency (Hz)': freqs_downsampled,
            'Magnitude': noisy_magnitude_downsampled
        })
        chart = alt.Chart(df).mark_area(opacity=0.5).encode(
            x=alt.X('Frequency (Hz):Q', scale=alt.Scale(type='log', domain=[1, sr/2]), title='Frequency (Hz, log scale)'),
            y=alt.Y('Magnitude', title='Magnitude'),
            color=alt.value(tertiary_color),
            tooltip=['Frequency (Hz)', 'Magnitude']
        ).properties(
            title="Frequency-Domain Magnitude Spectrum",
            width=500
        ).interactive()

    # Plot both noisy and cleaned signals
    else:
        cleaned_fft = np.fft.fft(cleaned_audio)
        cleaned_magnitude = np.abs(cleaned_fft[:len(freqs)//2])
        cleaned_magnitude_downsampled = cleaned_magnitude[::step]
        df = pd.DataFrame({
            'Frequency (Hz)': freqs_downsampled,
            'Noisy Magnitude': noisy_magnitude_downsampled,
            'Cleaned Magnitude': cleaned_magnitude_downsampled
        })
        df_melted = df.melt('Frequency (Hz)', var_name='Signal', value_name='Magnitude')
        chart = alt.Chart(df_melted).mark_area(opacity=0.5).encode(
            x=alt.X('Frequency (Hz):Q', scale=alt.Scale(type='log', domain=[1, sr/2]), title='Frequency (Hz, log scale)'),
            y=alt.Y('Magnitude', title='Magnitude'),
            color=alt.Color('Signal', scale=alt.Scale(domain=['Noisy Magnitude', 'Cleaned Magnitude'], range=[secondary_color, primary_color])),
            tooltip=['Frequency (Hz)', 'Magnitude', 'Signal']
        ).properties(
            title="Frequency-Domain Magnitude Spectrum",
            width=500
        ).interactive()

        # Plot cutoff frequencies as vertical lines
        if lowcut is not None and highcut is not None:
            cutoff_df = pd.DataFrame({
                'Frequency (Hz)': [lowcut, highcut],
                'Magnitude': [0, 0],
                'Cutoff Frequency': ['Low Cutoff', 'High Cutoff']
            })
            cutoff_lines = alt.Chart(cutoff_df).mark_rule(strokeDash=[5, 5]).encode(
                x=alt.X('Frequency (Hz):Q', scale=alt.Scale(type='log', domain=[1, sr/2])),
                color=alt.Color('Cutoff Frequency', scale=alt.Scale(domain=['Low Cutoff', 'High Cutoff'], range=['#1f77b4', '#ff7f0e'])),
                size=alt.value(1),
                tooltip=['Cutoff Frequency']
            )
            chart = alt.layer(chart, cutoff_lines).properties(
                autosize=alt.AutoSizeParams(type="fit", contains="padding")
            )

    st.altair_chart(chart, use_container_width=True)

@st.cache_data
def plot_filter_response(lowcut, highcut, sr, filter_type, order=5):
    """
    Plot the frequency response of the selected filter.

    Parameters:
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - sr: Sampling rate.
    - filter_type: Type of filter applied.
    - order: Filter order (for IIR filters).
    """
    if filter_type == 'Butterworth Band-pass':
        b, a = butter_bandpass(lowcut, highcut, sr, order)
    elif filter_type == 'FIR Band-pass':
        taps = fir_bandpass(lowcut, highcut, sr)
        b, a = taps, 1.0
    elif filter_type == 'IIR Band-pass':
        b, a = iir_bandpass(lowcut, highcut, sr, order)
    elif filter_type == 'Chebyshev Type I Band-pass':
        b, a = cheby1_bandpass(lowcut, highcut, sr, order)
    elif filter_type == 'Chebyshev Type II Band-pass':
        b, a = cheby2_bandpass(lowcut, highcut, sr, order)
    elif filter_type == 'Elliptic Band-pass':
        b, a = ellip_bandpass(lowcut, highcut, sr, order)
    elif filter_type == 'Bessel Band-pass':
        b, a = bessel_bandpass(lowcut, highcut, sr, order)

    # Frequency response calculation
    w, h = freqz(b, a, worN=2000)
    df = pd.DataFrame({
        'Frequency (Hz)': (sr * 0.5 / np.pi) * w,
        'Gain': abs(h)
    })

    # Plot the frequency response
    chart = alt.Chart(df).mark_line(opacity=0.5, color=primary_color).encode(
        x=alt.X('Frequency (Hz)', scale=alt.Scale(domain=(0, sr/2))),
        y=alt.Y('Gain', title='Gain'),
        tooltip=['Frequency (Hz)', 'Gain']
    ).properties(
        title=f"{filter_type} Frequency Response",
        width=500,
        autosize=alt.AutoSizeParams(type="fit", contains="padding")
    ).interactive()

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
    # Compute the spectral centroid
    spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sr)[0]
    
    # Convert the frames to time
    frames = range(len(spectral_centroid))
    t = librosa.frames_to_time(frames)
    
    # Prepare the data for plotting
    df = pd.DataFrame({
        'Time (s)': t,
        'Spectral Centroid (Hz)': spectral_centroid
    })

    # Create an Altair line chart
    chart = alt.Chart(df).mark_line(opacity=0.5, color=primary_color).encode(
        x=alt.X('Time (s)', title='Time (s)'),
        y=alt.Y('Spectral Centroid (Hz)', title='Spectral Centroid (Hz)'),
        tooltip=['Time (s)', 'Spectral Centroid (Hz)']
    ).properties(
        title="Spectral Centroid Over Time",
        width=500,
        autosize=alt.AutoSizeParams(type="fit", contains="padding")
    ).interactive()

    # Display the chart
    st.altair_chart(chart, use_container_width=True)


@st.cache_data
def plot_phase_response(lowcut, highcut, sr, filter_type, order=5):
    """
    Plot the phase response of the selected filter.

    Parameters:
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - sr: Sampling rate.
    - filter_type: Type of filter applied.
    - order: Filter order (for IIR filters).
    """
    if filter_type == 'Butterworth Band-pass':
        b, a = butter_bandpass(lowcut, highcut, sr, order)
    elif filter_type == 'FIR Band-pass':
        taps = fir_bandpass(lowcut, highcut, sr)
        b, a = taps, 1.0
    elif filter_type == 'IIR Band-pass':
        b, a = iir_bandpass(lowcut, highcut, sr, order)
    elif filter_type == 'Chebyshev Type I Band-pass':
        b, a = cheby1_bandpass(lowcut, highcut, sr, order)
    elif filter_type == 'Chebyshev Type II Band-pass':
        b, a = cheby2_bandpass(lowcut, highcut, sr, order)
    elif filter_type == 'Elliptic Band-pass':
        b, a = ellip_bandpass(lowcut, highcut, sr, order)
    elif filter_type == 'Bessel Band-pass':
        b, a = bessel_bandpass(lowcut, highcut, sr, order)

    # Calculate frequency response and phase
    w, h = freqz(b, a, worN=2000)
    phase = np.angle(h)

    df = pd.DataFrame({
        'Frequency (Hz)': (sr * 0.5 / np.pi) * w,
        'Phase (radians)': phase
    })

    # Plot the phase response
    chart = alt.Chart(df).mark_line(opacity=0.5, color=secondary_color).encode(
        x=alt.X('Frequency (Hz)', scale=alt.Scale(domain=(0, sr/2))),
        y=alt.Y('Phase (radians)', title='Phase (radians)'),
        tooltip=['Frequency (Hz)', 'Phase (radians)']
    ).properties(
        title=f"{filter_type} Phase Response",
        width=500,
        autosize=alt.AutoSizeParams(type="fit", contains="padding")
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

@st.cache_data
def plot_group_delay(lowcut, highcut, sr, filter_type, order=5):
    """
    Plot the group delay of the selected filter.

    Parameters:
    - lowcut: Low cutoff frequency.
    - highcut: High cutoff frequency.
    - sr: Sampling rate.
    - filter_type: Type of filter applied.
    - order: Filter order (for IIR filters).
    """
    if filter_type == 'Butterworth Band-pass':
        b, a = butter_bandpass(lowcut, highcut, sr, order)
    elif filter_type == 'FIR Band-pass':
        taps = fir_bandpass(lowcut, highcut, sr)
        b, a = taps, 1.0
    elif filter_type == 'IIR Band-pass':
        b, a = iir_bandpass(lowcut, highcut, sr, order)
    elif filter_type == 'Chebyshev Type I Band-pass':
        b, a = cheby1_bandpass(lowcut, highcut, sr, order)
    elif filter_type == 'Chebyshev Type II Band-pass':
        b, a = cheby2_bandpass(lowcut, highcut, sr, order)
    elif filter_type == 'Elliptic Band-pass':
        b, a = ellip_bandpass(lowcut, highcut, sr, order)
    elif filter_type == 'Bessel Band-pass':
        b, a = bessel_bandpass(lowcut, highcut, sr, order)

    # Calculate group delay
    w, h = freqz(b, a, worN=2000)
    unwrapped_phase = np.unwrap(np.angle(h))
    group_delay = -np.diff(unwrapped_phase) / np.diff(w)

    df = pd.DataFrame({
        'Frequency (Hz)': (sr * 0.5 / np.pi) * w[1:],  # Ignore first frequency bin (undefined group delay)
        'Group Delay (samples)': group_delay
    })

    # Plot group delay
    chart = alt.Chart(df).mark_line(opacity=0.5, color=tertiary_color).encode(
        x=alt.X('Frequency (Hz)', scale=alt.Scale(domain=(0, sr/2))),
        y=alt.Y('Group Delay (samples)', title='Group Delay (samples)'),
        tooltip=['Frequency (Hz)', 'Group Delay (samples)']
    ).properties(
        title=f"{filter_type} Group Delay",
        width=500,
        autosize=alt.AutoSizeParams(type="fit", contains="padding")
    ).interactive()

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
    signal_power = np.mean(np.square(original_audio))
    noise_power = np.mean(np.square(original_audio - cleaned_audio))
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
    """
    original_fft = np.fft.fft(original_audio)
    cleaned_fft = np.fft.fft(cleaned_audio)
    freqs = np.fft.fftfreq(len(original_fft), 1/sr)
    
    # Positive frequencies
    positive_freqs = freqs[:len(freqs)//2]
    original_magnitude = np.abs(original_fft[:len(freqs)//2])
    cleaned_magnitude = np.abs(cleaned_fft[:len(freqs)//2])

    # Calculate SNR in the frequency domain
    snr_values = 10 * np.log10((original_magnitude ** 2) / (np.abs(original_magnitude - cleaned_magnitude) ** 2 + 1e-10))

    # Downsample for plot clarity
    step = max(1, len(positive_freqs) // max_points)
    freqs_downsampled = positive_freqs[::step]
    snr_downsampled = snr_values[::step]
    
    df = pd.DataFrame({
        'Frequency (Hz)': freqs_downsampled,
        'SNR (dB)': snr_downsampled
    })
    
    # Plot the SNR vs frequency
    chart = alt.Chart(df).mark_line(opacity=0.7, color=tertiary_color).encode(
        x=alt.X('Frequency (Hz)', scale=alt.Scale(type='log', domain=[1, sr/2]), title='Frequency (Hz, log scale)'),
        y=alt.Y('SNR (dB)', title='SNR (dB)'),
        tooltip=['Frequency (Hz)', 'SNR (dB)']
    ).properties(
        title="SNR vs Frequency",
        width=500
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)

st.title("ClearWave")
st.header("1. Upload Audio")
audio_file = st.file_uploader("Upload your audio file", type=['wav', 'mp3'])

if audio_file is not None:
    st.audio(audio_file, format='audio/wav')
    audio_data, sr = load_audio(audio_file)
    st.success("Audio loaded successfully!")
    
    # Suggest bandpass cutoff frequencies
    lowcut_suggested, highcut_suggested = suggest_bandpass_values(audio_data, sr)
    st.write(f"Suggested Low Cutoff: {lowcut_suggested} Hz")
    st.write(f"Suggested High Cutoff: {highcut_suggested} Hz")

    # Time and Frequency domain analysis
    st.header("2. Time Domain and Frequency Analysis")
    plot_time_domain(audio_data, None, sr)
    plot_frequency_domain(audio_data, None, sr)

if audio_file is not None:
    st.header("3. Add Noise (Optional)")
    add_noise = st.checkbox("Add Noise to Audio")
    
    if add_noise:
        noise_type = st.selectbox("Select noise type", ["Low Frequency", "High Frequency", "Both"])
        noise_level = st.slider("Select noise level", 0.0, 1.0, 0.05)
        duration = len(audio_data) / sr
        time = np.linspace(0., duration, len(audio_data))
        low_freq_noise = np.sin(2 * np.pi * 50 * time) if noise_type in ["Low Frequency", "Both"] else np.zeros_like(audio_data)
        high_freq_noise = np.sin(2 * np.pi * 8000 * time) if noise_type in ["High Frequency", "Both"] else np.zeros_like(audio_data)
        noise = noise_level * (low_freq_noise + high_freq_noise)
        noisy_audio = audio_data + noise
        
        # Play and display noisy audio
        noisy_audio_buffer = io.BytesIO()
        sf.write(noisy_audio_buffer, noisy_audio, sr, format='WAV')
        noisy_audio_buffer.seek(0)
        st.audio(noisy_audio_buffer, format='audio/wav')
        st.success("Noise added successfully!")
        plot_time_domain(noisy_audio, audio_data, sr, noisy="Noisy", cleaned="Original")
    else:
        noisy_audio = audio_data

if audio_file is not None and noisy_audio is not None:
    st.header("4. Apply Noise Cancellation")
    filter_type = st.selectbox("Select filter type", ['Butterworth Band-pass', 'FIR Band-pass', 'IIR Band-pass', 'Chebyshev Type I Band-pass', 'Chebyshev Type II Band-pass', 'Elliptic Band-pass', 'Bessel Band-pass'])
    
    # Slider for low and high frequency cutoffs
    lowcut = st.slider("Low Frequency Cutoff", 50, 8000, lowcut_suggested, key="lowcut_slider")
    highcut = st.slider("High Frequency Cutoff", 50, 8000, highcut_suggested, key="highcut_slider")
    
    if lowcut > 0 and highcut > lowcut:
        cleaned_audio = apply_filter(noisy_audio, lowcut, highcut, sr, filter_type)
        
        # Play cleaned audio
        cleaned_audio_buffer = io.BytesIO()
        sf.write(cleaned_audio_buffer, cleaned_audio, sr, format='WAV')
        cleaned_audio_buffer.seek(0)
        st.audio(cleaned_audio_buffer, format='audio/wav')
        
        # Plot time-domain and frequency-domain for noisy and cleaned audio
        plot_time_domain(noisy_audio, cleaned_audio, sr)
        plot_frequency_domain(noisy_audio, cleaned_audio, sr, lowcut, highcut)
        
        # Additional analysis plots
        plot_spectral_centroid(audio_data, sr)
        plot_filter_response(lowcut, highcut, sr, filter_type)
        plot_phase_response(lowcut, highcut, sr, filter_type, order=5)
        plot_group_delay(lowcut, highcut, sr, filter_type, order=5)
        
        # Calculate and display SNR
        snr = calculate_snr(noisy_audio, cleaned_audio)
        st.write(f"Signal-to-Noise Ratio (SNR) after filtering: {snr:.2f} dB")
        
        # Plot SNR vs frequency
        plot_snr_vs_frequency(noisy_audio, cleaned_audio, sr)
