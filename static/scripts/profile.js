document.addEventListener("DOMContentLoaded", async () => {
  try {
    const response = await fetch("/profile/", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({ user, address }),
      });

    const result = await response.json();

    if (!result.success) {
      window.location.href = "/login/";
      return;
    }

    const user = result.user;
    const address = result.address;

    // CHECK WITH THE HTML IF THESE VALUES MATCHES
    document.getElementById("username").textContent = user.username;
    document.getElementById("email").textContent = user.email;
    document.getElementById("phone_number").textContent = user.email;
    document.getElementById("profile_picture").textContent = user.img_profile_path; // THIS COULD BE WRONG 
    document.getElementById("address").textContent = address.street_number + " " + address.street_name + " " + address.city + ", " + address.state_abrev + " " + address.zip_code;

  } catch (error) {
    console.error("Failed to fetch profile:", error);
  }
});
