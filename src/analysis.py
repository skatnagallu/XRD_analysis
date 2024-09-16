import numpy as np
import pandas as pd
from scipy.signal import savgol_filter, medfilt, find_peaks
from scipy import sparse
from scipy.sparse.linalg import spsolve


def load_data(file_path=None, header=None):
    # Load the dataset
    if file_path is None:
        file_path = "../data/300_750.txt"  # Replace with your actual file path

    if header is None:
        header = 12

    # Read the data, replacing commas with dots and converting to float
    data = pd.read_csv(
        file_path, sep="\s+", header=header, names=["2theta", "intensity"]
    )
    return data


def baseline_als_correction(intensity, lam, p, niter=10):
    """
    lam: This parameter controls the smoothness of the baseline. Higher values of λ result in a smoother baseline, 
    while lower values allow for more flexibility.
    p (asymmetry parameter): This controls how asymmetrically the peaks are penalized. 
    Typically, p is set between 0 and 1 (e.g., 0.01), 
    so that positive deviations (above the baseline) are penalized less than negative deviations (below the baseline),
    which forces the baseline to lie below the peaks.
    niter: Number of iterations to perform the fitting. Generally, a small number of iterations (e.g., 10) is sufficient.
    """

    L = len(intensity)
    D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
    w = np.ones(L)
    for i in range(niter):
        W = sparse.spdiags(w, 0, L, L)
        Z = W + lam * D.dot(D.transpose())
        z = spsolve(Z, w * intensity)
        w = p * (intensity > z) + (1 - p) * (intensity < z)
    return z


def savgol_correction(intensity, window_length=101, polyorder=2):
    # Apply Savitzky-Golay filter to smooth the data
    background = savgol_filter(
        intensity, window_length=window_length, polyorder=polyorder
    )
    corrected_intensity = intensity - background
    return corrected_intensity


def median_correction(intensity, kernel_size=51):
    # Apply a median filter to approximate the background (rolling window)
    background = medfilt(
        intensity, kernel_size=kernel_size
    )  # Adjust kernel size as necessary
    corrected_intensity = intensity - background
    return corrected_intensity


def linear_correction(theta, intensity, order=1):
    # Define a simple linear background (you can also use a more complex shape)
    background = np.polyval(
        np.polyfit([theta[0], theta[-1]], [intensity[0], intensity[-1]], order), theta
    )
    corrected_intensity = intensity - background
    return corrected_intensity
