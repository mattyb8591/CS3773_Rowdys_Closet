document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("signupForm");
  const messageDiv = document.getElementById("message");

  form.addEventListener("submit", async (event) => {
    event.preventDefault(); 

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    console.log("Form submitted with:", { username, email, password, confirmPassword }); // Debug log

    messageDiv.textContent = "";

    if (!username || !email || !password || !confirmPassword) {
      showMessage("All fields are required.", "red");
      return;
    }

    if (password !== confirmPassword) {
      showMessage("Passwords do not match.", "red");
      return;
    }

    if (password.length < 6) {
      showMessage("Password must be at least 6 characters long.", "red");
      return;
    }

    if (!isValidEmail(email)) {
      showMessage("Please enter a valid email address.", "red");
      return;
    }

    try {
      console.log("Sending fetch request to /signup/..."); // Debug log
      
      const response = await fetch("/signup/", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({ username, email, password }),
      });

      console.log("Response status:", response.status); // Debug log
      console.log("Response headers:", response.headers); // Debug log

      const result = await response.json();
      console.log("Response result:", result); // Debug log

      if (response.ok) {
        showMessage(result.message || "Account created successfully! Redirecting to login...", "green");
        form.reset();

        setTimeout(() => {
          window.location.href = "/"; 
        }, 2000);
      } else {
        showMessage(result.error || "Signup failed. Please try again.", "red");
      }
    } catch (error) {
      console.error("Fetch error:", error);
      showMessage("Network error. Please check your connection and try again.", "red");
    }
  });

  function showMessage(message, color) {
    messageDiv.textContent = message;
    messageDiv.style.color = color;
    messageDiv.style.fontWeight = "bold";
    messageDiv.style.marginTop = "10px";
    messageDiv.style.padding = "10px";
    messageDiv.style.border = `1px solid ${color}`;
    messageDiv.style.borderRadius = "5px";
  }

  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
});
