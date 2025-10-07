document.getElementById("signupForm").addEventListener("submit", async function (event) {
  event.preventDefault(); // Stop form from reloading the page

  const username = document.getElementById("username").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  try {
    const response = await fetch("http://127.0.0.1:5000/signup/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password })
    });

    const data = await response.json();

    if (response.ok) {
      document.getElementById("response").innerText = data.message;
      // optionally redirect after signup
      // window.location.href = "login.html";
    } else {
      document.getElementById("response").innerText = data.error;
    }

  } catch (error) {
    document.getElementById("response").innerText = "Network error. Try again.";
  }
});
