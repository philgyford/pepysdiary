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

        pepys.comments.init();

        pepys.topic.init();

        // Prettify the dates/times on comments.
        $('time.timeago').timeago();
    }
};

/**
 * Generically useful things.
 */
window.pepys.utilities = {

    /**
     * Returns a list of all the years, months, and number of days in each
     * month for which there are diary entries.
     */
    diary_years_months: function() {
        return {
            '1660':{'Jan':31,'Feb':29,'Mar':31,'Apr':30,'May':31,'Jun':30,'Jul':31,'Aug':31,'Sep':30,'Oct':31,'Nov':30,'Dec':31},
            '1661':{'Jan':31,'Feb':28,'Mar':31,'Apr':30,'May':31,'Jun':30,'Jul':31,'Aug':31,'Sep':30,'Oct':31,'Nov':30,'Dec':31},
            '1662':{'Jan':31,'Feb':28,'Mar':31,'Apr':30,'May':31,'Jun':30,'Jul':31,'Aug':31,'Sep':30,'Oct':31,'Nov':30,'Dec':31},
            '1663':{'Jan':31,'Feb':28,'Mar':31,'Apr':30,'May':31,'Jun':30,'Jul':31,'Aug':31,'Sep':30,'Oct':31,'Nov':30,'Dec':31},
            '1664':{'Jan':31,'Feb':29,'Mar':31,'Apr':30,'May':31,'Jun':30,'Jul':31,'Aug':31,'Sep':30,'Oct':31,'Nov':30,'Dec':31},
            '1665':{'Jan':31,'Feb':28,'Mar':31,'Apr':30,'May':31,'Jun':30,'Jul':31,'Aug':31,'Sep':30,'Oct':31,'Nov':30,'Dec':31},
            '1666':{'Jan':31,'Feb':28,'Mar':31,'Apr':30,'May':31,'Jun':30,'Jul':31,'Aug':31,'Sep':30,'Oct':31,'Nov':30,'Dec':31},
            '1667':{'Jan':31,'Feb':28,'Mar':31,'Apr':30,'May':31,'Jun':30,'Jul':31,'Aug':31,'Sep':30,'Oct':31,'Nov':30,'Dec':31},
            '1668':{'Jan':31,'Feb':28,'Mar':31,'Apr':30,'May':31,'Jun':30,'Jul':31,'Aug':31,'Sep':30,'Oct':31,'Nov':30,'Dec':31},
            '1669':{'Jan':31,'Feb':29,'Mar':31,'Apr':30,'May':31}
        };
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
 * Does the 'new' flags and highlighting on a comment's #hash.
 *
 * The 'New' flags are actually, for any element with the class "newable"
 * and a data-time attribute: it adds a "NEW" marker to any that are new for
 * this user, based on the cookies set in VisitTimeMiddleware.
 */
window.pepys.comments = {

    /**
     * When the user's last 'visit' ended. UTC unixtime.
     */
    prev_visit_end: null,

    init: function() {
        this.init_hash_link();
        this.init_newables();
    },

    init_hash_link: function() {
        var hash = window.location.hash.substring(1);

        if (hash) {
            if (hash.match(/^c\d+$/) && $('#'+hash).exists()) {
                $('#'+hash).addClass('focused');
            };
        };
    },

    init_newables: function() {
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
    }
};

/**
 * Anything around an Encyclopedia Topic page.
 */
window.pepys.topic = {

    valid_tabs: ['map', 'summary', 'wikipedia', 'wheatley', 'discussion',
                                                                 'references'],

    init: function() {
        this.init_tabs();
    },

    /**
     * Work out if we need to show one of the tabs based on the URL's #hash.
     * Also, set the URL's #hash when a tab is clicked.
     */
    init_tabs: function() {
        var hash = window.location.hash.substring(1);

        if (hash) {
            if (hash.match(/^c\d+$/) && $('#'+hash).exists()) {
                // The hash is like 'c1234' and there's a comment with that ID.
                $('#tab-discussion a').tab('show');
                $('html, body').animate({scrollTop: $('#'+hash).offset().top },
                                                                        500);

            } else if ($.inArray(hash, this.valid_tabs) >= 0) {
                // It's a valid tab ID.
                $('#tab-'+hash+' a').tab('show');

            } else if ($('#row-wikipedia').exists() && $('#wikipedia').exists()) {
                // We might be linking to a section under the Wikipedia tab.
                $('#tab-wikipedia a').tab('show');
            };
        };

        // When a tab is clicked, change the URL's hash.
        $('.nav-tabs a').on('shown', function (e) {
            var hash = e.target.hash;
            // We don't want to jump to the tab's content, so we change its
            // ID, then change the URL hash, then put the ID back.
            $(hash).attr('id', hash+'temp');
            window.location.hash = hash;
            $(hash+'temp').attr('id', hash);
        });
    },

    draw_references_chart: function(references) {

        // data ends up as an array of objects, each object for a month:
        // { 'name': 'Jan 1660', 'percent_refs': 42, 'num_refs': 13},
        // `num_refs` is the number of references for this topic in that month.
        // `percent_refs` is that number as a percentage of the number of
        // days in that month.
        var data = [];
        $.each(pepys.utilities.diary_years_months(), function(year, months) {
            $.each(months, function(month_name, month_days) {
                var m_y = month_name+' '+year;
                var num_refs = 0;
                var percent_refs = 0;
                if (m_y in references) {
                    // A number of references were passed in for this month.
                    num_refs = references[m_y];
                    percent_refs = Math.round((num_refs / month_days) * 100);
                };
                data.push({name: m_y,
                            num_refs: num_refs,
                            percent_refs: percent_refs});
            });
        });

        // Overall width/height available.
        // We did use #chart-references' width, but that might be hidden.
        var outer_width = $('.tab-content').width();
        var outer_height = Math.round(outer_width / 3.8);

        console.log(outer_width, outer_height);
        // Area around the actual chart (space for axes numbers etc).
        var margin = {top: 0, right: 0,
                        bottom: Math.round(outer_height / 10), left: 0};

        // Area of the chart itself (not including space for axes numbers).
        var inner_width = outer_width - margin.left - margin.right;
        var inner_height = outer_height - margin.top - margin.bottom;

        var font_size = Math.round(inner_height / 13);

        // The main chart area.
        var svg = d3.select('#chart-references').append('svg')
                .attr('class', 'chart')
                .attr('width', outer_width)
                .attr('height', outer_height)
            .append('g')
                .attr('transform',
                        'translate(' + margin.left + ',' + margin.top + ')');

        // The scales.
        var x = d3.scale.ordinal()
                .domain(d3.range(data.length))
                .rangeBands([0, inner_width], 0);
        var y = d3.scale.linear()
                .domain([0, 100])
                .range([inner_height, 0]);

        // Construct and then add the x axis.
        var tick_height = Math.round(inner_height / 20);
        var xAxis = d3.svg.axis()
                .scale(x)
                .orient('bottom')
                // Show only one tick per year (12 months):
                .tickValues([0, 12, 24, 36, 48, 60, 72, 84, 96, 108])
                .tickSize(tick_height, 0, 0)
                .tickFormat(function(d,i){
                    // This doesn't feel right, but it works.
                    // Returns the year from the month-year names: '1661'.
                    return data[d].name.substring(4, 8);
                });

        svg.append('g')
            .attr('class', 'axis axis-x')
            // Shift all the ticks the width of half a bar to the left.
            // (So they're at the edge of a bar, not in the center.)
            // And shift the whole thing to the bottom of the chart.
            .attr('transform', 'translate(-' + (x.rangeBand() / 2) + ',' +
                                                            inner_height + ')')
            .call(xAxis);

        // Shift all of the x-axis text labels to the right, so they're in the
        // middle of the 12 months they refer to.
        svg.selectAll('text')
            .attr('dx', function(d, i) {
                // Shift them all in relation to the width of the bars.
                var left_padding = x.rangeBand() * 6;
                if (i >= 9) {
                    // But the final one we move less, because the final year
                    // is only 5 months.
                    left_padding = x.rangeBand() * 2.5;
                };
                return left_padding;
            })
            // Add a bit of space above each label.
            .attr('dy', (font_size / 3))
            .attr('font-size', font_size + 'px');

        // Construct and then add the y axis.
        var yAxis = d3.svg.axis()
                .scale(y)
                .orient('left')
                // The values we want the grid lines to be for:
                .tickValues([25, 50, 75, 100])
                // Extend the tick marks across the full width.
                .tickSize(-inner_width, 0, 0)
                // Make the y-axis numbers just numbers.
                .tickFormat('');

        svg.append('g')
            .attr('class', 'axis axis-y')
            .call(yAxis);

        var tooltip = d3.select('body')
            .append('div')
            .attr('class', 'chart-tooltip')
            .style('font-size', font_size + 'px')
            .style('padding-left', Math.round(font_size / 2) + 'px')
            .style('padding-right', Math.round(font_size / 2) + 'px');

        // Draw the actual bars themselves.
        svg.selectAll('.bar')
                .data(data)
            .enter().append('rect')
                .attr('class', 'bar')
                .attr('x', function(d,i){ return x(d.name); })
                .attr('y', function(d){ return y(d.percent_refs); })
                .attr('width', x.rangeBand())
                .attr('height', function(d,i){
                                return inner_height - y(d.percent_refs); })
                .on('mouseover', function(d, i){
                    tooltip.html('<strong>' + d.num_refs + '</strong> (' + d.name + ')');
                    d3.select(this).classed('highlight', true);
                    tooltip.style('visibility', 'visible');
                })
                .on('mousemove', function(){
                    tooltip
                        .style('top', (event.pageY-10)+'px')
                        .style('left',(event.pageX+10)+'px');
                })
                .on('mouseout', function(){
                    d3.select(this).classed('highlight', false);
                    tooltip.style('visibility', 'hidden');
                });

        // chart.selectAll('text')
        //         .data(data)
        //     .enter().append('text')
        //         .attr('y', function(d){ return y(d.percent_refs); })
        //         .attr('x', function(d){ return x(d.name) + x.rangeBand() / 2; })
        //         .attr('dx', x.rangeBand())
        //         .attr('dy', '1em')
        //         .attr('text-anchor', 'end')
        //         .attr('fill', '#666')
        //         .text(function(d){ return d.num_refs; });
    }
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