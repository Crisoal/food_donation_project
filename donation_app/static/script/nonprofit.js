

// Script for AJAX data fetching


document.addEventListener('DOMContentLoaded', () => {
    // Fetch profile details from the API
    const fetchProfile = async () => {
        try {
            const response = await fetch('/api/nonprofit/profile/');
            if (!response.ok) throw new Error('Failed to fetch profile details');
            const profile = await response.json();

            // Populate the profile section dynamically
            document.querySelector('#org-name').textContent = profile.organization_name;
            document.querySelector('#mission-statement').textContent = profile.mission_statement;
            document.querySelector('#address').textContent = profile.address;
            document.querySelector('#contact-number').textContent = profile.contact_number;
            document.querySelector('#city').textContent = profile.city;
            document.querySelector('#state').textContent = profile.state;
            document.querySelector('#country').textContent = profile.country;
            document.querySelector('#areas-of-operation').textContent = profile.areas_of_operation.join(', ');
            document.querySelector('#requirements').textContent = profile.requirements_or_preferences;
            document.querySelector('#capacity').textContent = profile.capacity;
        } catch (error) {
            console.error('Error fetching profile:', error);
        }
    };

    fetchProfile();
});


document.addEventListener('DOMContentLoaded', () => {
    const donationDetailsModal = document.getElementById('donationDetailsModal');
    const donationDetailsContent = document.getElementById('donation-details-content');

    donationDetailsModal.addEventListener('show.bs.modal', (event) => {
        const button = event.relatedTarget; // Button that triggered the modal
        const donationId = button.getAttribute('data-donation-id'); // Extract donation ID

        // Clear existing content and show loading
        donationDetailsContent.innerHTML = '<p class="text-center">Loading...</p>';

        // Fetch donation details via AJAX
        fetch(`/api/donations/${donationId}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch donation details');
                }
                return response.json();
            })
            .then(data => {
                // Populate modal with donation details
                donationDetailsContent.innerHTML = `
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <p><strong>Donation ID:</strong> ${data.donation_id}</p>
                            <p><strong>Donor Name:</strong> ${data.donor_name}</p>
                            <p><strong>Donor Email:</strong> ${data.donor_email}</p>
                            <p><strong>Donor Phone:</strong> ${data.donor_phone}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Pickup Address:</strong> ${data.pickup_address}, ${data.city}, ${data.region}, ${data.country} (${data.postal_code})</p>
                            <p><strong>Status:</strong> ${data.status}</p>
                            <p><strong>Perishable Status:</strong> ${data.perishable_status}</p>
                            <p><strong>Pickup Date:</strong> ${data.pickup_date}</p>
                            <p><strong>Pickup Time:</strong> ${data.pickup_time}</p>
                        </div>
                    </div>
                    <h6 class="mt-4">Food Items:</h6>
                    <div class="table-responsive">
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Quantity</th>
                                    <th>Food Type</th>
                                    <th>Condition</th>
                                    <th>Expiry Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.food_items.map(item => `
                                    <tr>
                                        <td>${item.quantity} kg</td>
                                        <td>${item.food_type}</td>
                                        <td>${item.condition}</td>
                                        <td>${item.expiration_date}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            })
            .catch(error => {
                donationDetailsContent.innerHTML = `<p class="text-danger">Error loading details: ${error.message}</p>`;
            });
    });
});



// Fetch logistics updates
fetch('/api/get_logistics_updates/')
    .then(response => response.json())
    .then(data => {
        let updatesHtml = '';
        data.updates.forEach(update => {
            updatesHtml += `<li>${update.message} - ${update.timestamp}</li>`;
        });
        $('#logistics-updates').html(updatesHtml);
    });

// Fetch impact metrics
fetch('/api/get_impact_metrics/')
    .then(response => response.json())
    .then(data => {
        // Display total food donated and meals saved
        $('#total-donated').html(`<h5>Total Donated: ${data.total_donated} kg</h5>`);
        $('#meals-saved').html(`<h5>Meals Saved: ${data.meals_saved}</h5>`);

        // Display chart for impact
        var ctx = document.getElementById('impactChart').getContext('2d');
        var impactChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Total Donated', 'Meals Saved'],
                datasets: [{
                    label: 'Impact Metrics',
                    data: [data.total_donated, data.meals_saved],
                    backgroundColor: ['#4CAF50', '#FF9800'],
                    borderColor: ['#4CAF50', '#FF9800'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true
            }
        });
    });


// Simulate pickup process (for now)
function simulatePickup() {
    $('#pickup-status').html('<p>Pickup has been scheduled. Awaiting logistics update.</p>');
}
