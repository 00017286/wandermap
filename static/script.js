// Extract username from cookies
function getUsernameFromCookie() {
    const name = 'username=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return '';
}

// Get URL query parameter
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// Scroll to element with ID "target" if scrollToTarget=true in URL
if (getQueryParam("scrollToTarget") === "true") {
    const targetElement = document.getElementById("target");
    if (targetElement) {
        targetElement.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }
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

///////////////////////////////////////////////////////////////////////////////////////////////////////

// Photo gallery
let currentSlide = 0;

// Function to update slides
function updateSlides() {
    const slides = document.querySelectorAll('.slide'); // Get all slide elements
    const slidesContainer = document.querySelector('.slides'); // Get the container holding slides
    const galleryWidth = document.querySelector('.slides-container').clientWidth; // Get the width of the gallery container

    // Remove the "active" class from all slides and add it only to the current slide
    slides.forEach((slide, index) => {
        slide.classList.remove('active');
        if (index === currentSlide) {
            slide.classList.add('active');
        }
    });

    const slideWidth = slides[0].clientWidth + 20; // Calculate slide width, including margin
    const offset = -((currentSlide * slideWidth) - (galleryWidth - slideWidth) / 2); // Calculate offset to center the current slide
    slidesContainer.style.transform = `translateX(${offset}px)`; // Apply the offset transformation
}

// Function to move to the next slide
function nextSlide() {
    const slides = document.querySelectorAll('.slide');
    currentSlide = (currentSlide + 1) % slides.length; // Increase the slide index, loop back to the first slide if at the end
    updateSlides(); // Update slides
}

// Function to move to the previous slide
function prevSlide() {
    const slides = document.querySelectorAll('.slide');
    currentSlide = (currentSlide - 1 + slides.length) % slides.length; // Decrease the slide index, loop to the last slide if at the beginning
    updateSlides(); // Update slides
}

// Initial update of slides
updateSlides();

///////////////////////////////////////////////////////////////////////////////////////////////////////

document.addEventListener('DOMContentLoaded', function () {
    const subscribeBtn = document.getElementById("subscribe");
    const username = getUsernameFromCookie();

    fetch(`https://wandermap-1i48.onrender.com/check-subscription?username=${encodeURIComponent(username)}`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        if (data.subscription) {
            subscribeBtn.style.display = "none";
        }
    })
    .catch(error => {
        console.error("Error checking subscription:", error);
    });
});

// Pop-up for admins
document.addEventListener('DOMContentLoaded', function () {
    // Get elements from the page
    const adminBtn = document.getElementById("adminBtn"); // "For Admins" button
    const adminPopup = document.getElementById("adminPopup"); // The pop-up itself
    const closePopupBtn = document.getElementById("admin_closePopupBtn"); // Close button for the pop-up
    
    const submitBtn = document.getElementById("submitBtn"); // "Sign In" button

    // Show the pop-up when clicking on the "For Admins" button
    adminBtn.onclick = function (event) {
        event.preventDefault(); // Prevent default link behavior
        adminPopup.style.display = "flex"; // Show the pop-up
    };

    // Close the pop-up when clicking the close button
    closePopupBtn.onclick = function (event) {
        event.preventDefault(); // Prevent default action
        adminPopup.style.display = "none"; // Hide the pop-up
    };

    // Close the pop-up when clicking outside of it
    adminPopup.onclick = function (event) {
        if (event.target === adminPopup) {
            adminPopup.style.display = "none"; // Hide the pop-up
        }
    };

    // Click handler for the "Sign In" button inside the pop-up
    submitBtn.onclick = function (event) {
        event.preventDefault(); // Prevent default form submission behavior

        // Get form data
        const username = document.getElementById("admin_username").value;
        const password = document.getElementById("admin_password").value;

        // Send data to the server
        fetch('https://wandermap-1i48.onrender.com/admin-sign-in', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                admin_username: username,
                admin_password: password
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.userExists === true) {
                    // Redirect to admin_home.html
                    window.location.href = "/admin_home";
                } else {
                    // Show an error alert
                    showError("We don't have an admin with such credentials. Try another username or password.");
                }
            })
            .catch(error => {
                console.error("Error during admin sign-in:", error);
                showError("An error occurred. Please try again later.");
            });
    };
});

