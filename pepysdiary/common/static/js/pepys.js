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
        'cloudmade_api_key': '',
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
 * Anything about a particular Category.
 */
window.pepys.category = {

    // Both will be populated when draw_map() is called.
    category_id: null,
    map_categories: {},

    // Each category will have its map start at one of these centres/zooms:
    start_coords: {
        britain:   {latitude: 52.5196, longitude: -1.4069, zoom: 6},
        london:    {latitude: 51.5118, longitude: -0.1041, zoom: 13},
        environs:  {latitude: 51.5118, longitude: -0.1042, zoom: 11},
        waterways: {latitude: 52.1141, longitude: -0.8267, zoom: 7},
        whitehall: {latitude: 51.5040, longitude: -0.1257, zoom: 17},
        world:     {latitude: 24.0389, longitude: 38.0450, zoom: 2}
    },

    // Mapping a category ID to start coordinates.
    // If not listed, we default to using the 'london' coordinates.
    categories_start_coords: {
        '30': 'britain',
        '45': 'world',
        '180': 'whitehall',
        '209': 'waterways',
        '214': 'environs'
    },

    /**
     * Call this to set up initial categories data and draw the map.
     * data should have `category_id` (the category to display)
     * and `map_categories`, an object mapping category_id: category_title.
     */
    init_map: function(data) {
        this.resize_map();
        var that = this;
        $(window).resize(function(){
            that.resize_map();
        });
        this.map_categories = data.map_categories;
        if (this.is_valid_map_category_id(data.category_id)) {
            this.category_id = data.category_id;
            this.draw_category_map(this.category_id);
        };
    },

    /**
     * Assuming we've already called init_map() earlier, draw the map for a
     * particular category (which should be in this.map_categories).
     */
    draw_category_map: function(category_id){
        if ( ! this.is_valid_map_category_id(category_id)) {
            return;
        };
        this.category_id = category_id;

        // Work out which centre and zoom to draw.
        var start_coords = this.start_coords['london'];
        if (this.category_id.toString() in this.categories_start_coords) {
            start_coords = this.start_coords[
                                this.categories_start_coords[
                                    this.category_id.toString()
                                ]
                            ];
        };
        pepys.maps.init(start_coords);
    },

    /**
     * Make the map as big as possible.
     */
    resize_map: function() {
        var $container = $('.container-main');
        var $map = $('#map-frame');

        // Set the height of the main content container to stretch to the
        // bottom of the window.
        var container_height = $(window).height() - $container.offset().top - (
                        $container.outerHeight(true) - $container.height()
                    );
        // But let's set a useful minimum height, or the map might disappear
        // completely.
        if (container_height < 400) {
            container_height = 400;
        };
        // Set the map height to fill to the bottom of the container.
        var map_height = container_height - (
                                $map.offset().top - $container.offset().top
                            );

        $container.height(container_height + 'px');
        $map.height(map_height + 'px');
    },

    /**
     * Check that the category_id is a valid one for drawing maps with.
     */
    is_valid_map_category_id: function(category_id) {
        if (category_id.toString() in this.map_categories) {
            return true;
        } else {
            return false;
        };
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
            var hash = e.target.hash.substring(1);
            // We don't want to jump to the tab's content, so we change its
            // ID, then change the URL hash, then put the ID back.
            $(hash).attr('id', hash+'temp');
            window.location.hash = '#' + hash;
            $(hash+'temp').attr('id', hash);
        });
    },

    /**
     * A simple wrapper around some pepys.maps stuff, to draw a map for a
     * single Topic.
     * data has keys like: latitude, longitude, zoom, title.
     * And optionally: tooltip_text and one of polygon or path.
     */
    draw_map: function(data) {
        pepys.maps.init({
            'latitude': data.latitude,
            'longitude': data.longitude,
            'zoom': data.zoom
        });

        pepys.maps.add_place(data, true);
    },

    /**
     * Draw the d3 chart of diary references for this topic.
     * `references` is an object like this:
     * {
     *  'Jan 1660': 13,
     *  'Mar 1660': 3,
     *  'Dec 1663': 24,
     *  ...
     * }
     * Note that months with no references have no entry in the object.
     */
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
 * All the general map-related stuff.
 * Currently uses Leaflet.js, which we assume is already loaded.
 * Currently we assume there is a #map-frame div to draw the map in.
 */
