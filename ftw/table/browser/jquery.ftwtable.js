//
// create closure
//
(function($) {

  var $this = null;
  var $o = null;
  var DATA_KEY = 'ftwtable';

  //
  // ftwtable api
  // Example usage:
  //              $(obj).ftwtable('param', 'search', 'foo')
  //              $(obj).ftwtable('reload')
  //
  var methods = {

    init : function( options ) {
      // build main options before element iteration
      var opts = $.extend({}, $.fn.ftwtable.defaults, options);
      // iterate and reformat each matched element
      return this.each(function() {
        $this = $(this);
        $this.data(DATA_KEY, {});
        // build element specific options
        $o = $.meta ? $.extend({}, opts, $this.data()) : opts;
        // update element styles
        methods.param('show', 'templates');
        methods.param('path', '/');
        $o.onBeforeLoad();
        $.fn.ftwtable.createTable($this, buildQuery(), $o);
        //add events
        // $('th.sortable', $this).live('click', function(e){
        //     var hid = $(e.target).parent().attr('id');
        //     methods.param('sort_on', hid);
        // });
      });
    },

    reload : function( ) {
      $.fn.ftwtable.reloadTable($this, buildQuery(), $o);
    },

    param : function(key, value) {
      if (key && value){
        //$this.data(key, value);
        var data = $this.data(DATA_KEY);
        var new_data = {};
        new_data[key] = value;
        $.extend(data, new_data);
        return $this;
      } else if (key && value==undefined){
        return $this.data(DATA_KEY)[key];
      } else {
        return $this.data();
      }
    },

    select: function(start, end){
      $.fn.ftwtable.select(start, end);
    },

    deselect: function(start, end){
      $.fn.ftwtable.deselect(start, end);
    },

    destroy: function(start, end){
      $.fn.ftwtable.destroy(start, end);
    }
  };

  //
  // plugin definition
  //

  $.fn.ftwtable = function(method) {
    // Method calling logic
    if ( methods[method] ) {
      return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
    } else if ( typeof method === 'object' || ! method ) {
      return methods.init.apply( this, arguments );
    } else {
      $.error( 'Method ' +  method + ' does not exist on jQuery.ftwtable' );
      return null;
    }
  };

  //
  // private methods
  //

  function buildQuery(){
    var params = '';
    if(window.tabbedview != undefined){
      params = tabbedview.parse_params();
    }else{
      params = parseParams();
    }
    return $('link[rel=kss-base-url]').attr('href') + $o.url + '?' + params;
    //return $o.url+'?view_name='+tabbedview.prop('view_name');
    //return $o.url+'?show='+methods.param('show')+'&path='+methods.param('path');
  }


  //
  // Callbacks
  //

  function parseParams(){
    return $.param($this.data(DATA_KEY));
  }

  function onBeforeLoad(){
    return $this;
  }

  function onLoad(text, status, response){
    return $this;
  }

  function get_checkbox_range(start, end) {
    var all = $('#listing_container input[type=checkbox]:visible');
    if (start == 'all') {
      return all;

    } else if (start && end) {
      return all.slice(start, end + 1);

    } else if (end == undefined) {
      return all.eq(start);
    }
  }

  //
  // public methods
  //

  $.fn.ftwtable.createTable = function(table, query, options){
    $this.load(query, null, function(){
      tabbedview.view_container.trigger('gridRendered');
      $o.onLoad();
    });
  };

  $.fn.ftwtable.reloadTable = function(table, query, options){
    $.fn.ftwtable.createTable($this, buildQuery(), $o);
  };

  $.fn.ftwtable.select = function(start, end){
    return get_checkbox_range(start, end).attr('checked', true);
  };

  $.fn.ftwtable.deselect = function(start, end){
    return get_checkbox_range(start, end).attr('checked', false);
  };

  $.fn.ftwtable.destroy = function(start, end){
  };

  //
  // plugin defaults
  //

  $.fn.ftwtable.defaults = {
    url: '@@ftwtable/listing',
    timeout: 1000,
    cache: false,
    selectable: true,
    sortable: true,
    storage: false,
    onBeforeLoad: onBeforeLoad,
    onLoad: onLoad
  };
  //
  // end of closure
  //


})(jQuery);


