/**
 * Pekata ATS — Interactive guided tours using Driver.js
 * State persisted in localStorage, no backend changes needed.
 */
(function () {
    'use strict';

    const LS_PREFIX = 'pekata_tour_done_';

    // ── Helpers ────────────────────────────────────────────────
    function markDone(page) {
        localStorage.setItem(LS_PREFIX + page, '1');
    }
    function isDone(page) {
        return localStorage.getItem(LS_PREFIX + page) === '1';
    }
    function resetAll() {
        Object.keys(localStorage).forEach(function (k) {
            if (k.startsWith(LS_PREFIX)) localStorage.removeItem(k);
        });
    }

    /** Filter out steps whose element doesn't exist on the page */
    function filterSteps(steps) {
        return steps.filter(function (s) {
            if (!s.element) return true;               // steps without element always show
            return document.querySelector(s.element);   // skip missing elements
        });
    }

    /** Build and drive a tour for the given page key */
    function runTour(pageKey, opts) {
        opts = opts || {};
        var raw = TOURS[pageKey];
        if (!raw) return;

        var steps = filterSteps(raw);
        if (steps.length === 0) return;

        var driverObj = window.driver.js.driver({
            showProgress: true,
            animate: true,
            overlayColor: 'rgba(0,0,0,.55)',
            stagePadding: 8,
            stageRadius: 8,
            popoverClass: 'pekata-tour',
            nextBtnText: gettext('Siguiente'),
            prevBtnText: gettext('Anterior'),
            doneBtnText: gettext('Entendido'),
            progressText: '{{current}} ' + gettext('de') + ' {{total}}',
            steps: steps,
            onDestroyStarted: function () {
                if (!opts.skipMark) markDone(pageKey);
                driverObj.destroy();
            },
        });

        driverObj.drive();
    }

    // ── Tour definitions (per page) ──────────────────────────
    var TOURS = {
        company_list: [
            {
                popover: {
                    title: gettext('Bienvenido a Pekata ATS'),
                    description: gettext('Lo primero que necesitas es crear tu empresa. Toda la gestión de posiciones y candidatos se organiza dentro de una empresa.'),
                },
            },
            {
                element: '#tour-btn-new-company',
                popover: {
                    title: gettext('Crear empresa'),
                    description: gettext('Haz clic aquí para crear tu primera empresa. Rellena los datos básicos y, si quieres, usa la IA para mejorar la descripción.'),
                },
            },
            {
                element: '#tour-company-grid',
                popover: {
                    title: gettext('Tus empresas'),
                    description: gettext('Aquí aparecerán tus empresas. Haz clic en cualquiera para ver su dashboard con posiciones, candidatos y KPIs.'),
                },
            },
        ],

        company_form: [
            {
                popover: {
                    title: gettext('Crear tu empresa'),
                    description: gettext('Completa los datos de tu empresa. Cuanta más información añadas, mejores serán las sugerencias de la IA al generar ofertas de trabajo.'),
                },
            },
            {
                element: '#tour-company-basic',
                popover: {
                    title: gettext('Datos básicos'),
                    description: gettext('Nombre, descripción, web y logo. La descripción es especialmente importante: la IA la usará como contexto para generar ofertas.'),
                },
            },
            {
                element: '#tour-company-ai-btn',
                popover: {
                    title: gettext('Mejorar con IA'),
                    description: gettext('Escribe al menos el nombre y pulsa este botón. La IA generará una descripción profesional, beneficios y cultura automáticamente.'),
                },
            },
            {
                element: '#tour-company-offers',
                popover: {
                    title: gettext('Info para ofertas'),
                    description: gettext('Beneficios, jornada, política de remoto y cultura. Esta información se reutilizará en todas las ofertas que generes con IA.'),
                },
            },
        ],

        company_dashboard: [
            {
                element: '#tour-company-header',
                popover: {
                    title: gettext('Panel de empresa'),
                    description: gettext('Aquí verás la información general de la empresa: nombre, logo y enlace web.'),
                },
            },
            {
                element: '#tour-company-kpis',
                popover: {
                    title: gettext('Indicadores clave'),
                    description: gettext('Estos KPIs te muestran el total de posiciones, las activas y el número de candidatos de un vistazo.'),
                },
            },
            {
                element: '#tour-company-positions',
                popover: {
                    title: gettext('Tabla de posiciones'),
                    description: gettext('Aquí aparecen todas las posiciones de la empresa con su estado, tipo y candidatos.'),
                },
            },
            {
                element: '#tour-btn-edit-company',
                popover: {
                    title: gettext('Editar empresa'),
                    description: gettext('Haz clic aquí para modificar los datos de la empresa (nombre, web, logo...).'),
                },
            },
            {
                element: '#tour-btn-new-position',
                popover: {
                    title: gettext('Crear posición'),
                    description: gettext('Crea una nueva oferta de trabajo para esta empresa.'),
                },
            },
        ],

        position_list: [
            {
                element: '#tour-position-filters',
                popover: {
                    title: gettext('Filtros de estado'),
                    description: gettext('Filtra las posiciones por estado: todas, publicadas, borradores, pausadas o cerradas.'),
                },
            },
            {
                element: '#tour-position-table',
                popover: {
                    title: gettext('Listado de posiciones'),
                    description: gettext('Haz clic en cualquier posición para ver su detalle, candidatos y case studies.'),
                },
            },
            {
                element: '#tour-btn-new-position',
                popover: {
                    title: gettext('Nueva posición'),
                    description: gettext('Crea una nueva oferta de trabajo desde aquí.'),
                },
            },
        ],

        position_detail: [
            {
                element: '#tour-position-status',
                popover: {
                    title: gettext('Ciclo de vida'),
                    description: gettext('Cambia el estado de la posición: publícala, páusala o ciérrala según avance el proceso.'),
                },
            },
            {
                element: '#tour-position-description',
                popover: {
                    title: gettext('Descripción de la oferta'),
                    description: gettext('Contenido de la oferta: descripción, requisitos, beneficios y sobre la empresa.'),
                },
            },
            {
                element: '#tour-position-candidates',
                popover: {
                    title: gettext('Candidatos'),
                    description: gettext('Listado de candidatos para esta posición. Haz clic en uno para ver su perfil completo.'),
                },
            },
            {
                element: '#tour-position-info',
                popover: {
                    title: gettext('Datos de la oferta'),
                    description: gettext('Resumen con departamento, ubicación, tipo de empleo, salario y fechas clave.'),
                },
            },
            {
                element: '#tour-position-casestudies',
                popover: {
                    title: gettext('Case Studies'),
                    description: gettext('Si la posición incluye case study, aquí verás los casos creados y podrás añadir nuevos.'),
                },
            },
        ],

        position_form: [
            {
                element: '#tour-position-basic',
                popover: {
                    title: gettext('Información básica'),
                    description: gettext('Completa el título, departamento, ubicación, tipo de empleo y salario.'),
                },
            },
            {
                element: '#tour-position-ai-btn',
                popover: {
                    title: gettext('Generar con IA'),
                    description: gettext('Escribe al menos el título y pulsa este botón. La IA generará descripción, requisitos y beneficios automáticamente.'),
                },
            },
            {
                element: '#tour-position-content',
                popover: {
                    title: gettext('Contenido de la oferta'),
                    description: gettext('Edita o revisa el contenido generado. Puedes modificarlo libremente antes de guardar.'),
                },
            },
            {
                element: '#tour-position-options',
                popover: {
                    title: gettext('Opciones'),
                    description: gettext('Activa el case study si quieres enviar pruebas prácticas a los candidatos de esta posición.'),
                },
            },
        ],

        candidate_form: [
            {
                element: '#tour-candidate-cv',
                popover: {
                    title: gettext('Sube el CV'),
                    description: gettext('Sube un PDF y la IA extraerá automáticamente los datos del candidato (nombre, email, teléfono, LinkedIn).'),
                },
            },
            {
                element: '#tour-candidate-personal',
                popover: {
                    title: gettext('Datos personales'),
                    description: gettext('Estos campos se autocompletarán con la información extraída del CV. Puedes editarlos si necesitas corregir algo.'),
                },
            },
        ],

        candidate_detail: [
            {
                element: '#tour-candidate-status',
                popover: {
                    title: gettext('Estado del pipeline'),
                    description: gettext('Cambia el estado del candidato a medida que avanza en el proceso de selección.'),
                },
            },
            {
                element: '#tour-candidate-rating',
                popover: {
                    title: gettext('Valoración'),
                    description: gettext('Puntúa al candidato de 1 a 5 estrellas para priorizar entre candidatos.'),
                },
            },
            {
                element: '#tour-candidate-cv',
                popover: {
                    title: gettext('Currículum'),
                    description: gettext('Visualiza, descarga o sube un nuevo CV. La IA lo analizará automáticamente.'),
                },
            },
            {
                element: '#tour-candidate-ai',
                popover: {
                    title: gettext('Análisis IA'),
                    description: gettext('Resumen generado por IA con puntos fuertes, débiles y puntuación de encaje con la posición.'),
                },
            },
            {
                element: '#tour-candidate-interviews',
                popover: {
                    title: gettext('Entrevistas'),
                    description: gettext('Programa, consulta y gestiona las entrevistas del candidato.'),
                },
            },
            {
                element: '#tour-candidate-casestudies',
                popover: {
                    title: gettext('Casos prácticos'),
                    description: gettext('Envía case studies y consulta el estado de las entregas.'),
                },
            },
            {
                element: '#tour-candidate-evaluations',
                popover: {
                    title: gettext('Evaluación IA'),
                    description: gettext('Genera una evaluación global del candidato usando toda la información disponible (CV, entrevistas, case studies).'),
                },
            },
            {
                element: '#tour-candidate-notes',
                popover: {
                    title: gettext('Notas del reclutador'),
                    description: gettext('Espacio libre para anotar impresiones, recordatorios o comentarios sobre el candidato.'),
                },
            },
            {
                element: '#tour-candidate-actions',
                popover: {
                    title: gettext('Acciones rápidas'),
                    description: gettext('Accesos directos para programar entrevistas, generar casos prácticos o evaluaciones IA.'),
                },
            },
            {
                element: '#tour-candidate-sidebar-ai',
                popover: {
                    title: gettext('Resumen IA (sidebar)'),
                    description: gettext('Vista compacta del análisis IA con puntos fuertes y débiles en la barra lateral.'),
                },
            },
        ],

        interview_form: [
            {
                popover: {
                    title: gettext('Programar entrevista'),
                    description: gettext('Completa la fecha, hora, duración, entrevistador y ubicación o enlace de videollamada para programar la entrevista.'),
                },
            },
        ],

        interview_edit: [
            {
                popover: {
                    title: gettext('Editar entrevista'),
                    description: gettext('Tras realizar la entrevista, actualiza el estado, añade notas, puntos fuertes/débiles y una puntuación global.'),
                },
            },
        ],

        casestudy_form: [
            {
                element: '#tour-cs-briefing',
                popover: {
                    title: gettext('Tu idea'),
                    description: gettext('Escribe el título y una descripción breve de lo que quieres evaluar. La IA se encargará del resto.'),
                },
            },
            {
                element: '#tour-cs-ai-btn',
                popover: {
                    title: gettext('Generar con IA'),
                    description: gettext('Pulsa aquí para que la IA genere el contenido completo del case study basándose en tu briefing.'),
                },
            },
            {
                element: '#tour-cs-content',
                popover: {
                    title: gettext('Contenido generado'),
                    description: gettext('Revisa y edita el case study y los criterios de evaluación antes de guardarlo.'),
                },
            },
        ],

        casestudy_generate: [
            {
                popover: {
                    title: gettext('Caso práctico con IA'),
                    description: gettext('La IA genera automáticamente un caso práctico personalizado para este candidato basándose en su perfil y la posición. Puedes editar el resultado antes de enviarlo.'),
                },
            },
        ],

        evaluation_page: [
            {
                element: '#tour-eval-generate',
                popover: {
                    title: gettext('Generar evaluación'),
                    description: gettext('Pulsa este botón para que la IA analice toda la información del candidato (CV, entrevistas, case studies) y genere una evaluación global.'),
                },
            },
            {
                element: '#tour-eval-scores',
                popover: {
                    title: gettext('Puntuaciones'),
                    description: gettext('Desglose de puntuaciones: global, CV, entrevista y case study, con una recomendación final (contratar, esperar o rechazar).'),
                },
            },
        ],
    };

    // ── Auto-start tour on first visit ────────────────────────
    function autoStart() {
        var el = document.querySelector('[data-tour-page]');
        if (!el) return;
        var page = el.dataset.tourPage;
        if (!page || isDone(page)) return;
        // Small delay so the page is fully rendered
        setTimeout(function () { runTour(page); }, 600);
    }

    // Wait for both DOM and Driver.js to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', autoStart);
    } else {
        setTimeout(autoStart, 600);
    }

    // Expose for global access
    window.PekataTours = {
        run: runTour,
        resetAll: resetAll,
        isDone: isDone,
    };
})();
