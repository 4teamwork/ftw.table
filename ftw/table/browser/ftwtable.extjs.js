//
// create closure
//
(function($) {    
    
    var $this = null;
    var store = null;
    var grid = null;
    
    var selected_rows = null;
    
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
                var cm = new Ext.grid.ColumnModel({
                    columns: store.reader.meta.columns,
                    defaults: {
                            sortable: true,
                            menuDisabled: false,
                            width: 110
                        }
                    });
                grid = new Ext.grid.GridPanel({
                    store: store,
                    cm: cm,
                    stripeRows: true,
                    autoExpandColumn: 'Title',   
                    autoExpandMin: 200,
                    autoExpandMax: 300,
                    //autoHeight: true,
                    autoHeight:true,
                    renderTo: $this.attr('id'),
                    sm: new Ext.grid.RowSelectionModel({
                            listeners: {
                                selectionchange: function(smObj) {
                                    if(selected_rows){
                                        selected_rows.each(function(){
                                          $(this).find('input').attr('checked', false);
                                        });
                                    }
                                    selected_rows = $('.'+grid.view.selectedRowClass);
                                    selected_rows.each(function(){
                                       $(this).find('input').attr('checked', true); 
                                    });
                                }
                            }
                        })
                });
                //ugly hacks we need to use horizontal scrolling combined with autoHeight
                //enable horizontal scrolling
                $('.x-grid3-viewport').css('overflow', 'auto');
                //set width of the header div to the same value as the table
                var inner_width = $('.x-grid3-header table').width();
                $('.x-grid3-header').width(inner_width);
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
    
    $.fn.ftwtable.destroy = function(){
        if(grid){
            grid.destroy();
        }
        $this = null;
        store = null;
        grid = null;
        selected_rows = null;
    };
    
    $.fn.ftwtable.select = function(start, end){
        var sm = grid.getSelectionModel();
        if (start=='all'){
            sm.selectRange(0, store.totalLength-1);
        }else if (start && end){
            sm.selectRange(start, end);
        } else if (end == undefined){ 
            sm.selectRow(start);
        }  
    };
    
    $.fn.ftwtable.deselect = function(start, end){
        var sm = grid.getSelectionModel();
        if (start=='all'){
            sm.deselectRange(0, store.totalLength-1);
        }else if (start && end){
            sm.deselectRange(start, end);
        } else if (end == undefined){ 
            sm.deselectRow(start);
        }  
    };
//
// end of closure
//
})(jQuery);
