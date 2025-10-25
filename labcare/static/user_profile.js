function enableEdit(fieldId) {
  const input = document.getElementById(fieldId);
  input.removeAttribute("readonly");
  input.focus();
  input.style.borderColor = "#3b82f6";

  // Show save button
  document.getElementById("saveBtn").style.display = "flex";
}

function openPasswordModal() {
  document.getElementById("passwordModal").classList.add("active");
}

function closePasswordModal() {
  document.getElementById("passwordModal").classList.remove("active");
}

// Close modal on Escape key
document.addEventListener("keydown", function (event) {
  if (event.key === "Escape") {
    closePasswordModal();
  }
});
