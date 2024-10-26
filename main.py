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

def detect_text(num_of_lines, directory, lang):
    detected_text_list = []
    if (lang == 0):
        reader = easyocr.Reader(['ru', 'en'])
        print(num_of_lines)
        for i in range (1, num_of_lines + 1, 1):
            text_detections = reader.readtext(str(directory) + '/File_' + str(i) + '.png', detail = 0)
            detected_text_list.append(text_detections)
    else:
        reader = easyocr.Reader(['ru'])
        for i in range (1, num_of_lines + 1, 1):
            text_detections = reader.readtext(str(directory) + '/File_' + str(i) + '.png', detail = 0, allowlist = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧЪЫЬЭЮЯ0123456789.- ')
            detected_text_list.append(text_detections)
    return detected_text_list

def compute_metrics(full_list_gt, directory, lang):
    num_of_lines = len(full_list_gt)
    text_detected = detect_text(num_of_lines, directory, lang)
    levenshtein = []
    for i in range (0, num_of_lines, 1):
        permutations = list(itertools.permutations(full_list_gt[i]))
        gt_length = sum(len(subs) for subs in full_list_gt[i])
        # опускаем изображение, если gt для него нет
        if (gt_length != 0) : 
            min_distance = float('inf')
            best_permutation = None
            for perm in permutations:
                gt_joint = ' '.join(perm).lower()
                td_joint = ' '.join(text_detected[i]).lower()
                dist = distance(gt_joint, td_joint)/gt_length                  
                if dist < min_distance:
                    min_distance = dist
                    best_permutation = perm
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
    print(f"файл создан с первым столбцом.")


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
        print(f"новый столбец успешно добавлен в файл")
    else:
        print("количество строк в CSV не соответствует количеству элементов нового столбца")

def create_pivot_table(full_list_gt):
    type = ['Original', 'Contrast', 'FFA-Net']
    # надо записывать первый столбец отдельно, тк нужно дальше проверять длину столбцов. можно сделать проще, если сменить ориентацию таблицы
    # запись ведем так: original ru+eng, original ru, contrast ru+eng и тд
    # заголовков, получается, нет, если все же надо, то придется перезаписывать
    first_column = compute_metrics(full_list_gt, type[0], 0)
    create_csv_with_first_column(first_column)
    for i in range(1, 6, 1):    
            add_column_to_csv(compute_metrics(full_list_gt, type[int(i / 2)], i % 2))

def show_hist():
    with open('pivot_table_metrics.csv', 'r', newline='') as file:
        reader = csv.reader(file)
        data = list(reader)
        type = ['Original', 'Contrast', 'FFA-Net']
        lang = ['ru + eng', 'ru']
        for i in range(0, 6, 1):
            plt.subplot(3, 2, i + 1)
            plt.hist([row[i] for row in data], color = 'b')
            plt.title(type[int(i / 2)] + ", " + lang[i % 2])
        plt.tight_layout()
        plt.show()

def create_final_table():
    with open('final_table', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['','easyocr',''])
        writer.writerow(['','ru+eng','ru'])
        data = pd.read_csv('pivot_table_metrics.csv', header=None)
        writer.writerow(['original', str(round(data[0].mean(), 4)) + "\u00B1" + str(round(data[0].std(), 4)),
                        str(round(data[1].mean(), 4)) + "\u00B1" + str(round(data[1].std(), 4))])
        writer.writerow(['contrast', str(round(data[2].mean(), 4)) + "\u00B1" + str(round(data[2].std(), 4)),
                        str(round(data[3].mean(), 4)) + "\u00B1" + str(round(data[3].std(), 4))])
        writer.writerow(['ffa-net', str(round(data[4].mean(), 4)) + "\u00B1" + str(round(data[4].std(), 4)),
                        str(round(data[5].mean(), 4)) + "\u00B1" + str(round(data[5].std(), 4))])



def enhance_contrast(directory, num_of_pics):
    for i in range(1, num_of_pics + 1, 1):
        img = cv2.imread(directory + '/File_' + str(i) + '.png', 1)
        lab= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl = clahe.apply(l_channel)
        limg = cv2.merge((cl,a,b))
        enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        os.makedirs('Contrast', exist_ok=True)
        cv2.imwrite('Contrast/File_' +str(i)+'.png', enhanced_img)

def ffa_net():
    shutil.copytree('Original', 'FFA-Net', dirs_exist_ok=True)
    print("ffa takes too much time! srry")

def process_images(directory, num_of_pics):
    enhance_contrast(directory, num_of_pics)
    # пока я не знаю, как работать с ffa-net извне, поэтому пока заглушка
    ffa_net()

# собрали все строки из файла c  gt обратно в формате списка списков строк
full_list_gt = []
with open('ground_truth.txt', 'r') as file:
    for line in file:
        current_list = ast.literal_eval(line.strip())
        full_list_gt.append(current_list)

# за кол-во изображений принимаем кол-во строк, тк без эталонных данных распознавания нет смысла их обрабатывать, а также предполагается, что изображения пронумерованы от 1, просто пройтись по папке не получится, потому что gt расположены по порядку нумерации 
process_images('Original', len(full_list_gt))
# в этой функции создается таблица со значениями метрик по всем комбинациям параметров всех изображений
create_pivot_table(full_list_gt)
# show_hist()
# таблица с мат ожиданиями
create_final_table()