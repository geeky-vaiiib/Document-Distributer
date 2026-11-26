const filters = document.querySelector("form.filters");
if (filters) {
  for (const select of filters.querySelectorAll("select")) {
    select.addEventListener("change", () => filters.requestSubmit());
  }
}

const fileInput = document.querySelector("#document");
if (fileInput) {
  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    fileInput.setCustomValidity(file && file.size > 10 * 1024 * 1024
      ? "Choose a file that is 10 MB or smaller."
      : "");
    fileInput.reportValidity();
  });
}
