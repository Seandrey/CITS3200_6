// Functions used for editing page
// Author: Lara Posel (22972221), Joel Phillips (22967051)

/**
 * Append drop down to each field table cell of the class given
 * @param {string} className name of associated class
 * @param {{id: number, name: string}[]} dbQueryResults database query results
 */
function setupDropdown(className, dbQueryResults) {
    const dropdownToClone = document.createElement("select");
    for (const result of dbQueryResults) {
        const choice = document.createElement("option");
        choice.value = result.id; 
        choice.text = result.name;
        dropdownToClone.appendChild(choice);
    }
    dropdownToClone.disabled = true;

    const toSetup = document.getElementsByClassName(className);
    for (const node of toSetup) {
        const existingId = node.textContent;
        if (existingId !== null && existingId !== "") {
            const dropDownCopy = dropdownToClone.cloneNode(true);
            dropDownCopy.value = existingId;

            // remove node text contents
            node.textContent = "";

            node.appendChild(dropDownCopy);
        } else {
            // TODO: remove this else branch thing once remove old stuff
            const dropDownCopy = dropdownToClone.cloneNode(true);
            dropDownCopy.value = 0;
            node.appendChild(dropDownCopy);
        }
    }
}

/**
 * Restore an input to text form.
 * @param {HTMLInputElement} input 
 */
function restoreDateInput(input) {
    // restore upon exit
    const parent = input.parentElement;
    const dateVal = input.value;
    parent.removeChild(input);
    parent.textContent = dateVal;
}

function setup() {
    // -------------------------------------------------------------------------------------
    // Create 'Locations' drop down box: 
    // -------------------------------------------------------------------------------------

    // TODO: replace this with DB query of all locations
    //const locations = ["West Coast Eagles", "UWA Exercise & Performance Centre", "WACRH (Geraldton)", "Agility Rehabilitation", "Curtin Stadium"]; 
    //const locations = [{ id: 0, location: "West Coast Eagles" }, { id: 1, location: "UWA Exercise & Performance Centre" }, { id: 2, location: "WACRH (Geraldton)" }, { id: 3, location: "Agility Rehabilitation" }, { id: 4, location: "Curtin Stadium" }];

    // DEBUG
    if (locations == undefined) {
        console.log("locations undefined");
        console.log(locations);
    }

    setupDropdown("location-field", locations);

    // -------------------------------------------------------------------------------------
    // Create 'supervisors' drop down box: 
    // -------------------------------------------------------------------------------------

    // TODO: replace this with DB query of all supervisors
    //const supervisors = [{ id: 0, supervisor: "Jarryd Heasman" }, { id: 1, supervisor: "Joel Young" }, { id: 2, supervisor: "Ben Green" }, { id: 3, supervisor: "Emma Philipe" }, { id: 4, supervisor: "Kane Greenaway" }];

    setupDropdown("supervisor-field", supervisors);

    // -------------------------------------------------------------------------------------
    // Create 'exercise-prescription' drop down box: 
    // -------------------------------------------------------------------------------------

    //const exercisePrescription = [{ id: 0, activity: "Exercise Prescription" }, { id: 1, activity: "Other" }]

    setupDropdown("exercise-prescription-field", activities);

    // -------------------------------------------------------------------------------------
    // Create 'domain' drop down box: 
    // -------------------------------------------------------------------------------------

    //const domains = [{ id: 0, domain: "Health & Fitness" }, { id: 1, domain: "Sport & Performance" }, { id: 2, domain: "Healthy Aging" }, { id: 3, domain: "Paediatrics & Young People" }, { id: 4, domain: "Mental Health & Wellness" }]

    setupDropdown("domain-field", domains);

    // unit dropdown box
    //const units = [{id: 0, unit: "Unit1"}, {id: 1, unit: "Unit2"}, {id: 2, unit: "Unit3"}, {id: 3, unit: "Unit4"}];
    setupDropdown("unit-field", units);

    // -------------------------------------------------------------------------------------
    // Add event listeners to all drop downs to enable/disable editing
    // -------------------------------------------------------------------------------------

    const allSelects = document.getElementsByClassName('select');
    for (const tableData of allSelects) {
        tableData.addEventListener('dblclick', function () {
            const dropDown = this.firstElementChild;
            dropDown.removeAttribute("disabled");
        });

        tableData.addEventListener('change', function () {
            const dropDown = this.firstElementChild;
            dropDown.removeAttribute("disabled");
            this.style.backgroundColor = 'rgb(220, 227, 255)';
            dropDown.style.backgroundColor = 'rgb(220, 227, 255)';
        });

        tableData.addEventListener('mouseout', function () {
            const dropDown = this.firstElementChild;
            dropDown.removeAttribute("disabled");
        });
    }

    const minutesFields = document.getElementsByClassName('text-field');
    const initialMinutes = [];

    for (let i = 0; i < minutesFields.length; i++) {
        initialMinutes.push(minutesFields[i].innerText);

        minutesFields[i].addEventListener('dblclick', function () {
            this.contentEditable = 'true';
            this.focus();
            this.style.backgroundColor = '#ffcccc';
            this.style.color = 'black';
        });

        minutesFields[i].addEventListener('blur', function () {
            this.contentEditable = 'false';
            this.style.backgroundColor = '';
            this.style.color = 'rgb(165, 164, 164)';
            if (validateInput(this.innerText)) {
                this.style.color = "red";
            } else {
                if (this.innerText != initialMinutes[i])
                    this.style.backgroundColor = 'rgb(220, 227, 255)';
            }
        });

        minutesFields[i].addEventListener('keypress', function (event) {
            if (event.key == "Enter") {
                this.contentEditable = 'false';
                this.style.backgroundColor = '';
                if (this.innerText != initialMinutes[i])
                    this.style.backgroundColor = 'rgb(220, 227, 255)';
            }
        });

    }

    const descriptionFields = document.getElementsByClassName('desc-field');
    const initialDesc = [];

    for (let i = 0; i < descriptionFields.length; i++) {
        initialDesc.push(descriptionFields[i].innerText);

        descriptionFields[i].addEventListener('dblclick', function () {
            this.contentEditable = 'true';
            this.focus();
            this.style.backgroundColor = '#ffcccc';
            this.style.color = 'black';
        });

        descriptionFields[i].addEventListener('blur', function () {
            this.contentEditable = 'false';
            this.style.backgroundColor = '';
            this.style.color = 'rgb(165, 164, 164)';
            if (validateText(this.innerText)) {
                this.style.color = "red";
            } else {
                if (this.innerText != initialDesc[i])
                    this.style.backgroundColor = 'rgb(220, 227, 255)';
            }
        });

        descriptionFields[i].addEventListener('keypress', function (event) {
            if (event.key == "Enter") {
                this.contentEditable = 'false';
                this.style.backgroundColor = '';
                if (this.innerText != initialDesc[i])
                    this.style.backgroundColor = 'rgb(220, 227, 255)';
            }
        });

    }

    const dateFields = document.getElementsByClassName("date-field");
    for (const dateField of dateFields) {
        dateField.addEventListener("dblclick", () => {
            // check if has input already
            if (dateField.getElementsByTagName("input").length === 0) {
                const dateText = dateField.textContent;

                // create input with type date
                const input = document.createElement("input");
                input.type = "date";
                input.value = dateText;
                input.addEventListener("blur", () => restoreDateInput(input));
                
                // remove text and add input
                dateField.textContent = "";
                dateField.appendChild(input);
            }
        });
    }
}

