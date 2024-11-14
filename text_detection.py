import easyocr


def detect_text(num_of_lines, directory, lang):
    """
    Recognizes text from pics.

    Args:
        num_of_lines (int): number of lines, which is equal to the number of pics.
        directory (string): name of the currently processed directory.
        lang (int): 0 stands for Russian + English, 1 – for custom Russian.

    Returns:
        detected_text_list (list[list[str]]): list of recognized string lists.
    """
    detected_text_list = []
    if (lang == 0):
        reader = easyocr.Reader(['ru', 'en'])
        print(num_of_lines)
        for i in range(1, num_of_lines + 1, 1):
            text_detections = reader.readtext(str(directory) + '/File' + str(i) + '.png', detail=0)
            detected_text_list.append(text_detections)
    else:
        reader = easyocr.Reader(['ru'])
        for i in range(1, num_of_lines + 1, 1):
            text_detections = reader.readtext(str(directory) + '/File' + str(i) + '.png', detail=0, allowlist='абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧЪЫЬЭЮЯ0123456789.- ')
            detected_text_list.append(text_detections)
    return detected_text_list
