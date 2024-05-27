document.addEventListener("DOMContentLoaded", function() {
    var projectItems = document.querySelectorAll('.project-item');

    projectItems.forEach(function(item) {
        item.addEventListener('click', function() {
            var projectDetails = this.nextElementSibling;
            if (projectDetails && projectDetails.classList.contains('project-details')) {
                projectDetails.classList.toggle('hidden');
            }
        });
    });
});
