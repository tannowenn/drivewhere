const RENTAL_HOST = "localhost"
const RENTAL_PORT = 5002

const MASTER_HOST = "localhost"
const MASTER_PORT = 5100

// when user presses on their rented cars
// getting data from rental DB
window.onload = function () {
    // harded coded value user 3 (which is us rn)
    currentUserId = "3"

    fetch(`http://${RENTAL_HOST}:${RENTAL_PORT}/rental`, {
        method: "POST",
        headers: {
            "Content-Type" : "application/json"
        },
        body: JSON.stringify({
            address: "160139",
            status: "rented",
            userId: currentUserId
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
        var documentSelector = document.getElementById("rentedCarList")
        const cars = data.data.rental_list

        for (i=0; i<cars.length; i++) {
            var div = document.createElement("div")
            div.classList.add("col-md-4")
            div.classList.add("mb-3")
            var car = `
                <div class="card" style="width: 18rem;">
                <div class="card-body">
                    <h5 class="card-title">${cars[i].carMake} | ${cars[i].carModel}</h5>
                    <h6 class="card-subtitle mb-2 text-body-secondary">Capacity: ${cars[i].capacity} | Price per day: ${cars[i].pricePerDay}</h6>
                    <p class="card-text">Postal Code: ${cars[i].address}<br>Carplate: ${cars[i].carPlate}</p>
                    <p class="card-footer"><button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#returnCar" onclick="${addReturnRentalId(cars[i].rentalId)}">Return</button></p>
                    
                </div>
                </div>
            `
            div.innerHTML = car
            documentSelector.appendChild(div)
        }
    })
}

//owner completing the rental
function completeRental() {

    var rentalId = JSON.parse(localStorage.getItem("returnRentalId"))
    console.log(rentalId)
    let jsonBody = {
        "rentalId": rentalId
    }
    
    fetch(`http://${MASTER_HOST}:${MASTER_PORT}/master/rental/update`,
    {
        method: "PUT",
        headers: {
            "Content-type": "application/json"
        },
        body: JSON.stringify(jsonBody)
    })
    .then(response => response.json())
    .then(response => {
        switch (response["code"]) {
            case 200:
                console.log("success!")
                window.alert("Your car has successfully been returned and the money has been released to you!")
                location.reload()
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
function addReturnRentalId(returnRentalId) {
    localStorage.setItem("returnRentalId", JSON.stringify(returnRentalId))
}