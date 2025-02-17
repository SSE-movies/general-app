document.addEventListener('DOMContentLoaded', function() {
    function createNavbar(options = {}) {
        const {
            title = 'Dashboard',
            username = 'User',
            logoutUrl = '/logout'
        } = options;

        // Create navbar element
        const navbarHtml = `
            <nav class="bg-sage px-6 py-4 flex flex-col md:flex-row items-center w-full">
              <!-- Left Column: Title -->
              <div class="md:flex-1 flex justify-start items-center">
                <h1 class="text-taupe text-2xl font-bold">
                  ${title}
                </h1>
              </div>
            
              <!-- Center Column: Navigation Links -->
              <div class="md:flex-1 flex justify-center mt-2 md:mt-0">
                <ul class="flex space-x-8">
                  <li>
                    <a href="/search" class="text-cream hover:text-taupe px-3 py-2 rounded transition-colors">
                      Search
                    </a>
                  </li>
                  <li>
                    <a href="/my_watchlist" class="text-cream hover:text-taupe px-3 py-2 rounded transition-colors">
                      Watchlist
                    </a>
                  </li>
                </ul>
              </div>
            
              <!-- Right Column: Username & Logout -->
              <div class="md:flex-1 flex justify-end items-center space-x-4 mt-2 md:mt-0">
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