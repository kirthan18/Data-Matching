__author__ = 'kirthanaaraghuraman'

import json

PRODUCT_TYPE_WEIGHT = 0.5
KEYWORD_WEIGHT = 0.2
COWORD_WEIGHT = 0.1
MATERIAL_WEIGHT = 0.1
BRAND_WEIGHT = 0.1


#List of possible product types that could be associated with a laptop case
laptop_cases_types = ['Laptop Sleeves','Bags, Cases & Skins','Rolling Business Cases',
                      'Soft Sided Briefcase','Leather|15.4|Briefcases|Top Loading|Removable Shoulder Strap|Laptop Compatible',
                      'Laptop Cases', 'Hard Cases', 'Laptop Backpacks', 'Briefcases', 'Rolling Business Cases',
                      'Cases', 'Hard Shell', 'Messenger Bags','Messenger Bag','Attach Cases',
                      'Laptop Sleeve|Water Resistant', 'Water Resistant|Hardsided|Designed For Mac',
                      'Backpacks', 'Notebook carrying backpack', 'Notebook carrying case']

laptop_cases_product_types = ['Laptop Bags & Cases', 'Electronics Carrying Cases', 'Laptop Computers', 'Computer Cases',
                              'Backpacks','Handbags']

important_keywords = ['notebook', 'notebooks', 'computer', 'computers', 'macbook', 'macbooks', 'laptop', 'laptops',
                      'backpack', 'mac', 'macs', 'netbook']

co_words = ['sleeve', 'case', 'zippered', 'pocket', 'zipper', 'zipperless']

product_material_list = ['neoprene', 'nylon', 'polyester', 'duraceltex', 'leather', 'suede', 'cowhide', 'fabric',
                         'synthetic', 'quilted microfibre', 'cotton canvas', 'vinyl', 'twisted poly',
                         'leather top or full grain', 'ballistic nylon']

product_brand_list = ['mckleinusa', 'targus', 'mobile edge', 'case logic', 'kensington', 'higher ground', 'mcklein',
                      'david king', 'sumdex', 'netpack', 'designer sleeves', 'butterfly', 'solo', 'royce leather',
                      'travelon', 'maccase', 'caribee', 'leatherbay', 'antenna', 'team promark', 'ebags',
                      'franklincovey', 'designer sleeves', 'shoreline', 'travelon', 'ice red', 'casauri',
                      'protec', 'travelers choice', 'centon', 'ed hardy', 'looptworks']

negative_keywords = ['ipad', 'iphone']


#Reading file and obtaining product pairs and adding them to productList
def extract_json_objects(filename):
    line_count = 0
    product_list = []
    with open(filename,'r') as sampleFile:
        for line in sampleFile:
            json_object = ''
            json_objects = []
            for i in range(0,len(line)):
                if line[i] == '?':
                    if line[i+1] == '{':
                        j = i + 1
                        while line[j] != '?':
                            json_object = json_object + line[j]
                            j = j + 1
                        #print(jsonObject)
                        json_objects.append(json_object)
                        json_object = ''
                        if len(json_objects) == 2:
                            product_list.append(json_objects)
                            break
            line_count = line_count + 1
    return product_list
#print(line_count)
#print(json_object_count)
#print(len(product_list))

#For every product pair, extract the attribute value pairs
def extract_key_values_from_json(product_list):
    count = 0
    product_keys = []
    product_json_list = []
    for i in range(0, len(product_list)):
        json_objects = []
        for j in range(0, len(product_list[i])):
            json_string = product_list[i][j]
            try:
                parsed_json = json.loads(json_string)
                count = count + 1
            except Exception as e:
                print(e)
            #print(parsed_json)
            json_objects.append(parsed_json)
            if 'Type' in parsed_json.keys():
                if parsed_json['Type'][0] == 'default':
                    print(parsed_json['Product Long Description'])
            for key in parsed_json.keys():
                if key not in product_keys:
                    product_keys.append(key)
        product_json_list.append(json_objects)
    print(product_keys)
    return product_keys, product_json_list


