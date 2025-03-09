document.addEventListener("DOMContentLoaded", function () {
    const dropArea = document.getElementById("drop-area");
    const fileInput = document.getElementById("file-input");
    const fileInfo = document.getElementById("file-info");
    const uploadedFileName = document.getElementById("uploaded-file-name");
    const basicFields = document.getElementById("basic-fields");
    const advancedFields = document.getElementById("advanced-fields");
    const basicBtn = document.getElementById("basic-btn");
    const advancedBtn = document.getElementById("advanced-btn");
    const processForm = document.getElementById("process-form");
    const processBtn = document.getElementById("process-btn");
    const downloadSection = document.getElementById("download-section");
    const downloadLink = document.getElementById("download-link");

    dropArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropArea.classList.add("hover");
    });

    dropArea.addEventListener("dragleave", () => {
        dropArea.classList.remove("hover");
    });

    dropArea.addEventListener("drop", (e) => {
        e.preventDefault();
        dropArea.classList.remove("hover");

        if (e.dataTransfer.files.length > 0){
            fileInput.files = e.dataTransfer.files;
            console.log("File dropped:", fileInput.files[0].name)
            uploadFile();
        }
    });

    //dropArea.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", uploadFile);

    function uploadFile() {
        let file = fileInput.files[0];
        if (!file) return;

        let formData = new FormData();
        formData.append("bibfile", file);

        fetch("/upload", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                uploadedFileName.textContent = file.name;
                fileInfo.classList.remove("hidden");
                processBtn.classList.remove("hidden");
                downloadSection.style.display = "none";
                downloadLink.href = `#`;
            } else {
                alert("Upload failed! Please try again.");
            }
        })
        .catch(error => {
            console.error("Upload Error:", error);
            alert("Error uploading file.");
        });
    }

    processForm.addEventListener("submit", function(e) {
        e.preventDefault()

        let formData = new FormData(processForm);

        fetch("/process", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Processing completed!");
                downloadSection.style.display = "block";
                downloadLink.href = `/download/${data.filename}`;
            } else {
                alert("Processing failed! Please try again." + data.message);
            }
        })
        .catch(error => {
            console.error("Processing Error:" , error);
            alert("Error processing file.");
        });
    });

    document.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
        checkbox.addEventListener("change", syncCheckboxes);
    });

    document.querySelectorAll('#basic-fields input[type="checkbox"]').forEach((checkbox) => {
        let value = checkbox.value;
        updateBasicCheckbox(value);
    });

    window.toggleBasic = function () {
        if (basicFields.classList.contains("hidden")) {
            basicFields.classList.remove("hidden");
            basicBtn.classList.add("active");
            advancedFields.classList.add("hidden");
            advancedBtn.classList.remove("active");
        } else {
            basicFields.classList.add("hidden");
            basicBtn.classList.remove("active");
        }
    };

    window.toggleAdvanced = function () {
        if (advancedFields.classList.contains("hidden")) {
            advancedFields.classList.remove("hidden");
            advancedBtn.classList.add("active");
            basicFields.classList.add("hidden");
            basicBtn.classList.remove("active");
        } else {
            advancedFields.classList.add("hidden");
            advancedBtn.classList.remove("active");
        }
    };
    
    function syncCheckboxes(event) {
        let checkbox = event.target;
        let value = checkbox.value;
        let isChecked = checkbox.checked;
        let isBasic = checkbox.closest("#basic-fields") !== null;

        if (isBasic) {
            // Sync all checkboxes with the same value in Advanced (but keep different types independent)
            document.querySelectorAll(`#advanced-fields input[value="${value}"]`).forEach((box) => {
                box.checked = isChecked;
            });
        } else {
            // Advanced checkboxes only affect their own section, so we update Basic state
            updateBasicCheckbox(value);
        }
    }

    function updateBasicCheckbox(value) {
        let relatedCheckboxes = document.querySelectorAll(`#advanced-fields input[value="${value}"]`);

        let checkedCount = 0;
        let totalCount = relatedCheckboxes.length;

        relatedCheckboxes.forEach((box) => {
            if (box.checked) checkedCount++;
        });

        let basicCheckbox = document.querySelector(`#basic-fields input[value="${value}"]`);

        if (basicCheckbox) {
            if (checkedCount === 0) {
                basicCheckbox.indeterminate = false;
                basicCheckbox.checked = false;
            } else if (checkedCount === totalCount) {
                basicCheckbox.indeterminate = false;
                basicCheckbox.checked = true;
            } else {
                basicCheckbox.indeterminate = true;
            }
        }
    }
});
