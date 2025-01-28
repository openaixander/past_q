const courses = {{ courses_json|safe }}.map(course => ({
    id: course.pk,
    name: course.fields.name,
    code: course.fields.code
}));

document.getElementById('course').addEventListener('change', function() {
    const courseCodeInput = document.getElementById('course_code');
    const selectedCourse = courses.find(course => course.id === parseInt(this.value));
    courseCodeInput.value = selectedCourse ? selectedCourse.code : '';
});