// User pop-up
document.addEventListener('DOMContentLoaded', function () {
    // Get elements from the page
    const signBtn = document.getElementById("signBtn"); // "Sign In" button
    const popup = document.getElementById("userSignInPopup"); // The pop-up itself
    const closePopupBtn = document.getElementById("closePopupBtn"); // Close button for the pop-up
    const submitBtn = document.getElementById("userSubmitBtn"); // "Sign In" button inside the pop-up
    const signUpBtn = document.getElementById("userSignUpBtn"); // "Sign Up" button
    const recoverBtn = document.getElementById("recoverBtn"); // "Recover" button

    // Show the pop-up when clicking on "Sign In"
    signBtn.onclick = function (event) {
        event.preventDefault(); // Prevent default link behavior
        popup.style.display = "flex"; // Display the pop-up
    };

    // Close the pop-up when clicking on the close button
    closePopupBtn.onclick = function (event) {
        event.preventDefault(); // Prevent accidental form submission
        popup.style.display = "none"; // Hide the pop-up
    };

    // Close the pop-up when clicking outside of it
    window.onclick = function (event) {
        if (event.target === popup) {
            popup.style.display = "none";
        }
    };

    // "Sign In" button click handler inside the pop-up
    submitBtn.onclick = function (event) {
        event.preventDefault(); // Prevent default form behavior

        // Get form data
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        // Send data to the server for authentication
        fetch('https://wandermap-1i48.onrender.com/user-sign-in', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.userExists === true) {
                // Redirect to the user's home page
                window.location.href = `/${data.username}?scrollToTarget=true`;
            } else if (data.userBlocked === true) {
                // Show warning message if the user is blocked
                showWarning("Sorry, your account is blocked by the administrator! Reach out to polinadolgopolova@gmail.com for more information");
            } else {
                // Show error message if credentials are incorrect
                showError("We don't have a traveller with such credentials. Try another username or password.");
            }
        })
        .catch(error => {
            console.error("Error during traveller sign-in:", error);
            showError("An error occurred. Please try again later.");
        });
    };

    // "Sign Up" button click handler
    signUpBtn.onclick = function (event) {
        event.preventDefault(); // Prevent default form behavior

        // Get form data
        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();

        // Send data to the server for user registration
        fetch('/user-sign-up', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: username, password: password })
        })
        .then(response => response.json()) // Parse JSON response
        .then(data => {
            if (data.noUsername) {
                showWarning("Specify a username for your account");
                return;
            }
            if (data.noPassword) {
                showWarning("Specify a password for your account");
                return;
            }
            if (data.userExists) {
                showWarning("A user with this username already exists. Try to sign in instead.");
                return;
            }
            if (data.userExists === false) {
                // Redirect to the user's profile if registration is successful
                window.location.href = `/${data.username}/my_profile`;
            }
        })
        .catch(error => {
            console.error("Error during traveller sign-up:", error);
            showError("An error occurred. Please try again later.");
        });
    };

    // "Recover Password" button click handler
    recoverBtn.onclick = function (event) {
        event.preventDefault(); // Prevent default form behavior

        // Get the username input
        const username = document.getElementById("username").value.trim();

        // Send recovery request to the server
        fetch('/recover-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: username })
        })
        .then(response => response.json()) // Parse JSON response
        .then(data => {
            if (data.userExists == false) {
                showWarning("We don't have a traveller with such a username. Try entering another one.");
                return;
            }
            if (data.hasEmail == false) {
                showWarning("You don’t have an email in your profile. Please, write to polinadolgopolova@gmail.com to restore your profile.");
                return;
            }
            if (data.sentEmail == false) {
                showWarning("Failed to send email. Try again later.");
                return;
            }
            if (data.sentEmail) {
                showAlert("Recovering email sent. Check your email inbox.");
                return;
            }
        })
        .catch(error => {
            console.error("Error during sending recovering email:", error);
            showError("An error occurred. Please try again later.");
        });
    }
});

