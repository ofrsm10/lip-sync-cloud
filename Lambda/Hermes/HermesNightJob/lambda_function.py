import gc
import os
import tempfile
from datetime import datetime
import cv2
import mediapipe as mp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import List
from sklearn.preprocessing import minmax_scale
import boto3
from botocore.exceptions import NoCredentialsError

S3_BUCKET_NAME = 'lipsync'
s3_client = boto3.client('s3')
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# CONSTANTS:
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


def crop_helper(d1, d, min_seq_len1=5, min_seq_len2=17, max_break_len=6, mirror=False):
    start_indices = []
    end_indices = []
    start_index = None

    if mirror:
        d1_area = d1["area1"]
    else:
        d1_area = d1["area"]
    for i, area in enumerate(d1_area):
        if area > 600 and start_index is None:
            start_index = i
        elif area < 500 and start_index is not None:
            start_indices.append(start_index)
            end_indices.append(i)
            start_index = None
    if start_index is not None:
        start_indices.append(start_index)
        end_indices.append(len(d1) - 1)

    merged_start_indices = []
    merged_end_indices = []
    start_index = start_indices[0]
    end_index = end_indices[0]
    for i in range(1, len(start_indices)):
        if start_indices[i] - end_index <= max_break_len:
            end_index = end_indices[i]
        else:
            if end_index - start_index + 1 >= min_seq_len1:
                merged_start_indices.append(start_index)
                merged_end_indices.append(end_index)
            start_index = start_indices[i]
            end_index = end_indices[i]
    if end_index - start_index + 1 >= min_seq_len1:
        merged_start_indices.append(start_index)
        merged_end_indices.append(end_index)

    # Crop both dataframes into the same number of continuous sequences
    cropped_df = []
    for start, end in zip(merged_start_indices, merged_end_indices):
        if 55 >= end - start >= min_seq_len2:
            cropped_df.append(d.iloc[start - 1:end + 5])

    return cropped_df


def crop_sequences(df1, df2, df3):
    print("Cropping data frames")
    crop1 = crop_helper(df1, df2)
    crop2 = crop_helper(df1, df3, mirror=True)
    print(f"Cropped {len(crop1)} samples..")
    print(f"Cropped {len(crop2)} samples from mirrored video..")
    return crop1, crop2


def convex_hull(coordinates: List[tuple]) -> List[tuple]:
    def cross_product(a, b, c):
        x1 = b[0] - a[0]
        y1 = b[1] - a[1]
        x2 = c[0] - a[0]
        y2 = c[1] - a[1]
        return x1 * y2 - x2 * y1

    coordinates.sort()
    lower_hull = []
    for p in coordinates:
        while len(lower_hull) >= 2 and cross_product(lower_hull[-2], lower_hull[-1], p) < 0:
            lower_hull.pop()
        lower_hull.append(p)

    upper_hull = []
    for p in reversed(coordinates):
        while len(upper_hull) >= 2 and cross_product(upper_hull[-2], upper_hull[-1], p) < 0:
            upper_hull.pop()
        upper_hull.append(p)

    return lower_hull[:-1] + upper_hull[:-1]


def extract_mouth_histogram(frame, idxs, tongue_lower, tongue_upper,
                            teeth_lower, teeth_upper, index_list=INLINE):
    xi = idxs[LEFT][0]
    xf = idxs[RIGHT][0]
    yi = idxs[UPPER][1]
    yf = idxs[LOWER][1]

    height = frame.shape[0]
    width = frame.shape[1]
    points = []
    for idx in index_list:
        points.append(idxs[idx])
    mask = np.zeros((height, width), dtype=np.uint8)
    hull_points = convex_hull(points)
    points = np.array([hull_points], dtype=int)
    cv2.fillPoly(mask, points, 255)
    total_area = float(np.count_nonzero(mask))

    res = cv2.bitwise_and(frame, frame, mask=mask)
    hsv = cv2.cvtColor(res, cv2.COLOR_RGB2HSV)
    cropped = hsv[yi: yf, xi: xf]

    # Create masks for tongue and teeth regions
    tongue_mask = cv2.inRange(cropped, tongue_lower, tongue_upper)
    teeth_mask = cv2.inRange(cropped, teeth_lower, teeth_upper)

    tongue_area = cv2.countNonZero(tongue_mask)
    teeth_area = cv2.countNonZero(teeth_mask)

    tongue_ratio = round((tongue_area / total_area), 5)
    teeth_ratio = round((teeth_area / total_area), 5)

    return teeth_ratio, tongue_ratio, total_area