def identify_laptop_case(product_json_list):

    prediction_file = open("prediction_file.txt", 'a')

    for product_pair in product_json_list:
        for product in product_pair:

            product_confidence_score = 0.0
            product_type = ''
            product_material = ''
            product_brand = ''
            product_long_description = ''
            product_short_description = ''
            check_brand_in_desc = False

            if 'Type' in product:
                product_type = product['Type'][0]
            if 'Product Type' in product:
                product_type = product['Product Type'][0]
            if 'Material' in product:
                product_material = product['Material'][0].lower()
            if 'Product Long Description' in product:
                product_long_description = product['Product Long Description']
            if 'Product Short Description' in product:
                product_short_description = product['Product Short Description']

            if product_type in laptop_cases_types or product_type in laptop_cases_product_types:
                product_confidence_score = product_confidence_score + PRODUCT_TYPE_WEIGHT

            if product_material in product_material_list:
                product_confidence_score = product_confidence_score + MATERIAL_WEIGHT
                check_brand_in_desc = False
            else:
                check_brand_in_desc = True

            if product_brand in product_brand_list:
                product_confidence_score = product_confidence_score + BRAND_WEIGHT

            for keyword in important_keywords:
                for word in product_long_description:
                    if keyword in word:
                        product_confidence_score = product_confidence_score + KEYWORD_WEIGHT

            if check_brand_in_desc:
                for brand_name in product_brand_list:
                    for description in product_long_description:
                        if brand_name in description:
                            product_confidence_score = product_confidence_score + BRAND_WEIGHT

            for word in co_words:
                for description in product_long_description:
                    if word in description:
                        product_confidence_score = product_confidence_score + COWORD_WEIGHT

            for keyword in important_keywords:
                for word in product_short_description:
                    if keyword in word:
                        product_confidence_score = product_confidence_score + KEYWORD_WEIGHT

            for word in co_words:
                for description in product_short_description:
                    if word in description:
                        product_confidence_score = product_confidence_score + COWORD_WEIGHT

            print("Product confidence score = " + str(product_confidence_score))
            if product_confidence_score >= 0.7:
                print('Product identified as laptop case.')
                prediction_file.write('Y\n')
            elif product_confidence_score >= 0.4 and product_confidence_score < 0.7:
                print('Product maybe a laptop case.')
                prediction_file.write('IDK\n')
            else:
                print('Product not identified as laptop case.')
                prediction_file.write('N\n')


def get_accuracy(product_json_list):

    count = 0
    correct_instance = 0;
    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0
    false_negative_index = []
    idk_count = 0

    actual_pred_file = open('actual_prediction.txt', 'r')
    pred_file = open('prediction_file.txt', 'r')
    for i in range(650):
        line1 = actual_pred_file.readline()
        line2 = pred_file.readline()
        line1 = line1.replace('\n','')
        line2 = line2.replace('\n','')

        print(line1 + ' ' + line2)

        if line1 == line2:
            correct_instance = correct_instance + 1

        if line1 == 'Y':
            if line2 == 'Y':
                true_positive = true_positive + 1
            elif line2 == 'N':
                false_negative = false_negative + 1
                print('False negative identified in index : ' + str(i))
                false_negative_index.append(i/2)
        elif line1 == 'N':
            if line2 == 'N':
                true_negative = true_negative + 1
            elif line2 == 'Y':
                false_positive = false_positive + 1

        if line2 == 'IDK':
            idk_count = idk_count + 1

        count = count + 1
    print('Accuracy : ' + str(correct_instance/650))
    print('Total laptop cases to be identified : ' + str(true_positive + false_negative + idk_count))
    print('I dont know : ' + str(idk_count))
    print('True Positives : ' + str(true_positive))
    print('False Positive : ' + str(false_positive))
    print('True Negatives : ' + str(true_negative))
    print('False Negative : ' + str(false_negative))

    for index in false_negative_index:
        for product in product_json_list[int(index/2)]:
            for keys in product:
                print(keys)



def test_data():
    extract_json_objects('/Users/kirthanaaraghuraman/Documents/CS799/Data Matching - Implementation/Files/test_data.txt')
    extract_key_values_from_json()
    identify_laptop_case()


'''def analyse_false_negative():
    for index in false_negative_index:
        for product in product_json_list[int(index/2)]:
            for keys in product:
                print(keys)'''

def main():
    product_list = extract_json_objects('/Users/kirthanaaraghuraman/Documents/CS799/Data Matching - Implementation/Files/sample_product_pairs.txt')
    product_keys, product_json_list = extract_key_values_from_json(product_list)
    identify_laptop_case(product_json_list)
    get_accuracy(product_json_list)
    #analyse_false_negative()


if __name__ == "__main__":
     main()



