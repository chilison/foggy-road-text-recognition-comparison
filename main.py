import ast
import matplotlib.pyplot as plt
import csv
import table_creating


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


# collected all of the strings from the ground truth file and made a list of string lists
full_list_gt = []
with open('ground_truth.txt', 'r') as file:
    for line in file:
        current_list = ast.literal_eval(line.strip())
        full_list_gt.append(current_list)

# the number of pics is equal to the number of string lists since there is no reason to process images without ground truth data
# image_processing.process_images('original', len(full_list_gt))
# this function creates a pivot table of metrics for all parameter combinations
table_creating.create_pivot_table(full_list_gt)
# show_hist()
# and this function creates a neat table of expected values with standard deviation
table_creating.create_final_table()
