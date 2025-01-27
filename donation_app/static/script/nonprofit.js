

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
                // Determine the badge color based on donation status
                let statusBadge = '';
                if (data.status === 'pending') {
                    statusBadge = `<span class="badge bg-warning">Pending</span>`;
                } else if (data.status === 'assigned') {
                    statusBadge = `<span class="badge bg-primary">Assigned</span>`;
                } else if (data.status === 'completed') {
                    statusBadge = `<span class="badge bg-success">Completed</span>`;
                } else {
                    statusBadge = `<span class="badge bg-secondary">Unknown</span>`;
                }

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
                            <p><strong>Status:</strong> ${statusBadge}</p>
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
function simulatePickup(donationId) {
    // Simulate the pickup and change donation status
    $.ajax({
        type: 'POST',
        url: '{% url "simulate_pickup" %}',  // Create a Django URL for the backend to handle this request
        data: {
            'donation_id': donationId,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function (response) {
            if (response.success) {
                // Update the donation status and pickup date in the table dynamically
                $('#donation-' + donationId + ' .pickup-status').text('Pickup Scheduled');
                $('#donation-' + donationId + ' .pickup-date').text(response.pickup_date);
                // Optionally, show a success message
                alert('Pickup has been scheduled.');
            } else {
                alert('Error simulating pickup.');
            }
        }
    });
}


// Simulated data for Chart.js (Impact Chart)
const impactData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
        label: 'Impact Over Time (USD)',
        data: [3500, 4000, 2500, 3000, 4500, 5000],
        backgroundColor: 'rgba(45, 106, 79, 0.2)',
        borderColor: 'rgba(45, 106, 79, 1)',
        borderWidth: 2,
        tension: 0.3,
        fill: true,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: 'rgba(45, 106, 79, 1)',
        pointHoverBackgroundColor: 'rgba(45, 106, 79, 0.8)'
    }]
};

const ctx = document.getElementById('impactChart').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: impactData,
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    font: {
                        size: 14
                    }
                }
            },
            tooltip: {
                callbacks: {
                    label: function (tooltipItem) {
                        return tooltipItem.dataset.label + ': $' + tooltipItem.raw;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function (value) {
                        return '$' + value;
                    }
                }
            },
            x: {
                ticks: {
                    font: {
                        size: 12
                    }
                }
            }
        }
    }
});

// D3.js Interactive Graph (Traffic Impact Analysis)
const data = [
    { time: '00:00', impact: 35 },
    { time: '01:00', impact: 45 },
    { time: '02:00', impact: 40 },
    { time: '03:00', impact: 55 },
    { time: '04:00', impact: 60 },
    { time: '05:00', impact: 80 },
    { time: '06:00', impact: 75 }
];

const margin = { top: 20, right: 30, bottom: 50, left: 40 },
    width = 600 - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;

const svg = d3.select("#d3-graph")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

const x = d3.scaleBand()
    .domain(data.map(d => d.time))
    .range([0, width])
    .padding(0.1);

const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.impact)])
    .nice()
    .range([height, 0]);

svg.append("g")
    .selectAll(".bar")
    .data(data)
    .enter().append("rect")
    .attr("class", "bar")
    .attr("x", d => x(d.time))
    .attr("y", d => y(d.impact))
    .attr("width", x.bandwidth())
    .attr("height", d => height - y(d.impact))
    .attr("fill", "#2d6a4f")
    .append("title")
    .text(d => `Impact: ${d.impact}`);

svg.append("g")
    .attr("class", "x-axis")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x))
    .selectAll("text")
    .style("font-size", "12px")
    .style("text-anchor", "middle");

svg.append("g")
    .attr("class", "y-axis")
    .call(d3.axisLeft(y))
    .selectAll("text")
    .style("font-size", "12px");

// Handle Report Download
document.getElementById("downloadReport").addEventListener("click", function () {
    const reportContent = document.getElementById('v-pills-reporting').innerHTML;
    const blob = new Blob([reportContent], { type: 'application/html' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'report.html';
    link.click();
});


const chatContainer = document.getElementById('chat-container');
chatContainer.scrollTop = chatContainer.scrollHeight; // Keeps the latest message in view when new messages are added

function scrollToDonations() {
    const donationsSection = document.getElementById('donations-section');
    donationsSection.scrollIntoView({ behavior: 'smooth' });
}

document.addEventListener("DOMContentLoaded", () => {
    const capacityElement = document.getElementById("capacity");
    const capacityValue = capacityElement.textContent.trim();
    if (!capacityValue.toLowerCase().includes("beneficiaries")) {
        capacityElement.textContent = `${capacityValue} Beneficiaries`;
    }
});
