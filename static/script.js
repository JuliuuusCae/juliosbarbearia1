document.addEventListener("DOMContentLoaded", () => {

    // Módulo para gerenciar efeitos de página
    const PageEffects = (() => {
        const init = () => {
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

    // Módulo: Logo voa para o header ao rolar
    const LogoFlyEffect = (() => {
        const heroSection = document.querySelector(".hero");
        const innerLogo = document.querySelector(".inner");
        const headerLogo = document.querySelector(".header__logo");
        const header = document.querySelector(".header");

        // Cria o logo-img no header (escondido inicialmente)
        let headerLogoImg = null;

        const init = () => {
            if (!heroSection || !innerLogo || !headerLogo) return;

            // Insere imagem no lugar do texto do header
            headerLogoImg = document.createElement("img");
            headerLogoImg.src = "/static/logo.png";
            headerLogoImg.className = "header__logo-img";
            headerLogoImg.style.opacity = "0";
            headerLogo.parentNode.insertBefore(headerLogoImg, headerLogo);

            window.addEventListener("scroll", onScroll, { passive: true });
            onScroll();
        };

        const onScroll = () => {
            const scrollY = window.scrollY;
            const heroHeight = heroSection.offsetHeight;

            // Progresso do scroll dentro da hero (0 a 1)
            let progress = scrollY / heroHeight;
            if (progress > 1) progress = 1;

            // --- Hero logo: zoom out + fade out ---
            const scale = 1.5 - progress * 0.5;
            const heroOpacity = 1 - progress * 1.4; // some um pouco antes do fim
            innerLogo.style.transform = `scale(${Math.max(scale, 1)})`;
            innerLogo.style.opacity = Math.max(heroOpacity, 0);

            // --- Header: aparece a partir de 30% do scroll ---
            if (scrollY > heroHeight * 0.3) {
                header.classList.add("show");
            } else {
                header.classList.remove("show");
            }

            // --- Troca texto "Barbearia" pelo logo no header ---
            // A transição começa em 60% do scroll e termina em 90%
            const fadeStart = 0.6;
            const fadeEnd = 0.9;
            let logoProgress = (progress - fadeStart) / (fadeEnd - fadeStart);
            logoProgress = Math.min(Math.max(logoProgress, 0), 1);

            // Texto some, imagem aparece
            headerLogo.style.opacity = 1 - logoProgress;
            headerLogo.style.transform = `scale(${1 - logoProgress * 0.2})`;
            if (headerLogoImg) {
                headerLogoImg.style.opacity = logoProgress;
                headerLogoImg.style.transform = `scale(${0.8 + logoProgress * 0.2})`;
            }
        };

        return { init };
    })();

    // Módulo para gerenciar a seleção de data e recarregar a página
    const DateSelector = (() => {
        const dateInput = document.querySelector("input[type=\"date\"][name=\"data\"]");

        const init = () => {
            if (dateInput) {
                dateInput.addEventListener("change", handleDateChange);
            }
        };

        const handleDateChange = function() {
            const newDate = this.value;
            if (newDate) {
                window.location.href = `${window.location.origin}${window.location.pathname}?data=${newDate}`;
            }
        };

        return { init };
    })();

    // Inicializa todos os módulos
    PageEffects.init();
    TimeSlotSelector.init();
    ConfirmationModal.init();
    LogoFlyEffect.init();
    DateSelector.init();
});