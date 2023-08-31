axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

var list_languages = []
var list_groups = []
var list_courses = []
var list_texts = []
var list_text_types = []
var list_data = []
var list_data_grade = []
var list_enrollment_date = []

async function get_resquest_data_errors(){
    var languages = []
    var groups = []
    var courses = []
    var texts = []
    var text_types = []
    var data = []
    var data_grade = []
    var enrollment_date = []

    await axios({
                method: 'get',
                url: '',
                headers:{
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
                .then(
                    function (response){
                        data = response.data.data_type_errors
                        languages = response.data.list_languages
                        text_types = response.data.list_text_types
                        groups = response.data.list_groups
                        courses = response.data.list_courses
                        texts = response.data.list_texts
                        data_grade = response.data.data_grade_errors
                        enrollment_date = response.data.enrollment_date
                    })

    list_languages = languages
    list_groups = groups
    list_courses = courses
    list_texts = texts
    list_text_types = text_types
    list_data = data
    list_data_grade = data_grade
    list_enrollment_date = enrollment_date
}

async function post_request_data_errors(text_type, text, surname, name, patronymic, course, groups, date){
    var data = []
    var data_grade = []

    await axios({
        method: 'post',
        url:'',
        data: {
            'text_type_id': text_type,
            'text': text,
            'surname': surname,
            'name': name,
            'patronymic': patronymic,
            'course': course,
            'groups': groups,
            'date': date
        },
        headers:{
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
        .then(function (response){
            data = response.data.data_type_errors
            data_grade = response.data.data_grade_errors
        })

    list_data = data
    list_data_grade = data_grade
}

async function actions(){
    await get_resquest_data_errors()

    var data_for_language = list_data.filter(data => data.tag__tag_language==list_languages[0].id_language);
    var data_grade_for_language = list_data_grade.filter(data => data.grade__grade_language==list_languages[0].id_language)

    var title_of_page = new Vue({
        el: '#div_title',
        data: {
            title_page: 'Статистика ошибок в текстах'
        }
    })

    var filters = new Vue({
        el: '#filters',
        data: {
            checked_filters: [],
            text_types: list_text_types.filter(text_type => text_type.language_id==list_languages[0].id_language),
            selected_text_type: '',
            groups: list_groups,
            selected_group: '',
            surname: '',
            name: '',
            patronymic: '',
            courses: list_courses,
            selected_course: '',
            texts: list_texts.filter(text => text.language==list_languages[0].id_language),
            selected_text: '',
            group_dates: list_enrollment_date,
            selected_date: '',
        },
        methods:{
            async update_diagrams(){
                await post_request_data_errors(this.selected_text_type, this.selected_text, this.surname, this.name,
                    this.patronymic, this.selected_course, this.selected_group, this.selected_date)
                data_for_language = list_data.filter(data => data.tag__tag_language == languages.selected_language);
                data_grade_for_language = list_data_grade.filter(data => data.grade__grade_language== languages.selected_language)
                type_errors_bar.get_data()
                type_errors_bar.update_chart()
                type_errors_pie.get_data()
                type_errors_pie.update_chart()
                grade_errors_bar.get_data()
                grade_errors_bar.update_chart()
                grade_errors_pie.get_data()
                grade_errors_pie.update_chart()
            },
            on_change_text_type(){
                if (this.checked_filters.indexOf("text_types") != -1) {
                    this.update_diagrams()
                }
            },
            on_change_choice_text_types(){
                filter_text_type = document.getElementById("filter_text_type")
                if (this.checked_filters.indexOf("text_types") == -1){
                    filter_text_type.style.visibility = "hidden"
                    this.selected_text_type = ''
                    this.update_diagrams()
                }
                else {
                    filter_text_type.style.visibility = "visible"
                }
            },
            on_change_group(){
                if(this.checked_filters.indexOf("groups") != -1){
                    if (this.selected_group=='' || this.selected_date==''){
                        document.getElementById("error_group").style.display = 'block'
                    }
                    else {
                        document.getElementById("error_group").style.display = 'none'
                        this.update_diagrams()
                    }
                }
            },
            on_change_choice_group(){
                filter_date = document.getElementById("filter_date")
                filter_group = document.getElementById("filter_group")
                if(this.checked_filters.indexOf("groups") == -1){
                    filter_date.style.display = "none"
                    filter_group.style.visibility = "hidden"
                    document.getElementById("error_group").style.display = 'none'
                    this.selected_group = ''
                    this.selected_date = ''
                    this.update_diagrams()
                }
                else {
                    filter_date.style.display = "block"
                    filter_group.style.visibility = "visible"
                }
                document.getElementById("filter_student").disabled = !document.getElementById("filter_student").disabled
                document.getElementById("filter_courses").disabled = !document.getElementById("filter_courses").disabled
            },
            on_change_course(){
                if (this.checked_filters.indexOf("courses") != -1){
                    this.update_diagrams()
                }
            },
            on_change_choice_course(){
                filter_course = document.getElementById("filter_course")
                if(this.checked_filters.indexOf("courses") == -1){
                    filter_course.style.visibility = "hidden"
                    this.selected_course = ''
                    this.update_diagrams()
                }
                else {
                    filter_course.style.visibility = "visible"
                }
                document.getElementById("filter_groups").disabled = !document.getElementById("filter_groups").disabled
                document.getElementById("filter_student").disabled = !document.getElementById("filter_student").disabled
            },
            on_change_text(){
                if(this.checked_filters.indexOf("all_texts") != -1){
                    this.update_diagrams()
                }
            },
            on_change_choice_text(){
                filter_text = document.getElementById("filter_text")
                if(this.checked_filters.indexOf("all_texts") == -1){
                    filter_text.style.visibility = "hidden"
                    this.selected_text = ''
                    this.update_diagrams()
                }
                else {
                    filter_text.style.visibility = "visible"
                }
            },
            on_change_student(){
                if(this.checked_filters.indexOf("student") != -1){
                    if (this.surname == '' || this.name == ''){
                        document.getElementById("error_student").style.display = "block"
                    }
                    else {
                        document.getElementById("error_student").style.display = "none"
                        this.update_diagrams()
                    }
                }
            },
            on_change_choice_student(){
                filter_student = document.getElementById("filter_students")
                if(this.checked_filters.indexOf("student") == -1){
                    filter_student.style.display = "none"
                    document.getElementById("error_student").style.display = "none"
                    this.surname = ''
                    this.name = ''
                    this.patronymic = ''
                    this.update_diagrams()
                }
                else {
                    filter_student.style.display = "block"
                }
                document.getElementById("filter_groups").disabled = !document.getElementById("filter_groups").disabled
                document.getElementById("filter_courses").disabled = !document.getElementById("filter_courses").disabled
            },
            on_change_filters_for_student(){
                div_student_filters = document.getElementById("filters_for_student")

                if(div_student_filters.style.display == "block"){
                    div_student_filters.style.display = "none"
                }
                else {
                    div_student_filters.style.display = "block"
                }
            },
            on_change_filters_for_texts(){
                div_texts_filters = document.getElementById("filters_for_texts")

                if(div_texts_filters.style.display == "block"){
                    div_texts_filters.style.display = "none"
                }
                else {
                    div_texts_filters.style.display = "block"
                }
            }
        }
    })

    var languages = new Vue({
        el: '#languages',
        data: {
            languages: list_languages,
            selected_language: list_languages[0].id_language
        },
        methods: {
            on_change_language(){
                filters.texts = list_texts.filter(text => text.language==this.selected_language)
                filters.text_types = list_text_types.filter(text_type => text_type.language_id==this.selected_language);

                data_for_language = list_data.filter(data => data.tag__tag_language == this.selected_language);
                data_grade_for_language = list_data_grade.filter(data => data.grade__grade_language==this.selected_language)
                type_errors_bar.get_data()
                type_errors_bar.update_chart()
                type_errors_pie.get_data()
                type_errors_pie.update_chart()
                grade_errors_bar.get_data()
                grade_errors_bar.update_chart()
                grade_errors_pie.get_data()
                grade_errors_pie.update_chart()
            }
        }
    })

    var type_errors_bar = new Vue({
    el: '#type_errors_bar',
    data:{
        chart: {},
        labels: [],
        stars: [],
        chart_type: 'bar',
        chartColor: 'crimson',
        loading: false
    },
    methods: {
        mounted(){
            this.init_chart()
            this.get_data()
            this.update_chart()
        },
        init_chart() {
            this.chart = Vue.markRaw(new Chart(this.$refs.chart, {
                type: this.chart_type,
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Тип ошибки',
                        backgroundColor: 'crimson',
                        borderColor: 'crimson',
                        data: []
                    }]
                },
                options: {
                    responsive: true,
                    tooltips: {
                        mode: 'index'
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            }));
            },
        update_chart() {
            this.chart.data.labels = this.labels
            this.chart.data.datasets[0].data = this.stars
            this.chart.update()
        },
        get_data() {
            var labels = []
            var points = []

            for (let i=0; i<data_for_language.length; i++) {
                labels.push(data_for_language[i].tag__tag_text)
                points.push(data_for_language[i].count_data)
            }

            this.labels = labels
            this.stars = points
        },
    }
    })

    type_errors_bar.mounted()

    var type_errors_pie = new Vue({
    el: '#type_errors_pie',
    data:{
        chart: {},
        labels: [],
        stars: [],
        chart_type: 'pie',
        chartColor: 'crimson',
        loading: false
    },
    methods: {
        mounted(){
            this.init_chart()
            this.get_data()
            this.update_chart()
        },
        init_chart() {
            this.chart = Vue.markRaw(new Chart(this.$refs.chart, {
                type: this.chart_type,
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Тип ошибки',
                        backgroundColor: [
                            'rgba(163,221,203,1)',
                            'rgba(232,233,161,1)',
                            'rgba(230,181,102,1)',
                            'rgba(229,112,126,1)',
                            'rgba(100,112,255,1)',
                            'rgba(229,255,120,1)',
                            'rgba(254,0,126,1)',
                        ],
                        borderColor: [
                            'rgba(163,221,203,1)',
                            'rgba(232,233,161,1)',
                            'rgba(230,181,102,1)',
                            'rgba(229,112,126,1)',
                            'rgba(100,112,255,1)',
                            'rgba(229,255,120,1)',
                            'rgba(254,0,126,1)',
                        ],
                        data: []
                    }]
                },
                options: {
                    responsive: true,
                    tooltips: {
                        mode: 'index'
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            }));
            },
        update_chart() {
            this.chart.data.labels = this.labels
            this.chart.data.datasets[0].data = this.stars
            this.chart.update()
        },
        get_data() {
            var labels = []
            var points = []

            var count = 0
            for (let i=0; i<data_for_language.length; i++) {
                count += data_for_language[i].count_data
            }

            for (let i=0; i<data_for_language.length; i++) {
                labels.push(data_for_language[i].tag__tag_text)
                points.push(data_for_language[i].count_data * 100 / count)
            }

            this.labels = labels
            this.stars = points
        },
    }
    })

    type_errors_pie.mounted()

    var grade_errors_bar = new Vue({
    el: '#grade_errors_bar',
    data:{
        chart: {},
        labels: [],
        stars: [],
        chart_type: 'bar',
        chartColor: 'crimson',
        loading: false
    },
    methods: {
        mounted(){
            this.init_chart()
            this.get_data()
            this.update_chart()
        },
        init_chart() {
            this.chart = Vue.markRaw(new Chart(this.$refs.chart, {
                type: this.chart_type,
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Грубость ошибки',
                        backgroundColor: 'crimson',
                        borderColor: 'crimson',
                        data: []
                    }]
                },
                options: {
                    responsive: true,
                    tooltips: {
                        mode: 'index'
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            }));
            },
        update_chart() {
            this.chart.data.labels = this.labels
            this.chart.data.datasets[0].data = this.stars
            this.chart.update()
        },
        get_data() {
            var labels = []
            var points = []

            for (let i=0; i<data_grade_for_language.length; i++) {
                labels.push(data_grade_for_language[i].grade__grade_name)
                points.push(data_grade_for_language[i].count_data)
            }

            this.labels = labels
            this.stars = points
        },
    }
    })

    grade_errors_bar.mounted()

    var grade_errors_pie = new Vue({
    el: '#grade_errors_pie',
    data:{
        chart: {},
        labels: [],
        stars: [],
        chart_type: 'pie',
        chartColor: 'crimson',
        loading: false
    },
    methods: {
        mounted(){
            this.init_chart()
            this.get_data()
            this.update_chart()
        },
        init_chart() {
            this.chart = Vue.markRaw(new Chart(this.$refs.chart, {
                type: this.chart_type,
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Грубость ошибки',
                        backgroundColor: [
                            'rgba(100,112,255,1)',
                            'rgba(229,255,120,1)',
                            'rgba(254,0,126,1)',
                        ],
                        borderColor: [
                            'rgba(100,112,255,1)',
                            'rgba(229,255,120,1)',
                            'rgba(254,0,126,1)',
                        ],
                        data: []
                    }]
                },
                options: {
                    responsive: true,
                    tooltips: {
                        mode: 'index'
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            }));
            },
        update_chart() {
            this.chart.data.labels = this.labels
            this.chart.data.datasets[0].data = this.stars
            this.chart.update()
        },
        get_data() {
            var labels = []
            var points = []

            var count = 0
            for (let i=0; i<data_grade_for_language.length; i++) {
                count += data_grade_for_language[i].count_data
            }

            for (let i=0; i<data_grade_for_language.length; i++) {
                labels.push(data_grade_for_language[i].grade__grade_name)
                points.push(data_grade_for_language[i].count_data * 100 / count)
            }

            this.labels = labels
            this.stars = points
        },
    }
    })

    grade_errors_pie.mounted()
}

actions()
