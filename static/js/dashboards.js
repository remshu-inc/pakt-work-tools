var colors = [
    'rgba(255, 0, 0, 1)',
    'rgba(0, 255, 0, 1)',
    'rgba(0, 0, 255, 1)',
    'rgba(199, 21, 133, 1)',
    'rgba(255, 69, 0, 1)',
    'rgba(75, 0, 130, 1)',
    'rgba(255, 255, 0, 1)',
    'rgba(148, 0, 211, 1)',
    'rgba(139, 69, 19, 1)',
    'rgba(0, 128, 0, 1)',
    'rgba(188, 143, 143, 1)',
    'rgba(255, 0, 255, 1)',
    'rgba(128, 128, 0, 1)',

    'rgba(255, 0, 0, 0.9)',
    'rgba(0, 255, 0, 0.9)',
    'rgba(0, 0, 255, 0.9)',
    'rgba(199, 21, 133, 0.9)',
    'rgba(255, 69, 0, 0.9)',
    'rgba(75, 0, 130, 0.9)',
    'rgba(255, 255, 0, 0.9)',
    'rgba(148, 0, 211, 0.9)',
    'rgba(139, 69, 19, 0.9)',
    'rgba(0, 128, 0, 0.9)',
    'rgba(188, 143, 143, 0.9)',
    'rgba(255, 0, 255, 0.9)',
    'rgba(128, 128, 0, 0.9)',

    'rgba(255, 0, 0, 0.8)',
    'rgba(0, 255, 0, 0.8)',
    'rgba(0, 0, 255, 0.8)',
    'rgba(199, 21, 133, 0.8)',
    'rgba(255, 69, 0, 0.8)',
    'rgba(75, 0, 130, 0.8)',
    'rgba(255, 255, 0, 0.8)',
    'rgba(148, 0, 211, 0.8)',
    'rgba(139, 69, 19, 0.8)',
    'rgba(0, 128, 0, 0.8)',
    'rgba(188, 143, 143, 0.8)',
    'rgba(255, 0, 255, 0.8)',
    'rgba(128, 128, 0, 0.8)',

    'rgba(255, 0, 0, 0.7)',
    'rgba(0, 255, 0, 0.7)',
    'rgba(0, 0, 255, 0.7)',
    'rgba(199, 21, 133, 0.7)',
    'rgba(255, 69, 0, 0.7)',
    'rgba(75, 0, 130, 0.7)',
    'rgba(255, 255, 0, 0.7)',
    'rgba(148, 0, 211, 0.7)',
    'rgba(139, 69, 19, 0.7)',
    'rgba(0, 128, 0, 0.7)',
    'rgba(188, 143, 143, 0.7)',
    'rgba(255, 0, 255, 0.7)',
    'rgba(128, 128, 0, 0.7)',

    'rgba(255, 0, 0, 0.6)',
    'rgba(0, 255, 0, 0.6)',
    'rgba(0, 0, 255, 0.6)',
    'rgba(199, 21, 133, 0.6)',
    'rgba(255, 69, 0, 0.6)',
    'rgba(75, 0, 130, 0.6)',
    'rgba(255, 255, 0, 0.6)',
    'rgba(148, 0, 211, 0.6)',
    'rgba(139, 69, 19, 0.6)',
    'rgba(0, 128, 0, 0.6)',
    'rgba(188, 143, 143, 0.6)',
    'rgba(255, 0, 255, 0.6)',
    'rgba(128, 128, 0, 0.6)',

    'rgba(255, 0, 0, 0.5)',
    'rgba(0, 255, 0, 0.5)',
    'rgba(0, 0, 255, 0.5)',
    'rgba(199, 21, 133, 0.5)',
    'rgba(255, 69, 0, 0.5)',
    'rgba(75, 0, 130, 0.5)',
    'rgba(255, 255, 0, 0.5)',
    'rgba(148, 0, 211, 0.5)',
    'rgba(139, 69, 19, 0.5)',
    'rgba(0, 128, 0, 0.5)',
    'rgba(188, 143, 143, 0.5)',
    'rgba(255, 0, 255, 0.5)',
    'rgba(128, 128, 0, 0.5)',

    'rgba(255, 0, 0, 0.4)',
    'rgba(0, 255, 0, 0.4)',
    'rgba(0, 0, 255, 0.4)',
    'rgba(199, 21, 133, 0.4)',
    'rgba(255, 69, 0, 0.4)',
    'rgba(75, 0, 130, 0.4)',
    'rgba(255, 255, 0, 0.4)',
    'rgba(148, 0, 211, 0.4)',
    'rgba(139, 69, 19, 0.4)',
    'rgba(0, 128, 0, 0.4)',
    'rgba(188, 143, 143, 0.4)',
    'rgba(255, 0, 255, 0.4)',
    'rgba(128, 128, 0, 0.4)',
]


