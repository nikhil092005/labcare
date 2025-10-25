function previewImage(event) {
  const preview = document.getElementById("imagePreview");
  const file = event.target.files[0];

  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
      preview.classList.add("active");
    };
    reader.readAsDataURL(file);
  }
}

function clearPreview() {
  const preview = document.getElementById("imagePreview");
  preview.innerHTML = "";
  preview.classList.remove("active");
}
