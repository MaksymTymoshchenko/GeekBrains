from gungner import render

from patterns.behavioral_patterns import BaseSerializer, CreateView, DeleteView, FileWriter, UpdateView, ListView, EmailNotifier, SmsNotifier
from patterns.creational_patterns import Logger, Engine, Student, Category
from patterns.structural_patterns import Router, Debug
from patterns.architectural_system_pattern_mappers import MapperRegistry
from patterns.architectural_system_pattern_unit_of_work import UnitOfWork


engine = Engine()
log_writer = FileWriter('main')
logger = Logger(log_writer)
routes = {}
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)


# контроллер - главная страница
@Router(url='/', routes=routes)
class Index:
    @Debug(name='Index')
    def __call__(self, request):
        # print(logger, logger2)
        logger.log('LogLine: ' + str(request.get('date').strftime('%H:%M:%S')) + ' - главная страница!')
        return '200 OK', render('index.html', page='index')

@Router(url='/about', routes=routes)
class About:
    @Debug(name='About')
    def __call__(self, request):
        return '200 OK', render('about.html', page='about')

@Router(url='/learning', routes=routes)
class Learning:
    @Debug(name='Learning')
    def __call__(self, request):
        promocode = request.get('promocode', None)
        date = request.get('date', None)
        cities = ['Москва', 'Санкт-Петербург', 'Екатеринбург']
        courses = [
            {
                'title': 'Основы Python',
                'schedule': [
                    {
                        'date': 'Сб, 20 февраля 2021',
                        'time': '11:00 - 14:00'
                    },
                    {
                        'date': 'Сб, 6 марта 2021',
                        'time': '11:00 - 14:00'
                    },
                    {
                        'date': 'Сб, 20 марта 2021',
                        'time': '11:00 - 14:00'
                    },
                ]
            },
            {
                'title': 'Алгоритмы и структуры данных на Python',
                'schedule': [
                    {
                        'date': 'Сб, 10 апреля 2021',
                        'time': '11:00 - 13:00'
                    },
                    {
                        'date': 'Сб, 1 мая 2021',
                        'time': '11:00 - 13:00'
                    },
                    {
                        'date': 'Сб, 8 мая 2021',
                        'time': '11:00 - 13:00'
                    },
                ]
            },
            {
                'title': 'Основы Django',
                'schedule': [
                    {
                        'date': 'Сб, 26 июня 2021',
                        'time': '11:00 - 13:00'
                    },
                    {
                        'date': 'Сб, 3 июля 2021',
                        'time': '11:00 - 13:00'
                    },
                    {
                        'date': 'Сб, 10 июля 2021',
                        'time': '11:00 - 13:00'
                    },
                ]
            },
            {
                'title': 'Основы Flask',
                'schedule': [
                    {
                        'date': 'Сб, 28 августа 2021',
                        'time': '11:00 - 16:00'
                    },
                    {
                        'date': 'Сб, 4 сентября 2021',
                        'time': '11:00 - 16:00'
                    },
                    {
                        'date': 'Сб, 11 сентября 2021',
                        'time': '11:00 - 16:00'
                    },
                ]
            }
        ]
        return '200 OK', render('learning.html', date=date, cities=cities, courses=courses, promocode=promocode, page='learning')

@Router(url='/contact', routes=routes)
class Contact:
    @Debug(name='Contact')
    def __call__(self, request):
        if 'params' in request and request['method'] == 'POST':
            contact = ', '.join("{!s}={!r}".format(key,val) for (key,val) in request['params'].items())
            with open("contacts.txt", "a+") as contacts_file:
                contacts_file.write(contact + "\n")
        
        return '200 OK', render('contact.html', page='contact')

@Router(url='/categories/create', routes=routes)
class CategoriesCreateView(CreateView):
    template_name = 'category_create.html'
    page = 'categories'

    def create_object(self, data: dict):
        name = data.get('name')

        if not name:
            raise Exception('Необходимо указать имя категории!')
        
        category = Category(name=name)
        schema = {'name': name}
        category.mark_new(schema)
        UnitOfWork.get_current().commit()

@Router(url='/categories', routes=routes)
class CategoriesListView(ListView):
    template_name = 'categories.html'
    page = 'categories'
    context_object_name = 'categories_list'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('category')
        return mapper.all()

@Router(url='/categories/delete', routes=routes)
class CategoriesDeleteView(DeleteView):
    template_name = 'categories.html'
    page = 'categories'
    context_object_name = 'categories_list'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('category')
        return mapper.all()

    def delete_object(self, data: dict):
        category_id = data.get('id')
        category = Category(id=category_id)
        category.mark_removed()
        UnitOfWork.get_current().commit()

