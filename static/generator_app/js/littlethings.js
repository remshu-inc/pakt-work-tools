// the *very little* things
// made with ~~love~~ blood, sweat and tears
// by (almost) exclusively
// Mariella~

// button redirect
function redirectto(url) {
    window.location.href = url;
}

// back button redirect
function redirectback(url) {
    window.history.back();
    // window.location.replace(url);
}

// funnel texts based on selected student
// big assembly
async function loadTextsFromStudent(url, stud_id) {
    var result = await fetch(
        url, {
            headers: {
                "stud-id": stud_id
            }
        }
    );
    var responseData = await result.json();
    var pool = document.getElementById("change-on-reload");
    while (pool.children.length > 0) {
        pool.removeChild(pool.children[0]);
    }
    for (var idx = 0; idx < responseData.length; idx++) {
        var id = "textCheck" + responseData[idx].id_text;

        var outerDiv = document.createElement("div");
        outerDiv.classList.add("form-check");
        outerDiv.classList.add("moveable-input");

        var input = document.createElement("input");
        input.setAttribute("type", "checkbox");
        input.setAttribute("name", id);
        input.setAttribute("value", responseData[idx].id_text);
        input.setAttribute("onclick", "moveText(this)");
        input.classList.add("form-check-input");
        input.classList.add("textCheck");

        var label = document.createElement("label");
        label.setAttribute("for", id);
        label.classList.add("form-check-label");
        label.innerText = responseData[idx].header;

        outerDiv.appendChild(input);
        outerDiv.appendChild(label);
        pool.appendChild(outerDiv);
    }
    var masterSelect = document.getElementById("textCheckAll");
    if (responseData.length > 0) {
        masterSelect.checked = false;
    }
}

// load text names into the student generator
// lil assemble
async function loadTexts(url, stud_id) {
    var result = await fetch(
        url, {
            headers: {
                "stud-id": stud_id
            }
        }
    );
    var responseData = await result.json();
    // console.log(responseData);
    var attachableDiv = document.getElementById("textSelectionBox");
    for (var idx = 0; idx < responseData.length; idx++) {
        var id = "textCheck" + responseData[idx].id_text;

        var outerDiv = document.createElement("div");
        outerDiv.classList.add("form-check");

        var input = document.createElement("input");
        input.setAttribute("type", "checkbox");
        input.setAttribute("id", id);
        input.setAttribute("value", responseData[idx].id_text);
        input.setAttribute("onclick", "clickOnTextStudent(this)");
        input.classList.add("form-check-input");

        var label = document.createElement("label");
        label.setAttribute("for", id);
        label.classList.add("form-check-label");
        label.innerText = responseData[idx].header;

        outerDiv.appendChild(input);
        outerDiv.appendChild(label);
        attachableDiv.appendChild(outerDiv);
    }
}

// Student sort

function sortStudents() {
    var container = document.getElementById()
}

// End student sort

// Mistake selector section

function clickOnMistake() {
    var container = document.getElementById("mistakeCheckerContainer");
    var cboxes = container.querySelectorAll("input.mistakeChecker");
    var master = document.getElementById("mistakeCheckAll");
    var flag = false;
    for (var cbox of cboxes) {
        if (cbox.checked == false) {
            flag = true;
            break;
        }
    }
    if (flag) {
        master.checked = false;
    }
    else {
        master.checked = true;
    }
}

function checkAllCheckers() {
    var container = document.getElementById("mistakeCheckerContainer");
    var cboxes = container.querySelectorAll("input.mistakeChecker");
    // console.log(cboxes);
    var flag = false;
    for (var cbox of cboxes) {
        if (cbox.checked == false) {
            flag = true;
            break;
        }
    }
    if (flag) {
        // check all
        for (var cbox of cboxes) {
            cbox.checked = true;
        }
    }
    else {
        // uncheck all
        for (var cbox of cboxes) {
            cbox.checked = false;
        }
    }
}

// End mistake selector

// Student sort section

