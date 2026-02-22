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
            nextBtnText: 'Siguiente',
            prevBtnText: 'Anterior',
            doneBtnText: 'Entendido',
            progressText: '{{current}} de {{total}}',
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
        company_dashboard: [
            {
                element: '#tour-company-header',
                popover: {
                    title: 'Panel de empresa',
                    description: 'Aquí verás la información general de la empresa: nombre, logo y enlace web.',
                },
            },
            {
                element: '#tour-company-kpis',
                popover: {
                    title: 'Indicadores clave',
                    description: 'Estos KPIs te muestran el total de posiciones, las activas y el número de candidatos de un vistazo.',
                },
            },
            {
                element: '#tour-company-positions',
                popover: {
                    title: 'Tabla de posiciones',
                    description: 'Aquí aparecen todas las posiciones de la empresa con su estado, tipo y candidatos.',
                },
            },
            {
                element: '#tour-btn-edit-company',
                popover: {
                    title: 'Editar empresa',
                    description: 'Haz clic aquí para modificar los datos de la empresa (nombre, web, logo...).',
                },
            },
            {
                element: '#tour-btn-new-position',
                popover: {
                    title: 'Crear posición',
                    description: 'Crea una nueva oferta de trabajo para esta empresa.',
                },
            },
        ],

        position_list: [
            {
                element: '#tour-position-filters',
                popover: {
                    title: 'Filtros de estado',
                    description: 'Filtra las posiciones por estado: todas, publicadas, borradores, pausadas o cerradas.',
                },
            },
            {
                element: '#tour-position-table',
                popover: {
                    title: 'Listado de posiciones',
                    description: 'Haz clic en cualquier posición para ver su detalle, candidatos y case studies.',
                },
            },
            {
                element: '#tour-btn-new-position',
                popover: {
                    title: 'Nueva posición',
                    description: 'Crea una nueva oferta de trabajo desde aquí.',
                },
            },
        ],

        position_detail: [
            {
                element: '#tour-position-status',
                popover: {
                    title: 'Ciclo de vida',
                    description: 'Cambia el estado de la posición: publícala, páusala o ciérrala según avance el proceso.',
                },
            },
            {
                element: '#tour-position-description',
                popover: {
                    title: 'Descripción de la oferta',
                    description: 'Contenido de la oferta: descripción, requisitos, beneficios y sobre la empresa.',
                },
            },
            {
                element: '#tour-position-candidates',
                popover: {
                    title: 'Candidatos',
                    description: 'Listado de candidatos para esta posición. Haz clic en uno para ver su perfil completo.',
                },
            },
            {
                element: '#tour-position-info',
                popover: {
                    title: 'Datos de la oferta',
                    description: 'Resumen con departamento, ubicación, tipo de empleo, salario y fechas clave.',
                },
            },
            {
                element: '#tour-position-casestudies',
                popover: {
                    title: 'Case Studies',
                    description: 'Si la posición incluye case study, aquí verás los casos creados y podrás añadir nuevos.',
                },
            },
        ],

        position_form: [
            {
                element: '#tour-position-basic',
                popover: {
                    title: 'Información básica',
                    description: 'Completa el título, departamento, ubicación, tipo de empleo y salario.',
                },
            },
            {
                element: '#tour-position-ai-btn',
                popover: {
                    title: 'Generar con IA',
                    description: 'Escribe al menos el título y pulsa este botón. La IA generará descripción, requisitos y beneficios automáticamente.',
                },
            },
            {
                element: '#tour-position-content',
                popover: {
                    title: 'Contenido de la oferta',
                    description: 'Edita o revisa el contenido generado. Puedes modificarlo libremente antes de guardar.',
                },
            },
            {
                element: '#tour-position-options',
                popover: {
                    title: 'Opciones',
                    description: 'Activa el case study si quieres enviar pruebas prácticas a los candidatos de esta posición.',
                },
            },
        ],

        candidate_form: [
            {
                element: '#tour-candidate-cv',
                popover: {
                    title: 'Sube el CV',
                    description: 'Sube un PDF y la IA extraerá automáticamente los datos del candidato (nombre, email, teléfono, LinkedIn).',
                },
            },
            {
                element: '#tour-candidate-personal',
                popover: {
                    title: 'Datos personales',
                    description: 'Estos campos se autocompletarán con la información extraída del CV. Puedes editarlos si necesitas corregir algo.',
                },
            },
        ],

        candidate_detail: [
            {
                element: '#tour-candidate-status',
                popover: {
                    title: 'Estado del pipeline',
                    description: 'Cambia el estado del candidato a medida que avanza en el proceso de selección.',
                },
            },
            {
                element: '#tour-candidate-rating',
                popover: {
                    title: 'Valoración',
                    description: 'Puntúa al candidato de 1 a 5 estrellas para priorizar entre candidatos.',
                },
            },
            {
                element: '#tour-candidate-cv',
                popover: {
                    title: 'Currículum',
                    description: 'Visualiza, descarga o sube un nuevo CV. La IA lo analizará automáticamente.',
                },
            },
            {
                element: '#tour-candidate-ai',
                popover: {
                    title: 'Análisis IA',
                    description: 'Resumen generado por IA con puntos fuertes, débiles y puntuación de encaje con la posición.',
                },
            },
            {
                element: '#tour-candidate-interviews',
                popover: {
                    title: 'Entrevistas',
                    description: 'Programa, consulta y gestiona las entrevistas del candidato.',
                },
            },
            {
                element: '#tour-candidate-casestudies',
                popover: {
                    title: 'Casos prácticos',
                    description: 'Envía case studies y consulta el estado de las entregas.',
                },
            },
            {
                element: '#tour-candidate-evaluations',
                popover: {
                    title: 'Evaluación IA',
                    description: 'Genera una evaluación global del candidato usando toda la información disponible (CV, entrevistas, case studies).',
                },
            },
            {
                element: '#tour-candidate-notes',
                popover: {
                    title: 'Notas del reclutador',
                    description: 'Espacio libre para anotar impresiones, recordatorios o comentarios sobre el candidato.',
                },
            },
            {
                element: '#tour-candidate-actions',
                popover: {
                    title: 'Acciones rápidas',
                    description: 'Accesos directos para programar entrevistas, generar casos prácticos o evaluaciones IA.',
                },
            },
            {
                element: '#tour-candidate-sidebar-ai',
                popover: {
                    title: 'Resumen IA (sidebar)',
                    description: 'Vista compacta del análisis IA con puntos fuertes y débiles en la barra lateral.',
                },
            },
        ],

        interview_form: [
            {
                popover: {
                    title: 'Programar entrevista',
                    description: 'Completa la fecha, hora, duración, entrevistador y ubicación o enlace de videollamada para programar la entrevista.',
                },
            },
        ],

        interview_edit: [
            {
                popover: {
                    title: 'Editar entrevista',
                    description: 'Tras realizar la entrevista, actualiza el estado, añade notas, puntos fuertes/débiles y una puntuación global.',
                },
            },
        ],

        casestudy_form: [
            {
                element: '#tour-cs-briefing',
                popover: {
                    title: 'Tu idea',
                    description: 'Escribe el título y una descripción breve de lo que quieres evaluar. La IA se encargará del resto.',
                },
            },
            {
                element: '#tour-cs-ai-btn',
                popover: {
                    title: 'Generar con IA',
                    description: 'Pulsa aquí para que la IA genere el contenido completo del case study basándose en tu briefing.',
                },
            },
            {
                element: '#tour-cs-content',
                popover: {
                    title: 'Contenido generado',
                    description: 'Revisa y edita el case study y los criterios de evaluación antes de guardarlo.',
                },
            },
        ],

        casestudy_generate: [
            {
                popover: {
                    title: 'Caso práctico con IA',
                    description: 'La IA genera automáticamente un caso práctico personalizado para este candidato basándose en su perfil y la posición. Puedes editar el resultado antes de enviarlo.',
                },
            },
        ],

        evaluation_page: [
            {
                element: '#tour-eval-generate',
                popover: {
                    title: 'Generar evaluación',
                    description: 'Pulsa este botón para que la IA analice toda la información del candidato (CV, entrevistas, case studies) y genere una evaluación global.',
                },
            },
            {
                element: '#tour-eval-scores',
                popover: {
                    title: 'Puntuaciones',
                    description: 'Desglose de puntuaciones: global, CV, entrevista y case study, con una recomendación final (contratar, esperar o rechazar).',
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
