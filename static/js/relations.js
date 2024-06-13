var list_data_course = []
var list_data_fisher_course = []
var data_for_language_course = []
var data_fisher_for_language_course = []
var relations_course = []

var list_data_group = []
var list_data_fisher_group = []
var data_for_language_group = []
var data_fisher_for_language_group = []
var relations_group = []

var data_for_language = list_data.filter(data => data.language == list_languages[0].id_language)
var data_fisher_for_language = list_data_fisher.filter(data => data.language == list_languages[0].id_language)
choose_method_corpus()


async function post_request_enrollment_date(group) {
    var enrollment_date = []

    await axios({
        method: 'post',
        url: '',
        data: {
            'group': group,
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

async function post_request_course(course) {
    var data = []
    var data_fisher = []
    var relations = []

    await axios({
        method: 'post',
        url: '',
        data: {
            'course': course,
            'flag_post': 'course'
        },
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
        .then(function (response) {
            data = response.data.data_relation
            data_fisher = response.data.data_fisher
            relations = response.data.relation
        })

    list_data_course = data
    list_data_fisher_course = data_fisher
    relations_course = relations
}

async function post_request_group(group, date) {
    var data = []
    var data_fisher = []
    var relations = []

    await axios({
        method: 'post',
        url: '',
        data: {
            'group': group,
            'date': date,
            'flag_post': 'group'
        },
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
        .then(function (response) {
            data = response.data.data_relation
            data_fisher = response.data.data_fisher
            relations = response.data.relation
        })

    list_data_group = data
    list_data_fisher_group = data_fisher
    relations_group = relations
}


function choose_method_corpus() {
    if (relations[list_languages[0].id_language].method=='Fisher'){
        document.getElementById("card_stat_fisher_corpus").style.display = 'block'
        document.getElementById("corpus_fisher").style.display = 'block'
        document.getElementById("card_stat_pirson_corpus").style.display = 'none'
    }
    else {
        document.getElementById("card_stat_pirson_corpus").style.display = 'block'
        document.getElementById("corpus_fisher").style.display = 'none'
        document.getElementById("card_stat_fisher_corpus").style.display = 'none'
    }
}

function choose_method_course() {
    if (relations[list_languages[0].id_language].method=='Fisher'){
        document.getElementById("card_stat_fisher_course").style.display = 'block'
        document.getElementById("course_fisher").style.display = 'block'
        document.getElementById("card_stat_pirson_course").style.display = 'none'
    }
    else {
        document.getElementById("card_stat_pirson_course").style.display = 'block'
        document.getElementById("course_fisher").style.display = 'none'
        document.getElementById("card_stat_fisher_course").style.display = 'none'
    }
}

function choose_method_group() {
    if (relations[list_languages[0].id_language].method=='Fisher'){
        document.getElementById("card_stat_fisher_group").style.display = 'block'
        document.getElementById("group_fisher").style.display = 'block'
        document.getElementById("card_stat_pirson_group").style.display = 'none'
    }
    else {
        document.getElementById("card_stat_pirson_group").style.display = 'block'
        document.getElementById("group_fisher").style.display = 'none'
        document.getElementById("card_stat_fisher_group").style.display = 'none'
    }
}

function update_data() {
    relation_corpus.get_data()
    relation_corpus.update_chart()

    corpus_fisher.get_data()
    corpus_fisher.update_chart()
}

function update_data_for_language() {
    selected_language = document.getElementById("selected_language").value

    data_for_language = list_data.filter(data => data.language == selected_language)
    data_fisher_for_language = list_data_fisher.filter(data => data.language == selected_language)
    data_for_language_course = list_data_course.filter(data => data.language == selected_language)
    data_fisher_for_language_course = list_data_fisher_course.filter(data => data.language == selected_language)
    data_for_language_group = list_data_group.filter(data => data.language == selected_language)
    data_fisher_for_language_group = list_data_fisher_group.filter(data => data.language == selected_language)

    groups.groups = list_groups.filter(group => group.language == selected_language)
    courses.courses = list_courses.filter(course => course.language == selected_language)

    update_data()
}

function get_results_course() {
    results_course.result = relations_course[selected_language].result
    results_course.stat = relations_course[selected_language].stat
    results_course.pvalue = relations_course[selected_language].pvalue
    results_course.n = relations_course[selected_language].N
    choose_method_course()
    document.getElementById("btn-download-course").disabled = false
}

function cancel_course() {
    results_course.result = ''
    results_course.stat = ''
    results_course.pvalue = ''
    results_course.n = ''
    document.getElementById("card_stat_pirson_course").style.display = 'block'
    document.getElementById("card_stat_fisher_course").style.display = 'none'
    document.getElementById("course_fisher").style.display = 'none'
    document.getElementById("btn-download-course").disabled = true
}

function get_results_group() {
    results_group.result = relations_group[selected_language].result
    results_group.stat = relations_group[selected_language].stat
    results_group.pvalue = relations_group[selected_language].pvalue
    results_group.n = relations_group[selected_language].N
    choose_method_group()
    document.getElementById("btn-download-group").disabled = false
}

function cancel_group() {
    results_group.result = ''
    results_group.stat = ''
    results_group.pvalue = ''
    results_group.n = ''
    document.getElementById("card_stat_pirson_group").style.display = 'block'
    document.getElementById("card_stat_fisher_group").style.display = 'none'
    document.getElementById("group_fisher").style.display = 'none'
    document.getElementById("btn-download-group").disabled = true
}

function on_change_language() {
    selected_language = document.getElementById("selected_language").value

    results_corpus.result = relations[selected_language].result
    results_corpus.stat = relations[selected_language].stat
    results_corpus.pvalue = relations[selected_language].pvalue
    results_corpus.n = relations[selected_language].N
    choose_method_corpus()

    update_data_for_language()

    if (courses.selected_course != '--') {
        relation_course.get_data()
        relation_course.update_chart()

        course_fisher.get_data()
        course_fisher.update_chart()

        if (data_for_language_course.length != 0) {
            get_results_course()
        }
        else {
            cancel_course()
        }
    }

    if (groups.selected_group != '--' || groups.selected_date != '') {
        relation_group.get_data()
        relation_group.update_chart()

        group_fisher.get_data()
        group_fisher.update_chart()

        if (data_for_language_group.length != 0) {
            get_results_group()
        }
        else {
            cancel_group()
        }
    }
}


var results_corpus = new Vue({
    el: '#results_corpus',
    data: {
        result: relations[list_languages[0].id_language].result,
        stat: relations[list_languages[0].id_language].stat,
        pvalue: relations[list_languages[0].id_language].pvalue,
        n: relations[list_languages[0].id_language].N
    }
})

var courses = new Vue({
    el: '#courses',
    data: {
        courses: list_courses.filter(course => course.language == list_languages[0].id_language),
        selected_course: '--'
    },
    methods: {
        async on_change_course() {
            if (this.selected_course != '--') {
                await post_request_course(this.selected_course)

                selected_language = document.getElementById("selected_language").value
                data_for_language_course = list_data_course.filter(data => data.language == selected_language)
                data_fisher_for_language_course = list_data_fisher_course.filter(data => data.language ==
                                                                                                    selected_language)

                if (data_for_language_course.length != 0) {
                    get_results_course()
                }
                else {
                    cancel_course()
                    results_course.n = 0
                }

                results_course.course = this.selected_course
                document.getElementById("card_course").style.display = 'block'
            }
            else {
                list_data_course = []
                data_for_language_course = []
                list_data_fisher_course = []
                data_fisher_for_language_course = []

                cancel_course()
                results_course.course = ''
                document.getElementById("card_course").style.display = 'none'
            }

            relation_course.get_data()
            relation_course.update_chart()

            course_fisher.get_data()
            course_fisher.update_chart()
        }
    }
})

var results_course = new Vue({
    el: '#results_course',
    data: {
        result: '',
        stat: '',
        pvalue: '',
        n: '',
        course: ''
    }
})

var groups = new Vue({
    el: '#groups',
    data: {
        groups: list_groups.filter(group => group.language == list_languages[0].id_language),
        selected_group: '--',
        group_dates: [],
        selected_date: ''
    },
    methods: {
        async on_change_group_number() {
            if (this.selected_group == '--') {
                this.selected_date=''
                this.group_dates = []

                list_data_group = []
                data_for_language_group = []
                list_data_fisher_group = []
                data_fisher_for_language_group = []

                cancel_group()

                document.getElementById("error_group").style.display = 'none'
                document.getElementById("filter_group").classList.remove('border-danger')
                document.getElementById("filter_group").classList.remove('border')
                document.getElementById("error_group_date").style.display = 'none'
                document.getElementById("filter_group_date").classList.remove('border-danger')
                document.getElementById("filter_group_date").classList.remove('border')

                results_group.group = ''
                results_group.date = ''
                document.getElementById("card_group").style.display = 'none'

                relation_group.get_data()
                relation_group.update_chart()

                group_fisher.get_data()
                group_fisher.update_chart()
            }
            else {
                await post_request_enrollment_date(this.selected_group)
                this.group_dates = list_enrollment_date
            }
        },
        async on_change_group(){
            if (this.selected_group == '--') {
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

            if (this.selected_group != '--' && this.selected_date != '') {
                await post_request_group(this.selected_group, this.selected_date)

                selected_language = document.getElementById("selected_language").value
                data_for_language_group = list_data_group.filter(data => data.language == selected_language)
                data_fisher_for_language_group = list_data_fisher_group.filter(data => data.language ==
                                                                                                    selected_language)

                if (data_for_language_group.length != 0) {
                    get_results_group()
                }
                else {
                    cancel_group()
                    results_group.n = 0
                }

                results_group.group = this.selected_group
                results_group.date = this.selected_date
                document.getElementById("card_group").style.display = 'block'

                relation_group.get_data()
                relation_group.update_chart()

                group_fisher.get_data()
                group_fisher.update_chart()
            }
        }
    }
})

var results_group = new Vue({
    el: '#results_group',
    data: {
        result: '',
        stat: '',
        pvalue: '',
        n: '',
        group: '',
        date: ''
    }
})
