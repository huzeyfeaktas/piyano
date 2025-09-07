import cv2
import mediapipe as mp
import pygame

# Pygame başlatma (nota seslerini yüklemek için)
pygame.init()
notes = {
    'DO': pygame.mixer.Sound("do.mp3"),
    'RE': pygame.mixer.Sound("re.mp3"),
    'MI': pygame.mixer.Sound("mi.mp3"),
    'FA': pygame.mixer.Sound("fa.mp3"),
    'SOL': pygame.mixer.Sound("sol.mp3"),
    'LA': pygame.mixer.Sound("la.mp3"),
}

# Mediapipe el takip modülü başlatma
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Kamera başlatma
cap = cv2.VideoCapture(0)

# Tuşların koordinatlarını tanımla (ince ve uzun, ekranın üst kısmında)
keys = [
    {'name': 'DO', 'x1': 50, 'y1': 50, 'x2': 100, 'y2': 300},
    {'name': 'RE', 'x1': 110, 'y1': 50, 'x2': 160, 'y2': 300},
    {'name': 'MI', 'x1': 170, 'y1': 50, 'x2': 220, 'y2': 300},
    {'name': 'FA', 'x1': 230, 'y1': 50, 'x2': 280, 'y2': 300},
    {'name': 'SOL', 'x1': 290, 'y1': 50, 'x2': 340, 'y2': 300},
    {'name': 'LA', 'x1': 350, 'y1': 50, 'x2': 400, 'y2': 300},
]

# Önceki tuş durumu (sesin tekrar tekrar çalmaması için)
previous_key = None

def draw_keys(frame):
    """Piyano tuşlarını ekrana çiz"""
    for key in keys:
        cv2.rectangle(frame, (key['x1'], key['y1']), (key['x2'], key['y2']), (255, 255, 255), -1)
        cv2.putText(frame, key['name'], (key['x1'] + 10, key['y1'] + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

def check_finger_on_key(x, y):
    """Parmak koordinatları bir tuşa denk geliyorsa tuşun adını döndür"""
    for key in keys:
        if key['x1'] <= x <= key['x2'] and key['y1'] <= y <= key['y2']:
            return key['name']
    return None

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Kameradan görüntü alınamıyor!")
        break

    # BGR'den RGB'ye dönüştür (Mediapipe için gerekli)
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Tuşları ekrana çiz
    draw_keys(frame)

    # İşaret parmağı ucunu kontrol et
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # İşaret parmağı ucu: Landmarks[8]
            finger_x = int(hand_landmarks.landmark[8].x * frame.shape[1])
            finger_y = int(hand_landmarks.landmark[8].y * frame.shape[0])

            # Parmağın konumunu işaretle
            cv2.circle(frame, (finger_x, finger_y), 10, (0, 0, 255), -1)

            # Hangi tuşun üzerine geldiğini kontrol et
            current_key = check_finger_on_key(finger_x, finger_y)

            # Eğer yeni bir tuşa basılmışsa notayı çal
            if current_key and current_key != previous_key:
                notes[current_key].play()
                previous_key = current_key
            elif not current_key:
                previous_key = None

    # Görüntüyü göster
    cv2.imshow("Piano with Finger Detection", frame)

    # Çıkış için 'q' tuşuna bas
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Temizlik işlemleri
cap.release()
cv2.destroyAllWindows()
pygame.quit()
