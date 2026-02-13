import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import colorsys

def dominant_color(path):
    try:
        img = Image.open(path).convert("RGB")
    except:
        return None
        
    img = img.resize((50, 50), Image.Resampling.NEAREST)
    pixels = np.array(img).reshape(-1, 3)
    
    try:
        kmeans = KMeans(n_clusters=3, n_init=1, max_iter=100)
        kmeans.fit(pixels)
    except:
        return np.mean(pixels, axis=0)
    
    unique, counts = np.unique(kmeans.labels_, return_counts=True)
    indices = np.argsort(counts)[::-1]
    
    best_center = None
    
    for i in indices:
        center = kmeans.cluster_centers_[i]
        r, g, b = center
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        if s > 0.25 and v > 0.25:
            best_center = center
            break
            
    if best_center is None:
        best_center = kmeans.cluster_centers_[indices[0]]
        
    return best_center

def classify_color(rgb):
    if rgb is None: return "Unknown"
    r, g, b = rgb
    r, g, b = r/255, g/255, b/255
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h *= 360
    
    if s < 0.15:
        if v < 0.2: return "Black"
        if v > 0.90: return "White"
        return "Gray"
    
    if h < 15 or h >= 345: return "Red"
    if h < 35: return "Orange"
    if h < 65: return "Yellow"
    if h < 160: return "Green"
    if h < 195: return "Cyan"
    if h < 260: return "Blue"
    if h < 300: return "Purple"
    if h < 345: return "Pink"
    return "Mixed"