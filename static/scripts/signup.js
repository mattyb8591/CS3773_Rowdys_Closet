document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("signupForm");

  form.addEventListener("submit", async (event) => {
    event.preventDefault(); 

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    console.log("Form submitted with:", { username, email, password, confirmPassword }); // Debug log

    // STILL NEEDS TO SHOW ERROR MESSAGES
    if (!username || !email || !password || !confirmPassword) {
      return;
    }

    if (password !== confirmPassword) {
      return;
    }

    if (password.length < 6) {
      return;
    }

    if (!isValidEmail(email)) {
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
        form.reset();

        setTimeout(() => {
          window.location.href = "/"; 
        }, 2000);
      } else {
        // have error message to try again
      }
    } catch (error) {
      console.error("Fetch error:", error);
    }
  });

  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
});
