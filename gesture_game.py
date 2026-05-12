import cv2
import mediapipe as mp
import pyautogui
import time

# ------------------ Setup ------------------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# ------------------ State ------------------
threshold = 0.1
jump_threshold = 0.05
paused = False

ready_for_action = True
prev_nose_y = 0   # 🔥 for motion-based roll

# ------------------ Main Loop ------------------
while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb)

    key = cv2.waitKey(1) & 0xFF

    # -------- Keyboard control --------
    if key == ord('s'):
        paused = True
        print("STOPPED")

    elif key == ord('r'):
        paused = False
        print("RESUMED")

    elif key == ord('q') or key == 27:
        break

    # -------- Pause --------
    if paused:
        cv2.putText(frame, "STOPPED", (50, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        cv2.imshow("Game Control", frame)
        continue

    # -------- Pose --------
    if result.pose_landmarks:
        lm = result.pose_landmarks.landmark

        lw = lm[15]
        rw = lm[16]
        ls = lm[11]
        rs = lm[12]
        nose = lm[0]

        shoulder_y = (ls.y + rs.y) / 2
        center_x = (ls.x + rs.x) / 2

        # -------- Detection --------
        left_up = lw.y < shoulder_y - threshold
        right_up = rw.y < shoulder_y - threshold

        left_jump = lw.y < shoulder_y - jump_threshold
        right_jump = rw.y < shoulder_y - jump_threshold

        action = None

        # -------- EASY ROLL (motion-based) --------
        if (nose.y - prev_nose_y) > 0.035:
            action = "ROLL"

        # -------- FAST JUMP --------
        elif left_jump and right_jump:
            action = "JUMP"

        # -------- LEFT --------
        elif left_up:
            action = "LEFT" if lw.x < center_x else "RIGHT"

        # -------- RIGHT --------
        elif right_up:
            action = "RIGHT" if rw.x > center_x else "LEFT"

        prev_nose_y = nose.y  # update for next frame

        # -------- Perform action --------
        if action and ready_for_action:

            print(action)

            if action == "LEFT":
                pyautogui.press('left')

            elif action == "RIGHT":
                pyautogui.press('right')

            elif action == "JUMP":
                pyautogui.press('up')

            elif action == "ROLL":
                pyautogui.press('down')

            ready_for_action = False

        # -------- Reset trigger --------
        if not left_up and not right_up:
            ready_for_action = True

        mp_draw.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # -------- Display --------
    cv2.imshow("Game Control", frame)

cap.release()
cv2.destroyAllWindows()