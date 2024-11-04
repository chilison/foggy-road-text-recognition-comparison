This repository was created to compare different image processing methods to achieve the best EasyOCR text recognition results on hazy outdoor images.

## Usage
In order to use this repository one has to create a folder 'original' with original pictures in it and a 'ground_truth.txt' file. Pictures should be named as 'File*it's order*' and follow the same order as the corresponding string lists in the txt file.  

Also we're using [FSNet](https://github.com/c-yn/FSNet/tree/main) (specialized tool for image dehazing), which needs a pretrained model, download any ots one from [gdrive](https://drive.google.com/drive/folders/1AxZ7TbLYBLclOEe2F6YsrVkafMMXFmFs) and name it 'ots_model.pkl'. Processing may take a long time.

Example of the dataset and the ground truth file can be found [here](https://drive.google.com/drive/folders/1lbePqSww66iGddPmBdCAXud4Q8uzyL1q?usp=sharing).

~~~
python main.py
~~~

## Acknoledgements

Thanks, [FSNet](https://github.com/c-yn/FSNet/tree/main)!


