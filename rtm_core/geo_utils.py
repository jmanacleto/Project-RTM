"""
Módulo de Utilidades Geoespaciais (Geo Utils).

Implementa cálculos geométricos esféricos (Fórmula de Haversine)
vetorizados com NumPy, substituindo as aproximações euclidianas planas.
"""
import numpy as np


def haversine_vetorizado(lat1, lon1, lat2, lon2) -> np.ndarray:
    """
    Calcula a distância geodésica em quilômetros entre dois pontos ou arrays
    de coordenadas geográficas na superfície da Terra (esfera de raio médio ~6371 km).
    
    Substitui a distância euclidiana simples (dx^2 + dy^2) e a aproximação plana.
    """
    R = 6371.0  # Raio médio da Terra em km

    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    a = (
        np.sin(delta_phi / 2.0) ** 2
        + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))

    return R * c


def matriz_distancias_haversine(coords1: np.ndarray, coords2: np.ndarray) -> np.ndarray:
    """
    Calcula a matriz de distâncias (N x M) em quilômetros entre dois conjuntos de coordenadas:
    coords1: array (N, 2) [lat, lon]
    coords2: array (M, 2) [lat, lon]
    """
    lat1 = coords1[:, 0][:, np.newaxis]
    lon1 = coords1[:, 1][:, np.newaxis]
    lat2 = coords2[:, 0][np.newaxis, :]
    lon2 = coords2[:, 1][np.newaxis, :]

    return haversine_vetorizado(lat1, lon1, lat2, lon2)
