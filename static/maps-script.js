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

///////////////////////////////////////////////////////////////////////////////////////////////////////

// Function to load user maps
function fetchMaps(username) {
    if (!username) {
        showError("User is not logged in.");
        return;
    }

    fetch(`/maps?username=${encodeURIComponent(username)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const mapList = document.getElementById("mapList");
            mapList.innerHTML = "";

            if (!data.maps || data.maps.length === 0) {
                mapList.innerHTML = "<p>No maps found. Start by creating a new one!</p>";
                return;
            }

            data.maps.forEach(map => {
                const mapElement = document.createElement("div");
                mapElement.classList.add("map-item");

                // Container for waypoint images
                const waypointImages = document.createElement("div");
                waypointImages.classList.add("waypoint-images");

                map.waypoints.forEach(waypoint => {
                    if (!waypoint.images || waypoint.images.length === 0) return; // Skip if no images

                    waypoint.images.forEach(imageName => {
                        const img = document.createElement("img");
                        img.src = `/static/images/waypoints/${imageName.trim()}`;
                        img.alt = "Waypoint Image";
                        img.classList.add("waypoint-img");
                        waypointImages.appendChild(img);
                    });
                });

                // Create a button with data-map-id
                const viewMapButton = document.createElement("a");
                viewMapButton.classList.add("view-map");
                viewMapButton.textContent = "View Map";
                viewMapButton.setAttribute("data-map-id", map.id); // Add an attribute with the map ID

                // Fill in the HTML for the map card
                mapElement.innerHTML = `
                    <h2>${map.description || "Unnamed Map"}</h2>
                    <h3>
                        ${map.rating 
                            ? `<img src="/static/images/rating/star.png" alt="Star" class="rating-icon"> Rating: ${map.rating.toFixed(1)}` 
                            : `No rating yet`
                        }
                    </h3>
                `;

                mapElement.appendChild(viewMapButton);
                mapElement.appendChild(waypointImages);
                mapList.appendChild(mapElement);
            });
        })
        .catch(error => {
            console.error("Error fetching maps:", error);
            document.getElementById("mapList").innerHTML = "<p>Failed to load maps. Please try again later.</p>";
        });
}

// Load maps after the page has fully loaded
window.onload = () => {
    const username = getUsernameFromCookie();

    if (!username) {
        showError("User is not logged in");
        return;
    }

    fetchMaps(username);
};

///////////////////////////////////////////////////////////////////////////////////////////////////////

// Popup for adding map description
document.addEventListener("DOMContentLoaded", async () => {
    
    // Get references to popup and form elements
    const elements = {
        popup: document.getElementById("editWaypointPopup"), // Popup container
        closePopup: document.getElementById("closeEditDescriptionPopup"), // Close button
        waypointSelect: document.getElementById("editWaypointSelect"), // Dropdown list for waypoints
        mapDescription: document.getElementById("mapEditDescription"), // Map description input field
        waypointDescription: document.getElementById("editWaypointDescription"), // Waypoint description input field
        imageUpload: document.getElementById("editImageUpload"), // Image upload field
        imageList: document.getElementById("editImageList"), // Container for uploaded images
        saveWaypoint: document.getElementById("saveEditWaypoint"), // Save waypoint button
        pdfIcon: document.getElementById("pdfIcon")
    };

    const subscribeBtn = document.getElementById("subscribe");

    let waypoints = []; // Store waypoints

    // Function to load user's map from the server
    async function fetchMap(mapId) {
        try {
            const response = await fetch(`/get-map?mapId=${encodeURIComponent(mapId)}`);
            const data = await response.json();
    
            if (data) {
                selectedMapId = mapId;
                elements.mapDescription.value = data.description || "";
                waypoints = data.waypoints || [];
    
                elements.waypointSelect.innerHTML = waypoints.map((wp) =>
                    `<option value="${wp.id}">${wp.name}</option>`
                ).join("");
    
                // Wait for the waypoints list to update, then load the first waypoint
                if (waypoints.length) loadWaypointData(waypoints[0]);
            }
        } catch (error) {
            showError("Failed to get map");
        }
    }    
    
    // Function to load data for the selected waypoint
    function loadWaypointData(waypoint) {
        elements.waypointDescription.value = waypoint.description || "";
        elements.imageList.innerHTML = (waypoint.images || []).map((img) =>
            createImageElement(`/static/images/waypoints/${img}`, img, waypoint.id)
        ).join("");
    }

    // Function to create HTML for displaying uploaded images
    function createImageElement(src, imageName, waypointId) {
        return `<div class="image-container">
                    <img src="${src}" alt="Waypoint Image" class="waypoint-image">
                    <div class="delete-button" onclick="removeImage('${imageName}', '${waypointId}')">✖</div>
                </div>`;
    }

    // Function to remove an image from the server and update the image list
    window.removeImage = async function (imageName, waypointId) {
        try {
            // Save current descriptions
            const currentMapDescription = elements.mapDescription.value;
            const currentWaypointDescription = elements.waypointDescription.value;
        
            const response = await fetch("/remove-waypoint-image", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mapId: selectedMapId, waypointId, imageName }),
            });
    
            if (response.ok) {
                const currentWaypointId = elements.waypointSelect.value;
                await fetchMap(selectedMapId); // Reload map data
                
                // Restore user's selection in the list
                elements.waypointSelect.value = currentWaypointId;
                const selectedWaypoint = waypoints.find(wp => wp.id == currentWaypointId);
                if (selectedWaypoint) {
                    loadWaypointData(selectedWaypoint);
                }

                // Restore descriptions
                elements.mapDescription.value = currentMapDescription;
                elements.waypointDescription.value = currentWaypointDescription;
            } else {
                showError("Failed to delete image");
            }
        } catch (error) {
            console.error("Request error:", error);
        }
    };

    // Handler for changing the selected waypoint
    elements.waypointSelect.addEventListener("change", async () => {
        const waypointId = elements.waypointSelect.value;
        const mapId = document.getElementById("editWaypointPopup").getAttribute("data-map-id");
        
        const response = await fetch(`/get-waypoint?waypointId=${encodeURIComponent(waypointId)}&mapId=${encodeURIComponent(mapId)}`);
        const waypoint = await response.json();

        if (waypoint) {
            loadWaypointData(waypoint);
        }
    });
    
    // Image upload handler
    elements.imageUpload.addEventListener("change", async () => {
        const selectedWaypointId = elements.waypointSelect.value;
        if (!selectedWaypointId) return;

        const selectedWaypoint = waypoints.find(wp => wp.id == selectedWaypointId);
        if (!selectedWaypoint) return;

        const formData = new FormData();
        formData.append("mapId", selectedMapId);
        formData.append("waypointId", selectedWaypointId);
        
        for (const file of elements.imageUpload.files) {
            formData.append("images", file);
        }

        try {
            // Save current descriptions
            const currentMapDescription = elements.mapDescription.value;
            const currentWaypointDescription = elements.waypointDescription.value;

            const response = await fetch("/upload-waypoint-image", { method: "POST", body: formData });

            if (response.ok) {
                const result = await response.json();
                selectedWaypoint.images = result.images;
                loadWaypointData(selectedWaypoint);

                // Restore descriptions
                elements.mapDescription.value = currentMapDescription;
                elements.waypointDescription.value = currentWaypointDescription;
            } else {
                showError("Failed to upload image");
            }
        } catch (error) {
            console.error("Request error:", error);
        }

        elements.imageUpload.value = ""; // Clear file input field
    });

    // Waypoint data save handler
    elements.saveWaypoint.addEventListener("click", async () => {
        const selectedWaypointId = elements.waypointSelect.value;
        if (!selectedWaypointId) return;

        const selectedWaypoint = waypoints.find(wp => wp.id == selectedWaypointId);
        if (!selectedWaypoint) return;

        const response = await fetch("/save-waypoint", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                mapId: selectedMapId,
                waypointId: selectedWaypointId,
                mapDescription: elements.mapDescription.value,
                waypointDescription: elements.waypointDescription.value
            }),
        });
        const waypoint = await response.json();

        if (response.ok) {
            showAlert("Waypoint saved!");
        } else {
            showError("Failed to save waypoint");
        }
    });

    // Popup open handler when clicking the button
    document.getElementById("mapList").addEventListener("click", async (event) => {
        if (event.target.classList.contains("view-map")) { // Check if the click was on the "View Map" button
            const mapId = event.target.getAttribute("data-map-id"); // Get the map ID from data-map-id attribute
            document.getElementById("editWaypointPopup").setAttribute("data-map-id", mapId);
            
            if (!mapId) {
                showError("Map not found");
                return;
            }

            await fetchMap(mapId); // Pass mapId to the data loading function
            elements.popup.style.display = "flex";
            elements.pdfIcon.style.display = "flex";
        }
    });

    // Popup close handler
    elements.closePopup.addEventListener("click", () => {
        elements.popup.style.display = "none";
        elements.pdfIcon.style.display = "none";
        location.reload(); // Reload the page
    });

    document.getElementById("pdfIcon").addEventListener("click", async () => {
        const mapId = document.getElementById("editWaypointPopup").getAttribute("data-map-id");
        if (!mapId) {
            alert("Map ID not found!");
            return;
        }
    
        // Получаем статус подписки
        const response = await fetch(`/get-map?mapId=${encodeURIComponent(mapId)}&username=${encodeURIComponent(getUsernameFromCookie())}`)
        if (!response.ok) {
            alert("Failed to get map details!");
            return;
        }
        const data = await response.json();
        if (data.subscription === false) {
            window.location.href = `/${encodeURIComponent(getUsernameFromCookie())}/my_profile?scrollToSubscription=true`;
            return;
        }
    
        // Если подписка есть, продолжаем скачивание PDF
        showWarning("Downloading may take around 30 seconds. Please, wait!");
    
        const pdfResponse = await fetch(`/download-map-pdf?mapId=${encodeURIComponent(mapId)}`);
        if (!pdfResponse.ok) {
            alert("Failed to download PDF");
            return;
        }
    
        const blob = await pdfResponse.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `map_${mapId}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });
    

    // Subscribe

    subscribeBtn.addEventListener("click", async () => {
        window.location.href = `/${encodeURIComponent(getUsernameFromCookie())}/my_profile?scrollToSubscription=true`;
        return;
    });
});
