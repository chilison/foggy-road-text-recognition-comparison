from Levenshtein import distance
import itertools
import text_detection


def compute_metrics(full_list_gt, directory, lang):
    num_of_lines = len(full_list_gt)
    text_detected = text_detection.detect_text(num_of_lines, directory, lang)
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
