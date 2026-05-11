document.addEventListener("DOMContentLoaded", function () {

    const fileInput    = document.getElementById("fileInput");
    const uploadZone   = document.getElementById("uploadZone");
    const uploadPH     = document.getElementById("uploadPlaceholder");
    const previewWrap  = document.getElementById("previewWrap");
    const preview      = document.getElementById("preview");
    const removeBtn    = document.getElementById("removeBtn");
    const previewFname = document.getElementById("previewFilename");
    const searchForm   = document.getElementById("searchForm");
    const submitBtn    = document.getElementById("submitBtn");

    if (!fileInput) return;

    function showPreview(file) {
        preview.src = URL.createObjectURL(file);
        previewFname.textContent = file.name;
        uploadPH.style.display = "none";
        previewWrap.style.display = "flex";
    }

    function clearPreview() {
        preview.src = "";
        previewFname.textContent = "";
        uploadPH.style.display = "block";
        previewWrap.style.display = "none";
        fileInput.value = "";
    }

    fileInput.addEventListener("change", function (e) {
        const file = e.target.files[0];
        if (file) showPreview(file);
    });

    if (removeBtn) {
        removeBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            e.preventDefault();
            clearPreview();
        });
    }

    uploadZone.addEventListener("dragenter", function (e) {
        e.preventDefault();
        uploadZone.classList.add("drag-over");
    });

    uploadZone.addEventListener("dragover", function (e) {
        e.preventDefault();
        uploadZone.classList.add("drag-over");
    });

    uploadZone.addEventListener("dragleave", function () {
        uploadZone.classList.remove("drag-over");
    });

    uploadZone.addEventListener("drop", function (e) {
        e.preventDefault();
        uploadZone.classList.remove("drag-over");
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith("image/")) {
            const dt = new DataTransfer();
            dt.items.add(file);
            fileInput.files = dt.files;
            showPreview(file);
        }
    });

    if (searchForm && submitBtn) {
        searchForm.addEventListener("submit", function () {
            const textEl    = submitBtn.querySelector(".btn-search-text");
            const loadingEl = submitBtn.querySelector(".btn-search-loading");
            if (textEl)    textEl.style.display    = "none";
            if (loadingEl) loadingEl.style.display = "inline-flex";
            submitBtn.disabled = true;
        });
    }

    const bars = document.querySelectorAll(".score-bar-fill");
    bars.forEach(function (bar) {
        const targetWidth = bar.style.width;
        bar.style.width = "0%";
        setTimeout(function () { bar.style.width = targetWidth; }, 200);
    });

});