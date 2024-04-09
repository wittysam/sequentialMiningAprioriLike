from collections import defaultdict
from itertools import combinations, permutations
import sys


def read_data_file(file_path):
    data_records = {}
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split()
            if not parts:
                continue  # Skip empty lines

            id = int(parts[0])  # The first number is the ID
            if id not in data_records:
                data_records[id] = {}

            # Process pairs of (time, itemNumber)
            for i in range(1, len(parts), 2):
                time = int(parts[i])
                itemNumber = int(parts[i + 1])
                if time in data_records[id]:
                    # If the time already exists, append the itemNumber to the existing list
                    data_records[id][time].append(itemNumber)
                else:
                    # Otherwise, create a new list for this time
                    data_records[id][time] = [itemNumber]

    return data_records


#
def first(data_records):
    # 初始化一個字典來跟踪每個ItemNumbers組合出現在多少個不同的ID中
    item_combinations_count = defaultdict(set)

    # 遍歷data_records來填充item_combinations_count
    for id, times in data_records.items():
        seen_combinations = set()  # 用於記錄當前ID已處理的組合
        for time, itemNumbers in times.items():
            # 為當前列表生成所有可能的非空子集組合
            for r in range(1, len(itemNumbers) + 1):
                for combination in combinations(itemNumbers, r):
                    # 確保每個組合在當前ID中只被計數一次
                    if combination not in seen_combinations:
                        item_combinations_count[combination].add(id)
                        seen_combinations.add(combination)

    # 將set轉換成計數
    item_combinations_count = {
        items: len(ids) for items, ids in item_combinations_count.items()
    }

    return item_combinations_count


def filtering(min_supp, item_id_count):
    # 設定最小支持度閾值

    # 過濾掉不滿足最小支持度的組合
    filtered_combinations = {
        items: count for items, count in item_id_count.items() if count >= min_supp
    }

    # 印出過濾後結果
    # print(f"Filtered Combinations (min_supp >= {min_supp}):")
    # for items, count in sorted(filtered_combinations.items(), key=lambda x: len(x[0])):
    #     print(f"ItemNumbers: {items}, IDs: {count}")
    return filtered_combinations


def mapping(filtered_combinations):

    combination_to_new_number = {}
    new_number = 1
    for combination in filtered_combinations.keys():
        combination_to_new_number[combination] = new_number
        new_number += 1

    return combination_to_new_number


def find_new_numbers_for_combinations(item_numbers, combination_to_new_number):
    new_numbers = []
    for combination, new_num in combination_to_new_number.items():
        if set(combination).issubset(set(item_numbers)):
            new_numbers.append(new_num)
    return new_numbers


def update(data_records, iic_number):
    transformed_records = {}
    # ID: 1 ~ 20000
    for id, times in data_records.items():
        items_list = []
        for time, items in times.items():
            if len(items) == 1:
                if tuple(items) in iic_number.keys():
                    # print(tuple([iic_number[tuple(items)]]))
                    items_list.append(tuple([iic_number[tuple(items)]]))
            else:
                # print(items)
                k = len(items)
                tmp = list()
                # if k == 1:

                #     # 舉例來說：
                #     # items = [2232, 7092]
                #     # 不用check Combinations
                #     if tuple(items) in iic_number.keys():
                #         items_list.append(tuple([iic_number[tuple(items)]]))
                # else:
                # print(f"驗證現在輸出{items}只會是三個數字以上")
                while k > 0:
                    for subset in combinations(items, k):
                        # print(f"現在是:{subset}")
                        candidate = tuple(subset)
                        if candidate in iic_number.keys() and candidate != []:
                            tmp.append(iic_number[candidate])
                    k -= 1
                if tmp != []:
                    items_list.append(tuple(tmp))
        transformed_records[id] = items_list
    return transformed_records


def all_subsets_frequent(candidate, prev_frequent_itemsets):
    # print(prev_frequent_itemsets)
    for subset in combinations(candidate, len(candidate) - 1):
        if set(subset) not in prev_frequent_itemsets:
            return False
    return True


def generate_new_candidates(current_frequent, k, iic_number):
    # print(current_frequent)
    leng = len(current_frequent)
    new_candidates = list()
    if k == 2:
        for itemset in permutations(current_frequent, k):

            itemset = list(tuple([i]) for i in itemset)
            # print(itemset)
            cmprA = get_key_from_value(iic_number, itemset[0][0])
            cmprB = get_key_from_value(iic_number, itemset[1][0])
            if cmprA == cmprB:
                continue
            new_candidates.append(itemset)
        return new_candidates
    # print(f"What the fuck?{current_frequent}")
    for i in range(leng):
        for j in range(leng):
            if i == j:
                continue
            l = 0
            # print(current_frequent[i])
            # print(current_frequent[j])
            if j > i:
                front = list(current_frequent[i])
                behind = list(current_frequent[j])
            else:
                front = list(current_frequent[j])
                behind = list(current_frequent[i])
            for m in range(k - 2):
                if set(front[1 + m]) & set(behind[k - 2 - m - 1]):
                    l += 1
            if l == (k - 2):
                # print("--------HERE IS------------")

                # print(current_frequent[i] | current_frequent[j])
                tmp = [front[0]]
                for i in range(k - 1):
                    tmp.append(behind[i])
                # print(f"This is {tmp}")
                if tmp not in new_candidates:
                    new_candidates.append(tmp)

    return new_candidates


