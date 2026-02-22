document.addEventListener('alpine:init', function () {
    Alpine.data('notificationBell', function () {
        return {
            open: false,
            count: parseInt(document.querySelector('meta[name="unread-notification-count"]')?.content || '0', 10),
            notifications: [],
            polling: null,

            init: function () {
                var self = this;
                this.polling = setInterval(function () {
                    self.fetchCount();
                }, 30000);
            },

            destroy: function () {
                if (this.polling) clearInterval(this.polling);
            },

            get csrfToken() {
                var meta = document.querySelector('meta[name="csrf-token"]');
                if (meta) return meta.content;
                var match = document.cookie.match(/csrftoken=([^;]+)/);
                return match ? match[1] : '';
            },

            toggle: function () {
                this.open = !this.open;
                if (this.open) this.fetchList();
            },

            fetchCount: function () {
                var self = this;
                fetch('/notifications/count/')
                    .then(function (r) { return r.json(); })
                    .then(function (data) { self.count = data.count; })
                    .catch(function () {});
            },

            fetchList: function () {
                var self = this;
                fetch('/notifications/')
                    .then(function (r) { return r.json(); })
                    .then(function (data) { self.notifications = data.notifications; })
                    .catch(function () {});
            },

            markRead: function (n) {
                if (n.is_read) return;
                var self = this;
                fetch('/notifications/' + n.id + '/read/', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': this.csrfToken },
                }).then(function () {
                    n.is_read = true;
                    self.count = Math.max(0, self.count - 1);
                }).catch(function () {});
            },

            markAllRead: function () {
                var self = this;
                fetch('/notifications/read-all/', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': this.csrfToken },
                }).then(function () {
                    self.notifications.forEach(function (n) { n.is_read = true; });
                    self.count = 0;
                }).catch(function () {});
            },

            timeAgo: function (iso) {
                var diff = (Date.now() - new Date(iso).getTime()) / 1000;
                if (diff < 60) return 'ahora';
                if (diff < 3600) return Math.floor(diff / 60) + ' min';
                if (diff < 86400) return Math.floor(diff / 3600) + ' h';
                return Math.floor(diff / 86400) + ' d';
            },
        };
    });
});
