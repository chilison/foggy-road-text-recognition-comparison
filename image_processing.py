import subprocess
import cv2
import shutil
import os


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
