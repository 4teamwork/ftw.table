//
// create closure
//
(function($) {    
    
    $this = null;
    store = null;
    grid = null;
    locales = {};
    
    var selected_rows = null;
    
    $.fn.ftwtable.createTable = function(table, url){ 
        $this = table;
        store = new Ext.data.GroupingStore({
            remoteSort: true,
            baseParams: {lightWeight:false,ext: 'js'},
            //sortInfo: {field:'lastpost', direction:'DESC'},
            autoLoad: false,
            
            proxy: new Ext.data.HttpProxy({
                url: url,
                method: 'post'
            }),

            reader: new Ext.data.JsonReader(),
            
            groupField:'',
            remoteGroup:true,
            
            listeners: {
                
                metachange : function(store, meta){
                if (grid){
                    grid.destroy();
                }

                locales = store.reader.meta.translations;


                store.sortInfo = {
                    field: store.reader.meta.config.sort,
                    direction: store.reader.meta.config.dir
                };

                var cm = new Ext.grid.ColumnModel({
                    columns: store.reader.meta.columns,
                    defaults: {
                            sortable: false,
                            menuDisabled: false,
                            width: 110
                        }
                    });
                var visible_columns = 0;
                var hidden_columns = 0;
                var forceFit = false;
                for(var i=0; i < cm.columns.length; i++){
                    var col = cm.columns[i];
                    console.log(col);
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
                    store: store,
                    cm: cm,
                    stripeRows: true,
                    //autoExpandColumn: store.reader.meta.config.auto_expand_column,   
                    //autoExpandMin: 200,
                    //autoExpandMax: 300,
                    //autoHeight: true,
                    autoHeight:true,
                    view: new Ext.grid.GroupingView({
                               forceFit:forceFit,
                               //groupMode:'display',
                               //enableGrouping:false,
                               sortDescText: translate('sortDescText', 'Sort Descending'),
                               sortAscText: translate('sortAscText', 'Sort Ascending'),
                               columnsText: translate('columnsText', 'Columns'),
                               showGroupsText: translate('showGroupsText', 'Show in Groups'),
                               groupByText: translate('groupByText', 'Group By This Field'),
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
                                    })
                                    /*console.log(smObj);
                                    if(selected_rows){
                                        selected_rows.each(function(){
                                          $(this).find('input.selectable[type=checkbox]').attr('checked', false);
                                        });
                                    }
                                    selected_rows = $('.'+grid.view.selectedRowClass);
                                    selected_rows.each(function(){
                                       $(this).find('input.selectable[type=checkbox]').attr('checked', true); 
                                    });*/
                                },
                                beforerowselect: function( smObj, rowIndex, keepExisting, record ){
                                    /*if(smObj.isSelected(rowIndex)){
                                        return false;
                                    }*/
                                } 
                            }
                        })
                });
                if(store.reader.meta.config.auto_expand_column!=undefined){
                    grid.autoExpandColumn = store.reader.meta.config.auto_expand_column;     
                }
                grid.autoExpandMin = 200;
                grid.autoExpandMax = 300;
                grid.render($this.attr('id'));
                if(!forceFit){
                    //ugly hacks we need to use horizontal scrolling combined with autoHeight
                    //enable horizontal scrolling
                    $('.x-grid3-viewport').css('overflow', 'auto');
                    //set width of the header div to the same value as the table
                    var inner_width = $('.x-grid3-header table').width();
                    $('.x-grid3-header').width(inner_width);   
                }
                if(store.reader.meta.static != undefined){
                    $.each(store.reader.meta.static, function(key, value) { 
                        $('#'+key+'_container.ftwtable').html(value);
                    });   
                }
            }
            }
        });
        store.load();
        
        //special handling of select boxes
        $('input.selectable[type=checkbox]', $this).live('click', function(e){
            return false;
        })
        
        

        // $this.load(query, function(){           
        //     $o.onLoad();
        // });
    };
    
    translate = function(key, defaultValue){
        if(locales[key]){
            return locales[key];
        }else{
            return defaultValue || key; 
        }
    }
    
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