// Custom comparator for sorting
function studComparator(prv, nxt) {
    // return prv.localeCompare(nxt);
    
    if (prv.dataset.name < nxt.dataset.name) {
        return -1;
    }
    if (prv.dataset.name > nxt.dataset.name) {
        return 1;
    }
    return 0;
    
}

// Nuke sort - reset btn and flag
function resetSortFlag() {
    var sortFlag = document.getElementById("btn-sort");
    if (sortFlag) {
        sortFlag.dataset.flag = "none";
        sortFlag.firstElementChild.setAttribute("fill", "rgba(0, 0, 0, 0.847");
        sortFlag.firstElementChild.setAttribute("display", "inline");
        sortFlag.children[1].setAttribute("display", "none");
    }
}

// Sort all unselected students in lexicographical order for "lastname firstname"
function sortStudentsAscending(rev=false) {
    var draw = document.getElementById("change-on-reload");
    var studlist = draw.querySelectorAll("div.moveable-input");
    var studarray = Array.from(studlist);
    var sortedarray = studarray.sort(studComparator);
    if (rev) {
        sortedarray.reverse();
    }
    sortedarray.forEach(e => draw.appendChild(e));
}

// behavior of the sort button
// any sort should reset search results and hide the bar div
function sortStudents(inpt) {
    var toggleAsc = inpt.querySelector("#sort-icon-ascending");
    var toggleDesc = inpt.querySelector("#sort-icon-descending");
    
    clearSearchResult();

    if (inpt.dataset.flag == "false") {         // reverse sorted
        sortStudentsAscending();
        inpt.dataset.flag = "true";
        // change svg icon
        toggleAsc.setAttribute("display", "inline");
        toggleDesc.setAttribute("display", "none");
    }
    else if (inpt.dataset.flag == "true") {     // sorted lexicographically
        sortStudentsAscending(true);
        inpt.dataset.flag = "false";
        // change svg icon
        toggleAsc.setAttribute("display", "none");
        toggleDesc.setAttribute("display", "inline");
    }
    else {                                      // unsorted, start of execution (or found stuff)
        sortStudentsAscending();
        toggleAsc.setAttribute("fill", "#0d6efd");
        inpt.dataset.flag = "true";
    }
}

// End student sort

// Student search section

function highlightSrch(inpt) {
    inpt.value = "";
}

function bindEnterOnLoad() {
    var inpt = document.getElementById("name-srch");
    inpt.addEventListener('keydown', (e) => {
        if (e.key === "Enter") {
            searchStudentsByLastName(inpt.parentElement.children[1].firstElementChild);
        }
    });
}

function resetSearchBar() {
    var inpt = document.getElementById("name-srch");
    inpt.value = "";
}

function clearSearchResult() {
    var srch = document.getElementById("search-res");
    var searchedRes = srch.querySelectorAll(".moveable-input");
    var draw = document.getElementById("change-on-reload");
    for (var r of searchedRes) {
        draw.appendChild(r);
    }
    srch.style.display = "none";
}

function searchStudentsByLastName(inpt) {
    clearSearchResult();

    var ptrn = inpt.parentElement.parentElement.firstElementChild.value;
    if (ptrn.length == 0) return;
    var studlist = document.querySelectorAll(".moveable-input");
    var oo = document.getElementById("search-res");
    // console.log(studlist);
    var studarray = Array.from(studlist);
    var filtered = studarray.filter((ii => ii.dataset.name.includes(ptrn)));
    // if found - wreck the sort and group the result
    if (filtered.length > 0) {
        oo.style.display = "block";
        for (const res of filtered) {
            oo.appendChild(res);
        }
        resetSortFlag();
    }
}

// End student search

/*
 *  Note to self (mostly):
 *  The following function (moveText) and checkAllTexts() are reused in "send test.html"
 *  to shift selection of students rather than texts while also leaving room for
 *  filtering students based on group and/or course
 *  If you ever wish to change something in those 2, make sure to check
 *  that they work correctly on that page as well
 */

