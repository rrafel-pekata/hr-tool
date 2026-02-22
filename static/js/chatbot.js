document.addEventListener('alpine:init', function () {
    Alpine.data('chatbotWidget', function () {
        return {
            open: false,
            messages: [],
            input: '',
            loading: false,

            get csrfToken() {
                var el = document.querySelector('#chatbot-csrf input[name="csrfmiddlewaretoken"]');
                if (el) return el.value;
                // Fallback to cookie
                var match = document.cookie.match(/csrftoken=([^;]+)/);
                return match ? match[1] : '';
            },

            toggle: function () {
                this.open = !this.open;
                if (this.open) {
                    this.$nextTick(function () {
                        var input = document.querySelector('.chatbot-input');
                        if (input) input.focus();
                    });
                }
            },

            send: function () {
                var text = this.input.trim();
                if (!text || this.loading) return;

                this.messages.push({ role: 'user', content: text });
                this.input = '';
                this.loading = true;
                this.scrollToBottom();

                var self = this;
                fetch('/chatbot/message/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.csrfToken,
                    },
                    body: JSON.stringify({ message: text }),
                })
                .then(function (res) { return res.json(); })
                .then(function (data) {
                    self.loading = false;
                    if (data.answer) {
                        self.messages.push({ role: 'bot', content: data.answer });
                    } else if (data.error) {
                        self.messages.push({ role: 'bot', content: '<p>' + data.error + '</p>' });
                    }
                    self.scrollToBottom();
                })
                .catch(function () {
                    self.loading = false;
                    self.messages.push({ role: 'bot', content: '<p>Error de conexión. Inténtalo de nuevo.</p>' });
                    self.scrollToBottom();
                });
            },

            clear: function () {
                var self = this;
                fetch('/chatbot/clear/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.csrfToken,
                    },
                })
                .then(function () {
                    self.messages = [];
                })
                .catch(function () {
                    // silently fail
                });
            },

            // ── Tour integration ──────────────────────────────
            startTour: function () {
                this.open = false;
                var page = this.$el.dataset.tourPage || '';
                if (page && window.PekataTours) {
                    window.PekataTours.run(page, { skipMark: true });
                }
            },

            resetTours: function () {
                if (window.PekataTours) {
                    window.PekataTours.resetAll();
                    window.location.reload();
                }
            },

            handleKey: function (e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.send();
                }
            },

            scrollToBottom: function () {
                this.$nextTick(function () {
                    var container = document.querySelector('.chatbot-messages');
                    if (container) container.scrollTop = container.scrollHeight;
                });
            },
        };
    });
});
