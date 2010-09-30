//
// create closure
//
(function($) {    
    
    var $this = null;
    var $o = null;
    
    //
    // ftwtable api
    // Example usage:
    //              $(obj).ftwtable('param', 'search', 'foo') 
    //              $(obj).ftwtable('reload')
    
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
                       methods.reload();
                       
                       //add events

                       $('th.sortable', $this).live('click', function(e){
                           var hid = $(e.target).parent().attr('id');
                           methods.param('sort_on', hid);
                           debug_box.append('<div>sort on set: '+hid+'</div>');

                       });
                   });
                },
                
       reload : function( ) {
                   $.fn.ftwtable.createTable(buildQuery());
                },
                
       param : function(key, value) { 
                    if (key && value){
                        $.jStorage.set(key, value);
                        $this.data(key, value);
                    }else if(key && value==undefined){
                        var stored = $.jStorage.get(key);
                        if (stored != null){;
                            console.log('key ' + key + ' read from jstorage')
                            return stored
                        }else{
                            return $this.data(key);   
                        }
                    }else{
                        return $this.data();
                    }
                },
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
        }
    };
    
    //
    // private methods
    //
    
    function buildQuery(){
        return  url = $o.url+'?show='+methods.param('show')+'&path='+methods.param('path');
    }
    
    
    //
    // Callbacks
    //
    
    function onBeforeLoad(){
        console.info('beforeLoad');
    };
    
    function onLoad(text, status, response){
        console.info('onLoad');
    };
    
    //
    // public methods
    //

    $.fn.ftwtable.createTable = function(query){ 
        $this.load(query, function(){           
            $o.onLoad();
        });
    }
    
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
        onLoad: onLoad,
    };
//
// end of closure
//


})(jQuery);


