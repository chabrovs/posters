function deletePoster(posterId) {
    if (confirm('Are you sure you want to delete this poster?')) {
        fetch(`/posters/${posterId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                window.location.href = '{% url "posters_app:home" %}';  // Redirect after successful deletion
            } else {
                alert('An error occurred while trying to delete the poster.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var posterElement = document.getElementById('poster');
    var posterId = posterElement.getAttribute('csrf-token');

    console.log("Poster ID:", posterId);

});