async function post_request_enrollment_date(group, text, text_type) {
    var enrollment_date = []

    await axios({
        method: 'post',
        url: '',
        data: {
            'group': group,
            'text': text,
            'text_type': text_type,
            'flag_post': 'enrollment_date'
        },
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
	    }
	})
        .then(function (response) {
            enrollment_date = response.data.enrollment_date
        })

	list_enrollment_date = enrollment_date
}

async function post_request_all(text, text_type) {
    var texts = []
    var text_types = []

    await axios({
        method: 'post',
        url: '',
        data: {
            'text': text,
            'text_type': text_type,
            'flag_post': 'choice_all'
        },
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
	    }
	})
        .then(function (response) {
            texts = response.data.texts
            text_types = response.data.text_types
        })

	list_texts = texts
	list_text_types = text_types
}

async function post_request_group(group, enrollment_date, text, text_type) {
    var texts = []
    var text_types = []

    await axios({
        method: 'post',
        url: '',
        data: {
            'group': group,
            'enrollment_date': enrollment_date,
            'text': text,
            'text_type': text_type,
            'flag_post': 'choice_group'
        },
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
	    }
	})
	    .then(function (response) {
	        texts = response.data.texts
	        text_types = response.data.text_types
	    })

	list_texts = texts
	list_text_types = text_types
}

async function post_request_student(surname, name, patronymic, text, text_type) {
    var texts = []
    var text_types = []

    await axios({
        method: 'post',
        url: '',
        data: {
            'surname': surname,
            'name': name,
            'patronymic': patronymic,
            'text': text,
            'text_type': text_type,
            'flag_post': 'choice_student'
        },
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
	    }
	})
	    .then(function (response) {
	        texts = response.data.texts
	        text_types = response.data.text_types
	    })

	list_texts = texts
	list_text_types = text_types
}

async function post_request_course(course, text, text_type) {
    var texts = []
    var text_types = []

     await axios({
        method: 'post',
        url: '',
        data: {
            'course': course,
            'text': text,
            'text_type': text_type,
            'flag_post': 'choice_course'
        },
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
	 })
	    .then(function (response) {
	        texts = response.data.texts
	        text_types = response.data.text_types
	    })

    list_texts = texts
    list_text_types = text_types
}

async function post_request_text(group, enrollment_date, surname, name, patronymic, course, text, text_type) {
    var groups = []
    var courses = []
    var text_types = []

    await axios({
        method: 'post',
        url: '',
        data: {
            'group': group,
            'enrollment_date': enrollment_date,
            'surname': surname,
            'name': name,
            'patronymic': patronymic,
            'course': course,
            'text': text,
            'text_type': text_type,
            'flag_post': 'choice_text'
        },
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
	})
	    .then(function (response) {
	        groups = response.data.groups
	        courses = response.data.courses
	        text_types = response.data.text_types
	    })

	list_groups = groups
	list_courses = courses
	list_text_types = text_types
}

async function post_request_text_type(group, enrollment_date, surname, name, patronymic, course, text, text_type) {
    var groups = []
    var courses = []
    var texts = []

    await axios({
        method: 'post',
        url: '',
        data: {
            'group': group,
            'enrollment_date': enrollment_date,
            'surname': surname,
            'name': name,
            'patronymic': patronymic,
            'course': course,
            'text': text,
            'text_type': text_type,
            'flag_post': 'choice_text_type'
	    },
	    headers: {
	        'X-Requested-With': 'XMLHttpRequest',
	    }
	})
	    .then(function (response) {
	        groups = response.data.groups
	        courses = response.data.courses
	        texts = response.data.texts
	    })

	list_groups = groups
	list_courses = courses
	list_texts = texts
}


function on_change_font_size() {
    selected_font_size = document.getElementById("font_size").value
    Chart.defaults.font.size = selected_font_size
    update_data()
}