// move text from the pool into draw and vice versa
// big assemble
function moveText(inpt) {
    var el = inpt.parentElement;
    var draw = document.getElementById("dont-change-on-reload");
    var pool = document.getElementById("change-on-reload");
    var srch = document.getElementById("search-res")
    var container = el.parentElement;
    if (container.id == "dont-change-on-reload") {
        inpt.checked = false;
        pool.appendChild(el);
        resetSortFlag();
    }
    else {
        inpt.checked = true;
        draw.appendChild(el);
    }
    var masterCheckbox = document.getElementById("master-select").children[0].children[0];
    if (pool.children.length + srch.children.length == 0) {
        masterCheckbox.checked = true;
    }
    else {
        masterCheckbox.checked = false;
    }
}

// check for the master select on any click
// lil assemble
function clickOnTextStudent(cbox) {
    var pool = document.getElementById("textSelectionBox");
    var opts = pool.children;
    // console.log(opts);
    var cntChecked = 0;
    var cntUnchecked = 0;
    for (var idx = 1; idx < opts.length; idx++) {
        if (opts[idx].firstChild.checked == true) {
            cntChecked++;
        }
        else {
            cntUnchecked++;
        }
    }
    // console.log(cntChecked, cntUnchecked);
    if (cntUnchecked == 0) {
        opts[0].firstElementChild.checked = true;
    }
    else {
        opts[0].firstElementChild.checked = false;
    }
}

// master select behavior for lil assemble
function selectAllTextsStudent(cbox) {
    var pool = document.getElementById("textSelectionBox");
    var opts = pool.children;
    // console.log(opts);
    var cntChecked = 0;
    var cntUnchecked = 0;
    for (var idx = 1; idx < opts.length; idx++) {
        if (opts[idx].firstChild.checked == true) {
            cntChecked++;
        }
        else {
            cntUnchecked++;
        }
    }
    if (cntUnchecked > 0) {
        cbox.checked = true;
        for (var idx = 1; idx < opts.length; idx++) {
            opts[idx].firstElementChild.checked = true;
        }
    }
    else {
        cbox.checked = false;
        for (var idx = 1; idx < opts.length; idx++) {
            opts[idx].firstElementChild.checked = false;
        }
    }
}

// convoluted behavior of the select all checkbox on texts
// big assemble
function checkAllTexts(cbox) {
    var draw = document.getElementById("dont-change-on-reload");
    var pool = document.getElementById("change-on-reload");
    var srch = document.getElementById("search-res");
    var checked = draw.getElementsByClassName("moveable-input");
    var unchecked = pool.children;
    if (unchecked.length + srch.children.length > 0) {
        // select all
        while (unchecked.length > 0) {
            var divChckbx = unchecked[0];
            var inpt = divChckbx.firstElementChild;
            inpt.checked = true;
            draw.append(divChckbx);
        }
        while (srch.children.length > 0) {
            srch.firstElementChild.firstElementChild.checked = true;
            draw.append(srch.firstElementChild);
        }
        clearSearchResult();
    }
    else {
        // deselect all
        while (checked.length > 0) {
            var divChckbx = checked[0];
            var inpt = divChckbx.firstElementChild;
            inpt.checked = false;
            pool.append(divChckbx);
        }
        resetSortFlag();
    }
}

function checkAllCheckboxes(draw_id, pool_id) {
    var draw = document.getElementById(draw_id);
    var pool = document.getElementById(pool_id);
    var checked = draw.getElementsByClassName("moveable-input");
    var unchecked = pool.children;
    if (unchecked.length > 0) {
        // select all
        while (unchecked.length > 0) {
            var divChckbx = unchecked[0];
            var inpt = divChckbx.firstElementChild;
            inpt.checked = true;
            draw.append(divChckbx);
        }
    }
    else {
        // deselect all
        while (checked.length > 0) {
            var divChckbx = checked[0];
            var inpt = divChckbx.firstElementChild;
            inpt.checked = false;
            pool.append(divChckbx);
        }
    }
}

