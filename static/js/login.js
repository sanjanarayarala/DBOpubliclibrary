document.getElementById("loginForm").addEventListener("submit", function (e) {
    e.preventDefault(); // Prevent form submission

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    
    // Dummy credentials (replace with a real server-side check in a production environment)
    const users = {
        "admin": { password: "adminpass", role: "admin" },
        "user": { password: "userpass", role: "user" }
    };

    if (users[username] && users[username].password === password) {
        // Redirect based on role
        if (users[username].role === "admin") {
            window.location.href = "index2.html"; // Admin page
        } else if (users[username].role === "user") {
            window.location.href = "index.html"; // User page
        }
    } else {
        document.getElementById("error-message").style.display = "block";
    }
});
