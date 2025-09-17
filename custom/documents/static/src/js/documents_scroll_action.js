odoo.define("documents/static/src/js/documents_scroll_action", function (require) {
    "use strict";

    $(document).ready(function () {
        $(document).on('click', '.o_kanban_record', function () {
            let container = $('.o_content');
            if (container.length) {
                console.log('container: ', container)
                container.animate({
                    scrollLeft: container[0].scrollWidth
                }, 600); // 600ms animation
            }
        });
    });
});
