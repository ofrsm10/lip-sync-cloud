import mediapipe as mp
import os
import cv2
import numpy as np
import pandas as pd
from Utils.extract_features import extract_features
from Utils.general_utils import convex_hull
from Utils.pandas_utils import crop_sequences
from Utils.plots import save_boundary_plot, save_files_and_plots

FACEMESH_LIPS = frozenset([(61, 146), (146, 91), (91, 181), (181, 84), (84, 17),
                           (17, 314), (314, 405), (405, 321), (321, 375),
                           (375, 291), (61, 185), (185, 40), (40, 39), (39, 37),
                           (37, 0), (0, 267),
                           (267, 269), (269, 270), (270, 409), (409, 291),
                           (78, 95), (95, 88), (88, 178), (178, 87), (87, 14),
                           (14, 317), (317, 402), (402, 318), (318, 324),
                           (324, 308), (78, 191), (191, 80), (80, 81), (81, 82),
                           (82, 13), (13, 312), (312, 311), (311, 310),
                           (310, 415), (415, 308)])
UPPER = 13
LOWER = 14
LEFT = 78
RIGHT = 308
TOP_RIGHT = 80
TOP_LEFT = 310
BOTTOM_RIGHT = 88
BOTTOM_LEFT = 402
CUTOFF = 1
OUTLINE = [0, 17, 37, 39, 40, 61, 84, 91, 146, 181, 185, 267, 269, 270, 291, 314, 321, 375, 405, 409]
INLINE = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 95, 88, 178, 87, 14, 317, 402, 318, 324]
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils


class SessionHandler:
    def __init__(self, root, i_d):
        self.id = i_d
        self.root = root
        self.teeth = None
        self.tongue = None

    def get_mask(self, image_file):
        # Get the cropped HSV image and mask
        image = cv2.imread(os.path.join(self.root, self.id, image_file))
        cropped, mask = self.crop_mouth(image)

        # Define initial parameter values
        h_low = 0
        h_high = 180
        s_low = 0
        s_high = 255
        v_low = 0
        v_high = 255

        # Define the target filtered percentage for each parameter
        target_percentages = [0.6, 0.56, 0.54, 0.52, 0.5, 0.48]

        # Loop through each parameter and adjust its value until the target filtered percentage is reached
        for i, percentage in enumerate(target_percentages):
            while True:
                # Create a mask using the current parameter values
                mask_h = cv2.inRange(cropped, (h_low, s_low, v_low), (h_high, s_high, v_high))
                # Calculate the percentage of pixels that are filtered out
                filtered_pixels = cv2.countNonZero(mask_h)
                total_area = float(np.count_nonzero(mask))
                filtered_percentage = filtered_pixels / total_area

                # If the target filtered percentage is reached, break out of the loop
                if filtered_percentage <= percentage:
                    break

                # Adjust the current parameter value
                if i == 0:
                    h_low += 1
                elif i == 1:
                    h_high -= 1
                elif i == 2:
                    s_low += 1
                elif i == 3:
                    s_high -= 1
                elif i == 4:
                    v_low += 1
                elif i == 5:
                    v_high -= 1


        # Apply the final mask to the cropped image
        final_mask = cv2.bitwise_and(cropped, cropped, mask=mask_h)

        # Show the filtered image with the new mask
        filtered_image = cv2.cvtColor(final_mask, cv2.COLOR_HSV2BGR)
        cv2.imshow("Filtered Image", filtered_image)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Get the parameters of the final mask
        params = {"lower": np.array([h_low, s_low, v_low]), "upper": np.array([h_high, s_high,v_high])}
        return params

    def crop_mouth(self, image):
        with mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5) as face_mesh:
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            results = face_mesh.process(image)
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    slopes, idxs = mp_drawing.get_3D_contour_features(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_LIPS)

                    xi = idxs[LEFT][0]
                    xf = idxs[RIGHT][0]
                    yi = idxs[UPPER][1]
                    yf = idxs[LOWER][1]

                    height = image.shape[0]
                    width = image.shape[1]
                    points = []
                    index_list = INLINE
                    for idx in index_list:
                        points.append(idxs[idx])
                    mask = np.zeros((height, width), dtype=np.uint8)
                    hull_points = convex_hull(points)
                    points = np.array([hull_points], dtype=int)
                    cv2.fillPoly(mask, points, 255)
                    res = cv2.bitwise_and(image, image, mask=mask)
                    hsv = cv2.cvtColor(res, cv2.COLOR_RGB2HSV)
                    cropped = hsv[yi: yf, xi: xf]
                    return cropped, mask


