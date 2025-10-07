var elUsername = document.getElementById('username');
var elPassword = document.getElementById('password');

if (elUsername) {
  elUsername.addEventListener('blur', function () {
    checkUsername(5);
  });
}

if (elPassword) elPassword.addEventListener('blur', checkUsername);
function checkUsername(minLength, elUsername, elMsg)
{ 
	// Get username input
	if (elUsername.value.length < minLength)
	{ // If username too short
		elMsg.innerHTML = 'Username must be 5 characters or more'; // Set msg
	}
else
	{ // Otherwise
	elMsg.innerHTML = ''; // Clear message
	}

}