//
// create closure
//
(function($) {    
    
    var $this = null; // reference to the jQuery table object
    var store = null;
    var grid = null;
    var options = null;
    var locales = {}; // Stores the translated strings fetched from the server. Use translate(msgid, defaultValue)
    
    $.fn.ftwtable.createTable = function(table, url, options){ 
        options = options;
        $this = table;
        store = new Ext.data.GroupingStore({
            // set up the store
            remoteSort: true,
            autoLoad: false,  
            groupField: '', // kinda ugly way to trick the table into disable grouping by default
            remoteGroup: true,
            autoDestroy:true,
            
            //params that will be sent with every request 
            baseParams: {   
                ext: 'json', 
                tableType: 'extjs', // lets the server know that this is a request from EXTJS ...
                mode: 'json' // ... and that we want JSON data to be returned
                },
            
            proxy: new Ext.data.HttpProxy({
                url: url,
                method: 'POST',
                disableCaching: true // adds a unique cache-buster GET param to requests
                // TODO: autoAbort isn't working yet in EXTJS 3.3.0.
                // autoAbort: true, // Automatically aborts previous AJAX requests
            }),

            // JSON Reader is configured using the data contained in the AJAX response  
            reader: new Ext.data.JsonReader(),
            
            listeners: {
                
                // will be called if we get new metadata from the server. E.g. diffrent columns.
                metachange : function(store, meta){
                // On metadachange we have to create a new grid. Therefore destroy the old one 
                if (grid){
                    grid.destroy();
                }

                // translations contains the translated strings that will be used in the ui. 
                locales = store.reader.meta.translations;

                // sorting information
                store.sortInfo = {
                    field: store.reader.meta.config.sort,
                    direction: store.reader.meta.config.dir
                };

                // Set up the ColumnModel
                var cm = new Ext.grid.ColumnModel({
                    columns: store.reader.meta.columns,
                    defaults: {
                            sortable: false,
                            menuDisabled: false,
                            width: 110
                        }
                    });
                    
                // If we have less than 5 visible columns the grid will be 
                // rendered with forceFit
                var visible_columns = 0;
                var hidden_columns = 0;
                var forceFit = false;
                for(var i=0; i < cm.columns.length; i++){
                    var col = cm.columns[i];
                    if(col.hidden != undefined && col.hidden == true){
                        hidden_columns++;
                    }else{
                        visible_columns++; 
                    }
                }
                if(visible_columns<=5){
                    forceFit = true;
                }    
                grid = new Ext.grid.GridPanel({
                    //set up the GridPanel
                    store: store,
                    cm: cm,
                    stripeRows: true,
                    autoHeight:true,
                    view: new Ext.grid.GroupingView({
                               forceFit:forceFit,
                               //enableGrouping:false,
                               // Text visible in the grids ui.
                               sortDescText: translate('sortDescText', 'Sort Descending'),
                               sortAscText: translate('sortAscText', 'Sort Ascending'),
                               columnsText: translate('columnsText', 'Columns'),
                               showGroupsText: translate('showGroupsText', 'Show in Groups'),
                               groupByText: translate('groupByText', 'Group By This Field'),
                               // E.g.: Auftragstyp: Zum Bericht / Antrag (2 Objekte)
                               groupTextTpl: '{text} ({[values.rs.length]} {[values.rs.length > 1 ? "'+translate('itemsPlural', 'Items')+'" : "'+translate('itemsSingular', 'Item')+'"]})'
                           }),
                    sm: new Ext.grid.RowSelectionModel({
                            listeners: {
                                selectionchange: function(smObj) {
                                    var records = smObj.selections.map;
                                    var ds = this.grid.store;
                                    $this.find('input.selectable:checked').attr('checked', false);
                                    $.each(records, function(key, value){
                                        var index = ds.indexOfId(key);
                                        $('input.selectable').eq(index).attr('checked', true);
                                    });
                                },
                                beforerowselect: function( smObj, rowIndex, keepExisting, record ){
                                    /*if(smObj.isSelected(rowIndex)){
                                        return false;
                                    }*/
                                }
                            }
                        }),
                    listeners: {
                        afterrender: function(panel){
                            
                            if(!forceFit){
                                //ugly hacks we need to use horizontal scrolling combined with autoHeight
                                //enable horizontal scrolling
                                $('.x-grid3-viewport').css('overflow', 'auto');
                                //set width of the header div to the same value as the table
                                var inner_width = $('.x-grid3-header table').width();
                                $('.x-grid3-header').width(inner_width);   
                            }
                            
                            /* meta.static contains plain html that we inject into the DOM using key+'_container' as selector.
                            E.G.:
                            "static":{
                                     "batching":"<!-- Navigation -->"
                                     [...]
                                  },
                            $('#batching_container.ftwtable') will be replaced with "<!-- Navigation -->"
                            */ 
                            if(store.reader.meta['static'] != undefined){
                                $.each(store.reader.meta['static'], function(key, value) { 
                                    $('#'+key+'_container.ftwtable').replaceWith(value);
                                });   
                            }
                            options.onLoad();
                        }
                    }
                });
                // set up autoExpandColumn
                if(store.reader.meta.config.auto_expand_column!=undefined){
                    grid.autoExpandColumn = store.reader.meta.config.auto_expand_column;     
                }
                grid.autoExpandMin = 200;
                grid.autoExpandMax = 300;
                
                // render the table if ther're records to show.
                if(store.reader.jsonData.rows.length){
                    grid.render($this.attr('id'));
                }else{
                    //show message and abord
                    $('#message_no_contents').show();  
                    return;
                }
            }
            }
        });

        // start the magic.
        store.load();

        //special handling of select boxes
        $('input.selectable[type=checkbox]', $this).live('click', function(e){
            return false;
        });
        
    };


    translate = function(key, defaultValue){
        if(locales[key]){
            return locales[key];
        }else{
            return defaultValue || key; 
        }
    };
    
    $.fn.ftwtable.reloadTable = function(table, query){ 
        grid.destroy();
        $.fn.ftwtable.createTable(table, query);
    };
    
    $.fn.ftwtable.destroy = function(){
        if(grid){
            grid.destroy();
        }
        if(store){
            store.destroy();
        }
        $this = null;
        store = null;
        grid = null;
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
