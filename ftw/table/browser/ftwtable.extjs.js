//
// create closure
//
(function($) {    
    
    var $this = null;
    
    $.fn.ftwtable.createTable = function(table, url){ 
        $this = table;
        
        console.log('bfore');
        
        var store = new Ext.data.Store({
            remoteSort: true,
            baseParams: {lightWeight:true,ext: 'js'},
            //sortInfo: {field:'lastpost', direction:'DESC'},
            autoLoad: {params:{start:0, limit:500}},

            proxy: new Ext.data.HttpProxy({
                url: url,
                method: 'post'
            }),

            reader: new Ext.data.JsonReader({
                root: 'rows',
                totalProperty: 'totalCount',
                fields: [
                    {name: 'path_radiobutton', type: 'string' },
                    {name: 'created', type: 'string'},
                    {name: 'Title', type: 'string'}
                ]
            })
        });
        
        
        var grid = new Ext.grid.GridPanel({
            store: store,
            columns: [
                {id:'path_radiobutton',header: '', width: 30,sortable: false, dataIndex: 'path_radiobutton'},
                {id:'Title',header: 'Title', sortable: true, dataIndex: 'Title'},
                {id:'created',header: 'Created', width: 160, sortable: true, dataIndex: 'created'}
            ],
            stripeRows: true,
            autoExpandColumn: 'Title',
            width: '100%',    
            height: 200
        });
        
        grid.render('template_chooser');

        // $this.load(query, function(){           
        //     $o.onLoad();
        // });
    };
//
// end of closure
//
})(jQuery);