class DataManager:
    def __init__(self):
        self.db_path = "C:\\Users\\LZW3P1\\PycharmProjects\\lip reader\\Data_Base"
        self.sessions_path = "C:\\Users\\LZW3P1\\PycharmProjects\\lip reader\\Data_Bot\\Sessions"

    def process_directories(self):

        path = self.sessions_path
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                subdir = os.path.join(root, dir)
                session_handler = SessionHandler(root,dir)
                for file in os.listdir(subdir):
                    if file.startswith('teeth'):
                        # teeth
                        session_handler.teeth = session_handler.get_mask(file)
                    if file.startswith('tongue'):
                        # tongue
                        session_handler.tongue = session_handler.get_mask(file)
                        # session_handler.tongue = {"lower":np.array([0, 20, 60]), "upper":np.array([20, 180, 255])}
                    elif file.endswith('.mp4'):
                        mp4_file = os.path.join(subdir, file)
                        word = file.rstrip('.mp4')
                        x_d = []
                        y_d = []
                        frames_features = []
                        frames_features1 = []

                        new_dir1 = ""
                        new_dir2 = ""
                        print(f"Creating data for word: {word}..")
                        print("collecting frames for feature extraction..")
                        with mp_face_mesh.FaceMesh(
                                static_image_mode=True,
                                max_num_faces=1,
                                refine_landmarks=True,
                                min_detection_confidence=0.5) as face_mesh:
                            vidObj = cv2.VideoCapture(mp4_file)
                            fs = int(vidObj.get(cv2.CAP_PROP_FPS))
                            success = 1

                            while success:

                                success, image = vidObj.read()
                                if not success:
                                    continue

                                image.flags.writeable = True
                                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                                mirror_image = cv2.flip(image, flipCode=1)

                                results1 = face_mesh.process(image)
                                if results1.multi_face_landmarks:
                                    features, area, shape = extract_features(results1, image, session_handler.teeth['lower'], session_handler.teeth['upper'],
                                                                             session_handler.tongue['lower'], session_handler.tongue['upper'])
                                    frames_features.append(features)
                                    x_d.append(area)

                                results2 = face_mesh.process(mirror_image)
                                if results2.multi_face_landmarks:
                                    features1, area1, shape1 = extract_features(results2, image, session_handler.teeth['lower'], session_handler.teeth['upper'],
                                                                                session_handler.tongue['lower'], session_handler.tongue['upper'])
                                    frames_features1.append(features1)
                                    y_d.append(area1)

                            cv2.destroyAllWindows()

                        print(f"Done collecting features from {len(x_d)} frames..")

                        if not os.path.exists(f'C:\\Users\\LZW3P1\\PycharmProjects\\lip reader\\Data_Base\\{word}'):
                            os.mkdir(f'C:\\Users\\LZW3P1\\PycharmProjects\\lip reader\\Data_Base\\{word}')

                        k = 1
                        while True:
                            new_dir1 = "iteration" + "{:03d}".format(k)
                            if not os.path.exists(f'C:\\Users\\LZW3P1\\PycharmProjects\\lip reader\\Data_Base\\{word}\\{new_dir1}'):
                                os.mkdir(f'C:\\Users\\LZW3P1\\PycharmProjects\\lip reader\\Data_Base\\{word}\\{new_dir1}')
                                new_dir2 = new_dir1 + "_mirror"
                                os.mkdir(f'C:\\Users\\LZW3P1\\PycharmProjects\\lip reader\\Data_Base\\{word}\\{new_dir2}')
                                break
                            k += 1

                        with open(f'C:\\Users\\LZW3P1\\PycharmProjects\\lip reader\\Data_Base\\{word}\\{new_dir1}\\features_raw.csv', 'w', newline='') as file:
                            features_df = pd.DataFrame(frames_features)
                            features_df.to_csv(file)
                        with open(f'C:\\Users\\LZW3P1\\PycharmProjects\\lip reader\\Data_Base\\{word}\\{new_dir2}\\features_raw.csv', 'w', newline='') as file:
                            m_features_df = pd.DataFrame(frames_features1)
                            m_features_df.to_csv(file)

                        data3 = {"features": frames_features, "area": x_d, "area1": y_d}
                        collection_df = pd.DataFrame(data3)
                        save_boundary_plot(collection_df, f"C:\\Users\\LZW3P1\\PycharmProjects\\lip reader\\Data_Base\\{word}")

                        cropped_features, cropped_m_features = crop_sequences(collection_df, features_df, m_features_df)

                        save_files_and_plots(cropped_features, cropped_m_features, x_d, fs, f"C:\\Users\\LZW3P1\\PycharmProjects\\lip reader\\Data_Base\\{word}\\{new_dir1}")


if __name__ == '__main__':
    data_manager = DataManager()
    data_manager.process_directories()