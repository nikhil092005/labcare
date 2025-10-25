document.getElementById('registrationForm').addEventListener('submit', function(event) {
    event.preventDefault();
    // Example frontend validation (add your own/expand as needed)
    let uid = document.getElementById('uid').value.trim();
    let name = document.getElementById('name').value.trim();
    let email = document.getElementById('email').value.trim();
    let password = document.getElementById('password').value.trim();
    let mobile = document.getElementById('mobile_number').value.trim();
    let course = document.getElementById('course').value.trim();

    if (!uid || !name || !email || !password || !mobile || !course) {
        alert("All fields are required.");
        return;
    }

    // Here you can send the data to your backend using fetch/ajax
    alert("Registration Successful!\n(Connect this to your backend for real operation)");
});
