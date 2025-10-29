document.addEventListener('DOMContentLoaded', function () {
    // --- Theme Toggler ---
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        const body = document.body;
        const themeIcon = themeToggle.querySelector('i');

        function setDarkTheme(isDark) {
            body.classList.toggle('dark-mode', isDark);
            if (themeIcon) {
                themeIcon.classList.toggle('bi-sun-fill', !isDark);
                themeIcon.classList.toggle('bi-moon-fill', isDark);
            }
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            const event = new Event('theme-changed');
            document.dispatchEvent(event);
        }

        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        setDarkTheme(savedTheme ? savedTheme === 'dark' : prefersDark);

        themeToggle.addEventListener('click', () => {
            setDarkTheme(!body.classList.contains('dark-mode'));
        });
    }

    // --- Modal Loader ---
    const generalModal = document.getElementById('generalModal');
    if (generalModal) {
        generalModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const url = button.getAttribute('data-url');
            const modalContent = generalModal.querySelector('.modal-content');

            fetch(url)
                .then(response => response.text())
                .then(html => {
                    modalContent.innerHTML = html;
                    const form = modalContent.querySelector('form');
                    // Only set the form action if it's not already set by the template
                    if (form && !form.getAttribute('action')) {
                        form.setAttribute('action', url);
                    }
                })
                .catch(error => {
                    modalContent.innerHTML = '<div class="modal-body"><p>Error loading content.</p></div>';
                    console.error('Error loading modal content:', error);
                });
        });
    }

    // --- Back to Top Button ---
    const backToTopButton = document.getElementById("backToTopBtn");
    if (backToTopButton) {
        window.onscroll = function() {
            if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
                backToTopButton.style.display = "block";
            } else {
                backToTopButton.style.display = "none";
            }
        };
        backToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // --- Toast Initializer ---
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(function (toastEl) {
        const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
        toast.show();
        return toast;
    });

    // --- Cookie Consent ---
    const banner = document.getElementById('cookieConsentBanner');
    const acceptBtn = document.getElementById('acceptCookie');
    const declineBtn = document.getElementById('declineCookie');

    if (banner && acceptBtn && declineBtn) {
        function setCookie(name, value, days) {
            let expires = "";
            if (days) {
                const date = new Date();
                date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                expires = "; expires=" + date.toUTCString();
            }
            document.cookie = name + "=" + (value || "")  + expires + "; path=/";
        }

        function getCookie(name) {
            const nameEQ = name + "=";
            const ca = document.cookie.split(';');
            for(let i = 0; i < ca.length; i++) {
                let c = ca[i];
                while (c.charAt(0) === ' ') c = c.substring(1, c.length);
                if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
            }
            return null;
        }

        if (!getCookie('cookie_consent')) {
            banner.style.display = 'block';
        }

        acceptBtn.addEventListener('click', function () {
            setCookie('cookie_consent', 'true', 365);
            banner.style.display = 'none';
        });

        declineBtn.addEventListener('click', function () {
            setCookie('cookie_consent', 'false', null); // Session cookie
            banner.style.display = 'none';
        });
    }
});