function moveCheckbox(draw_id, pool_id, inpt) {
    var el = inpt.parentElement;
    var draw = document.getElementById(draw_id);
    var pool = document.getElementById(pool_id);
    var container = el.parentElement;
    if (container.id == pool_id) {
        inpt.checked = true;
        draw.appendChild(el);
    }
    else {
        inpt.checked = false;
        pool.appendChild(el);
    }
    var masterCheckbox = draw.children[0].children[0];
    if (pool.children.length == 0) {
        masterCheckbox.checked = true;
    }
    else {
        masterCheckbox.checked = false;
    }
}

// big assemble collapse settings panel
function collapseSettings() {
    // collapse div
    var divToCollapse = document.getElementsByClassName("collapsible-window")[0];
    divToCollapse.style.display = "none";
    var settingsWindow = document.getElementById("left-side");

    // swap buttons
    var leftBtn = document.getElementById("collapse-arrow");
    var rightBtn = document.getElementById("expand-arrow");

    // because bootstrap behaves exacly how you want it to
    leftBtn.style.display = "none";
    rightBtn.style.display = "block";
    settingsWindow.classList.remove('col-5');
    settingsWindow.classList.add("col-auto");
    rightBtn.parentElement.classList.remove("col-1");
}

// big assemble expand settings panel
function expandSettings() {
    // expand div
    var divToExpand = document.getElementsByClassName("collapsible-window")[0];
    divToExpand.style.display = "block";
    var settingsWindow = document.getElementById("left-side");

    // swap buttons
    var leftBtn = document.getElementById("collapse-arrow");
    var rightBtn = document.getElementById("expand-arrow");
    
    // mega crutches go brrrr (again)
    leftBtn.style.display = "block";
    rightBtn.style.display = "none";
    settingsWindow.classList.add('col-5');
    settingsWindow.classList.remove("col-auto");
    rightBtn.parentElement.classList.add("col-1");
}

// big assemble choose or unchoose sentence
function moveSentence(sentence) {
    var divToMove = sentence.parentElement.parentElement.parentElement;
    var pool = document.getElementById("sentence-pool");
    var draw = document.getElementById("sentence-draw");
    // console.log(sentence.id)
    
    if (divToMove.parentElement.id == "sentence-draw") {
        // remove back to pool
        sentence.checked = false;
        pool.append(divToMove);
        unchecked_tasks.push(checked_tasks.find((task) => task.markup_id == sentence.id.substring(4)))
        checked_tasks.splice(checked_tasks.findIndex((task) => task.markup_id == sentence.id.substring(4)), 1)
    }
    else {
        // add to draw
        sentence.checked = true;
        draw.append(divToMove);
        checked_tasks.push(unchecked_tasks.find((task) => task.markup_id == sentence.id.substring(4)))
        unchecked_tasks.splice(unchecked_tasks.findIndex((task) => task.markup_id == sentence.id.substring(4)), 1)
    }
    // console.log(checked_tasks)
    // console.log(unchecked_tasks)
}

// big assemble
// syncs up the mark criteria
// makes sure that mk5 >= mk4 >= mk3
function verifyMarkSelectors(inpt, mk) {
    let mk5 = document.getElementById("inputMark5");
    let mk4 = document.getElementById("inputMark4");
    let mk3 = document.getElementById("inputMark3");
    let inptval = inpt.value;
    if (mk == 5 && inptval < mk4.value) {
        mk5.value = mk4.value;
    }
    if (mk == 4) {
        if (inptval < mk3.value) mk4.value = mk3.value;
        if (inptval > mk5.value) mk4.value = mk5.value;
    }
    if (mk == 3 && inptval > mk4.value) {
        mk3.value = mk4.value;
    }
}

var unchecked_tasks = []
var checked_tasks = []

