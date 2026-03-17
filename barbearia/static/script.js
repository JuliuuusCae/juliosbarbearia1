document.addEventListener("DOMContentLoaded", () => {
    // Módulo para gerenciar efeitos de página
    const PageEffects = (() => {
        const init = () => {
            // Animação ao carregar a página
            document.body.classList.add("fade-in");
            setupPageTransition();
        };

        const setupPageTransition = () => {
            const links = document.querySelectorAll("a");
            links.forEach(link => {
                link.addEventListener("click", function(e) {
                    const destino = this.href;
                    if (destino && destino.startsWith(window.location.origin)) {
                        e.preventDefault();
                        document.body.classList.add("fade-out");
                        setTimeout(() => {
                            window.location.href = destino;
                        }, 300); 
                    }
                });
            });
        };

        return { init };
    })();

    // Módulo para gerenciar a seleção de horários
    const TimeSlotSelector = (() => {
        const slots = document.querySelectorAll(".slot input[type=\"radio\"]");

        const init = () => {
            slots.forEach(slot => {
                slot.addEventListener("change", handleSlotChange);
            });
        };

        const handleSlotChange = function() {
            document.querySelectorAll(".slot").forEach(el => {
                el.classList.remove("ativo");
            });
            this.parentElement.classList.add("ativo");
        };

        return { init };
    })();

    // Módulo para gerenciar o modal de confirmação
    const ConfirmationModal = (() => {
        const form = document.getElementById("formAgendamento");
        const modal = document.getElementById("confirmModal");
        const btnSim = document.getElementById("confirmarSim");
        const btnNao = document.getElementById("confirmarNao");

        let permitirEnvio = false;

        const init = () => {
            if (form && modal && btnSim && btnNao) {
                form.addEventListener("submit", handleSubmit);
                btnSim.addEventListener("click", handleConfirm);
                btnNao.addEventListener("click", handleCancel);
            }
        };

        const handleSubmit = (e) => {
            if (!permitirEnvio) {
                e.preventDefault();
                modal.style.display = "flex";
            }
        };

        const handleConfirm = () => {
            permitirEnvio = true;
            form.submit();
        };

        const handleCancel = () => {
            modal.style.display = "none";
        };

        return { init };
    })();

    // Módulo para gerenciar efeitos de scroll (incluindo Zoom Out)
    const ScrollEffects = (() => {
        const header = document.querySelector(".header");
        const innerLogo = document.querySelector(".inner");
        const heroSection = document.querySelector(".hero");

        let ticking = false;

        const init = () => {
            window.addEventListener("scroll", updateScrollEffects, { passive: true });
            updateScrollEffects(); 
        };

        const updateScrollEffects = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const scrollY = window.scrollY;

                    // 1. Efeito de mostrar/esconder header
                    if (header) {
                        if (scrollY > 100) {
                            header.classList.add("show");
                        } else {
                            header.classList.remove("show");
                        }
                    }

                    // 2. Efeito de ZOOM OUT no Scroll (Logo Hero)
                    if (innerLogo && heroSection) {
                        const heroHeight = heroSection.offsetHeight;
                        // Calcula a escala: começa em 1.5 e diminui até 1 conforme rola
                        // O zoom out acontece enquanto o usuário rola pela seção hero
                        let scrollFraction = scrollY / heroHeight;
                        if (scrollFraction > 1) scrollFraction = 1;
                        
                        // Escala vai de 1.5 (zoom in inicial) para 1.0 (zoom out no scroll)
                        const scaleValue = 1.5 - (scrollFraction * 0.5);
                        
                        // Opacidade diminui conforme rola para sumir suavemente
                        const opacityValue = 1 - scrollFraction;

                        innerLogo.style.transform = `scale(${scaleValue})`;
                        innerLogo.style.opacity = opacityValue;
                    }

                    ticking = false;
                });
                ticking = true;
            }
        };

        return { init };
    })();

    // Inicializa todos os módulos
    PageEffects.init();
    TimeSlotSelector.init();
    ConfirmationModal.init();
    ScrollEffects.init();
});