def calculate_support(data_records, candidates):
    support_counts = defaultdict(int)
    candidate_sets = [list(candidate) for candidate in candidates]
    # print(candidate_sets)

    # ID 1 ~ 20000
    for id, items_list in data_records.items():
        # print(f"WATCH HERE:{items_list}")
        # print(items_list)

        if len(items_list) == 0:
            continue
        for candidate in candidate_sets:
            # print(f"What out bitch{candidate}")
            seen_list = []
            p, q = 0, 0
            p_end = len(items_list)
            q_end = len(candidate)
            # print(f"交易中：{items_list}")
            # print(p_end)
            # print(items_list[p_end - 1])
            # print(f"比較：{candidate}")
            # print(q_end)
            # print(candidate[q_end - 1])
            if q_end > p_end:
                # 資料比ID中的長
                continue
            else:
                while p < p_end and q < q_end:
                    # print(f"item{items_list[p]}")
                    # print(f"candidate{candidate[q]}")
                    # print(candidate[q] & items_list[p])
                    # if len(candidate[q]) == 2:
                    # print(f"item{items_list}")
                    # print(f"candidate{candidate}")
                    # print()
                    # print(candidate[q] & items_list[p])
                    if (set(candidate[q]) & set(items_list[p])) == set(candidate[q]):
                        # print("換下一個")
                        p += 1
                        q += 1
                    else:
                        # print("找不到")
                        p += 1
                if q == (q_end):
                    # if len(tuple(candidate)) == 3:
                    #     print(f"現在在處理的是：{tuple(candidate)}")
                    #     print(f"item: {items_list}")
                    #     print(f"candidate: {candidate}")
                    # print(candidate[q] & items_list[p])

                    support_counts[tuple(candidate)] += 1
                    # print(
                    #     f"現在{[tuple(candidate)]}的數量有 + 1，變成{support_counts[tuple(candidate)]}"
                    # )

    return support_counts


def get_key_from_value(d, val):
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None


def apriori_like_algorithm(data_records, min_supp, item_id_count, iic_number):
    current_frequent = [
        iic_number[item]
        for item in item_id_count.keys()
        if item_id_count[item] >= min_supp
    ]

    output = dict()
    output[1] = current_frequent
    k = 2
    while True:
        new_candidates = generate_new_candidates(current_frequent, k, iic_number)
        # print(new_candidates)

        support_counts = calculate_support(data_records, new_candidates)

        tmp = dict()
        for itemset, count in support_counts.items():
            if count >= int(min_supp):
                tmp[itemset] = count
        output[k] = tmp
        new_frequent = [
            list(candidate)
            for candidate, count in support_counts.items()
            if count >= int(min_supp)
        ]

        if not new_frequent:  # not new_frequent :
            break
        current_frequent = new_frequent
        k += 1
    return output


if __name__ == "__main__":

    file_path = "seqdata.dat.txt"
    data_records = read_data_file(file_path)
    # data_records = {ID: {TIME: ITEM}}

    min_supp = float(input("Please input minimum support(0~1):")) * len(data_records)
    item_id_count = first(data_records)
    # item_id_count = {tuple(itemset): count}

    item_id_count = filtering(min_supp, item_id_count)
    # print(item_id_count)

    iic_number = mapping(item_id_count)
    # print(iic_number)
    # iic_number = {tuple: int}
    # (2227,) : 12

    data_records = update(data_records, iic_number)
    # 舉例
    # 19948: [(12,), (12,), (12,)]
    # print(data_records)
    output = apriori_like_algorithm(data_records, min_supp, item_id_count, iic_number)
    # print(output)

    orig_stdout = sys.stdout
    path = "output.txt"
    f = open(path, "w")
    sys.stdout = f

    for i in output.keys():
        if i == 1:
            continue
        else:
            for itemset in output[i].keys():
                end = 0
                for item in itemset:
                    if end == (len(itemset) - 1):
                        all = len(get_key_from_value(iic_number, item[0]))
                        if all == 1:
                            print(get_key_from_value(iic_number, item[0])[0], end=" ")
                        else:
                            print("{", end=" ")
                            for j in range(all):
                                print(
                                    f" {get_key_from_value(iic_number, item[0])[j]} ",
                                    end=" ",
                                )

                            print("}", end=" ")

                    else:
                        all = len(get_key_from_value(iic_number, item[0]))
                        if all == 1:
                            print(
                                get_key_from_value(iic_number, item[0])[0], end=" -1 "
                            )

                        else:
                            print("{", end=" ")
                            for j in range(all):
                                print(
                                    f" {get_key_from_value(iic_number, item[0])[j]} ",
                                    end=" ",
                                )
                            print("}", end=" -1 ")

                    end += 1
                print(f"SUP: {output[i][itemset]}")
    sys.stdout = orig_stdout
    f.close()
