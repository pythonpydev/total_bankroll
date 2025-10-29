document.addEventListener('DOMContentLoaded', function () {
    const banner = document.getElementById('cookieConsentBanner');
    const acceptBtn = document.getElementById('acceptCookie');
    const declineBtn = document.getElementById('declineCookie');

    // If the banner elements don't exist on the page, do nothing.
    if (!banner || !acceptBtn || !declineBtn) {
        return;
    }

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
});