window.pepys.maps = {

    // Will be the Leaflet map object.
    map: null,

    /**
     * Draw the actual map.
     * map_data has keys for 'latitude', 'longitude' and 'zoom'.
     */
    init: function(map_data) {

        this.map = L.map('map-frame').setView(
                    [map_data.latitude, map_data.longitude], map_data.zoom);
        L.tileLayer(
            'http://{s}.tile.cloudmade.com/' + pepys.controller.config.cloudmade_api_key + '/997/256/{z}/{x}/{y}.png',
            {
                attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
                maxZoom: 18
            }
        ).addTo(this.map);

        this.init_overlays();

        // The map is probably inside a tab on a Topic detail page.
        // If the page opened to a different tab, then the map won't have
        // been drawn properly.
        // So when we switch to the map tab, re-draw the map.
        if ($('#tab-map').exists()) {
            var that = this;
            $('a[data-toggle="tab"]').on('shown', function (e) {
                if ($(e.target).attr('href') == '#map') {
                    that.map.invalidateSize(false);
                };
                return true;
            });
        };
    },

    /**
     * Add the overlays for areas on all maps.
     */
    init_overlays: function() {
        var london_wall_overlay = L.layerGroup([
            L.polyline(
                // Drawn from Hollar's 1666 map after the Great Fire:
                // http://commons.wikimedia.org/wiki/File:Map.London.gutted.1666.jpg
                [[51.511046,-0.104113],[51.513864,-0.104027],[51.513824,-0.102482],[51.516494,-0.101473],[51.516641,-0.095927],[51.517823,-0.095347],[51.51781,-0.095192],[51.518608,-0.094644],[51.517643,-0.090101],[51.516862,-0.085562],[51.516214,-0.081636],[51.515112,-0.079147],[51.514024,-0.077151],[51.51365,-0.076593],[51.509424,-0.075821]],
                {stroke: true, color: '#333333', opacity: 0.8}
            )
        ]);

        var built_area_overlay = L.layerGroup([
            L.polygon(
                // Roughly done from Hollar's Plan of London Before the Fire (1666):
                // http://link.library.utoronto.ca/hollar/digobject.cfm?Idno=Hollar_k_2465&size=zoom&query=london&type=search
                [[51.494931,-0.12454],[51.495172,-0.132179],[51.495813,-0.13308],[51.49795,-0.13381],[51.498912,-0.137758],[51.49803,-0.139647],[51.499473,-0.14235],[51.500542,-0.139904],[51.501984,-0.140891],[51.50324,-0.13763],[51.504869,-0.139604],[51.507941,-0.131879],[51.50949,-0.133424],[51.509864,-0.133038],[51.510746,-0.13381],[51.512722,-0.130806],[51.516488,-0.133166],[51.516675,-0.130849],[51.517236,-0.125828],[51.519505,-0.121279],[51.521588,-0.114112],[51.522229,-0.111065],[51.52311,-0.110335],[51.523377,-0.107288],[51.523217,-0.10673],[51.523751,-0.106645],[51.524392,-0.103126],[51.524232,-0.102696],[51.526795,-0.091453],[51.52303,-0.090208],[51.523324,-0.087161],[51.523591,-0.081453],[51.524045,-0.079265],[51.529038,-0.078492],[51.528931,-0.077419],[51.525353,-0.076432],[51.523805,-0.076132],[51.520734,-0.073729],[51.517049,-0.071154],[51.523217,-0.044374],[51.521722,-0.043087],[51.515313,-0.069523],[51.510772,-0.066776],[51.512375,-0.053043],[51.510826,-0.051842],[51.512642,-0.037766],[51.50949,-0.028667],[51.508101,-0.027294],[51.506499,-0.028667],[51.508796,-0.034676],[51.509544,-0.038023],[51.509651,-0.04283],[51.509223,-0.046091],[51.508101,-0.049009],[51.506819,-0.051327],[51.506125,-0.052271],[51.50324,-0.048065],[51.501477,-0.051584],[51.499981,-0.056734],[51.499286,-0.062828],[51.498565,-0.067849],[51.499526,-0.071239],[51.497469,-0.078664],[51.497736,-0.081968],[51.499179,-0.081882],[51.501156,-0.082655],[51.502465,-0.083385],[51.503881,-0.084071],[51.502118,-0.085144],[51.502679,-0.091066],[51.50121,-0.092268],[51.494611,-0.083942],[51.493756,-0.085444],[51.499126,-0.09407],[51.498404,-0.095787],[51.49966,-0.097718],[51.502759,-0.093598],[51.503934,-0.095959],[51.50551,-0.096259],[51.507006,-0.095873],[51.507113,-0.099478],[51.505163,-0.101109],[51.502225,-0.100508],[51.500568,-0.101066],[51.50121,-0.102096],[51.503667,-0.102053],[51.505297,-0.102267],[51.507861,-0.103855],[51.508021,-0.106859],[51.507621,-0.11085],[51.507006,-0.113597],[51.505323,-0.112438],[51.504068,-0.110722],[51.502305,-0.108962],[51.501156,-0.107889],[51.500916,-0.109563],[51.503534,-0.111752],[51.504869,-0.113811],[51.506632,-0.114799],[51.505965,-0.116472],[51.504282,-0.117803],[51.502625,-0.118446],[51.501584,-0.115786],[51.500889,-0.114884],[51.499767,-0.112782],[51.499339,-0.113597],[51.499927,-0.115614],[51.49974,-0.116773],[51.499259,-0.118232],[51.499794,-0.118361],[51.500488,-0.115571],[51.502011,-0.118833],[51.499607,-0.119562],[51.496641,-0.120292],[51.495332,-0.120034],[51.494664,-0.117202],[51.491725,-0.120292],[51.489053,-0.121837],[51.486514,-0.12351],[51.487102,-0.125527],[51.490148,-0.123124],[51.492633,-0.121751],[51.494664,-0.12115],[51.494931,-0.12454]],
                {stroke: false, fill: true, fillColor: '#666666', fillOpacity: 0.4}
            )
        ]);

        var great_fire_overlay = L.layerGroup([
            L.polygon(
                // Drawn from Hollar's 1666 map after the Great Fire:
                // http://commons.wikimedia.org/wiki/File:Map.London.gutted.1666.jpg
                [[51.514204,-0.109756],[51.514885,-0.109928],[51.515353,-0.109756],[51.515807,-0.109456],[51.515753,-0.108511],[51.516154,-0.108318],[51.516114,-0.107481],[51.516394,-0.10731],[51.517022,-0.106516],[51.516595,-0.106452],[51.516955,-0.105164],[51.516955,-0.104885],[51.517329,-0.104842],[51.517556,-0.104477],[51.51781,-0.103619],[51.51773,-0.102847],[51.517369,-0.102503],[51.517189,-0.102476],[51.517085,-0.101339],[51.516822,-0.100003],[51.516812,-0.098716],[51.516621,-0.095932],[51.517803,-0.095283],[51.51781,-0.095192],[51.518608,-0.094644],[51.517636,-0.09023],[51.517222,-0.089757],[51.517102,-0.089382],[51.516862,-0.088341],[51.516528,-0.088041],[51.516007,-0.088148],[51.515927,-0.087891],[51.51568,-0.085959],[51.515613,-0.085745],[51.515486,-0.085831],[51.515313,-0.085369],[51.515046,-0.084983],[51.514438,-0.084243],[51.513477,-0.084254],[51.513437,-0.084007],[51.513016,-0.084189],[51.512889,-0.083545],[51.513096,-0.083385],[51.512989,-0.082451],[51.512789,-0.082515],[51.512729,-0.082194],[51.512602,-0.082194],[51.512261,-0.081207],[51.512054,-0.080616],[51.511494,-0.08037],[51.510959,-0.080509],[51.510011,-0.080745],[51.50953,-0.079629],[51.50927,-0.079823],[51.509043,-0.079147],[51.508863,-0.078771],[51.508302,-0.079179],[51.507841,-0.079361],[51.508328,-0.081389],[51.508542,-0.083621],[51.508909,-0.087011],[51.509023,-0.087837],[51.508983,-0.090272],[51.509197,-0.09201],[51.509677,-0.093534],[51.510265,-0.095787],[51.510692,-0.098534],[51.510826,-0.100272],[51.510853,-0.103126],[51.510866,-0.106409],[51.510893,-0.109477],[51.513911,-0.109949],[51.513964,-0.109627],[51.514204,-0.109756]],
                {stroke: false, fill: true, fillColor: '#cc6666', fillOpacity: 0.3}
            )
        ]);

        L.control.layers(
            {}, // For different map styles.
            {
                'City of London wall': london_wall_overlay,
                'Built-up London (rough)': built_area_overlay,
                'Great Fire damage': great_fire_overlay
            }
        ).addTo(this.map);
    },

    /**
     * Add a single place on a map. Might be a marker, polygon or path.
     * place_data has keys for 'latitude', 'longitude', 'title'.
     * Optional keys: 'tooltip_text', and one of 'polygon' or 'path'.
     * 'polygon' and 'path' are strings like:
     * '51.513558,-0.104268;51.513552,-0.104518;...'
     * show_popup is true/false: Should the popup be open immediately?
     */
    add_place: function(place_data, show_popup) {
        // Will be a Marker, Polygon, or Polyline.
        var place;
        if ('polygon' in place_data) {
            place = L.polygon(
                this.string_to_coords(place_data['polygon'])
            ).addTo(this.map);

        } else if ('path' in place_data) {
            place = L.polyline(
                this.string_to_coords(place_data['path'])
            ).addTo(this.map);

        } else {
            place = L.marker(
                [place_data.latitude, place_data.longitude],
                {
                    title: place_data.title
                }
            ).addTo(this.map);
        };

        var popup_html = '<strong>' + place_data.title + '</strong>';
        if ('tooltip_text' in place_data && place_data.tooltip_text !== '') {
            popup_html += '<br />' + place_data.tooltip_text;
        };
        place.bindPopup(popup_html, {
            minWidth: 150
        });

        if (show_popup === true) {
            place.openPopup();
        };
    },

    /**
     * Turns this:
     * '51.513558,-0.104268;51.513552,-0.104518;...'
     * into this:
     * [[51.513558,-0.104268],[51.513552,-0.104517],...]
     */
    string_to_coords: function(str) {
        var arr = [];
        $.each(str.split(';'), function(n, pair) {
            ll = pair.split(',');
            arr.push([parseFloat(ll[0]), parseFloat(ll[1])]);
        });
        return arr;
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


/**
 * http://timeago.yarp.com/
 * v 1.0.2. See jquery.timeago.js for uncompressed version.
 * Copyright (c) 2008-2013, Ryan McGeary (ryan -[at]- mcgeary [*dot*] org)
 */
(function(e){if(typeof define==="function"&&define.amd){define(["jquery"],e)}else{e(jQuery)}})(function(e){function n(){var t=r(this);if(Math.abs(s(t.datetime))<7*86400*1e3){if(!isNaN(t.datetime)){e(this).text(i(t.datetime))}}return this}function r(n){n=e(n);if(!n.data("timeago")){n.data("timeago",{datetime:t.datetime(n)});var r=e.trim(n.text());if(r.length>0&&!(t.isTime(n)&&n.attr("title"))){n.attr("title",r)}}return n.data("timeago")}function i(e){return t.inWords(s(e))}function s(e){return(new Date).getTime()-e.getTime()}e.timeago=function(t){if(t instanceof Date){return i(t)}else if(typeof t==="string"){return i(e.timeago.parse(t))}else if(typeof t==="number"){return i(new Date(t))}else{return i(e.timeago.datetime(t))}};var t=e.timeago;e.extend(e.timeago,{settings:{refreshMillis:6e4,allowFuture:false,strings:{prefixAgo:null,prefixFromNow:null,suffixAgo:"ago",suffixFromNow:"from now",seconds:"less than a minute",minute:"about a minute",minutes:"%d minutes",hour:"about an hour",hours:"about %d hours",day:"a day",days:"%d days",month:"about a month",months:"%d months",year:"about a year",years:"%d years",wordSeparator:" ",numbers:[]}},inWords:function(t){function l(r,i){var s=e.isFunction(r)?r(i,t):r;var o=n.numbers&&n.numbers[i]||i;return s.replace(/%d/i,o)}var n=this.settings.strings;var r=n.prefixAgo;var i=n.suffixAgo;if(this.settings.allowFuture){if(t<0){r=n.prefixFromNow;i=n.suffixFromNow}}var s=Math.abs(t)/1e3;var o=s/60;var u=o/60;var a=u/24;var f=a/365;var c=s<45&&l(n.seconds,Math.round(s))||s<90&&l(n.minute,1)||o<45&&l(n.minutes,Math.round(o))||o<90&&l(n.hour,1)||u<24&&l(n.hours,Math.round(u))||u<42&&l(n.day,1)||a<30&&l(n.days,Math.round(a))||a<45&&l(n.month,1)||a<365&&l(n.months,Math.round(a/30))||f<1.5&&l(n.year,1)||l(n.years,Math.round(f));var h=n.wordSeparator||"";if(n.wordSeparator===undefined){h=" "}return e.trim([r,c,i].join(h))},parse:function(t){var n=e.trim(t);n=n.replace(/\.\d+/,"");n=n.replace(/-/,"/").replace(/-/,"/");n=n.replace(/T/," ").replace(/Z/," UTC");n=n.replace(/([\+\-]\d\d)\:?(\d\d)/," $1$2");return new Date(n)},datetime:function(n){var r=t.isTime(n)?e(n).attr("datetime"):e(n).attr("title");return t.parse(r)},isTime:function(t){return e(t).get(0).tagName.toLowerCase()==="time"}});e.fn.timeago=function(){var e=this;e.each(n);var r=t.settings;if(r.refreshMillis>0){setInterval(function(){e.each(n)},r.refreshMillis)}return e};document.createElement("abbr");document.createElement("time")})