// Pop-up for adding a new waypoint to the draft map
document.addEventListener("DOMContentLoaded", () => {

    // Get references to UI elements
    const popup = document.getElementById("addWaypointsPopup");
    const closePopup = document.getElementById("closePopup");
    const addWaypointBtn = document.getElementById("addWaypoint");
    const deleteDraftmapBtn = document.getElementById("deleteDraftmap");
    const waypointsList = document.getElementById("waypointsList");
    const newWaypointInput = document.getElementById("newWaypoint");
    const latitudeInput = document.getElementById("latitude");
    const longitudeInput = document.getElementById("longitude");
    const getCoordinatesBtn = document.getElementById("getCoordinates");
    const suggestionsList = document.getElementById("suggestionsList"); // Element for displaying address suggestions

    // Initialize Leaflet map
    let map = L.map('map').setView([52.3676, 4.9041], 15);
    let markersLayer = L.layerGroup().addTo(map);

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Dynamically retrieve username from cookies
    const username = getUsernameFromCookie();
    if (!username) {
        showError("User is not logged in.");
    }

    // Open the pop-up when "Add Waypoints" button is clicked
    document.getElementById("button-1").addEventListener("click", async () => {
        const response = await fetch("/draftmap", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username }),
        });

        if (response.ok) {
            const data = await response.json();
            waypointsList.innerHTML = "";
            markersLayer.clearLayers();

            // Populate the list with existing waypoints
            if (data.waypoints) {
                data.waypoints.forEach((wp) => {
                    const li = document.createElement("li");
                    li.textContent = `${wp.name} (${wp.latitude}, ${wp.longitude}) `;
                    waypointsList.appendChild(li);

                    L.marker([wp.latitude, wp.longitude]).addTo(markersLayer)
                        .bindPopup(`<b>${wp.name}</b><br>(${wp.latitude}, ${wp.longitude})`);
                });
            }

            popup.style.display = "flex";
        } else {
            showError("Failed to load waypoints.");
        }
    });

    // Close the pop-up when "X" button is clicked
    closePopup.addEventListener("click", () => {
        popup.style.display = "none";
    });

    // Close the pop-up when clicking outside of it
    popup.onclick = function (event) {
        if (event.target === popup) {
            popup.style.display = "none";
        }
    };

    // Add a new waypoint
    addWaypointBtn.addEventListener("click", async (event) => {
        event.preventDefault();

        const name = newWaypointInput.value.trim();
        const latitude = latitudeInput.value.trim();
        const longitude = longitudeInput.value.trim();

        if (!name) {
            showWarning("Enter a waypoint name!");
        }

        const response = await fetch("/add-waypoint", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username,
                name,
                latitude,
                longitude
            }),
        });

        if (response.ok) {
            const li = document.createElement("li");
            li.textContent = `${name} (${latitude}, ${longitude})`;
            waypointsList.prepend(li);

            L.marker([latitude, longitude]).addTo(markersLayer)
                .bindPopup(`<b>${name}</b><br>(${latitude}, ${longitude})`).openPopup();
        } else {
            showError("Failed to add waypoint");
            console.error("Failed to add waypoint", error);
        }
    });

    // Delete all waypoints from the draft map
    deleteDraftmapBtn.addEventListener("click", async (event) => {
        event.preventDefault();

        try {
            const response = await fetch("/delete-waypoints", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username }),
            });

            const data = await response.json();

            if (response.ok && data.success) {
                showAlert("Waypoints deleted successfully from your draft map");

                // Clear the waypoints list in the UI
                waypointsList.innerHTML = "";

                // Remove markers from the map
                markersLayer.clearLayers();
            } else {
                showError("Failed to delete waypoints");
                console.error("Failed to delete waypoints:", data.error);
            }
        } catch (error) {
            showError("An error occurred while deleting waypoints");
            console.error("Error deleting waypoints:", error);
        }

    });

    const GOOGLE_MAPS_API_KEY = "AIzaSyDn3JWKWIt2LewhXKSj98GoffxlmQvxUmQ";
    
    // Initialize Google Places Autocomplete
    const autocomplete = new google.maps.places.Autocomplete(newWaypointInput, {
        types: ["geocode"], // Restrict to address-based search
    });

    // Handle input event and fetch address suggestions
    newWaypointInput.addEventListener("input", async () => {
        const query = newWaypointInput.value.trim();
        if (!query) {
            suggestionsList.innerHTML = ''; // Clear the suggestion list if input is empty
            return;
        }

        try {
            // Fetch place predictions from Google Places API
            const service = new google.maps.places.AutocompleteService();
            service.getPlacePredictions({ input: query }, (predictions, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK && predictions) {
                    suggestionsList.innerHTML = ''; // Clear previous suggestions
                    // Limit the number of suggestions to 5
                    predictions.slice(0, 5).forEach(prediction => {
                        const li = document.createElement('li');
                        li.textContent = prediction.description;
                        li.addEventListener("click", () => {
                            newWaypointInput.value = prediction.description; // Fill input with selected address
                            suggestionsList.innerHTML = ''; // Clear suggestions after selection
                        });
                        suggestionsList.appendChild(li);
                    });
                } else {
                    suggestionsList.innerHTML = ''; // Clear list if no suggestions
                }
            });
        } catch (error) {
            console.error("Error fetching predictions:", error);
        }
    });

    // Handle address selection from autocomplete
    autocomplete.addListener("place_changed", function () {
        const place = autocomplete.getPlace();
        if (!place.geometry) {
            console.error("No details available for input: " + newWaypointInput.value);
            return;
        }

        // Get coordinates (latitude and longitude)
        const latitude = place.geometry.location.lat();
        const longitude = place.geometry.location.lng();

        console.log("Selected place:", {
            name: place.name,
            address: place.formatted_address,
            latitude: latitude,
            longitude: longitude,
        });
    });

    // Fetch coordinates from Google Maps API based on entered address
    getCoordinatesBtn.addEventListener("click", async (event) => {
        event.preventDefault();

        const address = newWaypointInput.value.trim();

        if (!address) {
            showWarning("Please enter an address.");
            return;
        }

        try {
            // Construct the API request URL
            const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(address)}&key=${GOOGLE_MAPS_API_KEY}`;
            
            // Send request
            const response = await fetch(url);
            const data = await response.json();

            if (data.status === "OK" && data.results.length > 0) {
                // Extract coordinates from response
                const { lat, lng } = data.results[0].geometry.location;

                // Fill coordinate input fields
                latitudeInput.value = lat.toFixed(6);
                longitudeInput.value = lng.toFixed(6);
            } else {
                showWarning("Address not found. Please try again.");
            }
        } catch (error) {
            console.error("Error fetching coordinates:", error);
            showError("Failed to fetch coordinates. Please check your connection and try again.");
        }
    });
});

// Pop-up for adding recommended waypoints to draftmap  
document.addEventListener("DOMContentLoaded", () => {  
    const popup = document.getElementById("recommendationsPopup"); // The pop-up window with recommendations  
    const closePopup = document.getElementById("closeRecommendationsPopup"); // Button to close the pop-up  
    const recommendationsList = document.getElementById("recommendedWaypointsList"); // List of recommended waypoints  
    const addChosenBtn = document.getElementById("addChosenWaypoints"); // Button to add selected waypoints  

    const username = getUsernameFromCookie(); // Retrieve the username from cookies  

    // Event handler for the "Observe Recommendations" button  
    document.getElementById("button-2").addEventListener("click", async () => {  
        // Show the preloader  
        document.getElementById('preloader').style.display = 'flex';  

        try {  
            // Send a request to get recommendations  
            const response = await fetch(`/recommendations?username=${username}`, {  
                method: "GET", // HTTP GET method  
                headers: { "Content-Type": "application/json" }, // Specify JSON data type  
            });  

            const data = await response.json(); // Convert the response to JSON  

            if (response.ok) {  
                // Check if there are waypoints available for recommendations  
                if (!data.hasWaypoints) {  
                    showWarning("Add waypoints to your map to get recommendations"); // Warning message if no waypoints  
                    return;  
                }  

                // Clear the recommendations list before displaying new data  
                recommendationsList.innerHTML = "";  
                data.recommendedWaypoints.forEach((wp) => {  
                    const div = document.createElement("div");  

                    div.innerHTML = `  
                        <input type="checkbox" id="wp-${wp.id}" name="waypoints" value="${wp.id}">  
                        <label for="wp-${wp.id}">${wp.name} (${wp.distance}km to ${wp.draftWaypointName})</label>  
                    `;  
                    recommendationsList.appendChild(div); // Add the new waypoint to the list  
                });  

                // Display the pop-up  
                popup.style.display = "flex";  
            } else {  
                // Show an error message if the server request fails  
                showError("Failed to fetch recommendations.");  
            }  
        } catch (error) {  
            // Log the error in the console and notify the user  
            console.error('Error fetching recommendations:', error);  
            showError("Error when fetching recommendations. Add more data on your profile!");  
        } finally {  
            // Hide the preloader after the request is completed  
            document.getElementById('preloader').style.display = 'none';  
        }  
    });  

    // Handle closing the pop-up  
    closePopup.addEventListener("click", () => {  
        popup.style.display = "none";  
    });  

    // Close the pop-up when clicking outside of it  
    popup.onclick = function (event) {  
        if (event.target === popup) {  
            popup.style.display = "none";  
        }  
    };  

    // Handle adding selected waypoints to the map  
    addChosenBtn.addEventListener("click", async (event) => {  
        event.preventDefault();  

        // Get the list of selected waypoints  
        const selectedWaypoints = Array.from(  
            document.querySelectorAll("input[name='waypoints']:checked")  
        ).map((checkbox) => checkbox.value);  

        // Check if any waypoints were selected  
        if (selectedWaypoints.length === 0) {  
            showWarning("Choose recommended waypoints to add"); // Warning if no waypoints are selected  
            return;  
        }  

        // Send the selected waypoints to the server  
        const response = await fetch("/add-chosen-waypoints", {  
            method: "POST", // HTTP POST method  
            headers: { "Content-Type": "application/json" }, // Specify JSON data type  
            body: JSON.stringify({ username, waypoints: selectedWaypoints }), // Send data  
        });  

        if (response.ok) {  
            showAlert("Waypoints successfully added to your map."); // Show success message  
            popup.style.display = "none"; // Close the pop-up  
        } else {  
            showError("Failed to add chosen waypoints"); // Show error message  
        }  
    });  
});  

// Initialize SortableJS for reordering waypoints in the list
Sortable.create(document.getElementById('waypointsOrderList'), {
    animation: 150,
});

// Pop-up for setting the order of waypoints in draftmap
document.addEventListener("DOMContentLoaded", () => {
    const waypointsOrderPopup = document.getElementById("waypointsOrderPopup"); // Pop-up element
    const closeWaypointsOrderPopup = document.getElementById("closeWaypointsOrderPopup"); // Close button
    const waypointsOrderList = document.getElementById("waypointsOrderList"); // List of waypoints
    const setWaypointsOrderBtn = document.getElementById("setWaypointsOrder"); // Button to save the order
    const username = getUsernameFromCookie(); // Retrieve username from cookies

    // Event listener for the button with id="button-3"
    document.getElementById("button-3").addEventListener("click", async () => {
        // Show preloader while loading data
        document.getElementById('preloader').style.display = 'flex';

        try {
            // API call to fetch waypoints for the user
            const response = await fetch(`/waypoints?username=${username}`, {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            });

            const data = await response.json(); // Convert response to JSON

            if (response.ok) {
                // Ensure there are at least two waypoints to proceed
                if (!data.waypoints || data.waypoints.length < 2) {
                    showWarning("Need at least two waypoints to calculate the route");
                    return;
                }

                // Clear the list before adding new waypoints
                waypointsOrderList.innerHTML = "";
                data.waypoints.forEach((wp) => {
                    const li = document.createElement("li"); // Create a list item
                    li.setAttribute('data-id', wp.id); // Store waypoint ID as an attribute
                    li.textContent = `${wp.name} (${wp.latitude}, ${wp.longitude})`; // Display waypoint name and coordinates
                    waypointsOrderList.appendChild(li); // Add item to the list
                });

                // Show the pop-up
                waypointsOrderPopup.style.display = "flex";

                // Initialize SortableJS to allow reordering of waypoints
                Sortable.create(waypointsOrderList, {
                    animation: 150,
                    onEnd: () => { // Event triggered when dragging ends
                        console.log("Order changed!");
                    },
                });
            } else {
                showError("Failed to fetch waypoints."); // Display error if request fails
            }
        } catch (error) {
            console.error('Error fetching waypoints:', error); // Log error to console
            document.getElementById('preloader').style.display = 'none'; // Hide preloader on error
            showError("Error fetching waypoints"); // Show error message to user
        } finally {
            // Hide preloader after request completes
            document.getElementById('preloader').style.display = 'none';
        }
    });

    // Close pop-up when the close button is clicked
    closeWaypointsOrderPopup.addEventListener("click", () => {
        waypointsOrderPopup.style.display = "none";
    });

    // Close pop-up when clicking outside of it
    waypointsOrderPopup.onclick = function (event) {
        if (event.target === waypointsOrderPopup) {
            waypointsOrderPopup.style.display = "none";
        }
    };

    // Handle waypoint order update and send data to the server
    setWaypointsOrderBtn.addEventListener("click", async (event) => {
        event.preventDefault(); // Prevent default button behavior

        // Retrieve the updated order of waypoints
        const updatedWaypoints = [];
        Array.from(waypointsOrderList.children).forEach((li, index) => {
            updatedWaypoints.push({
                id: li.getAttribute("data-id"), // Waypoint ID
                setWaypointOrder: index + 1, // New order index
            });
        });

        // Send the updated order to the server
        const response = await fetch("/set-waypoints-order", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, waypoints: updatedWaypoints }),
        });

        if (response.ok) {
            showAlert("Waypoints order updated successfully."); // Show success message
        } else {
            showError("Failed to update waypoints order."); // Show error message
        }
    });
});
// Popup for adding map description
document.addEventListener("DOMContentLoaded", async () => {
    const elements = {
        popup: document.getElementById("waypointPopup"),
        closePopup: document.getElementById("closeDescriptionPopup"),
        waypointSelect: document.getElementById("waypointSelect"),
        mapDescription: document.getElementById("mapDescription"),
        waypointDescription: document.getElementById("waypointDescription"),
        imageUpload: document.getElementById("imageUpload"),
        imageList: document.getElementById("imageList"),
        saveWaypoint: document.getElementById("saveWaypoint"),
    };

    const username = getUsernameFromCookie();
    let waypoints = [];

    // Fetch draft map data from the server
    async function fetchDraftMap() {
        try {
            const response = await fetch(`/get-draft-map?username=${username}`);
            const data = await response.json();

            if (data) {
                elements.mapDescription.value = data.description || "";
                waypoints = data.waypoints || [];
                
                // Populate waypoint dropdown
                elements.waypointSelect.innerHTML = waypoints.map((wp) =>
                    `<option value="${wp.id}">${wp.name}</option>`
                ).join("");
                
                // Load the first waypoint data if available
                if (waypoints.length) loadWaypointData(waypoints[0]);
            }
        } catch (error) {
            console.error("Error fetching draft map:", error);
        }
    }

    // Load waypoint details into the UI
    function loadWaypointData(waypoint) {
        elements.waypointDescription.value = waypoint.description || "";
        elements.imageList.innerHTML = (waypoint.images || []).map((img) =>
            createImageElement(`/static/images/waypoints/${img}`, img, waypoint.id)
        ).join("");
    }

    // Create an image element with a delete button
    function createImageElement(src, imageName, waypointId) {
        return `<div class="image-container">
                    <img src="${src}" alt="Waypoint Image" class="waypoint-image">
                    <div class="delete-button" onclick="removeImage('${imageName}', '${waypointId}')">✖</div>
                </div>`;
    }

    // Remove an image from the waypoint
    window.removeImage = async function (imageName, waypointId) {
        try {
            const response = await fetch("/remove-draft-waypoint-image", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: username,
                    waypointId: waypointId,
                    imageName: imageName
                }),
            });
    
            if (response.ok) {
                const currentWaypointId = elements.waypointSelect.value; // Remember the current selection
                await fetchDraftMap(); // Refresh waypoints data
    
                // Restore selection after data refresh
                elements.waypointSelect.value = currentWaypointId;
                
                // Reload the selected waypoint data
                const selectedWaypoint = waypoints.find(wp => wp.id == currentWaypointId);
                if (selectedWaypoint) {
                    loadWaypointData(selectedWaypoint);
                }
            } else {
                showError("Failed to delete image");
            }
        } catch (error) {
            showError("Request error");
        }
    };

    // Handle waypoint selection change
    elements.waypointSelect.addEventListener("change", () => {
        const selectedWaypoint = waypoints.find(wp => wp.id == elements.waypointSelect.value);
        if (selectedWaypoint) loadWaypointData(selectedWaypoint);
    });

    // Handle image upload
    elements.imageUpload.addEventListener("change", async () => {
        const selectedWaypointId = elements.waypointSelect.value;
        if (!selectedWaypointId) return;

        const selectedWaypoint = waypoints.find(wp => wp.id == selectedWaypointId);
        if (!selectedWaypoint) return;

        const formData = new FormData();
        formData.append("username", username);
        formData.append("waypointId", selectedWaypointId);
        
        for (const file of elements.imageUpload.files) {
            formData.append("images", file);
        }

        try {
            const response = await fetch("/upload-draft-waypoint-image", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                selectedWaypoint.images = result.images;
                loadWaypointData(selectedWaypoint);
            } else {
                showError("Failed to upload image");
            }
        } catch (error) {
            showError("Request error");
        }

        elements.imageUpload.value = "";
    });

    // Save waypoint details
    elements.saveWaypoint.addEventListener("click", async () => {
        const selectedWaypointId = elements.waypointSelect.value;
        if (!selectedWaypointId) return;

        const selectedWaypoint = waypoints.find(wp => wp.id == selectedWaypointId);
        if (!selectedWaypoint) return;

        const response = await fetch("/save-draft-waypoint", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: username,
                waypointId: selectedWaypointId,
                mapDescription: elements.mapDescription.value,
                waypointDescription: elements.waypointDescription.value
            }),
        });

        if (response.ok) {
            showAlert("Saved successfully!");
        } else {
            showError("Failed to save.");
        }
    });

    // Open popup and fetch data
    document.getElementById("button-4").addEventListener("click", async () => {
        console.log("Opening popup, fetching data...");
        await fetchDraftMap();
        elements.popup.style.display = "flex";
    });

    // Close popup event handlers
    elements.closePopup.addEventListener("click", () => { elements.popup.style.display = "none"; });
    elements.popup.addEventListener("click", (event) => { if (event.target === elements.popup) elements.popup.style.display = "none"; });
});

// Map save confirmation popup handling
document.addEventListener("DOMContentLoaded", () => {
    const saveMapButton = document.getElementById("button-5"); // Map save button
    const confirmationPopup = document.getElementById("confirmationPopup");
    const confirmYesButton = document.getElementById("confirmYes");
    const confirmNoButton = document.getElementById("confirmNo");
    const closePopupButton = document.getElementById("closePopup");

    // Show confirmation popup on save button click
    saveMapButton.addEventListener("click", async () => {
        confirmationPopup.style.display = "flex";
    });

    // Handle "Yes" click (saving the map)
    confirmYesButton.addEventListener("click", async () => {
        const username = getUsernameFromCookie(); // Get username from cookies

        try {
            const response = await fetch("/map", {
                method: "POST", 
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username })
            });

            const data = await response.json();

            if (response.ok) {
                if (data.hasWaypoints === false) {
                    showWarning("To save your map, add at least one waypoint.");
                } else if (data.hasWaypoints === true) {
                    showAlert("Your map is saved! You can edit it on the 'My maps' page.");
                }
            } else {
                showError("An error occurred while saving your map. Please try again later.");
            }
        } catch (error) {
            console.error("Error saving map:", error);
            showError("An error occurred. Please check your connection and try again.");
        }

        // Close the popup after saving
        confirmationPopup.style.display = "none";
    });

    // Handle "No" click (close popup without saving)
    confirmNoButton.addEventListener("click", () => {
        confirmationPopup.style.display = "none";
    });

    // Close popup when clicking outside
    confirmationPopup.onclick = function (event) {
        if (event.target === confirmationPopup) {
            confirmationPopup.style.display = "none";
        }
    };

    // Close popup on close button click
    closePopupButton.addEventListener("click", () => {
        confirmationPopup.style.display = "none";
    });

    // Subscribe
    const subscribeBtn = document.getElementById("subscribe");

    subscribeBtn.addEventListener("click", async () => {
        window.location.href = `/${encodeURIComponent(getUsernameFromCookie())}/my_profile?scrollToSubscription=true`;
        return;
    });
});
