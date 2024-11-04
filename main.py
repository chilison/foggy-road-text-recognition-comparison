import ast
import itertools
import easyocr
from Levenshtein import distance
import matplotlib.pyplot as plt
import shutil
import os
import csv
import cv2
import pandas as pd
import subprocess


def detect_text(num_of_lines, directory, lang):
    detected_text_list = []
    if (lang == 0):
        reader = easyocr.Reader(['ru', 'en'])
        print(num_of_lines)
        for i in range(1, num_of_lines + 1, 1):
            text_detections = reader.readtext(str(directory) + '/File_' + str(i) + '.png', detail=0)
            detected_text_list.append(text_detections)
    else:
        reader = easyocr.Reader(['ru'])
        for i in range(1, num_of_lines + 1, 1):
            text_detections = reader.readtext(str(directory) + '/File' + str(i) + '.png', detail=0, allowlist='абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧЪЫЬЭЮЯ0123456789.- ')
            detected_text_list.append(text_detections)
    return detected_text_list


def compute_metrics(full_list_gt, directory, lang):
    num_of_lines = len(full_list_gt)
    text_detected = detect_text(num_of_lines, directory, lang)
    levenshtein = []
    for i in range(0, num_of_lines, 1):
        permutations = list(itertools.permutations(full_list_gt[i]))
        gt_length = sum(len(subs) for subs in full_list_gt[i])
        # omits pics with no ground truth
        if (gt_length != 0):
            min_distance = float('inf')
            # best_permutation = None
            for perm in permutations:
                gt_joint = ' '.join(perm).lower()
                td_joint = ' '.join(text_detected[i]).lower()
                dist = distance(gt_joint, td_joint) / gt_length
                if dist < min_distance:
                    min_distance = dist
                    # best_permutation = perm
            min_distance = round(min_distance if min_distance < 1 else 1, 4)
            levenshtein.append(min_distance)
        # print(i, gt_length, min_distance, best_permutation, text_detected[i])
    return levenshtein


def create_csv_with_first_column(first_column):
    file_name = 'pivot_table_metrics.csv'
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        for value in first_column:
            writer.writerow([value])
    print("file with the first column was created")


def add_column_to_csv(new_column):
    file_name = 'pivot_table_metrics.csv'
    with open(file_name, 'r', newline='') as file:
        reader = csv.reader(file)
        data = list(reader)
    if len(new_column) == len(data):
        for i, row in enumerate(data):
            row.append(new_column[i])
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        print("new column was successfully added")
    else:
        print("the number of rows does not match the number of elements of the new column")


def create_pivot_table(full_list_gt):
    type = ['original', 'contrast', 'results/FSNet/test']
    # first column has to be written separately as you further need to check the length of the previous columns
    # can be done easier by adding by rows, the orientation of the table has to be changed though
    # the table follows this order: original ru+eng, original ru, contrast ru+eng, etc.
    # there is no header, if one is needed, the .csv file has to be rewritten
    first_column = compute_metrics(full_list_gt, type[0], 0)
    create_csv_with_first_column(first_column)
    for i in range(1, 6, 1):
        add_column_to_csv(compute_metrics(full_list_gt, type[int(i / 2)], i % 2))


def show_hist():
    with open('pivot_table_metrics.csv', 'r', newline='') as file:
        reader = csv.reader(file)
        data = list(reader)
        type = ['original', 'contrast', 'results/FSNet/test']
        lang = ['ru + eng', 'ru']
        for i in range(0, 6, 1):
            plt.subplot(3, 2, i + 1)
            plt.hist([row[i] for row in data], color='b')
            plt.title(type[int(i / 2)] + ", " + lang[i % 2])
        plt.tight_layout()
        plt.show()


def create_final_table():
    with open('final_table', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['', 'easyocr', ''])
        writer.writerow(['', 'ru+eng', 'ru'])
        data = pd.read_csv('pivot_table_metrics.csv', header=None)
        writer.writerow(['original', str(round(data[0].mean(), 4)) + "\u00B1" + str(round(data[0].std(), 4)),
                        str(round(data[1].mean(), 4)) + "\u00B1" + str(round(data[1].std(), 4))])
        writer.writerow(['contrast', str(round(data[2].mean(), 4)) + "\u00B1" + str(round(data[2].std(), 4)),
                        str(round(data[3].mean(), 4)) + "\u00B1" + str(round(data[3].std(), 4))])
        writer.writerow(['fsnet', str(round(data[4].mean(), 4)) + "\u00B1" + str(round(data[4].std(), 4)),
                        str(round(data[5].mean(), 4)) + "\u00B1" + str(round(data[5].std(), 4))])


def enhance_contrast(directory, num_of_pics):
    for i in range(1, num_of_pics + 1, 1):
        img = cv2.imread(directory + '/File' + str(i) + '.png', 1)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l_channel)
        limg = cv2.merge((cl, a, b))
        enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        os.makedirs('contrast', exist_ok=True)
        cv2.imwrite('contrast/File' + str(i) + '.png', enhanced_img)


def fsnet(directory):
    fsnet_main_path = os.path.join('libs', 'FSNet', 'Dehazing', 'OTS', 'main.py')
    os.makedirs('reside-outdoor/test/gt', exist_ok=True)
    os.makedirs('reside-outdoor/test/hazy', exist_ok=True)
    shutil.copytree(directory, 'reside-outdoor/test/gt', dirs_exist_ok=True)
    shutil.copytree(directory, 'reside-outdoor/test/hazy', dirs_exist_ok=True)
    data_dir = 'reside-outdoor'
    # models are available at https://drive.google.com/drive/folders/1bZb9L660t4jL2wAqr23iTg6eyAnCuUBt?usp=sharing, add any of them and name it 'ots_model'
    test_model = 'ots_model.pkl'
    command = [
        'python', fsnet_main_path,
        '--data_dir', data_dir,
        '--test_model', test_model,
        '--save_image', 'True'
    ]
    print("Executing command:", command)
    subprocess.run(command, check=True)
    # shutil.copytree('original', 'results/FSNet/test', dirs_exist_ok=True)
    print("fsnet takes too much time! srry")


def process_images(directory, num_of_pics):
    enhance_contrast(directory, num_of_pics)
    fsnet(directory)


# collected all of the strings from the ground truth file and made a list of string lists
full_list_gt = []
with open('ground_truth.txt', 'r') as file:
    for line in file:
        current_list = ast.literal_eval(line.strip())
        full_list_gt.append(current_list)

# the number of pics is equal to the number of string lists since there is no reason to process images without ground truth data
process_images('original', len(full_list_gt))
# this function creates a pivot table of metrics for all parameter combinations
create_pivot_table(full_list_gt)
# show_hist()
# and this function creates a neat table of expected values with standard deviation
create_final_table()
