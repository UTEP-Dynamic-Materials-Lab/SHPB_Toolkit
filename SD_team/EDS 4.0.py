#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 13:49:06 2025

@author: sofiacabello
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Path
folder_path = "/Users/sofiacabello/UTEP/Senior Design"  

# Read EDS
def read_spectrum_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    
    data_start = None
    energy = []
    counts = []
    
    # Find start of spectrum data
    for i, line in enumerate(lines):
        if "#SPECTRUM" in line:  
            data_start = i + 1
            break
    
    if data_start is not None:
        for line in lines[data_start:]:
            parts = line.strip().split(",")  
            if len(parts) == 2:
                try:
                    e_val = float(parts[0])
                    c_val = float(parts[1])

                  
                    if e_val >= 0:
                        energy.append(e_val)
                        counts.append(c_val)

                except ValueError:
                    continue

    return np.array(energy), np.array(counts)

# remove background noise
def remove_background(counts, window_size=50):
    if len(counts) == 0:
        return counts
    baseline = np.convolve(counts, np.ones(window_size)/window_size, mode='same')
    return counts - baseline

# NIST transition energy database
nist_db = {
    "Cr": [5.415, 5.947, 0.573, 0.5],
    "Fe": [6.404, 7.058, 0.703, 0.615],
    "C": [0.277],
    "Ni": [7.478, 8.265, 0.851, 0.762, 0.743],
    "Mn": [5.899, 6.49, 0.636, 0.556],
    "Si": [1.74],
    "Mo": [17.48, 19.609, 19.965, 2.293, 2.395, 2.12, 2.831, 2.016, 0.193],
}

# Identify elements
def identify_elements(peaks, energy, tolerance=0.1):
    detected_elements = []
    for peak in peaks:
        peak_energy = energy[peak]
        for element, transitions in nist_db.items():
            if any(abs(peak_energy - t) <= tolerance for t in transitions):
                detected_elements.append((peak_energy, element))
    return detected_elements

# Ensure output directory exists
output_path = os.path.join(folder_path, "plots")
os.makedirs(output_path, exist_ok=True)

# Run different files
for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):
        file_path = os.path.join(folder_path, filename)
        
        # Read spectrum data
        energy, counts = read_spectrum_file(file_path)
        
        if len(energy) == 0 or len(counts) == 0:
            print(f"Skipping {filename} due to missing or corrupted data.\n")
            continue
        
        # Remove background
        counts_corrected = remove_background(counts)

        # keV to eV
        energy_ev = energy * 1000  

        # Normalize intensity to match the expected peak heights
        counts_corrected = counts_corrected / np.max(counts_corrected) * 3500  

        # lower detection threshold
        peaks, _ = find_peaks(counts_corrected, height=np.max(counts_corrected) * 0.05)

        # Plot spectrum
        plt.figure(figsize=(10, 5))
        plt.plot(energy_ev, counts_corrected, linewidth=1.2, color="navy", label="Spectrum")

        # Mark peaks
        plt.scatter(energy_ev[peaks], counts_corrected[peaks], color='red', label="Peaks")

        # Overlapping Labels
        for i, (peak_energy, element) in enumerate(identify_elements(peaks, energy)):
            y_position = counts_corrected[np.where(energy_ev == peak_energy * 1000)[0][0]]
            
            # Stagger labels up/down based on index
            vertical_offset = 15 if i % 2 == 0 else -15  
            horizontal_offset = -20 if i % 3 == 0 else 20  

            plt.annotate(element, (peak_energy * 1000, y_position),
                         textcoords="offset points",
                         xytext=(horizontal_offset, vertical_offset),
                         ha='center', fontsize=10, color='blue', rotation=15)

        
        plt.xlabel("Energy (eV)")
        plt.ylabel("Intensity (Counts)")
        plt.title("Energy Dispersive X-ray Spectrum")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()

        plt.savefig(os.path.join(output_path, f"{filename}_spectrum.png"))
        plt.show(block=True)  
        plt.close()


