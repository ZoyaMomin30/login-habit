document.getElementById('habitForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Get form values
    const habitName = document.getElementById('habit').value;
    const targetQuantity = document.getElementById('quantity').value;
    
    // Hide habit form and show pixel form
    document.getElementById('habitForm').style.display = 'none';
    document.getElementById('pixelFormContainer').style.display = 'block';
    
    // Update habit title
    document.getElementById('habitTitle').textContent = habitName;
    
    // Update pixel form placeholder with target quantity
    document.getElementById('pixelQuantity').placeholder = `Target: ${targetQuantity} hours`;
    
    // Here you would also make an AJAX call to create the Pixela graph
    // and update the iframe src, but keeping it simple for this example
    
    // For demo purposes, we'll just show the container
    document.getElementById('graphContainer').style.display = 'block';
});

if ("{{ habit_created }}" === "True") {
    localStorage.setItem('habit_created', 'true');
}

// Optional: Add this to prevent form resubmission on refresh
if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}