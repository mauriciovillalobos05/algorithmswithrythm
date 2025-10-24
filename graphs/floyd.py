import numpy as np

nodes = [
    "Goxmont", "Zrusall", "Adaset", "Ertonwell", "Niaphia", "Lagos",
    "Duron", "Blebus", "Togend", "Ontdale", "Goding", "Ylane",
    "Strento", "Oriaron"
]

adj_matrix = np.array([
#  Gox Zru Ada Ert Nia Lag Dur Ble Tog Ont God Yla Str Ori
 [  0,112,103,  0,212,  0,  0,  0,  0,  0,  0,  0,  0,  0], # Goxmont
 [112,  0, 15,  0,  0,  0,  0,  0,  0,  0,  0,  0,121,  0], # Zrusall
 [103, 15,  0,130,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], # Adaset
 [  0,  0,130,  0, 56,  0,121,  0,  0,  0,  0,  0,  0,  0], # Ertonwell
 [212,  0,  0, 56,  0,300,  0,  0,  0,  0,  0,  0,  0,  0], # Niaphia
 [  0,  0,  0,  0,300,  0,119,  0,  0,  0,  0,  0,  0,  0], # Lagos
 [  0,  0,  0,121,  0,119,  0,160,  0,  0,  0,  0,  0,  0], # Duron
 [  0,  0,  0,  0,  0,  0,160,  0,121,165,  0,  0,  0,291], # Blebus
 [  0,  0,  0,  0,  0,  0,  0,121,  0,210,  0,  0,  0,  0], # Togend
 [  0,  0,  0,  0,  0,  0,  0,165,210,  0, 98,  0,  0,219], # Ontdale
 [  0,  0,  0,  0,  0,  0,  0,  0,  0, 98,  0, 88,  0,  0], # Goding
 [  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 88,  0, 99,117], # Ylane
 [  0,121,  0,  0,  0,  0,  0,  0,  0,  0,  0, 99,  0,221], # Strento
 [  0,  0,  0,  0,  0,  0,  0,291,  0,219,  0,117,221,  0], # Oriaron
])