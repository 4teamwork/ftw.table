//
// create closure
//
(function($) {    
    
    var $this = null;
    var $o = null;
    var _params = {};
    
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
                // build element specific options
                $o = $.meta ? $.extend({}, opts, $this.data()) : opts;
                // update element styles
                methods.param('show', 'templates');
                methods.param('path', '/');
                $o.onBeforeLoad();
                //methods.reload();
                $.fn.ftwtable.createTable($this, buildQuery());
               //add events
               // $('th.sortable', $this).live('click', function(e){
               //     var hid = $(e.target).parent().attr('id');
               //     methods.param('sort_on', hid);
               // });
            });
        },

        reload : function( ) {
            $.fn.ftwtable.reloadTable($this, buildQuery());
        },

        param : function(key, value) { 
            if (key && value){
                $this.data(key, value);
                return $this;
            } else if (key && value==undefined){
                return $this.data(key);   
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
        return $('link[rel=kss-base-url]').attr('href')+$o.url+'?'+tabbedview.parse_params();
        //return $o.url+'?view_name='+tabbedview.prop('view_name');

        //return $o.url+'?show='+methods.param('show')+'&path='+methods.param('path');
    }
    
    
    //
    // Callbacks
    //
    
    function onBeforeLoad(){
        return $this;
    };
    
    function onLoad(text, status, response){
        return $this;
    };
    
    //
    // public methods
    //

    $.fn.ftwtable.createTable = function(query){ 
        $this.load(query, function(){           
            $o.onLoad();
        });
    };
    
    $.fn.ftwtable.reloadTable = function(query){ 
    };
    
    $.fn.ftwtable.select = function(start, end){ 
        // TODO: implement table selection
        //console.log(start+' '+end);
    };
    
    $.fn.ftwtable.deselect = function(start, end){ 
        // TODO: implement table selection
        //console.log(start+' '+end);
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
        onBeforeLoad: null,
        onLoad: onLoad
    };
//
// end of closure
//


})(jQuery);


