class DashboardManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupCardHoverEffects();
        this.setupTableAnimations();
        this.setupWelcomeAnimation();
    }

    setupCardHoverEffects() {
        const cards = document.querySelectorAll('.function-card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-8px)';
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
            });
        });
    }

    setupTableAnimations() {
        const tableRows = document.querySelectorAll('.table tbody tr');
        tableRows.forEach((row, index) => {
            row.style.opacity = '0';
            row.style.transform = 'translateX(-20px)';
            setTimeout(() => {
                row.style.transition = 'all 0.3s ease';
                row.style.opacity = '1';
                row.style.transform = 'translateX(0)';
            }, index * 100);
        });
    }

    setupWelcomeAnimation() {
        const welcomeSection = document.querySelector('.welcome-section');
        if (welcomeSection) {
            welcomeSection.style.opacity = '0';
            welcomeSection.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                welcomeSection.style.transition = 'all 0.6s ease';
                welcomeSection.style.opacity = '1';
                welcomeSection.style.transform = 'translateY(0)';
            }, 100);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new DashboardManager();
});