def extract_features(results, frame, teeth_lower=np.array([110, 0, 65]), teeth_upper=np.array([177, 127, 204]),
                     tongue_lower=np.array([0, 20, 60]), tongue_upper=np.array([20, 180, 255])):
    for face_landmarks in results.multi_face_landmarks:
        slopes, idxs = mp_drawing.get_3D_contour_features(
            image=frame,
            landmark_list=face_landmarks,
            connections=mp_face_mesh.FACEMESH_LIPS)
        x_diff = abs(idxs[RIGHT][0] - idxs[LEFT][0])
        y_diff = abs(idxs[UPPER][1] - idxs[LOWER][1])
        ratio = y_diff / x_diff
        area = x_diff * y_diff
        features = [0, 0, 0, 0]

        if area >= 500:
            if y_diff > 3:
                teeth, tongue, area = extract_mouth_histogram(frame, idxs, tongue_lower, tongue_upper, teeth_lower,
                                                              teeth_upper)
            else:
                teeth = tongue = 0
            features = [ratio, area, teeth, tongue]
        else:
            ratio = area = 0
        return features, area, ratio


def save_features_plot(base_path):
    with tempfile.NamedTemporaryFile() as temp_file:
        plt.savefig(temp_file.name)
        temp_file.seek(0)
        s3_key = f'{base_path}/features_norm.png'
        s3_upload_file(temp_file.name, S3_BUCKET_NAME, s3_key)


def save_files_and_plots(c_features, m_features, base_path):
    print(f"Saving..")
    for i, df in enumerate(c_features):
        path = f"sequence_{i:03d}"
        s3_path = f'{base_path}/{path}'
        s3_create_directory(s3_path)

        file_path = "features_norm.csv"
        df.columns = ['ratio', 'area', 'teeth', 'tongue']
        df['area'] = minmax_scale(df['area'])
        df_csv = df.to_csv(index=False)
        s3_key = f'{s3_path}/{file_path}'
        s3_upload_data(df_csv, S3_BUCKET_NAME, s3_key)

        plt.figure()
        plt.title(f'normalized features')
        for col in df.columns:
            plt.plot(df[col], label=col)
        plt.tight_layout()
        with tempfile.NamedTemporaryFile() as temp_file:
            plt.savefig(temp_file.name)
            temp_file.seek(0)
            s3_key = f'{s3_path}/features_norm.png'
            s3_upload_file(temp_file.name, S3_BUCKET_NAME, s3_key)
        plt.close()

    print(f"Saving mirrored..")
    mirrored_base_path = f'{base_path}_mirror'
    for i, df in enumerate(m_features):
        path = f"sequence_{i:03d}"
        s3_path = f'{mirrored_base_path}/{path}'
        s3_create_directory(s3_path)

        file_path = "features_norm.csv"
        df.columns = ['ratio', 'area', 'teeth', 'tongue']
        df['area'] = minmax_scale(df['area'])
        df_csv = df.to_csv(index=False)
        s3_key = f'{s3_path}/{file_path}'
        s3_upload_data(df_csv, S3_BUCKET_NAME, s3_key)


def s3_create_directory(s3_path):
    try:
        s3_client.put_object(Body='', Bucket=S3_BUCKET_NAME, Key=f'{s3_path}/')
        print(f"Created directory in S3: {s3_path}")
    except NoCredentialsError:
        print("AWS credentials not found.")
    except Exception as e:
        print(f"Failed to create directory in S3: {e}")


def s3_upload_file(file_path, bucket, s3_key):
    try:
        s3_client.upload_file(file_path, bucket, s3_key)
        print(f"Uploaded file to S3: {s3_key}")
    except NoCredentialsError:
        print("AWS credentials not found.")
    except Exception as e:
        print(f"Failed to upload file to S3: {e}")


def s3_upload_data(data, bucket, s3_key):
    try:
        s3_client.put_object(Body=data, Bucket=bucket, Key=s3_key)
        print(f"Uploaded data to S3: {s3_key}")
    except NoCredentialsError:
        print("AWS credentials not found.")
    except Exception as e:
        print(f"Failed to upload data to S3: {e}")
