// script/admin.js

// Fetch and populate donor data
function fetchDonors() {
    const donorTableBody = document.getElementById('donor-table-body');
    axios.get('/get-donors/')
        .then(response => {
            if (response.data.status === 'success') {
                const donors = response.data.donors;
                donorTableBody.innerHTML = ''; // Clear previous rows
                donors.forEach(donor => {
                    const row = `
                        <tr onclick="viewDonorDetails(${donor.id})" style="cursor: pointer;">
                            <td>${donor.id}</td>
                            <td>${donor.name}</td>
                            <td>${donor.email}</td>
                            <td>${donor.phone}</td>
                            <td>
                                <button class="btn btn-sm" onclick="editDonor(event, ${donor.id})"><i class="fa-regular fa-pen-to-square"></i></button>
                                <button class="btn btn-sm" onclick="deleteDonor(event, ${donor.id})"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>
                    `;
                    donorTableBody.innerHTML += row;
                });
            } else {
                console.error('Failed to fetch donors:', response.data.message);
            }
        })
        .catch(error => {
            console.error('Error fetching donors:', error);
        });
}


// Display detailed donor information
function viewDonorDetails(donorId) {
    axios.get(`/get-donor/${donorId}`)
        .then(response => {
            if (response.data.status === 'success') {
                const donor = response.data.donor;

                // Populate donor details
                document.getElementById('donor-id').textContent = donor.id;
                document.getElementById('donor-name').textContent = donor.name;

                // Update Call and Email icons with functionality
                const callIcon = `<a href="tel:${donor.phone}" id="call-donor" class="btn btn-sm btn-success mx-1">
                                    <i class="fa-solid fa-phone-volume"></i>
                                  </a>`;
                const emailIcon = `<a href="mailto:${donor.email}" id="email-donor" class="btn btn-sm btn-info mx-1">
                                    <i class="fa-regular fa-envelope"></i>
                                   </a>`;
                document.getElementById('contact-actions').innerHTML = callIcon + emailIcon;

                // Populate donation history
                const history = donor.donation_history?.map(item => 
                    `<li class="list-group-item">${item.date}: $${item.amount}</li>`
                ).join('') || '<li class="list-group-item">No donations found</li>';
                document.getElementById('donation-history').innerHTML = history;

                document.getElementById('donor-details').style.display = 'block';
            } else {
                console.error('Failed to fetch donor details:', response.data.message);
            }
        })
        .catch(error => {
            console.error('Error fetching donor details:', error);
        });
}



// Handle Add Donor form submission
document.getElementById('submit-add-donor').addEventListener('click', function () {
    const name = document.getElementById('donor-name-input').value;
    const email = document.getElementById('donor-email-input').value;
    const phone = document.getElementById('donor-phone-input').value;
    const address = document.getElementById('donor-address-input').value;
    const addAnother = document.getElementById('add-another-donor').checked;

    if (name && email && phone) {
        axios.post('/add-donor/', {
            name, email, phone, address
        }).then(response => {
            if (response.data.status === 'success') {
                alert('Donor added successfully');
                if (!addAnother) {
                    document.getElementById('add-donor-form').reset();
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addDonorModal'));
                    modal.hide();
                }
                fetchDonors();  // Reload the donor list after adding a donor
            } else {
                alert('Failed to add donor: ' + response.data.message);
            }
        }).catch(error => {
            console.error('Error adding donor:', error);
        });

        if (addAnother) {
            document.getElementById('add-donor-form').reset();
        }
    } else {
        alert('Please fill in all required fields.');
    }
});

// Fetch and populate donor details for editing
function editDonor(event, donorId) {
    event.stopPropagation(); // Prevent row click event
    axios.get(`/get-donor/${donorId}`)
        .then(response => {
            if (response.data.status === 'success') {
                const donor = response.data.donor;

                // Populate the form with donor data
                document.getElementById('edit-donor-id').value = donor.id;
                document.getElementById('edit-donor-name').value = donor.name;
                document.getElementById('edit-donor-email').value = donor.email;
                document.getElementById('edit-donor-phone').value = donor.phone;
                document.getElementById('edit-donor-address').value = donor.address;

                // Show the modal
                const editModal = new bootstrap.Modal(document.getElementById('editDonorModal'));
                editModal.show();
            } else {
                alert('Failed to fetch donor details: ' + response.data.message);
            }
        })
        .catch(error => {
            console.error('Error fetching donor details:', error);
        });
}

// Submit edited donor details
document.getElementById('submit-edit-donor').addEventListener('click', function () {
    const donorId = document.getElementById('edit-donor-id').value;
    const name = document.getElementById('edit-donor-name').value;
    const email = document.getElementById('edit-donor-email').value;
    const phone = document.getElementById('edit-donor-phone').value;
    const address = document.getElementById('edit-donor-address').value;

    if (name && email && phone) {
        axios.put(`/edit-donor/${donorId}/`, {
            name, email, phone, address
        }).then(response => {
            if (response.data.status === 'success') {
                alert('Donor updated successfully');
                fetchDonors(); // Refresh donor list
                const modal = bootstrap.Modal.getInstance(document.getElementById('editDonorModal'));
                modal.hide();
            } else {
                alert('Failed to update donor: ' + response.data.message);
            }
        }).catch(error => {
            console.error('Error updating donor:', error);
        });
    } else {
        alert('Please fill in all required fields.');
    }
});


function deleteDonor(event, donorId) {
    event.stopPropagation();  // Prevent table row click event from firing
    if (confirm('Are you sure you want to delete this donor?')) {
        axios.post(`/delete-donor/${donorId}/`)
            .then(response => {
                if (response.data.status === 'success') {
                    alert('Donor deleted successfully');
                    fetchDonors();  // Reload the donor list after deletion
                } else {
                    alert('Failed to delete donor: ' + response.data.message);
                }
            })
            .catch(error => {
                console.error('Error deleting donor:', error);
            });
    }
}


// Fetch and populate donation data
function fetchDonations() {
    const donationTableBody = document.getElementById('donation-table-body');
    axios.get('/get-donations/')
        .then(response => {
            if (response.data.status === 'success') {
                const donations = response.data.donations;
                donations.forEach(donation => {
                    const row = `
                        <tr>
                            <td>${donation.donation_id}</td>
                            <td>${donation.donor_name}</td>
                            <td>${donation.donor_email}</td>
                            <td>${JSON.stringify(donation.food_items)}</td>
                            <td>${donation.pickup_address}</td>
                            <td>${donation.city}</td>
                            <td>${donation.region}</td>
                            <td>${donation.country}</td>
                            <td>${donation.pickup_date}</td>
                            <td>${donation.pickup_time}</td>
                            <td>${donation.agreement_sent ? 'Yes' : 'No'}</td>
                            <td>${donation.agreement_signed ? 'Yes' : 'No'}</td>
                        </tr>
                    `;
                    donationTableBody.innerHTML += row;
                });
            } else {
                console.error('Failed to fetch donations:', response.data.message);
            }
        })
        .catch(error => {
            console.error('Error fetching donations:', error);
        });
}

// Initialize the page by fetching data
document.addEventListener('DOMContentLoaded', function () {
    fetchDonors();
    fetchDonations();
});
