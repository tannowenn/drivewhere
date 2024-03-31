// getting data from rental DB
function getOpenListing() {

    var address = document.getElementById("searchAddress").value

    fetch("http://localhost:5100/master/rental", {
        method: "POST",
        headers: {
            "Content-Type" : "application/json"
        },
        body: JSON.stringify({
            address: address,
            status: "open",
            userId: null
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("network response was not ok")
        }
        return response.json()
    })
    .then(data => {
        console.log("Data:", data.data.rental_list)
        var documentSelector = document.getElementById("carList")
        const cars = data.data.rental_list
        // reset everything
        documentSelector.innerHTML = ""
        for (i=0; i<cars.length; i++) {
            var div = document.createElement("div")
            div.classList.add("col-md-4")
            div.classList.add("mb-3")
            var car = `
              <div class="card" style="width: 18rem;">
                <div class="card-body">
                  <h5 class="card-title">${cars[i].carMake} ${cars[i].carModel}</h5>
                  <h6 class="card-subtitle mb-2 text-body-secondary">Capacity: ${cars[i].capacity} | Price per day: ${cars[i].pricePerDay}</h6>
                  <p class="card-text">${cars[i].distance} away from you <br>Carplate: ${cars[i].carPlate}<br>Contact Number: ${cars[i].phoneNum}</p>
                  <p class="card-footer"><button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#rentCar" onclick="addRentalId(${cars[i].rentalId})">Rent</button></p>
                  
                </div>
              </div>
            `
            
            div.innerHTML = car
            documentSelector.appendChild(div)
        }

        
    })

    .catch(error => {
        console.error("Error fetching data:", error)
    })
}

// handle new post
function createRental() {
    var userId = "3" 
    var carModel = document.getElementById("carModel").value
    var carMake = document.getElementById("carMake").value
    var capacity = document.getElementById("capacity").value
    var carPlate = document.getElementById("carPlate").value
    var address = document.getElementById("createAddress").value
    var pricePerDay = document.getElementById("pricePerDay").value

    let jsonBody = {
        "userId": userId,
        "carModel": carModel,
        "carMake": carMake,
        "capacity": capacity,
        "carPlate": carPlate,
        "address": address,
        "pricePerDay": pricePerDay,
        "status": "open"
    }
    
    fetch("http://localhost:5002/rental/create",
    {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: JSON.stringify(jsonBody)
    })
    .then(response => response.json())
    .then(response => {
        switch (response["code"]) {
            case 201:
                alert("Successfully created your listing!")
                window.location.reload()
                break
            default:
                alert("Something went wrong with creating your listing!")
                window.location.reload()
                console.log(`ERROR: ${response["code"]}: ${response["message"]}`)
        }
    })
    .catch(error => {
        // Errors when calling the service; such as network error, 
        // service offline, etc
        console.log(error);
    })
}

// user renting a car
function requestRental() {
    var rentalId = String(JSON.parse(localStorage.getItem("rentalId")))
    var userId = "3" //renter's userId
    var days = document.getElementById("daysRent").value

    let jsonBody = {
        "rentalId": rentalId,
        "userId": userId,
        "days": days
    }
    
    fetch("http://localhost:5100/master/rental/request",
    {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: JSON.stringify(jsonBody)
    })
    .then(response => response.json())
    .then(response => {
        switch (response["code"]) {
            case 200:
                window.location.href = response["data"]["url"]
                break
            default:
                console.log(`ERROR: ${response["code"]}: ${response["message"]}`)
        }
    })
    .catch(error => {
        // Errors when calling the service; such as network error, 
        // service offline, etc
        console.log(error);
    })
}

//adding rentalId to localStorage
function addRentalId(rentalId) {
    localStorage.setItem("rentalId", JSON.stringify(rentalId))
}