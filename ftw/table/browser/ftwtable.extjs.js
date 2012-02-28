Ext.grid.FTWTableGroupingView = Ext.extend(Ext.grid.GroupingView, {
  // private
  onGroupByClick : function(){
    this.grid.store.baseParams['groupBy'] = this.cm.getDataIndex(this.hdCtxIndex);
    this.enableGrouping = true;

    // if we have a tabbedview, we need to tell it that we
    // are not grouping anymore
    if(typeof(tabbedview) != "undefined") {
      tabbedview.param('groupBy', store.baseParams['groupBy']);
    }

    if(store.baseParams['groupBy'] && this.grid.store.sortInfo.field == 'draggable') {
      // we are grouping and sorting by draggable - do not allow this.
      // let's just sort by the groupBy-column
      this.grid.store.sort(store.baseParams['groupBy'], 'ASC');
    }

    this.beforeMenuShow(); // Make sure the checkboxes get properly set when changing groups
    this.refresh();
    this.grid.store.reload();
  },
  // private
  onColumnWidthUpdated : function(col, w, tw){
    Ext.grid.GroupingView.superclass.onColumnWidthUpdated.call(this, col, w, tw);
    this.updateGroupWidths();
    //set width of the header div to the same value as the table
    //we need a few extra pixel to make the resizable handle draggable
    var inner_width = $('.x-grid3-header table').width() + 5;
    $('.x-grid3-header').width(inner_width);
  }
});

function reset_grid_state() {
  jq.ajax({
    url: '@@tabbed_view/setgridstate',
    cache: false,
    type: "POST",
    data: {
       gridstate: "{}",
       view_name: stateName()
    },
    success: function() {
      location.reload();
    }
  });
};

Ext.state.FTWPersistentProvider = Ext.extend(Ext.state.Provider, {
  constructor : function(config){
    Ext.state.FTWPersistentProvider.superclass.constructor.call(this);
    Ext.apply(this, config);
  },

  // private
  set : function(name, value){
    Ext.state.FTWPersistentProvider.superclass.set.call(this, name, value);
    $.ajax({
      url: '@@tabbed_view/setgridstate',
      cache: false,
      type: "POST",
      data: {
        // XXX does JSON.stringify work always?
        gridstate: JSON.stringify(this.state[name]),
        view_name: stateName()
      }
    });
  },

  get : function(name, defaultValue){
    if(!this.state[name] && store.reader.meta.config.gridstate) {
      this.state[name] = JSON.parse(store.reader.meta.config.gridstate);
    }
    return typeof this.state[name] == "undefined" ?
      defaultValue : this.state[name];
  }


});


