// Extract username from cookies
function getUsernameFromCookie() {
    const name = 'username=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') { // Remove leading spaces
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) { // Return the cookie value if found
            return c.substring(name.length, c.length);
        }
    }
    return ''; // Return an empty string if not found
}
// Function to display success notifications
function showAlert(message) {
    var alertElement = document.createElement('div');
    alertElement.classList.add('alert');
    alertElement.textContent = message;
    document.body.appendChild(alertElement);

    setTimeout(function() {
        alertElement.classList.add('show'); // Show animation
    }, 10);

    setTimeout(function() {
        alertElement.classList.remove('show');
        alertElement.classList.add('hide');

        setTimeout(function() {
            alertElement.remove(); // Remove notification from DOM
        }, 500);
    }, 4000); // Display duration
}
// Function to display warning notifications
function showWarning(message) {
    var alertElement = document.createElement('div');
    alertElement.classList.add('warning');
    alertElement.textContent = message;
    document.body.appendChild(alertElement);

    setTimeout(function() {
        alertElement.classList.add('show');
    }, 10);

    setTimeout(function() {
        alertElement.classList.remove('show');
        alertElement.classList.add('hide');

        setTimeout(function() {
            alertElement.remove();
        }, 500);
    }, 4000);
}
// Function to display error notifications
function showError(message) {
    var alertElement = document.createElement('div');
    alertElement.classList.add('error');
    alertElement.textContent = message;
    document.body.appendChild(alertElement);

    setTimeout(function() {
        alertElement.classList.add('show');
    }, 10);

    setTimeout(function() {
        alertElement.classList.remove('show');
        alertElement.classList.add('hide');

        setTimeout(function() {
            alertElement.remove();
        }, 500);
    }, 4000);
}

document.addEventListener("DOMContentLoaded", () => {
    function scrollToSubscription() {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get("scrollToSubscription") === "true") {
            const subscribeElement = document.getElementById("saveChanges");
            if (subscribeElement) {
                setTimeout(() => {
                    subscribeElement.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
                }, 500); // Waiting for 500 ms in case of delayed block loading
            }
        }
    }

    scrollToSubscription();
});


///////////////////////////////////////////////////////////////////////////////////////////////////////

// Event handler for the "Save Changes" button on the profile page
window.onload = () => {

    // Get the "Save Changes" button element
    const saveChangesBtn = document.getElementById("saveChanges");
    
    // Retrieve the username from the cookie
    const username = getUsernameFromCookie();

    // Add a click event listener to the "Save Changes" button
    saveChangesBtn.addEventListener("click", async (event) => {
        event.preventDefault(); // Prevent the default form submission behavior

        // Collect user input values from the form fields
        const formData = {
            userName: username,
            email: document.getElementById("email").value,
            name: document.getElementById("name").value,
            surname: document.getElementById("surname").value,
            dateOfBirth: document.getElementById("dateOfBirth").value,
            gender: document.getElementById("gender").value,
            maritalState: document.getElementById("maritalState").value,
            hasKids: document.getElementById("hasKids").checked,
            hasPets: document.getElementById("hasPets").checked,
            extrovert: document.getElementById("extrovert").checked,
            natureLover: document.getElementById("natureLover").checked,
            museumLover: document.getElementById("museumLover").checked,
            sportLover: document.getElementById("sportLover").checked
        };

        try {
            // Send the form data to the server using a POST request
            const response = await fetch("/update-profile", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData),
                cache: "no-cache",
            });

            // Check if the response is successful
            if (!response.ok) throw new Error("Failed to update profile");

            // Show success message
            showAlert("Profile updated successfully");
        } catch (error) {
            // Show error message and log the error
            showError("Failed to update profile");
            console.error("Error:", error);
        }
    });
    
    // Subscribe
    const subscribeBtn = document.getElementById("subscribe");
    if (subscribeBtn) {
        subscribeBtn.addEventListener("click", async () => {
            window.location.href = `/${encodeURIComponent(username)}/my_profile?scrollToSubscription=true`;
        });
    }

    const stripeBtn = document.getElementById("subscribe-button");
    if (stripeBtn) {
        stripeBtn.addEventListener("click", function () {
            fetch("/create-checkout-session", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ username: username })
            })
            .then(response => response.json())
            .then(session => {
                window.location.href = session.url;
            })
            .catch(error => console.error("Error:", error));
        });
    }

    const unsubscribeBtn = document.getElementById("unsubscribe-button");
    if (unsubscribeBtn) {
        unsubscribeBtn.addEventListener("click", function () {
            fetch("/unsubscribe", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username: username }),
            })
            .then(response => response.json())
            .then(data => {
                showAlert(data.message);
            })
            .catch(error => console.error("Error:", error));
        });
    } 
};
