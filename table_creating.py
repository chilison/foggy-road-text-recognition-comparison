import pandas as pd
import csv
import metrics_computation


def create_csv_with_first_column(first_column):
    """
    Сreates .csv file with the first column.

    Args:
        first_column (list[float]): first column to be added to the table, by default is original ru+eng.
    """
    file_name = 'pivot_table_metrics.csv'
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        for value in first_column:
            writer.writerow([value])
    print("file with the first column was created")


def add_column_to_csv(new_column):
    """
    Adds columns (apart from the first one) to the already existing .csv file.

    Args:
        new_column (list[float]): new column to be added to the table.
    """
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
    """
    Invokes functions for creating and filling a pivot table.

    Args:
        full_list_gt (list[list[string]]): list of string list of ground truth which you prepare yourself.
    """
    type = ['original', 'contrast', 'results/FSNet/test']
    # first column has to be written separately as you further need to check the length of the previous columns
    # can be done easier by adding by rows, the orientation of the table has to be changed though
    # the table follows this order: original ru+eng, original ru, contrast ru+eng, etc.
    # there is no header, if one is needed, the .csv file has to be rewritten
    first_column = metrics_computation.compute_metrics(full_list_gt, type[0], 0)
    create_csv_with_first_column(first_column)
    for i in range(1, 6, 1):
        add_column_to_csv(metrics_computation.compute_metrics(full_list_gt, type[int(i / 2)], i % 2))


def create_final_table():
    """
    Creates a final table of expected values with standard deviation.
    """
    with open('final_table.csv', 'w', newline='') as file:
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