// load sentences into the big assemble
// now that i think about it it could break on us but realistically it shouldn't
// not when there are at most 50 sentences being spat out at a given time
async function loadSentencesTeacher(url) {
    // here be loading i guess????
    // console.log("TODO: load sentences");
    var jsonParams = {};

    // get checked texts
    var textids = [];
    var checked = document.getElementById("dont-change-on-reload").getElementsByClassName("moveable-input");
    for (var i = 0; i < checked.length; i++) {
        textids.push(checked[i].firstElementChild.value);
    }
    jsonParams["text_ids"] = textids;
    
    // get mistake parameters
    var mistakeTypes = [];
    var orth = document.getElementById("mistakeCheck1").checked;
    if (orth == true) {
        mistakeTypes.push("1");
    }
    var gram = document.getElementById("mistakeCheck2").checked;
    if (gram == true) {
        mistakeTypes.push("2");
    }
    jsonParams["mistake_types"] = mistakeTypes;

    // get max number of sentences
    var maxcnt = Number(document.getElementById("inputTaskAmount").value);
    if (maxcnt > 50) {
        maxcnt = 50;
        document.getElementById("inputTaskAmount").value = 50;
    }
    if (maxcnt <= 0) {
        maxcnt = 1;
        document.getElementById("inputTaskAmount").value = 1;
    }
    jsonParams["sentence_count"] = maxcnt

    // do data magic
    var response = await fetch(url, {
        method: "POST",
        body: JSON.stringify(jsonParams)
    })
    var data = await response.json();

    console.log(data);
    unchecked_tasks = unchecked_tasks.concat(data)

    // spit out sentences
    var pool = document.getElementById("sentence-pool");
    for (var i = 0; i < data.length; i++) {
        var datum = data[i];

        // sentence frame
        var outerDiv = document.createElement("div");
        outerDiv.classList.add("row", "align-items-center", "border-bottom");

        // checkbox
        var cboxOuterWrapper = document.createElement("div");
        cboxOuterWrapper.classList.add("col-auto");
        var cboxInnerWrapper = document.createElement("div");
        cboxInnerWrapper.classList.add("form-check");
        var cbox = document.createElement("input");
        cbox.classList.add("form-check-input");
        cbox.setAttribute("type", "checkbox");
        cbox.setAttribute("value", datum.markup_id);
        cbox.setAttribute("id", "cbox" + datum.markup_id);
        cbox.setAttribute("onclick", "moveSentence(this)");

        // the sentence itself
        var sentenceOuterWrapper = document.createElement("div");
        sentenceOuterWrapper.classList.add("col-11");
        var sentenceInnerWrapper = document.createElement("div");
        sentenceInnerWrapper.classList.add("container", "rounded", "my-2", "py-2");
        var sentenceText = document.createElement("p");
        var txt = datum.text_before + " ______ " + datum.text_after + (datum.inf ? " (" + datum.inf + ")" : "");
        sentenceText.innerHTML = txt;

        // variant selectbox
        var selectWrapper = document.createElement("div");
        selectWrapper.classList.add("form", "col-3");
        if (datum.input_type == 1) {
            var input = document.createElement("select");
            input.classList.add("form-select");
            input.setAttribute("id", "select" + datum.markup_id);
            var optBlank = document.createElement("option");
            optBlank.setAttribute("value", datum.inf);
            optBlank.setAttribute("disabled", "");
            optBlank.setAttribute("selected", "");
            optBlank.text = "Варианты ответа";
            input.appendChild(optBlank);

            for (var j = 0; j < datum.variants.length; j++) {
                var variant = datum.variants[j].variant_text;
                var opt = document.createElement("option");
                opt.setAttribute("value", variant);
                opt.text = variant;
                input.appendChild(opt);
            }
        } else {
            var input = document.createElement("input");
            input.placeholder = "Введите ответ"
            input.setAttribute("id", "select" + datum.markup_id);
        }

        // assemble the structure
        selectWrapper.appendChild(input);
        sentenceInnerWrapper.appendChild(sentenceText);
        sentenceInnerWrapper.appendChild(selectWrapper);
        sentenceOuterWrapper.appendChild(sentenceInnerWrapper);

        cboxInnerWrapper.appendChild(cbox);
        cboxOuterWrapper.appendChild(cboxInnerWrapper);

        outerDiv.appendChild(cboxOuterWrapper);
        outerDiv.appendChild(sentenceOuterWrapper);

        pool.appendChild(outerDiv);
    }
}

