class Information:
    """
    Класс Information - воспомогательный класс для реализации метода str
    Создан, чтобы избежать дублирования кода в классах Student и Mentor
    Также содержит функцию get_average_rating, которая возвращает среднюю оценку и вызывается в методе str
    """
    def __str__(self):
        string_for_print = f"Имя: {self.name}\nФамилия: {self.surname}"
        if self.CLASS_TYPE == "lecturer":
            string_for_print += f"\nСредняя оценка за лекции: {self.get_average_rating()}"
        if self.CLASS_TYPE == "student":
            string_for_print += f"\nСредняя оценка за домашние задания: {self.get_average_rating()}"
            string_for_print += f"\nКурсы в процессе изучения: {', '.join(self.courses_in_progress)}"
            string_for_print += f"\nЗавершенные курсы: {', '.join(self.finished_courses)}"
        return string_for_print

    def get_average_rating(self) -> float:
        """ Функция возвращает округлённую среднюю оценку
        Для этого происходит распаковка всех значений словаря self.grades и подсчет средней оценки
        :return: средняя оценка (вещественное число) или сообщение "Оценок нет"
        """
        if self.grades.values():
            grades_lst = [i for a in self.grades.values() for i in a]
            return round(sum(grades_lst) / len(grades_lst), 1)
        return "Оценок нет"


class Student(Information):
    """
    Класс Student унаследован от класса Information для реализации метода str
    Содержит функцию set_rates для оценки лектора
    """
    CLASS_TYPE = "student"

    def __init__(self, name: str, surname: str, gender: str):
        self.name = name
        self.surname = surname
        self.gender = gender
        self.finished_courses = []
        self.courses_in_progress = []
        self.grades = {}

    def set_rates(self, lecturer: "Lecturer", course: str, grade: int) -> None:
        """
        Функция присваивает оценку лектору. Присваивание оценки происходит после проверок на причастность студента к курсу,
        а также причастность лектора к курсу, корректность оценки.
        Перед присваиванием оценки идёт обновление словаря grades для лектора в соответствующем метод - update_rating().
        Это необходимо для синхронизации курсов лектора и ключей в словаре с оценками,
        так как при добавлении курсов courses_attached нет связи со словарем grades.
        :param lecturer: экземпляр класса Lecturer
        :param course: название курса
        :param grade: оценка (целое число от 1 до 10)
        :return: None
        """
        if not course in self.courses_in_progress + self.finished_courses:
            raise ValueError("Студент не был на данном курсе")
        if course not in lecturer.courses_attached:
            raise ValueError("Данный лектор не ведёт этот курс")
        if type(grade) != int or grade not in range(1, 11):
            raise TypeError("Оценка должны быть целым числом от 1 до 10")
        lecturer.update_rating()
        lecturer.grades[course] += [grade]


class Mentor(Information):
    """
    Класс Mentor унаследован от класса Information для реализации метода str
    Описывает общие характеристики лекторов и ревьюеров
    """
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname
        self.courses_attached = []


class Lecturer(Mentor):
    """
    Класс Lecturer унаследован от класса Mentor
    Содержит воспомогательную функцию update_rating
    """
    CLASS_TYPE = "lecturer"

    def __init__(self, name: str, surname: str):
        super().__init__(name, surname)
        self.grades = {}

    def update_rating(self) -> None:
        """
        Функция обновляет исходный словарь grades (добавляет ключи из списка courses_attached)
        :return: None
        """
        for course in self.courses_attached:
            if course not in self.grades:
                self.grades[course] = []


class Reviewer(Mentor):
    """
    Класс Reviewer унаследован от класса Mentor
    Предназначен для оценки студентов - метод rate_hw
    """
    CLASS_TYPE = "reviewer"

    def rate_hw(self, student: Student, course: str, grade: int) -> None:
        """
        Функция присваивает оценку студенту
        :param student: экземпляр класса Student
        :param course: название курса
        :param grade: оценка (целое число от 1 до 10)
        :return: None
        """
        if isinstance(student, Student) and course in self.courses_attached and course in student.courses_in_progress:
            if course in student.grades:
                student.grades[course] += [grade]
            else:
                student.grades[course] = [grade]
        else:
            raise ValueError("Ошибка в оценке")


student_1 = Student('Some', 'Student', 'your_gender')
student_1.courses_in_progress += ['Python']
student_1.courses_in_progress += ['Git']
student_1.finished_courses += ["C++"]
student_2 = Student('Some2', 'Student2', 'your_gender')
student_2.courses_in_progress += ['Python']
student_2.courses_in_progress += ['Git', "C++"]
student_2.finished_courses += ["java"]

lecturer_1 = Lecturer('Some', 'Lecturer')
lecturer_1.courses_attached += ['Python']
lecturer_1.courses_attached += ['Git']
lecturer_2 = Lecturer('Some2', 'Lecturer2')
lecturer_2.courses_attached += ['Git']
lecturer_2.courses_attached += ['C++']

reviewer_1 = Reviewer('Some', 'Reviewer')
reviewer_1.courses_attached += ['Python']
reviewer_2 = Reviewer('Some2', 'Reviewer2')
reviewer_2.courses_attached += ['Git']
reviewer_2.courses_attached += ['C++']

reviewer_1.rate_hw(student_1, 'Python', 9)
reviewer_1.rate_hw(student_1, 'Python', 10)
reviewer_2.rate_hw(student_1, 'Git', 8)
reviewer_2.rate_hw(student_2, 'Git', 7)
reviewer_2.rate_hw(student_2, 'C++', 8)
reviewer_1.rate_hw(student_1, 'Python', 7)

student_1.set_rates(lecturer_1, 'Python', 8)
student_1.set_rates(lecturer_1, 'Python', 9)
student_1.set_rates(lecturer_1, 'Git', 10)
student_2.set_rates(lecturer_2, 'Git', 9)
student_2.set_rates(lecturer_2, 'C++', 10)

print("Информация о студентах: ")
print(student_1)
print(student_2)
print()

print("Информация о лекторах: ")
print(lecturer_1)
print(lecturer_2)
print()

print("Информация о ревьюерах: ")
print(reviewer_1)
print(reviewer_2)
print()


def average_rating_by_course(appreciated: list, course: str) -> float:
    """ Функция возвращает среднюю оценку по курсу
    По заданию требуется реализовать 2 функции, но так как функционал у них один, решил оставить 1 функцию
    :param appreciated: студентов или лекторов, экземпляры классов Student или Lecturer
    :param course: название курса
    :return: средняя оценка
    """
    ratings = []
    for subject in appreciated:
        if course in subject.grades:
            ratings += subject.grades[course]
    return round(sum(ratings) / len(ratings), 1)


print("Средняя оценка студентов по курсу Python: ")
print(average_rating_by_course([student_1, student_2], 'Python'))
print()

print("Средняя оценка студентов по курсу Git: ")
print(average_rating_by_course([student_1, student_2], 'Git'))
print()

print("Средняя оценка студентов по курсу C++: ")
print(average_rating_by_course([student_1, student_2], 'C++'))
print()

print("Средняя оценка лекторов по курсу Python: ")
print(average_rating_by_course([lecturer_1, lecturer_2], 'Python'))
print()

print("Средняя оценка лекторов по курсу Git: ")
print(average_rating_by_course([lecturer_1, lecturer_2], 'Git'))
print()

print("Средняя оценка лекторов по курсу C++: ")
print(average_rating_by_course([lecturer_1, lecturer_2], 'C++'))



