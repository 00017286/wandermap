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
                }, 500); // Ждём 500 мс на случай отложенной загрузки блока
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
    subscribeBtn.addEventListener("click", async () => {
        window.location.href = `/${encodeURIComponent(username)}/my_profile?scrollToSubscription=true`;
        return;
    });

    document.getElementById("subscribe-button").addEventListener("click", function () {
        fetch("/create-checkout-session", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username: username })
         })
        .then(response => response.json())
        .then(session => {
            window.location.href = session.url; // Перенаправляем пользователя на Stripe Checkout
        })
        .catch(error => console.error("Error:", error));
    });

    document.addEventListener("DOMContentLoaded", () => {
    const unsubscribeBtn = document.getElementById("unsubscribe-button");

    if (!unsubscribeBtn) {
        console.error("Unsubscribe button not found!");
        return;
    }

    console.log("Unsubscribe button found!");

    unsubscribeBtn.addEventListener("click", () => {
        console.log("Unsubscribe button clicked!"); // Проверяем, сработал ли клик

        const username = getUsernameFromCookie();
        console.log("Username:", username);

        fetch("/unsubscribe", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: username }),
        })
        .then(response => response.json())
        .then(data => {
            console.log("Response:", data);
            alert(data.message);
        })
        .catch(error => console.error("Error:", error));
    });
});

};