async function saveTestTeacher(url, redirect_url) {

    if (checked_tasks.length == 0) {
        alert("А упражнения то не выбраны")
        return
    }

    // try to save test
    // if successful, redirect
    var s3 = document.getElementById("inputMark3").value;
    var s4 = document.getElementById("inputMark4").value;
    var s5 = document.getElementById("inputMark5").value;
    var name = document.getElementById("inputTestName").value;
    var jsonParams = {
        "name": name,
        "score_for_3": s3/100,
        "score_for_4": s4/100,
        "score_for_5": s5/100,
        "tasks": [],
    };

    // get tasks for test
    var draw = document.getElementById("sentence-draw");
    for (const task of checked_tasks) {
        task.inf = task.inf || ""
        jsonParams.tasks.push(task);
    }
    console.log(jsonParams);

    var result = await fetch(url, {
        method: "POST",
        body: JSON.stringify(jsonParams)
    });
    result = await result.json()
    /*
    var data = await result.json();
    // console.log(data);
    if (data.test_id !== undefined) {
        redirectto("/tests/menu/");
    }
    */
    // "{% url 'generator_app:assigned_students' 12345 %}"
    const ret_url = redirect_url.replace("12345", result.test_id)
   redirectto(ret_url);
}

async function makeTestStudent(urlSentences, urlTest, urlAssign, stud_id) {
    // get fixed number of sentences (see above)
    var textSelector = document.getElementById("textSelectionBox");
    var txts = [];
    var jsonParams = {};
    for (var i = 1; i < textSelector.children.length; i++) {
        var entry = textSelector.children[i];
        if (entry.querySelector("input").checked == true) {
            txts.push(entry.querySelector("input").value);
        }
    }
    jsonParams.text_ids = txts;

    var mistakeTypes = [];
    var orth = document.getElementById("mistakeCheck1").checked;
    if (orth == true) {
        mistakeTypes.push("1");
    }
    var gram = document.getElementById("mistakeCheck2").checked;
    if (gram == true) {
        mistakeTypes.push("2");
    }
    jsonParams.mistake_types = mistakeTypes;

    var maxcnt = Number(document.getElementById("inputTaskAmount").value);
    if (maxcnt > 50) {
        maxcnt = 50;
        document.getElementById("inputTaskAmount").value = 50;
    }
    if (maxcnt <= 0) {
        maxcnt = 1;
        document.getElementById("inputTaskAmount").value = 1;
    }
    jsonParams.sentence_count = maxcnt;

    var response = await fetch(urlSentences, {
        method: "POST",
        body: JSON.stringify(jsonParams)
    })
    var data = await response.json();
    // console.log(data);

    var sentencesData = [];
    if (data.length > maxcnt) {
        // select maxcnt exercises at random
        sentencesData = reshuffleSentences(data, maxcnt);
    }
    else if (data.length <= maxcnt && data.length > 0) {
        // make the test regardless but notify the user of the lack of exerises
        sentencesData = data;
    }
    else {
        alert("maxcnt is wrong somehow");
        return;
    }

    // // omega crutch
    // for (var i = 0; i < sentencesData.length; i++) {
    //     sentencesData[i].input_type = 0;
    //     var newvars = [];
    //     for (var j = 0; j < sentencesData[i].variants.length; j++) {
    //         newvars.push({
    //             "variant_text": sentencesData[i].variants[j]
    //         });
    //     }
    //     sentencesData[i].variants = newvars;
    // }
    console.log(sentencesData)

    // make test
    var testName = document.getElementById("inputTestName").value;
    var json2 = {
        "name": testName,
        "score_for_3": 0.6,
        "score_for_4": 0.8,
        "score_for_5": 0.9,
        "tasks": []
    };
    // console.log(json2);

    for (const task of sentencesData) {
        task.inf = task.inf || ""
        json2.tasks.push(task);
    }

    var result = await fetch(urlTest, {
        method: "POST",
        body: JSON.stringify(json2)
    });
    var data2 = await result.json();

    // TODO: check for successful save and assign

    // !!! Static redirect, may break if url configs change !!!
    redirectto(`/tests/${data2.test_id}/solve/`);
}

