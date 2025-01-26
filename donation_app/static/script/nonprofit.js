// Script for AJAX data fetching

    $(document).ready(function () {
        // Fetch signed agreements
        fetch('/api/get_signed_agreements/')
            .then(response => response.json())
            .then(data => {
                let agreementsHtml = '<ul>';
                data.agreements.forEach(agreement => {
                    agreementsHtml += `<li>${agreement.name} - ${agreement.date}</li>`;
                });
                agreementsHtml += '</ul>';
                $('#signed-agreements').html(agreementsHtml);
            });

        // Fetch donation status
        fetch('/api/get_donations_status/')
            .then(response => response.json())
            .then(data => {
                let statusHtml = '<ul>';
                data.donations.forEach(donation => {
                    statusHtml += `<li>Donation ID: ${donation.id}, Status: ${donation.status}</li>`;
                });
                statusHtml += '</ul>';
                $('#donation-status').html(statusHtml);
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
    });

    // Simulate pickup process (for now)
    function simulatePickup() {
        $('#pickup-status').html('<p>Pickup has been scheduled. Awaiting logistics update.</p>');
    }
