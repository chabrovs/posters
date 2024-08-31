window.addEventListener('scroll', function() {
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight) {
        document.body.classList.add('scrolled');   

    } else {
        document.body.classList.remove('scrolled');
    }
});

$(document).ready(function() {
    // Function to handle active class change
    $('body > header > nav > div > ul:nth-child(2) > li').click(function() {
        // Remove 'active' class from all <li>
        $('body > header > nav > div > ul:nth-child(2) > li').removeClass('active');
        
        // Add 'active' class to the clicked <li>
        $(this).addClass('active');
        
        // Save the index of the active <li> to localStorage
        var activeIndex = $('body > header > nav > div > ul:nth-child(2) > li').index(this);
        localStorage.setItem('activeIndex', activeIndex);
    });

    $('body > header > nav > div > ul.nav.navbar-nav.navbar-right > li').click(function() {
        $('body > header > nav > div > ul:nth-child(2) > li').removeClass('active');
        // Add 'active' class to the clicked <li>
        $(this).addClass('active');
        
        // Save the index of the active <li> to localStorage
        var activeIndex = $('body > header > nav > div > ul:nth-child(2) > li').index(this);
        localStorage.setItem('activeIndex', activeIndex);
    });
    
    // On page load, check for the stored index in localStorage
    var savedIndex = localStorage.getItem('activeIndex');
    
    // If an index was saved, set the corresponding <li> as active
    if (savedIndex !== null) {
        $('body > header > nav > div > ul:nth-child(2) > li').removeClass('active');
        $('body > header > nav > div > ul:nth-child(2) > li').eq(savedIndex).addClass('active');
    }
    
});