document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("signupForm");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    var elMsg = document.getElementById("feedback");
    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    // STILL NEEDS TO SHOW ERROR MESSAGES
    if (!username || !email || !password || !confirmPassword) {
      elMsg.innerHTML = "You must fill out every field."
      return;
    }

    if (password !== confirmPassword) {
      elMsg.innerHTML = "Password fields aren't the same."
      return;
    }

    if (password.length < 6) {
      elMsg.innerHTML = "Password needs to be longer than 6 characters."
      return;
    }

    if (!isValidEmail(email)) {
      elMsg.innerHTML = "Not a valid email."
      return;
    }

    try {   
      const response = await fetch("/signup/", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({ username, email, password }),
      });

      const result = await response.json();

      if (response.ok) {
        form.reset();

        setTimeout(() => {
          window.location.href = "/"; 
        }, 2000);
      } else {
        elMsg.innerHTML = "Error with submitting form. Try again"
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