var filters = new Vue({
    el: '#form_filters',
    data: {
        groups: list_groups.filter(group => group.language == list_languages[0].id_language),
        selected_group: '',
        group_dates:  list_enrollment_date,
        selected_date: '',
        surname: '',
        name: '',
        patronymic: '',
        courses: list_courses.filter(course => course.language == list_languages[0].id_language),
        selected_course: '',
        texts: list_texts.filter(text => text.language == list_languages[0].id_language),
        selected_text: '',
        text_types: list_text_types.filter(text_type => text_type.language_id == list_languages[0].id_language),
        selected_text_type: ''
    },
    methods: {
        on_change_choice_student_filters() {
            if (document.getElementById('groups').checked) {
                document.getElementById("enrollment_date").style.visibility = "visible"
            }
            else {
                document.getElementById("enrollment_date").style.visibility = "hidden"
                document.getElementById("error_group").style.display = 'none'
                document.getElementById("error_group_date").style.display = 'none'
                document.getElementById("filter_group").classList.remove('border-danger')
                document.getElementById("filter_group").classList.remove('border')
                document.getElementById("filter_group_date").classList.remove('border-danger')
                document.getElementById("filter_group_date").classList.remove('border')
            }

            if (!document.getElementById('student').checked) {
                document.getElementById("error_student_surname").style.display = "none"
                document.getElementById("error_student_name").style.display = "none"
                document.getElementById("surname").classList.remove('border-danger')
                document.getElementById("surname").classList.remove('border')
                document.getElementById("name").classList.remove('border-danger')
                document.getElementById("name").classList.remove('border')
            }

            this.selected_group = ''
            this.selected_date = ''
            this.surname = ''
            this.name = ''
            this.patronymic = ''
            this.selected_course = ''
            this.group_dates = []
        },
        async update_diagrams() {
            await post_request_data()
            update_data_for_language()
        },
        update_text_filters_for_language() {
            selected_language = document.getElementById("selected_language").value
            this.texts = list_texts.filter(text => text.language == selected_language)
            this.text_types = list_text_types.filter(text_type => text_type.language_id == selected_language)
        },
        update_text_and_student_filters_for_language(flag_text) {
            selected_language = document.getElementById("selected_language").value
            this.groups = list_groups.filter(group => group.language == selected_language)
            this.courses = list_courses.filter(course => course.language == selected_language)

            if (flag_text) {
                this.text_types = list_text_types.filter(text_type => text_type.language_id == selected_language)
            }
            else {
                this.texts = list_texts.filter(text => text.language == selected_language)
            }
        },
        async on_change_choice_all() {
            if (legend_filters.emotion == '' && legend_filters.self_rating == '') {
                await post_request_all(this.selected_text, this.selected_text_type)
                this.update_text_filters_for_language()
            }

            this.update_diagrams()

            legend_filters.group = ''
            legend_filters.enrollment_date = ''
            legend_filters.surname = ''
            legend_filters.name = ''
            legend_filters.patronymic = ''
            legend_filters.course = ''

            document.getElementById("card_group").style.display = 'none'
            document.getElementById("card_student").style.display = 'none'
            document.getElementById("card_course").style.display = 'none'
        },
        async on_change_group_number() {
            await post_request_enrollment_date(this.selected_group, this.selected_text, this.selected_text_type)
            this.group_dates = list_enrollment_date
        },
        async on_change_group(){
            if (this.selected_group == '') {
                document.getElementById("error_group").style.display = 'block'
                document.getElementById("filter_group").classList.add('border')
                document.getElementById("filter_group").classList.add('border-danger')
            }
            else {
                document.getElementById("error_group").style.display = 'none'
                document.getElementById("filter_group").classList.remove('border-danger')
                document.getElementById("filter_group").classList.remove('border')
            }

            if (this.selected_date == '') {
                document.getElementById("error_group_date").style.display = 'block'
                document.getElementById("filter_group_date").classList.add('border')
                document.getElementById("filter_group_date").classList.add('border-danger')
            }
            else {
                document.getElementById("error_group_date").style.display = 'none'
                document.getElementById("filter_group_date").classList.remove('border-danger')
                document.getElementById("filter_group_date").classList.remove('border')
            }

            if (this.selected_group != '' && this.selected_date != '') {
                if (legend_filters.emotion == '' && legend_filters.self_rating == '') {
                    await post_request_group(this.selected_group, this.selected_date, this.selected_text,
                                                this.selected_text_type)
                    this.update_text_filters_for_language()
                }

                this.update_diagrams()

                legend_filters.group = this.selected_group
                legend_filters.enrollment_date = this.selected_date
                legend_filters.surname = ''
                legend_filters.name = ''
                legend_filters.patronymic = ''
                legend_filters.course = ''

                document.getElementById("card_group").style.display = 'block'
                document.getElementById("card_student").style.display = 'none'
                document.getElementById("card_course").style.display = 'none'
            }
        },
        async on_change_student() {
            if (this.surname == '') {
                document.getElementById("error_student_surname").style.display = "block"
                document.getElementById("surname").classList.add('border')
                document.getElementById("surname").classList.add('border-danger')
            }
            else {
                document.getElementById("error_student_surname").style.display = "none"
                document.getElementById("surname").classList.remove('border-danger')
                document.getElementById("surname").classList.remove('border')
            }

            if (this.name == '') {
                document.getElementById("error_student_name").style.display = "block"
                document.getElementById("name").classList.add('border')
                document.getElementById("name").classList.add('border-danger')
            }
            else {
                document.getElementById("error_student_name").style.display = "none"
                document.getElementById("name").classList.remove('border-danger')
                document.getElementById("name").classList.remove('border')
            }

            if (this.surname != '' && this.name != ''){
                if (legend_filters.emotion == '' && legend_filters.self_rating == '') {
                    await post_request_student(this.surname, this.name, this.patronymic, this.selected_text,
                                                this.selected_text_type)
                    this.update_text_filters_for_language()
                }

                this.update_diagrams()

                legend_filters.group = ''
                legend_filters.enrollment_date = ''
                legend_filters.surname = this.surname
                legend_filters.name = this.name
                legend_filters.patronymic = this.patronymic
                legend_filters.course = ''

                document.getElementById("card_group").style.display = 'none'
                document.getElementById("card_student").style.display = 'block'
                document.getElementById("card_course").style.display = 'none'
            }
        },
        async on_change_course() {
            if (legend_filters.emotion == '' && legend_filters.self_rating == '') {
                await post_request_course(this.selected_course, this.selected_text, this.selected_text_type)
                this.update_text_filters_for_language()
            }

            this.update_diagrams()

            legend_filters.group = ''
            legend_filters.enrollment_date = ''
            legend_filters.surname = ''
            legend_filters.name = ''
            legend_filters.patronymic = ''
            legend_filters.course = this.selected_course

            document.getElementById("card_group").style.display = 'none'
            document.getElementById("card_student").style.display = 'none'
            document.getElementById("card_course").style.display = 'block'
        },
        async on_change_choice_text() {
            if (!document.getElementById('filter_all_texts').checked) {
                this.selected_group = ''
                this.selected_date = ''
                this.group_dates = []
                this.selected_text = ''

                if (legend_filters.emotion == '' && legend_filters.self_rating == '') {
                    await post_request_text(this.selected_group, this.selected_date, this.surname, this.name,
                                            this.patronymic, this.selected_course, this.selected_text,
                                            this.selected_text_type)
                    this.update_text_and_student_filters_for_language(true)
                }

                this.update_diagrams()

                legend_filters.text = ''
                document.getElementById("card_text").style.display = 'none'
            }
        },
        async on_change_text() {
            this.selected_group = ''
            this.selected_date = ''
            this.group_dates = []

            if (legend_filters.emotion == '' && legend_filters.self_rating == '') {
                await post_request_text(this.selected_group, this.selected_date, this.surname, this.name,
                                        this.patronymic, this.selected_course, this.selected_text,
                                        this.selected_text_type)
                this.update_text_and_student_filters_for_language(true)
            }

            this.update_diagrams()

            legend_filters.text = this.selected_text
            document.getElementById("card_text").style.display = 'block'
        },
        async on_change_choice_text_types() {
            if (!document.getElementById('filter_text_types').checked) {
                this.selected_group = ''
                this.selected_date = ''
                this.group_dates = []
                this.selected_text_type = ''

                if (legend_filters.emotion == '' && legend_filters.self_rating == '') {
                    await post_request_text_type(this.selected_group, this.selected_date, this.surname, this.name,
                                                 this.patronymic, this.selected_course, this.selected_text,
                                                 this.selected_text_type)
                    this.update_text_and_student_filters_for_language(false)
                }

                this.update_diagrams()

                legend_filters.text_type = ''
                document.getElementById("card_text_type").style.display = 'none'
            }
        },
        async on_change_text_type() {
            this.selected_group = ''
            this.selected_date = ''
            this.group_dates = []

            if (legend_filters.emotion == '' && legend_filters.self_rating == '') {
                await post_request_text_type(this.selected_group, this.selected_date, this.surname, this.name,
                                             this.patronymic, this.selected_course, this.selected_text,
                                             this.selected_text_type)
                this.update_text_and_student_filters_for_language(false)
            }

            this.update_diagrams()

            selected_text_type = list_text_types.filter(text_type => text_type.id_text_type == this.selected_text_type)
            legend_filters.text_type = selected_text_type[0].text_type_name
            document.getElementById("card_text_type").style.display = 'block'
        }
    }
})

var legend_filters = new Vue({
    el: '#legend_checked_filters',
    data: {
        group: '',
        enrollment_date: '',
        surname: '',
        name: '',
        patronymic: '',
        course: '',
        text: '',
        text_type: '',
        emotion: '',
        self_rating:''
    }
})
