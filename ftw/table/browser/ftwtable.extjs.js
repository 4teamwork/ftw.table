//approach for own selection model

// Ext.grid.FTWTableCheckboxSelectionModel = Ext.extend(Ext.grid.RowSelectionModel, {
// 
//     
//     
//     header : '<div class="x-grid3-hd-checker">&#160;</div>',
//     
//     width : 20,
//     
//     sortable : false,
// 
//     
//     menuDisabled : true,
//     fixed : true,
//     hideable: false,
//     dataIndex : '',
//     id : 'checker',
//     isColumn: true, 
// 
//     constructor : function(){
//         Ext.grid.FTWTableCheckboxSelectionModel.superclass.constructor.apply(this, arguments);
//         if(this.checkOnly){
//             this.handleMouseDown = Ext.emptyFn;
//         }
//     },
// 
//     
//     initEvents : function(){
//         Ext.grid.FTWTableCheckboxSelectionModel.superclass.initEvents.call(this);
//         this.grid.on('render', function(){
//             Ext.fly(this.grid.getView().innerHd).on('mousedown', this.onHdMouseDown, this);
//         }, this);
//     },
// 
//     
//     processEvent : function(name, e, grid, rowIndex, colIndex){
//         console.log(name);
//         if (name == 'mousedown') {
//             this.onMouseDown(e, e.getTarget());
//             return false;
//         } else {
//             return Ext.grid.Column.prototype.processEvent.apply(this, arguments);
//         }
//     },
// 
//     
//     onMouseDown : function(e, t){
//         console.log(123);
//         if(e.button === 0 && t.className == 'x-grid3-row-checker'){ 
//             e.stopEvent();
//             var row = e.getTarget('.x-grid3-row');
//             if(row){
//                 var index = row.rowIndex;
//                 if(this.isSelected(index)){
//                     this.deselectRow(index);
//                 }else{
//                     this.selectRow(index, true);
//                     this.grid.getView().focusRow(index);
//                 }
//             }
//         }
//     },
// 
//     
//     onHdMouseDown : function(e, t) {
//         if(t.className == 'x-grid3-hd-checker'){
//             e.stopEvent();
//             var hd = Ext.fly(t.parentNode);
//             var isChecked = hd.hasClass('x-grid3-hd-checker-on');
//             if(isChecked){
//                 hd.removeClass('x-grid3-hd-checker-on');
//                 this.clearSelections();
//             }else{
//                 hd.addClass('x-grid3-hd-checker-on');
//                 this.selectAll();
//             }
//         }
//     },
// 
//     
//     renderer : function(v, p, record){
//         return '<div class="x-grid3-row-checker">&#160;</div>';
//     }
// });

//
// create closure
//
(function($) {    
    
    $this = null; // reference to the jQuery table object
    store = null;
    grid = null;
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
            autoDestroy:false,
            
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

                var sm =  new Ext.grid.RowSelectionModel();
                var columns = store.reader.meta.columns;
                
                // Set up the ColumnModel
                var cm = new Ext.grid.ColumnModel({
                    columns: columns,
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
                    columnLines: true,
                    store: store,
                    cm: cm,
                    stripeRows: true,
                    autoHeight:true,
                    xtype: "grid",
                    //XXX: GridDragDropRowOrder has to be the first plugin!
                    plugins: [new Ext.ux.dd.GridDragDropRowOrder({
                        copy: false, // false by default
                        scrollable: true, // enable scrolling support (default is false)
                        targetCfg: {}, // any properties to apply to the actual DropTarget
                        listeners: {
                            afterrowmove: function(dropTarget, rowIndex, rindex, selections){
                                var new_order = [];
                                for(var i = 0; i<store.getCount(); i++){
                                    new_order.push(store.getAt(i).json.id);
                                }
                                $.ajax({
                                   url: '@@tabbed_view/reorder',
                                   cache: true,
                                   type: "POST",
                                   data: {
                                       new_order: new_order
                                   } 
                                });
                            }
                        }
                    })],

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
                    sm: sm,
                    listeners: {
                        afterrender: function(panel){

                            //drag 'n' drop reordering is only available if sort field is 'draggable'
                            if(store.sortInfo.field == 'draggable'){
                                unlockDragDrop();
                            }else{
                                lockDragDrop();
                            }

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
                                    $('#'+key+'_container.ftwtable').html(value);
                                });   
                            }
                            options.onLoad();
                            
                        }
                    }
                });
                // set up autoExpandColumn
                if(store.reader.meta.config.auto_expand_column!=undefined){
                    grid.autoExpandColumn = store.reader.meta.config.auto_expand_column;
                    grid.autoExpandMin = 200;
                    grid.autoExpandMax = 300;
                }

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

    };
    
    unlockDragDrop = function(){
      //XXX: We assume that [0] is the GridDragDropRowOrder plugin
      grid.plugins[0].target.unlock();  
      grid.ddText = "{0} selected rowen{1}";  
      $this.removeClass('draglocked');
    };
    
    lockDragDrop = function(){
      //XXX: We assume that [0] is the GridDragDropRowOrder plugin
      grid.plugins[0].target.lock();  
      grid.ddText = translate('dragDropLocked', "Drag 'n' Drop not possible");  
      $this.addClass('draglocked');
    };


    translate = function(key, defaultValue){
        if(locales[key]){
            return locales[key];
        }else{
            return defaultValue || key; 
        }
    };
    
    $.fn.ftwtable.reloadTable = function(table, query, options){ 
        $.fn.ftwtable.destroy();
        $.fn.ftwtable.createTable(table, query, options);
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
