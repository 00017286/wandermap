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

function searchMaps() {
    const searchText = document.getElementById("search-input").value.toLowerCase();
    const maps = document.querySelectorAll(".map-item");

    maps.forEach(map => {
        const description = map.querySelector("h2").textContent.toLowerCase();
        if (description.includes(searchText)) {
            map.style.display = "block"; // Show the map if it matches the search
        } else {
            map.style.display = "none"; // Hide the map if it doesn't match
        }
    });
}

///////////////////////////////////////////////////////////////////////////////////////////////////////

// Function to fetch user's maps
function fetchMaps(username) {
    return fetch(`/all-maps?username=${encodeURIComponent(username)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const mapList = document.getElementById("mapList");
            mapList.innerHTML = "";

            // Если карт нет, показываем сообщение
            if (!data.maps || data.maps.length === 0) {
                mapList.innerHTML += "<p>No maps found. Start by creating a new one!</p>";
                return;
            }

            // Получаем текущую опцию сортировки
            const sortOption = document.getElementById("sortOptions").value;

            // Сортировка карт по рейтингу
            if (sortOption === "rating-desc") {
                data.maps.sort((a, b) => (b.rating || 0) - (a.rating || 0));
            } else if (sortOption === "rating-asc") {
                data.maps.sort((a, b) => (a.rating || 0) - (b.rating || 0));
            }

            // Отображаем карты
            data.maps.forEach(map => {
                const mapElement = document.createElement("div");
                mapElement.classList.add("map-item");

                const waypointImages = document.createElement("div");
                waypointImages.classList.add("waypoint-images");

                map.waypoints.forEach(waypoint => {
                    if (!waypoint.images || waypoint.images.length === 0) return;

                    waypoint.images.forEach(imageName => {
                        const img = document.createElement("img");
                        img.src = `/static/images/waypoints/${imageName.trim()}`;
                        img.alt = "Waypoint Image";
                        img.classList.add("waypoint-img");
                        waypointImages.appendChild(img);
                    });
                });

                const viewMapButton = document.createElement("a");
                viewMapButton.classList.add("view-map");
                viewMapButton.textContent = "View Map";
                viewMapButton.setAttribute("data-map-id", map.id);

                mapElement.innerHTML = `
                    <h2>${map.description || "Unnamed Map"}</h2>
                    <h3>
                        ${map.rating 
                            ? `<img src="/static/images/rating/star.png" alt="Star" class="rating-icon"> Rating: ${map.rating.toFixed(1)} (${map.reviewsNumber} rated)`  
                            : `No rating yet`
                        }
                    </h3>
                `;

                mapElement.appendChild(viewMapButton);
                mapElement.appendChild(waypointImages);
                mapList.appendChild(mapElement);
            });

            // Если подписка отключена и пришло ограниченное число карт
            if (data.subscription === false) {
                const subscriptionBlock = document.createElement("div");
                subscriptionBlock.id = "subscriptionBlock";
                subscriptionBlock.style.textAlign = "center"; // Центрируем кнопку

                const subscribeButton = document.createElement("button");
                subscribeButton.id = "subscribeToViewAllMaps";
                subscribeButton.type = "button";
                subscribeButton.textContent = "Subscribe on WanderMap to view all maps!";
                subscribeButton.onclick = () => {
                    window.location.href = `/${encodeURIComponent(username)}/my_profile?scrollToSubscription=true`;
                };

                subscriptionBlock.appendChild(subscribeButton);
                mapList.appendChild(subscriptionBlock);
            }
        })
        .catch(error => {
            console.error("Error fetching maps:", error);
            document.getElementById("mapList").innerHTML = "<p>Failed to load maps. Please try again later.</p>";
        });
}

// Load maps after the page is fully loaded
window.onload = () => {
    const username = getUsernameFromCookie();

    if (!username) {
        username = 'unauthorized';
    }

    // Fetch maps and apply search filter after loading
    fetchMaps(username).then(() => {
        searchMaps();
    });
    
};

///////////////////////////////////////////////////////////////////////////////////////////////////////

// Popup for viewing the map
document.addEventListener("DOMContentLoaded", async () => {
    
    // Get references to popup elements and form controls
    const elements = {
        popup: document.getElementById("viewMapPopup"), // Popup container   
        closePopup: document.getElementById("viewClosePopup"), // Close button
        waypointSelect: document.getElementById("viewWaypointSelect"), // Dropdown for waypoints
        mapTitle: document.getElementById("viewMapTitle"), // Map title field
        waypointDescription: document.getElementById("viewWaypointDescription"), // Waypoint description field
        imageList: document.getElementById("viewImageList"), // Container for uploaded images

        ratingPopup: document.getElementById("ratingPopup"), // Rating popup
        fullMapPopup: document.getElementById("fullMapPopup"), // Full map popup
        mapIcon: document.getElementById("mapIcon"), // Icon to open map popup
        reviewIcon: document.getElementById("reviewIcon"), // Icon to open review popup
        reviewPopup: document.getElementById("reviewPopup"), // Review popup container
        reviewTextarea: document.getElementById("reviewDescription"), // Textarea for user review
        saveReviewButton: document.getElementById("saveReview"), // Button to save review
    };

    const username = getUsernameFromCookie(); // Retrieve username from cookies

    let map;
    let markersLayer;

    // Initialize the map on page load
    if (document.getElementById("fullMapContainer")) {
        map = L.map('fullMapContainer').setView([52.3676, 4.9041], 10);
        markersLayer = L.layerGroup().addTo(map); // Initialize marker layer

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);

        // Hide the container initially
        document.getElementById("fullMapContainer").style.display = "none";
    } else {
        console.error("Map element not found!");
    }

    // Event handler for map icon click
    elements.mapIcon.addEventListener("click", async () => {
        const mapId = document.getElementById("viewMapPopup").getAttribute("data-map-id");

        const response = await fetch(`/get-map?mapId=${encodeURIComponent(mapId)}&username=${encodeURIComponent(username)}`);
        const data = await response.json();

        if (!data || !data.waypoints) {
            console.error("Error: No waypoints found");
            return;
        }

        markersLayer.clearLayers(); // Clear existing markers

        const bounds = L.latLngBounds(); // Create bounds for auto-centering

        data.waypoints.forEach((wp) => {
            const marker = L.marker([wp.latitude, wp.longitude])
                .addTo(markersLayer)
                .bindPopup(`<b>${wp.name}</b><br>(${wp.latitude}, ${wp.longitude})`);

            bounds.extend(marker.getLatLng()); // Extend bounds with marker coordinates
        });

        if (bounds.isValid()) { 
            map.fitBounds(bounds, { padding: [50, 50] }); // Adjust map view to fit markers
        }

        // Show the map container before displaying the popup
        document.getElementById("fullMapContainer").style.display = "block";

        setTimeout(() => {
            map.invalidateSize(); // Refresh map size to fit container
            if (bounds.isValid()) {
                map.fitBounds(bounds, { padding: [50, 50] });
            }
        }, 300);
        
        elements.fullMapPopup.style.display = "flex";
    });

    // Close popup when clicking outside
    elements.fullMapPopup.onclick = function (event) {
        if (event.target === elements.fullMapPopup) {
            elements.fullMapPopup.style.display = "none";
        }
    };

    // Event handler for review icon click
    elements.reviewIcon.addEventListener("click", async () => {
        const mapId = document.getElementById("viewMapPopup").getAttribute("data-map-id");

        // Получаем статус подписки
        const response1 = await fetch(`/get-map?mapId=${encodeURIComponent(mapId)}&username=${encodeURIComponent(username)}`);
        if (!response1.ok) {
            alert("Failed to get map details!");
            return;
        }
        const data1 = await response1.json();
        if (data1.subscription === false) {
            // Если подписка неактивна, переводим на страницу профиля для оформления подписки
            window.location.href = `/${encodeURIComponent(username)}/my_profile?scrollToSubscription=true`;
            return;
        }

        const response = await fetch(`/get-review?mapId=${encodeURIComponent(mapId)}&username=${encodeURIComponent(username)}`);
        const data = await response.json();

        // Populate textarea with user's review
        elements.reviewTextarea.value = data.review || "";

        // Populate the reviews list from other users
        const otherReviewsList = document.getElementById("otherReviewsList");
        const noReviewsText = document.getElementById("noReviewsText");

        otherReviewsList.innerHTML = ""; // Clear the list before inserting new items

        if (data.reviews.length > 0) {
            noReviewsText.style.display = "none"; // Hide "No reviews yet" text
            data.reviews.forEach(review => {
                const li = document.createElement("li");
                li.innerHTML = `<strong>${review.username}:</strong> ${review.description}`;
                otherReviewsList.appendChild(li);
            });
        } else {
            noReviewsText.style.display = "block"; // Show "No reviews yet" text
        }
        
        elements.reviewPopup.style.display = "flex";
    });

    // Close review popup when clicking outside
    elements.reviewPopup.onclick = function (event) {
        if (event.target === elements.reviewPopup) {
            elements.reviewPopup.style.display = "none";
        }
    };

    // Event handler for saving a review
    elements.saveReviewButton.addEventListener("click", async (event) => {
        event.preventDefault();

        const mapId = document.getElementById("viewMapPopup").getAttribute("data-map-id");
        const reviewText = elements.reviewTextarea.value;

        if (!reviewText){
            showWarning("Add text to save review");
            return;
        }
        
        const response = await fetch("/review", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                mapId: mapId,
                username: username,
                review: reviewText
            })
        });

        const result = await response.json();
        if (result.status === "success") {
            showAlert("Review saved!");
        } else {
            showError("Couldn't save review. Try again later");
        }
    });

    let stars = []; // Declare stars globally inside DOMContentLoaded
    if (!ratingPopup) {
        console.error("Error: ratingPopup element not found in DOM.");
    } else {
        stars = elements.ratingPopup.querySelectorAll(".star"); // Assign value to the global variable
    }

    // Function to update star ratings visually
    function updateStars(rating) {
        stars.forEach(star => {
            star.classList.toggle("active", star.dataset.value <= rating);
        });
    }

    // Function to send the rating to the server
    async function sendRating(mapId, rating) {
        try {
            const response = await fetch("/rate-map", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, mapId, rating })
            });

            if (!response.ok) throw new Error("Error saving rating");
        } catch (error) {
            showError("Couldn't save your rating. Try again later");
        }
    }

    // Add event listeners to stars
    stars.forEach(star => {
        star.addEventListener("click", async () => {
            const rating = star.dataset.value;
            const mapId = document.getElementById("viewMapPopup").getAttribute("data-map-id");
            updateStars(rating);
            await sendRating(mapId, rating);
        });
    });

    // Function to fetch the user's map from the server
    async function fetchMap(mapId) {
        try {
            const response = await fetch(`/get-map?mapId=${encodeURIComponent(mapId)}&username=${encodeURIComponent(username)}`);
            const data = await response.json();
            updateStars(data.rating);

            if (data) {
                elements.mapTitle.textContent = data.description || "No description available";
                waypoints = data.waypoints || [];

                elements.waypointSelect.innerHTML = waypoints.map((wp) =>
                    `<option value="${wp.id}">${wp.name}</option>`
                ).join("");

                if (waypoints.length) loadWaypointData(waypoints[0]);
            }
        } catch (error) {
            console.error("Failed to get map", error);
        }
    }

    // Function to load waypoint data
    function loadWaypointData(waypoint) {
        elements.waypointDescription.innerHTML = waypoint.description 
            ? waypoint.description.replace(/\n/g, "<br>") 
            : "No description available";
        elements.imageList.innerHTML = (waypoint.images || []).map((img) =>
            `<div class="image-container">
                <img src="/static/images/waypoints/${img}" alt="Waypoint Image" class="view-waypoint-image">
            </div>`
        ).join("");
    }

    if (elements.waypointSelect) {
        elements.waypointSelect.addEventListener("change", async () => {
            const waypointId = elements.waypointSelect.value;
            const mapId = document.getElementById("viewMapPopup").getAttribute("data-map-id");
            
            try {
                const response = await fetch(`/get-waypoint?waypointId=${encodeURIComponent(waypointId)}&mapId=${encodeURIComponent(mapId)}`);
                const waypoint = await response.json();
                if (waypoint) loadWaypointData(waypoint);
            } catch (error) {
                console.error("Ошибка загрузки точки маршрута:", error);
            }
        });
    }

    // Handler for opening the pop-up when clicking the button
    document.getElementById("mapList").addEventListener("click", async (event) => {
        if (event.target.classList.contains("view-map")) { // Check if the click was on the "View Map" button
            const mapId = event.target.getAttribute("data-map-id"); // Get the map ID from the data-map-id attribute
            document.getElementById("viewMapPopup").setAttribute("data-map-id", mapId);

            if (!mapId) {
                showError("Map not found");
                return;
            }

            await fetchMap(mapId); // Pass mapId to the data loading function
            elements.popup.style.display = "flex";
            elements.ratingPopup.style.display = "flex";
            elements.mapIcon.style.display = "flex";
            elements.reviewIcon.style.display = "flex";
        }
    });

    document.getElementById("sortOptions").addEventListener("change", () => {
        if (username) {
            fetchMaps(username);
        }
    });

    const scrollToTopButton = document.getElementById("scrollToTop");
    // Show the button when the user scrolls down
    window.addEventListener("scroll", function () {
        if (window.scrollY > 300) {
            scrollToTopButton.style.display = "block";
        } else {
            scrollToTopButton.style.display = "none";
        }
    });
    // Smoothly scroll the page up when clicking the button
    scrollToTopButton.addEventListener("click", function () {
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    });

    // Handler for closing the pop-up
    elements.closePopup.addEventListener("click", () => {
        elements.popup.style.display = "none";
        elements.ratingPopup.style.display = "none";
        elements.mapIcon.style.display = "none";
        elements.reviewIcon.style.display = "none";
    });
    // Close the pop-up when clicking outside of it
    elements.popup.onclick = function (event) {
        if (event.target === elements.popup) {
            elements.popup.style.display = "none";
            elements.ratingPopup.style.display = "none";
            elements.mapIcon.style.display = "none";
            elements.reviewIcon.style.display = "none";
        }
    };

});