function reshuffleSentences(array, l) {
    for (var i = array.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
    return array.slice(0, l);
}

function showRenameModal() {
    var modal = document.getElementById("nameModal");
    var inpt = document.getElementById("inputTestName");
    modal.addEventListener('show.bs.modal', () => {
        inpt.focus();
    });
    modal.show();
}

function wireDeleteButton(entry_id) {
    var btn = document.getElementById("deleteTestButton");
    btn.setAttribute("value", entry_id);
}

async function triggerDeleteTest(url) {
    var tid = document.getElementById("deleteTestButton").value;
    // console.log(tid);
    await deleteTest(url, tid);
    var entry = document.getElementById("entry" + tid);
    entry.parentElement.removeChild(entry);
}

async function getAssignData(url, test_id, urlback) {
    var draw = document.getElementById("dont-change-on-reload").children;
    if (draw.length < 1) return;
    for (var i = 0; i < draw.length; i++) {
        var stud_id = draw[i].querySelector("input").value;
        var res = await sendTest(url, test_id, stud_id);
        // console.log(res.text());
        // console.log(res.json());
    }
    redirectto(urlback);
}

// TODO: call delete test api from any delete button
async function deleteTest(url, test_id) {
    return await fetch(url, {
        method: 'DELETE',
        body: JSON.stringify({test_id: test_id})
    })
}

function some_func(e, test_id, task_id) {
    saveAnswer(
        url, 
        test_id, 
        task_id,
        document.getElementById(`SelectAnswer${task_id}`).value
    )
}

// TODO: call check answer api from "pass test.html"
async function saveAnswer(url, test_id, task_id, stud_answer) {
    return await fetch(url, {
        method: 'POST',
        body: JSON.stringify({
            "test_id": test_id,
            "task_id": task_id,
            "stud_answer": stud_answer,
        })
    })
}

// TODO: call save test results api from "pass test.html"
async function submitTest(url, test_id, back) {
    var response = await fetch(url, {
        method: 'POST',
        body: JSON.stringify({
            "test_id": test_id,
        })
    });
    redirectto(back);
}

// TODO: in "send test.html" collect selected student ids and 
// perform a batch send
async function sendTest(url, test_id, stud_id) {
    return await fetch(url, {
        method: 'POST',
        body: JSON.stringify({
            "test_id": test_id,
            "stud_id": stud_id,
        })
    })
}

(e, test_id) => {
    students = [] // Получить студентиков с селекта
    for (let stud of students) {
        sendTest(url, test_id, stud)
    }
}

async function unassignTest(url) {
    var test_id = document.getElementById("testIdGetter").value;
    var stud_id = document.getElementById("deleteTestButton").value;
    console.log(test_id, stud_id);
    var res = await unsendTest(url, test_id, stud_id);
    var data = await res.text();
    if (data === "okay") {
        var entry = document.getElementById("entry"+stud_id);
        entry.parentElement.removeChild(entry);
    }
}

// TODO: call unsend api from "test result all students.html"
async function unsendTest(url, test_id, stud_id) {
    return await fetch(url, {
        method: 'POST',
        body: JSON.stringify({
            "test_id": test_id,
            "stud_id": stud_id,
        })
    })
}

async function getCheckData(url, test_id, task_id) {
    var answer = document.getElementById("task" + task_id).value;
    var res = await saveAnswer(url, test_id, task_id, answer);
    var data = await res.json();
    // console.log(data);
    var pool = document.getElementById("verdictPool");
    var dest = document.getElementById("verdict" + task_id);
    if (dest.children.length > 0) dest.removeChild(dest.children[0]);
    if (data.status) {
        // display checkmark
        dest.appendChild(pool.children[0].cloneNode(true));
    }
    else {
        // display crossmark
        dest.appendChild(pool.children[1].cloneNode(true));
    }
}

// --- lowest priority ---

// TODO: call export api from any export button
async function exportTest(test_id,name, url) {
    console.log(name)
    return await fetch(url, {
        method: 'POST',
        body: JSON.stringify({
            "test_id": test_id,
        })
    })
    .then((res) => res.blob())
    .then((blob) => URL.createObjectURL(blob))
    .then((href) => {
    Object.assign(document.createElement('a'), {
        href,
        download: `${name}.docx`,
    }).click();

  })
}

async function exportReport(test_ids, stud_ids, name, url) {
    return await fetch(url, {
        method: 'POST',
        body: JSON.stringify({
            "test_ids": test_ids,
            "stud_ids": stud_ids,
        })
    })
    .then((res) => res.blob())
    .then((blob) => URL.createObjectURL(blob))
    .then((href) => {
    Object.assign(document.createElement('a'), {
        href,
        download: `${name}.docx`,
    }).click();

  })
}

async function makeReport(url) {
    var draw_tests = document.getElementById("draw-tests").children;
    var draw_students = document.getElementById("draw-students").children;

    if (draw_tests.length <= 1 || draw_students.length <= 1) return;

    let stud_ids = []
    for (var i = 1; i < draw_students.length; i++) {
        stud_ids.push(draw_students[i].querySelector("input").value)
    }

    let test_ids = []
    for (var i = 1; i < draw_tests.length; i++) {
        test_ids.push(draw_tests[i].querySelector("input").value)
    }

    console.log(stud_ids)
    console.log(test_ids)

    return exportReport(test_ids, stud_ids, "Отчёт", url)
    // redirectto(urlback);
}

// TODO: get all groups

// TODO: get students by group

// Newest: edit and save parts of individual tasks
// because no one wants to see the -EMPTY- tags scattered about
// the test like stray rocks in a shoe
var changed_tasks = [];

function toggle_editor(printable) {
    var grp = printable.parentElement;
    var writable = grp.querySelector("input");
    writable.classList.remove("e-hidden");
    writable.value = printable.textContent;
    printable.classList.add("e-hidden");
    writable.focus();
}

// Revert editor back to printable 
// and log the changes to save later in one batch
function untoggle_editor(writable) {
    var grp = writable.parentElement;
    var printable = grp.querySelector("p");
    printable.classList.remove("e-hidden");
    writable.classList.add("e-hidden");
    if (printable.textContent === writable.value) {
        console.log("unchanged, not pushing");
        return;
    }
    printable.textContent = writable.value;
    half_indicator = writable.id.split("-")[1];
    task_id = parseInt(writable.id.split("-")[2]);
    for (let task of changed_tasks) {
        if (task.task_id == task_id && task.half == half_indicator) {
            task.new_text = writable.value;
            console.log(changed_tasks);
            return;
        }
    }
    changed_tasks.push({
        "task_id": task_id,
        "half": half_indicator,
        "new_text": writable.value
    });
    console.log(changed_tasks);
}

// Actually save whatever's changed in preview
// btw yes it's test preview.html
// and i'm still weirded out by the whitespaces

function cancel_changes() {
    // there's a more elegant way (reset just the changes
    // instead of reloading _everything_)
    // but it's almost 12am and i'm low on grape juice
    window.location.reload();
}

async function register_changes(url) {
    // console.log(changed_tasks);
    if (changed_tasks.length > 0) {
        res = await (await save_changes(url)).json();
        // console.log(res);
        var checker = document.getElementById("editor-save-success");
        checker.classList.remove("e-hidden");
    }
}

async function save_changes(url) {
    return await fetch(url, {
        method: "POST",
        body: JSON.stringify(changed_tasks)
    });
}

function untoggle_checker() {
    var checker = document.getElementById("editor-save-success");
    if (!checker.classList.contains("e-hidden")) {
        checker.classList.add("e-hidden");
    }
}