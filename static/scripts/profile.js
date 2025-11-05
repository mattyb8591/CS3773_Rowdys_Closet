document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("profileForm");
  const messageBox = document.getElementById("message");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = {
      username: document.getElementById("username").value.trim(),
      email: document.getElementById("email").value.trim(),
      phone: document.getElementById("phone").value.trim(),
      street_number: document.getElementById("street_number").value.trim(),
      street_name: document.getElementById("street_name").value.trim(),
      city: document.getElementById("city").value.trim(),
      state: document.getElementById("state").value.trim(),
      zip_code: document.getElementById("zip_code").value.trim(),
    };

    Object.keys(formData).forEach((key) => {
      if (formData[key] === "") {
        delete formData[key];
      }
    });

    try {
      const response = await fetch("/profile/update", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const result = await response.json();

      if (result.success) {
        messageBox.textContent = "Profile updated successfully!";
        messageBox.style.color = "green";
        setTimeout(() => {
          window.location.href = result.redirect_url || "/profile/";
        }, 1000);
      } else {
        messageBox.textContent = result.error || "Failed to update profile.";
        messageBox.style.color = "red";
      }
    } catch (err) {
      console.error("Error updating profile:", err);
      messageBox.textContent = "Error connecting to server.";
      messageBox.style.color = "red";
    }
  });
});