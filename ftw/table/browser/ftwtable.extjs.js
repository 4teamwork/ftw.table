//
// create closure
//
(function($) {    
    
    var $this = null;
    store = null;
    var grid = null;
    
    $.fn.ftwtable.createTable = function(table, url){ 
        $this = table;
        
        
        store = new Ext.data.Store({
            remoteSort: true,
            baseParams: {lightWeight:false,ext: 'js'},
            //sortInfo: {field:'lastpost', direction:'DESC'},
            autoLoad: false,

            proxy: new Ext.data.HttpProxy({
                url: url,
                method: 'post'
            }),

            reader: new Ext.data.JsonReader(),
            
            listeners: {
                metachange : function(store, meta){
                if (grid){
                    grid.destroy();
                }
                grid = new Ext.grid.GridPanel({
                    store: store,
                    columns: store.reader.meta.columns,
                    stripeRows: true,
                    autoExpandColumn: 'Title',
                    width: '100%',    
                    height: 200,
                });
                grid.render('template_chooser');
            }
            }
        });
        
        store.load();
        

        // $this.load(query, function(){           
        //     $o.onLoad();
        // });
    };
    
    $.fn.ftwtable.reloadTable = function(table, query){ 
        grid.destroy();
        $.fn.ftwtable.createTable(table, query);
    };
//
// end of closure
//
})(jQuery);