@Router(url='/courses/create', routes=routes)
class CreateCourse:
    category_id = 0

    def __call__(self, request):
        logger.log('LogLine: ' + str(request.get('date').strftime('%H:%M:%S')) + ' - создание курса!')
        if request['method'] == 'POST':
            name = request['params'].get('name', None)
            type_alias = request['params'].get('type_alias', None)

            # TODO: Session postback
            if not name:
                raise Exception('Необходимо указать название курса!')

            if type_alias not in ['webinar', 'interactive', 'video']:
                raise Exception('Некорректный тип курса!')
                
            category = None
            if self.category_id != 0:
                category = engine.get_category_by_id(int(self.category_id))

                course = engine.create_course(type_alias, name, category)
                engine.courses.append(course)

            return '200 OK', render('courses.html', courses_list=engine.courses)

        else:
            try:
                self.category_id = request['params'].get('id')
                category = engine.get_category_by_id(int(self.category_id))

                return '200 OK', render('course_create.html', category=category)
            except KeyError:
                return '200 OK', 'Сначала нужно добавить категории!'

@Router(url='/courses', routes=routes)
class CoursesList:
    def __call__(self, request):
        logger.log('LogLine: ' + str(request.get('date').strftime('%H:%M:%S')) + ' - список курсов!')
        try:
            mapper = MapperRegistry.get_current_mapper('category')
            category = mapper.get_by_id(request['params'].get('id'))
            # category = engine.get_category_by_id(request['params'].get('id'))

            return '200 OK', render('courses.html', courses_list=category.courses, page='courses')
        
        except KeyError:
            return '200 OK', 'Список курсов пуст!'

@Router(url='/courses/copy', routes=routes)
class CopyCourse:
    def __call__(self, request):
        logger.log('LogLine: ' + str(request.get('date').strftime('%H:%M:%S')) + ' - копирование курса!')
            
        try:
            name = request['params'].get('name', None)
            
            if not name:
                raise Exception('Не указано название курса, который будет скопирован!')

            copied_course = engine.get_course_by_name(name)

            if not copied_course:
                raise Exception('Курс с таким именем не найден!')

            if copied_course:
                new_name = f'copy_{name}'
                course = copied_course.clone()
                course.name = new_name
                engine.courses.append(course)

            return '200 OK', render('courses.html', courses_list=engine.courses)
        
        except KeyError:
            return '200 OK', 'Список курсов пуст!'

@Router(url='/courses/edit', routes=routes)
class CoursesUpdateView(UpdateView):
    template_name = 'course_create.html'
    page = 'courses'
    context_object_name = 'course'

    def get_object(self, data: dict):
        id = data.get('id')

        if not id:
            raise Exception('Пустой идентификатор курса!')

        return engine.get_course_by_id(id)

    def update_object(self, data: dict):
        course = self.get_object(data)

        name = data.get('name')

        if not name:
            raise Exception('Необходимо указать название курса!')

        course.attach(email_notifier)
        course.attach(sms_notifier)

        # обновление пока не делаю - просто демо observer
        if (name != course.name):
            course.notify()
        

@Router(url='/students/create', routes=routes)
class StudentsCreateView(CreateView):
    template_name = 'student_create.html'
    page = 'students'

    def create_object(self, data: dict):
        name = data.get('name')

        if not name:
            raise Exception('Необходимо указать имя студента!')
        
        student = Student(name=name)
        schema = {'name': name}
        student.mark_new(schema)
        UnitOfWork.get_current().commit()

@Router(url='/students', routes=routes)
class StudentsListView(ListView):
    template_name = 'students.html'
    page = 'students'
    context_object_name = 'students_list'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('student')
        return mapper.all()


@Router(url='/students/add', routes=routes)
class AddStudentByCourseCreateView(CreateView):
    template_name = 'student_add.html'

    def get_context_data(self):
        context = super().get_context_data()
        mapper = MapperRegistry.get_current_mapper('student')
        context['courses'] = engine.courses
        context['students'] = mapper.all()
        return context

    def create_object(self, data: dict):
        course_name = data.get('course_name')
        course = engine.get_course_by_name(course_name)

        student_name = data.get('student_name')
        student = engine.get_student_by_name(student_name)
        course.add_student(student)

@Router(url='/students/delete', routes=routes)
class StudentsDeleteView(DeleteView):
    template_name = 'students.html'
    page = 'students'
    context_object_name = 'students_list'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('student')
        return mapper.all()

    def delete_object(self, data: dict):
        student_id = data.get('id')
        student = Student(id=student_id)
        student.mark_removed()
        UnitOfWork.get_current().commit()

@Router(url='/api/courses', routes=routes)
class CourseApi:
    def __call__(self, request):
        return '200 OK', BaseSerializer(engine.courses).save()