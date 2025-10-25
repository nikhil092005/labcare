function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  sidebar.classList.toggle("active");
}

function searchIssues() {
  const input = document.getElementById("searchIssue").value.toLowerCase();
  const cards = document.querySelectorAll(".issue-card");

  cards.forEach((card) => {
    const header = card.querySelector("h3").textContent.toLowerCase();
    const details = card
      .querySelector(".issue-details")
      .textContent.toLowerCase();

    if (header.includes(input) || details.includes(input)) {
      card.style.display = "block";
    } else {
      card.style.display = "none";
    }
  });
}

function viewIssue(issueId) {
  // Redirect to issue detail page (you'll create this later)
  window.location.href = `/issue/${issueId}`;
}

// Close sidebar when clicking outside
document.addEventListener("click", function (event) {
  const sidebar = document.getElementById("sidebar");
  const menuBtn = document.querySelector(".menu-btn");

  if (!sidebar.contains(event.target) && !menuBtn.contains(event.target)) {
    sidebar.classList.remove("active");
  }
});
