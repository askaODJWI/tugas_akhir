document.addEventListener('DOMContentLoaded', function () {
            document.querySelectorAll('.accordion-item').forEach(item => {
                const collapseElement = item.querySelector('.accordion-collapse');
                const carouselElement = item.querySelector('.carousel');

                if (collapseElement && carouselElement) {
                    let carouselInstance = bootstrap.Carousel.getInstance(carouselElement);
                    if (carouselInstance) {
                        collapseElement.addEventListener('hide.bs.collapse', function () {
                            carouselInstance.pause();
                        });
                        collapseElement.addEventListener('show.bs.collapse', function () {
                            carouselInstance.cycle();
                        });
                    } else {
                        // Fallback or error logging if carousel instance isn't found
                        // This might happen if the carousel HTML is malformed or Bootstrap JS hasn't processed it yet.
                        // For dynamically added content, ensure carousels are initialized after insertion.
                        // console.warn('Carousel instance not found for:', carouselElement);
                    }
                }
            });
        });
function toggleResults() {
    const full = document.getElementById("full-results");
    const cbrs = document.getElementById("cbrs-results");
    const isFullVisible = full.style.display !== "none";

    full.style.display = isFullVisible ? "none" : "block";
    cbrs.style.display = isFullVisible ? "block" : "none";
}