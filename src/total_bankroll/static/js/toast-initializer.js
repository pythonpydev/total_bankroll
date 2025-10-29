document.addEventListener('DOMContentLoaded', function () {
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    const toastList = toastElList.map(function (toastEl) {
        // Create a new toast instance and show it
        const toast = new bootstrap.Toast(toastEl, { delay: 5000 }); // 5 second delay
        toast.show();
        return toast;
    });
});