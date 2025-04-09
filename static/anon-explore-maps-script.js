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
// Функция загрузки карт пользователя 
function fetchMaps(username) {
    return fetch(`/all-maps?username=${' '}`)
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

                // Контейнер для изображений точек маршрута
                const waypointImages = document.createElement("div");
                waypointImages.classList.add("waypoint-images");

                map.waypoints.forEach(waypoint => {
                    if (!waypoint.images || waypoint.images.length === 0) return; // Пропускаем, если нет изображений

                    waypoint.images.forEach(imageName => {
                        const img = document.createElement("img");
                        img.src = `/static/images/waypoints/${imageName.trim()}`;
                        img.alt = "Waypoint Image";
                        img.classList.add("waypoint-img");
                        waypointImages.appendChild(img);
                    });
                });

                // Создаем кнопку с data-map-id
                const viewMapButton = document.createElement("a");
                viewMapButton.classList.add("view-map");
                viewMapButton.textContent = "View Map";
                viewMapButton.setAttribute("data-map-id", map.id); // Добавляем атрибут с ID карты

                // Заполняем HTML карточки карты
                mapElement.innerHTML = `
                    <h2>${map.description || "Unnamed Map"}</h2>
                    <h3>
                        ${map.rating 
                            ? `<img src="/static/images/rating/star.png" alt="Star" class="rating-icon"> 
                               Rating: ${map.rating.toFixed(1)} (${map.reviewsNumber} rated)`
                            : "No rating yet"
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

// Загрузка карт после полной загрузки страницы
window.onload = () => {
    let username = getUsernameFromCookie();  // Используем let, чтобы присвоить значение в дальнейшем

    if (!username) {
        username = 'unauthorized';  // Теперь это не вызывает ошибку
    }

    fetchMaps(username).then(() => searchMaps()); // Применяем фильтр после загрузки карт
};

///////////////////////////////////////////////////////////////////////////////////////////////////////

// поп-ап по просмотру карты
document.addEventListener("DOMContentLoaded", async () => {
    
    // Получаем ссылки на элементы поп-апа и формы
    const elements = {
        popup: document.getElementById("viewMapPopup"), // Контейнер всплывающего окна
        fullMapPopup: document.getElementById("fullMapPopup"),
        mapIcon: document.getElementById("mapIcon"),
        closePopup: document.getElementById("viewClosePopup"), // Кнопка закрытия поп-апа
        waypointSelect: document.getElementById("viewWaypointSelect"), // Выпадающий список точек маршрута
        mapTitle: document.getElementById("viewMapTitle"), // Поле описания карты
        waypointDescription: document.getElementById("viewWaypointDescription"), // Поле описания точки маршрута
        imageList: document.getElementById("viewImageList"), // Контейнер для загруженных изображений
    };

    const username = getUsernameFromCookie(); // Получаем имя пользователя из куков

    let map;
    let markersLayer;

    // Инициализация карты сразу при загрузке страницы
    if (document.getElementById("fullMapContainer")) {
        map = L.map('fullMapContainer').setView([52.3676, 4.9041], 10);
        markersLayer = L.layerGroup().addTo(map); // Инициализируем markersLayer

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);

        // Изначально скрываем контейнер
        document.getElementById("fullMapContainer").style.display = "none";
    } else {
        console.error("Элемент карты не найден!");
    }

    // Обработчик клика по иконке карты
    if (elements.mapIcon) {
        elements.mapIcon.addEventListener("click", async () => {
            const mapId = document.getElementById("viewMapPopup").getAttribute("data-map-id");
            if (!mapId) return console.error("Map ID is missing");

            try {
                const response = await fetch(`/get-map?mapId=${encodeURIComponent(mapId)}&username=${encodeURIComponent(username)}`);
                const data = await response.json();

                if (!data || !data.waypoints) {
                    console.error("Ошибка: точки маршрута не найдены");
                    return;
                }

                markersLayer.clearLayers();
                const bounds = L.latLngBounds();

                data.waypoints.forEach((wp) => {
                    const marker = L.marker([wp.latitude, wp.longitude])
                        .addTo(markersLayer)
                        .bindPopup(`<b>${wp.name}</b><br>(${wp.latitude}, ${wp.longitude})`);
                    bounds.extend(marker.getLatLng());
                });

                if (bounds.isValid()) { 
                    map.fitBounds(bounds, { padding: [50, 50] });
                }

                document.getElementById("fullMapContainer").style.display = "block";

                setTimeout(() => {
                    map.invalidateSize();
                    if (bounds.isValid()) {
                        map.fitBounds(bounds, { padding: [50, 50] });
                    }
                }, 300);
                
                elements.fullMapPopup.style.display = "flex";
            } catch (error) {
                console.error("Ошибка загрузки карты:", error);
            }
        });
    }

    // Закрытие поп-апа
    if (elements.fullMapPopup) {
        elements.fullMapPopup.onclick = function (event) {
            if (event.target === elements.fullMapPopup) {
                elements.fullMapPopup.style.display = "none";
            }
        };
    }

    // Функция загрузки карты
    async function fetchMap(mapId) {
        try {
            const response = await fetch(`/get-map?mapId=${encodeURIComponent(mapId)}&username=${encodeURIComponent(username)}`);
            const data = await response.json();

            if (data) {
                elements.mapTitle.textContent = data.description || "No description available";
                const waypoints = data.waypoints || [];
                
                elements.waypointSelect.innerHTML = waypoints.map((wp) =>
                    `<option value="${wp.id}">${wp.name}</option>`
                ).join("");

                if (waypoints.length) loadWaypointData(waypoints[0]);
            }
        } catch (error) {
            console.error("Failed to get map", error);
        }
    }

    // Загрузка данных точки маршрута
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

    // Обработчик смены точки маршрута
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

    // Открытие карты
    const mapList = document.getElementById("mapList");
    if (mapList) {
        mapList.addEventListener("click", async (event) => {
            if (event.target.classList.contains("view-map")) {
                const mapId = event.target.getAttribute("data-map-id");
                if (!mapId) return console.error("Map not found");

                document.getElementById("viewMapPopup").setAttribute("data-map-id", mapId);
                await fetchMap(mapId);
                document.getElementById("viewMapPopup").style.display = "flex";
                document.getElementById("mapIcon").style.display = "flex";
            }
        });
    }

    // Кнопка "вверх"
    const scrollToTopButton = document.getElementById("scrollToTop");
    if (scrollToTopButton) {
        window.addEventListener("scroll", () => {
            scrollToTopButton.style.display = window.scrollY > 300 ? "block" : "none";
        });
        scrollToTopButton.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // Закрытие поп-апа
    if (elements.closePopup) {
        elements.closePopup.addEventListener("click", () => {
            elements.popup.style.display = "none";
            elements.mapIcon.style.display = "none";
        });
    }

    if (elements.popup) {
        elements.popup.onclick = function (event) {
            if (event.target === elements.popup) {
                elements.popup.style.display = "none";
                elements.mapIcon.style.display = "none";
            }
        };
    }
});