import cv2, numpy as np, matplotlib.pyplot as plt, glob

# --- Lista plików do przetworzenia ---
image_paths = glob.glob("./assets/tray*.jpg")   # lub podaj ręcznie listę

def analyze_tray(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Nie można otworzyć: {image_path}")
        return

    print(f"\n{'='*40}\nPlik: {image_path}\n{'='*40}")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 1.5)

    # --- Kontur tacki ---
    edges    = cv2.Canny(blurred, 50, 150)
    kernel   = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed   = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("Nie znaleziono konturu tacki")
        return
    tray_contour = max(contours, key=cv2.contourArea)

    # --- Monety ---
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT,
        dp=1.2, minDist=40, param1=50, param2=50, minRadius=20, maxRadius=80
    )

    VAL_LARGE, VAL_SMALL, THRESHOLD_RADIUS = 5.0, 1.0, 34
    large_on = small_on = large_off = small_off = 0

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center   = (int(i[0]), int(i[1]))
            is_inside = cv2.pointPolygonTest(tray_contour, center, False) >= 0
            is_large  = i[2] > THRESHOLD_RADIUS
            if is_inside:
                large_on += is_large; small_on += not is_large
            else:
                large_off += is_large; small_off += not is_large

    print(f"Na tacce   → Duże: {large_on}, Małe: {small_on}  ({large_on*VAL_LARGE + small_on*VAL_SMALL} PLN)")
    print(f"Poza tacką → Duże: {large_off}, Małe: {small_off}  ({large_off*VAL_LARGE + small_off*VAL_SMALL} PLN)")


for path in image_paths:
    analyze_tray(path)