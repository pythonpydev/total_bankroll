document.addEventListener('DOMContentLoaded', function () {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    const themeIcon = themeToggle.querySelector('i');

    function setDarkTheme(isDark) {
        body.classList.toggle('dark-mode', isDark);
        themeIcon.classList.toggle('bi-sun-fill', !isDark);
        themeIcon.classList.toggle('bi-moon-fill', isDark);
        localStorage.setItem('theme', isDark ? 'dark' : 'light');

        // Dispatch a custom event after the theme is set
        const event = new Event('theme-changed');
        document.dispatchEvent(event);
    }

    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    setDarkTheme(savedTheme ? savedTheme === 'dark' : prefersDark);

    themeToggle.addEventListener('click', () => {
        setDarkTheme(!body.classList.contains('dark-mode'));
    });
});