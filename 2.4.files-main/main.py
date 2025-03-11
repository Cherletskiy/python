import pprint


def get_dict(recipes: str) -> dict:
    """
    Функция принимает на вход путь до файла с рецептами, читает построчно и формируеет словарь с рецептами.
    :param recipes: путь до файла
    :return: словарь вида:
    {
    'Омлет': [
    {'ingredient_name': 'Яйцо', 'quantity': 2, 'measure': 'шт.'},
    {'ingredient_name': 'Молоко', 'quantity': 100, 'measure': 'мл'},
    {'ingredient_name': 'Помидор', 'quantity': 2, 'measure': 'шт'}
    ],
    }
    """
    dict_rep = {}
    with open(recipes, "r", encoding="utf-8") as f:
        while True:
            name = f.readline().strip()
            if name == "":
                break
            count = int(f.readline().strip())
            dict_rep[name] = []
            for i in range(count):
                ing, count, unit = f.readline().strip().split(" | ")
                dict_rep[name].append({"ingredient_name": ing, "quantity": int(count), "measure": unit})
            f.readline()
    return dict_rep


def get_shop_list_by_dishes(dishes: list, person_count: int) -> dict:
    """
    Функция принимает на вход список блюд и количество человек, возвращает словарь необходимых ингредиентов.
    :param dishes: список блюд
    :param person_count: количество человек
    :return: словарь необходимых ингредиентов
    """
    if not isinstance(dishes, list) and not isinstance(person_count, int):
        raise TypeError("Неверный тип данных")
    if person_count <= 0:
        raise ValueError("Количество человек должно быть больше нуля")
    if not dishes:
        raise ValueError("Список блюд не может быть пустым")
    shop_list = {}
    for dish in dishes:
        if dish in cook_book:
            for ing in cook_book[dish]:
                if ing["ingredient_name"] not in shop_list:
                    shop_list[ing["ingredient_name"]] = {"measure": ing["measure"], "quantity": ing["quantity"] * person_count}
                else:
                    shop_list[ing["ingredient_name"]]["quantity"] += ing["quantity"] * person_count
        else:
            raise ValueError(f"Блюдо {dish} отсутствует в книге рецептов")
    return shop_list


cook_book = get_dict('recipes.txt')
# print(cook_book)
# pprint.pprint(cook_book)

shop_list = get_shop_list_by_dishes(['Запеченный картофель', 'Омлет'], 2)
# pprint.pprint(shop_list)

# shop_list_2 = get_shop_list_by_dishes(['Омлет', 'Фахитос'], 3)
# pprint.pprint(shop_list_2)


def get_sorted_file(files: list) -> str:
    """
    Функция принимает на вход список файлов,
    возвращает содержимое всех файлов в одном файле отсортированном по количеству строк.
    :param files: списки с названием файлов для сортировки и объединения
    :return: строки из созданного файла. Содержимое файла предваряется служебной информацией на 2-х строках:
     имя файла и количество строк в нем.
    """
    if not isinstance(files, list):
        raise TypeError("Неверный тип данных")
    if not files:
        raise ValueError("Список файлов не может быть пустым")
    file_result = 'result.txt'
    new_file = open(file_result, "w", encoding="utf-8")
    new_file.close()
    with open(file_result, "a", encoding="utf-8") as f:
        res = []
        for file in files:
            with open(file, "r", encoding="utf-8") as f2:
                lines = [line.strip() for line in f2.readlines()]
                res.append([f2.name, str(len(lines)), *lines, ""])
        res.sort(key=lambda x: int(x[1]))
        for i in res:
            s = "\n".join(i)
            f.write(s)
    with open(file_result, "r", encoding="utf-8") as f:
        return f.read()

get_sorted_file(['1.txt', '2.txt', '3.txt'])
# print(get_sorted_file(['1.txt', '2.txt', '3.txt']))

