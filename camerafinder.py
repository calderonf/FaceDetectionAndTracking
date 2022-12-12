from pymf import get_MF_devices
import cv2

device_list = get_MF_devices()
cv_index = None
for i, device_name in enumerate(device_list):
    # find index of camera you want
    q = input(f"Wanna use {device_name}?\n")
    if q.strip() == "YES":
        cv_index = i
        break

if cv_index is None:
    print("Not found")
else:
    # make sure you use Media Foundation
    cap = cv2.VideoCapture(cv_index + cv2.CAP_MSMF)
    while (cap.isOpened):
        ret, frame = cap.read()
        if ret:
            cv2.imshow("frame", frame)
            k = cv2.waitKey(1)
            if k > 0:
                break
        else:
            break
    cap.release()
    cv2.destroyAllWindows()