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

let allTravellers = [];  // Stores all travellers and maps

// Fetches the list of travellers and their maps
function fetchTravellers() {
    fetch('/manage-maps')
        .then(response => response.json())
        .then(data => {
            allTravellers = data;  // Save data for searching
            displayTravellers(allTravellers);  // Display the travellers immediately
        })
        .catch(error => console.error('Error fetching travellers:', error));
}

// Displays travellers and their maps
function displayTravellers(travellers) {
    const travellerListContainer = document.getElementById('traveller-list');
    travellerListContainer.innerHTML = '';  // Clear the container

    travellers.forEach(traveller => {
        const travellerDiv = document.createElement('div');
        travellerDiv.classList.add('traveller');

        // Traveller information
        travellerDiv.innerHTML = `
            <h3>Traveller ${traveller.userName} (${traveller.name} ${traveller.surname})</h3>
            <div>
                ${traveller.blocked ? 
                    `<button class="unblock-btn" onclick="toggleBlock('${traveller.userName}', false)">Unblock</button>` :
                    `<button class="block-btn" onclick="toggleBlock('${traveller.userName}', true)">Block</button>`
                }
            </div>
            <div>
                <h4>Maps:</h4>
                <ul>
                    ${traveller.maps.map(map => `
                        <li>
                            Map id: ${map.id}, description: ${map.description}
                            <button class="deleteMap-btn" onclick="deleteMap(${map.id})">Delete</button>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
        travellerListContainer.appendChild(travellerDiv);
    });
}

// Searches for travellers based on input
function searchTravellers() {
    const query = document.getElementById('search-input').value.toLowerCase();
    console.log("Search query:", query); // Debugging log

    const filteredTravellers = allTravellers.filter(traveller => {
        console.log("Checking traveller:", traveller.userName);
        return (
            traveller.userName?.toLowerCase().includes(query) ||
            traveller.name?.toLowerCase().includes(query) ||
            traveller.surname?.toLowerCase().includes(query) ||
            (traveller.maps && traveller.maps.some(map => 
                map.id?.toString().includes(query) || map.description?.toLowerCase().includes(query)
            ))
        );
    });

    displayTravellers(filteredTravellers);
}

// Blocks or unblocks a traveller
function toggleBlock(username, block) {
    const endpoint = block ? '/block-user' : '/unblock-user';
    fetch(endpoint, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username })
    })
    .then(response => response.json())
    .then(data => {
        if (data.noRecord) {
            showError("Couldn't find traveller to change");
        } else {
            showAlert(data.message);
            fetchTravellers();  // Refresh the list
        }
    })
    .catch(error => console.error('Error:', error));
}

// Deletes a map
function deleteMap(mapId) {
    fetch('/delete-map', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mapId: mapId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.noRecord) {
            showError("Couldn't find map to delete");
        } else {
            showAlert(data.message);
            fetchTravellers();  // Refresh the list
        }
    })
    .catch(error => console.error('Error:', error));
}

// Load travellers when the page loads
window.onload = fetchTravellers;
