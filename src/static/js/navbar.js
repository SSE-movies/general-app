document.addEventListener('DOMContentLoaded', function() {
    function createNavbar(options = {}) {
        const {
            title = 'Dashboard',
            username = 'User',
            logoutUrl = '/logout'
        } = options;

        // Create navbar element
        const navbarHtml = `
            <nav class="bg-sage p-4 flex justify-between items-center">
                <h1 class="text-taupe text-2xl font-bold">${title}</h1>
                <div class="flex items-center space-x-4">
                    <span class="text-cream hidden md:inline">
                        Logged in as: ${username}
                    </span>
                    <a href="${logoutUrl}" class="bg-golden text-cream px-4 py-2 rounded hover:opacity-90">
                        Logout
                    </a>
                </div>
            </nav>
        `;

        // Create a container for the navbar
        const navbarContainer = document.createElement('div');
        navbarContainer.innerHTML = navbarHtml.trim();
        
        // Insert the navbar at the top of the body
        document.body.insertBefore(navbarContainer.firstChild, document.body.firstChild);
    }

    // Expose the function globally so it can be called from other scripts
    window.createNavbar = createNavbar;
});