// create closure
//
(function($) {
  $this = null; // reference to the jQuery table object
  store = null;
  grid = null;
  var options = null;
  var locales = {}; // Stores the translated strings fetched from
  // the server. Use translate(msgid, defaultValue)
  Ext.state.Manager.setProvider(new Ext.state.FTWPersistentProvider());

  $.fn.ftwtable.createTable = function(table, url, opts){
    options = opts;
    $this = table;
    store = new Ext.data.GroupingStore({
      // set up the store
      remoteSort: true,
      autoLoad: false,
      groupField: '', // kinda ugly way to trick the table into disable grouping by default
      remoteGroup: false,
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
          if(store.reader.meta.config.group != undefined){
            store.groupField = store.reader.meta.config.group;
          }

          // On metadachange we have to create a new grid. Therefore destroy the old one
          if (grid){
            // if the grid exists, let the state provider store
            // our config
            Ext.state.Manager.set(stateName(), grid.getState());
            // and destroy the grid
            grid.destroy();
          }

          // translations contains the translated strings that will be used in the ui.
          locales = store.reader.meta.translations;
          // sorting information
          store.sortInfo = {
            field: store.reader.meta.config.sort,
            direction: store.reader.meta.config.dir
          };

          var sm =  new Ext.grid.RowSelectionModel({listeners: {
            selectionchange: function(smObj) {
              var records = smObj.selections.map;
              var ds = this.grid.store;
              $this.find('input.selectable:checked').attr('checked', false);
              $.each(records, function(key, value){
                var index = ds.indexOfId(key);
                $('input.selectable').eq(index).attr('checked', true);
              });
            }
          }});

          var columns = store.reader.meta.columns;
          // workaround to make the last column resizeable in IE - add an
          // empty column
          columns.push({
            dataIndex: "dummy",
            header: "",
            id: "dummy",
            menuDisabled: true,
            sortable: false,
            width: 1});
          // Set up the ColumnModel

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
            if(col.hidden != undefined && col.hidden === true){
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
            stateful: true,
            stateId: stateName(),
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
                    cache: false,
                    type: "POST",
                    data: {
                      new_order: new_order
                    }
                  });
                }
              }
            })],

            view: new Ext.grid.FTWTableGroupingView({
              forceFit:forceFit,
              groupMode:'value',
              hideGroupedColumn: true,
              //enableGrouping:false,
              // Text visible in the grids ui.
              sortDescText: translate('sortDescText', 'Sort Descending'),
              sortAscText: translate('sortAscText', 'Sort Ascending'),
              columnsText: translate('columnsText', 'Columns'),
              showGroupsText: translate('showGroupsText', 'Show in Groups'),
              groupByText: translate('groupByText', 'Group By This Field'),
              // E.g.: Auftragstyp: Zum Bericht / Antrag (2 Objekte)
              groupTextTpl: '{text} ({[values.rs.length]} {[values.rs.length > 1 ? "'+translate('itemsPlural', 'Items')+'" : "'+translate('itemsSingular', 'Item')+'"]})',
              showGroupName: false
            }),

            sm: sm,

            listeners: {
              groupchange: function(grid, state) {
                if(!state) {
                  // hide the groupBy column - which was just enabled
                  // because grouping was disabled
                  var groupByCol = grid.grid.colModel.getIndexById('groupBy');
                  if(groupByCol !== -1) {
                    grid.grid.colModel.setHidden(groupByCol, true);
                  }

                  // reload the store - this removes grouping and
                  // reenables batching etc.
                  store.baseParams['groupBy'] = '';
                  store.reload();
                }

                // if we have a tabbedview, we need to tell it that we
                // are not grouping anymore
                if(typeof(tabbedview) != "undefined") {
                  tabbedview.param('groupBy', store.baseParams['groupBy']);
                }
              },

              beforerender: function(grid) {
                // When the state is loaded, somehow the columns
                // marked as hidden are not set to hidden
                // automatically in the column model. So let's hide
                // them manually before rendering.
                var state = Ext.state.Manager.get(stateName());
                if(state) {
                  for(var i=0; i<state.columns.length; i++) {
                    if(state.columns[i].hidden) {
                      var index = grid.colModel.getIndexById(state.columns[i].id);
                      if(index !== -1) {
                        grid.colModel.setHidden(index, true);
                      }
                    }
                  }
                }
              },

              viewready: function(grid) {
                // Somehow the width of columns, which was stored
                // persistently in the grid state, is overriden while
                // rendering the grid. After everything is visible we
                // need to fix the width of each column.
                var state = Ext.state.Manager.get(stateName());
                if(state) {
                  for(var i=0; i<state.columns.length; i++) {
                    var index = grid.colModel.getIndexById(state.columns[i].id);
                    if(index !== -1) {
                      grid.colModel.setColumnWidth(index, state.columns[i].width);
                    }
                  }
                }

                if(!forceFit){
                  //ugly hacks we need to use horizontal scrolling combined with autoHeight
                  //enable horizontal scrolling
                  $('.x-grid3-viewport').css('overflow', 'auto');
                  //set width of the header div to the same value as the table
                  //we need a few extra pixel to make the resizable handle draggable
                  var inner_width = $('.x-grid3-header table').width() + 5;
                  $('.x-grid3-header').width(inner_width);
                }

                // Checkboxes / radios are usually have the
                // "selectable" css class. When using a extjs
                // selection model, they are not selectable anymore
                // because of the event handling system of
                // extjs. Therefore we disable the click event on checkboxes.
                $(".selectable").click(function(event) {
                  event.preventDefault();
                });
                // pre-selected checkboxes should be selected rows. We have to
                // tell ext-js to select these
                var sm = grid.getSelectionModel();
                $("input[checked=checked]").each(function(i, e) {
                  sm.selectRow($(e).closest(".x-grid3-row").index(), 1);
                });

                /* Hide the "No contents" element if we have
                   no contents */
                $('#message_no_contents').hide();
              },

              afterrender: function(panel){
                //drag 'n' drop reordering is only available if sort field is 'draggable'
                if(store.sortInfo.field == 'draggable'){
                  unlockDragDrop();
                }else{
                  lockDragDrop();
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

                // We shouldn't be able to group and sort by "draggable" at the
                // same time.
                // So we need to disable sorting by "draggable" when
                // grouping is enabled, and enable it when grouping is disabled.
                var draggableCol = grid.colModel.getColumnById('draggable');
                if(draggableCol) {
                  if(store.baseParams['groupBy']) {
                    // grouping is enabled
                    draggableCol.sortable = false;
                  } else {
                    // grouping is disabled
                    draggableCol.sortable = true;
                  }
                }
                $this.trigger('gridRendered');
              },

              sortchange: function(panel, sortInfo) {
                // disable sorting on column "draggable" when sorting
                // by this column. This disables reversing the sort
                // order of "draggable", because it does not make
                // sense (since it's objectPositionInParent)
                var col = grid.colModel.getColumnById('draggable');
                if(col) {
                  if(sortInfo.field == 'draggable' && sortInfo.direction == 'ASC') {
                    col.sortable = false;
                  } else if(sortInfo.field == 'draggable' && sortInfo.direction == 'DESC') {
                    // not very nice: force to sort ascending, when
                    // sorting on "draggable". Descending does not
                    // make any sense..
                    store.sort(sortInfo.field, 'ASC');
                  } else {
                    col.sortable = true;
                  }
                }
              }
            }
          });
          // end grid=

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
    grid.ddText = translate('selectedRowen', '{0} selected rowen{1}');
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

  stateName = function() {
    // returns the name of the state - which includes the current tab
    // since multiple states are present when switching between tabs
    // in tabbedview
    if(typeof(tabbedview) != "undefined") {
      return tabbedview.prop('view_name').replace('.', '-');
    } else {
      return location.href.split('/').reverse()[0].replace('.', '-').replace('@', '');
    }
  };

  $.fn.ftwtable.reloadTable = function(table, query, options){
    if(store.reader.meta['static'] != undefined){
      $.each(store.reader.meta['static'], function(key, value) {
        $('#'+key+'_container.ftwtable').html('');
      });
    }
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