// -------------------------------------------------------------------------------------
// Event listeners to edit text fields (only minutes for now, still need to add date editing) 
// -------------------------------------------------------------------------------------
function validateInput(value) {
    const number = Number(value);
    if (!(Number.isInteger(number))) {
        alert("Please enter a positive integer in the minutes field.");
        return true;
    } else {
        return false;
    }
}

function validateText(value) {
    if (!(typeof value === 'string' || value instanceof String)) {
        console.log("IS STRING")
        return true;
    } else {
        return false;
    }
}

/**
 * Get numerical value of selected option for given class in given row
 * @param {HTMLTableRowElement} rowElem row to search inside
 * @param {string} className class to search for
 * @returns select value
 */
function getSelectValue(rowElem, className) {
    const select_parent = rowElem.getElementsByClassName(className);
    console.assert(select_parent.length === 1);
    console.assert(select_parent[0].classList.contains("select"));

    const selectItself = select_parent[0].getElementsByTagName("select");
    console.assert(selectItself.length === 1);

    const actualSelect = selectItself[0];

    const parsedInt = parseInt(actualSelect.value);
    console.assert(!isNaN(parsedInt));

    return parsedInt;
}

/**
 * Get text value of certain field in a certain row
 * @param {HTMLTableRowElement} rowElem row to search inside
 * @param {string} className class to search for
 * @returns text value
 */
function getTextField(rowElem, className) {
    const textParent = rowElem.getElementsByClassName(className);
    console.assert(textParent.length === 1);
    
    return textParent[0].textContent;
}

/**
 * Gets numerical value of minutes field in certain row
 * @param {HTMLTableRowElement} rowElem row to search inside
 * @returns numerical value in minutes
 */
function getMinutesField(rowElem) {
    const text = getTextField(rowElem, "minutes-field");

    const parsedInt = parseInt(text);
    console.assert(!isNaN(parsedInt));

    return parsedInt;
}

/**
 * Gets text value of activity field in certain row - Must Place Description back on row to work
 * @param {HTMLTableRowElement} rowElem row to search inside
 * @returns string value in desc
 */
function getdescriptionField(rowElem) {
    const text = getTextField(rowElem, "desc-field");

    return text;
}

/**
 * Gets date value of date field in certain row
 * @param {HTMLTableRowElement} rowElem row to search inside
 * @returns date value
 */
function getDateField(rowElem) {
    // first, ensure date is in text form. if not, make it
    const dateFields = rowElem.getElementsByClassName("date-field");
    console.assert(dateFields.length === 1);
    const input = dateFields[0].getElementsByTagName("input");
    if (input.length !== 0) 
        restoreDateInput(input[0]);

    const text = getTextField(rowElem, "date-field");

    const parsedDate = new Date(text);
    console.assert(!isNaN(parsedDate));

    return parsedDate.toJSON();
}

/**
 * Submits update for a given row.
 * @param {number} id id of row
 * @param {HTMLButtonElement} button_elem button element clicked
 */
function submitUpdate(id, button_elem) {
    // get table row
    const row_elem = button_elem.parentElement.parentElement;
    console.assert(row_elem instanceof HTMLTableRowElement);

    // make object
    const gameObj = {
        logid: id,
        studentid: studentid,
        locationid: getSelectValue(row_elem, "location-field"),
        supervisorid: getSelectValue(row_elem, "supervisor-field"),
        activityid: getSelectValue(row_elem, "exercise-prescription-field"),
        domainid: getSelectValue(row_elem, "domain-field"),
        minutes_spent: getMinutesField(row_elem),
        record_date: getDateField(row_elem),
        unitid: getSelectValue(row_elem, "unit-field"),
        // Not detecting activity desk? Act same as minutes field
        activitydesc: getdescriptionField(row_elem)
    };
    console.log(gameObj);

    fetch("/reports/submit_edit", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(gameObj)
    })
    // TODO: reload page afterwards?
}

setup();
