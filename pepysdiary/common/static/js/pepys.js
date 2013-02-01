// So we can do things like if ($('.classname').exists()) {}
jQuery.fn.exists = function(){return jQuery(this).length>0;};

/**
 * Checks whether a value is numeric or not. Returns true/false.
 */
function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
};

window.pepys = {};

window.pepys.controller = {

    // Defaults. Override by passing values in {'config':{}} to init().
    config: {
        'static_prefix': ''
    },

    init: function(spec) {
        if ('config' in spec) {
            $.extend(this.config, spec.config);
        };

        if ('tooltips' in spec) {
            pepys.tooltips.init(spec.tooltips);
        };

        pepys.newables.init();
    }

};


/**
 * For displaying the hover tooltips over links in Diary Entries and Letters.
 */
window.pepys.tooltips = {

    tooltips: {},

    encyclopedia_link_re: null,

    /**
     * tooltips is an array of dictionaries.
     * Each dictionary has 'id', 'title', 'text' and 'thumbnail_url' keys.
     */
    init: function(tooltips) {
        this.tooltips = tooltips;

        // Regular expression to match the topic ID in an encyclopedia link.
        // eg, '149' from 'http://www.pepysdiary.com/encyclopedia/149/';
        this.encyclopedia_link_re = /\/(\d+)\/$/;

        this.prepare_tooltips();
    },

    /**
     * Prepare all the Bootstrap tooltips for all the links.
     */
    prepare_tooltips: function() {
        var that = this;
        $('article.entry, article.letter').find('a').each(function(idx) {
            id = that.id_from_encyclopedia_url($(this).attr('href'));
            if (id in that.tooltips) {
                var tip_options = {
                    title: that.tooltips[id].title,
                    content: that.tooltip_content(
                        that.tooltips[id].text, that.tooltips[id].thumbnail_url),
                    trigger: 'hover',
                    placement: 'right',
                    html: true
                    // For debugging CSS etc:
                    // delay: { show: 0, hide: 100000 }
                };
                if (that.tooltips[id].thumbnail_url) {
                    // We want to make the popovers wider when there's a
                    // thumbnail. Ideally we'd just add a class to the .popover
                    // but we can't do that. So we have to define this custom
                    // template, which should be identical to the default, with
                    // `popover-hasthumbnail` added to .popover and
                    // `clearfix` added to .popover-content.
                    // Original template: https://github.com/twitter/bootstrap/blob/master/js/bootstrap-popover.js#L102
                    tip_options.template = '<div class="popover popover-hasthumbnail"><div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content clearfix"></div></div></div>';
                };
                $(this).popover(tip_options);
            };
        });
    },

    /**
     * Passed a URL like http://www.pepysdiary.com/encyclopedia/123/ it returns
     * '123'. Or '' if the URL doesn't match that pattern.
     */
    id_from_encyclopedia_url: function(url) {
        if (!url) {
            return '';
        };
        if (url.indexOf('/encyclopedia/') == -1) {
            return '';
        };
        // Return the ID from the URL:
        return this.encyclopedia_link_re.exec(url)[1];
    },

    /**
     * Generate the content portion of a tooltip.
     * Varies, depending if there's a thumbnail or not.
     */
    tooltip_content: function(text, thumbnail_url) {
        if (thumbnail_url) {
            return '<div class="popover-thumbtext">' + text + '</div><img src="' +
                thumbnail_url +
                '" class="thumbnail" width="100" height="120" alt="Thumbnail" />';
        } else {
            return text;
        };
    }
};


/**
 * For any comments
 * (well, any element with the class "newable" and a data-time attribute)
 * adds a "NEW" marker to any that are new for this user, based on the
 * cookies set in VisitTimeMiddleware.
 */
window.pepys.newables = {

    /**
     * When the user's last 'visit' ended. UTC unixtime.
     */
    prev_visit_end: null,

    init: function() {
        this.get_cookies();
        this.set_markers();
    },

    /**
     * We only need to know the end of their previous visit, if any.
     */
    get_cookies: function() {
        cookie_value = readCookie('prev_visit_end');
        if (isNumber(cookie_value)) {
            this.prev_visit_end = parseInt(cookie_value, 10);
        };
    },

    /**
     * Any element with a class of .newable should have a `data-time` element
     * containing a UTC unixtime of when that comment was posted.
     * If it's newer than the end of the user's last visit, we add the .is-new
     * class to its .newflag element, and add 'New' text inside it.
     */
    set_markers: function() {
        var that = this;
        $('.newable').each(function(idx){
            if (that.prev_visit_end === null ||
                parseInt($(this).data('time'), 10) > that.prev_visit_end) {
                $('i.newflag', $(this)).addClass('is-new').html(
                                    '<span>New</span>').attr('title', 'New');
            };
        });
    },
};


/**
 * Provides a readCookie() function.
 * eg, my_value = readCookie('cookie_name');
 */
(function(){
    var cookies;

    function readCookie(name,c,C,i){
        if(cookies){ return cookies[name]; }

        c = document.cookie.split('; ');
        cookies = {};

        for(i=c.length-1; i>=0; i--){
           C = c[i].split('=');
           cookies[C[0]] = C[1];
        };

        return cookies[name];
    };

    window.readCookie = readCookie; // or expose it however you want
})();