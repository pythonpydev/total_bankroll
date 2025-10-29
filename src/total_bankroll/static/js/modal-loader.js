document.addEventListener('DOMContentLoaded', function () {
    var generalModal = document.getElementById('generalModal');
    if (generalModal) {
        generalModal.addEventListener('show.bs.modal', function (event) {
            var button = event.relatedTarget; // Button that triggered the modal
            var url = button.getAttribute('data-url'); // Extract info from data-url attribute
            var modalContent = generalModal.querySelector('.modal-content');

            // Load content from the URL into the modal body
            fetch(url)
                .then(response => response.text())
                .then(html => {
                    modalContent.innerHTML = html;
                    // After loading content, find the form and set its action
                    const form = modalContent.querySelector('form');
                    if (form) {
                        form.action = url;
                    }
                })
                .catch(error => {
                    modalContent.innerHTML = '<div class="modal-body"><p>Error loading content.</p></div>';
                    console.error('Error loading modal content:', error);
                });
        });
    }
});