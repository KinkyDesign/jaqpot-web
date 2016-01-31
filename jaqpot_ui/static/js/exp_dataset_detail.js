
     $(document).ready( function () {

        var oTable = $('#dataset').DataTable( {
        "bJQueryUI": true,
        "bScrollCollapse": true,
        "bAutoWidth": false,
        "bPaginate":false,
        "dom": 'ft',
        "sScrollX": "100%",
        "sScrollXInner": "100%",
        "editable": true,

         "fnDrawCallback": function( oSettings )
         {
            $('.dataTables_scrollBody table thead tr').css({ 'height' : '0px' });
        },
        "fnInitComplete": function(oSettings, json)
         {
            $('.dataTables_scrollBody table thead tr').css({ 'height' : '0px' });
        },
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
        switch(aData[1]){
            case '1':
                $(nRow).css('color', 'red')
                break;
        }
        var tab = $('#dataset').DataTable();
        tab.columns(1).visible( false );
    }

        });

    } );


function myFunction() {
            var tab = $('#dataset').DataTable();
            tab.columns(1).visible( false );
            //tab.columns('.column').visible( false );
            for ( var i=1 ; i<4 ; i++ ) {
                tab.columns(i).visible( false );
            }
            tab.columns(':contains(A2V)').visible( true );
            tab.columns.adjust().draw( false ); // adjust column sizing and redraw
        }
$(function () {
  $('[data-toggle="tooltip"]').tooltip({
    container : 'body'
  });


});

//display tooltip right
$('[data-toggle="tool"]').tooltip({
    'placement': 'left'
});

/* setTimeout(function ()
  {
    oTable.fnAdjustColumnSizing();
  }, 10 );*/
 $('#dataset tbody td').editable( function( sValue ) {
		/* Get the position of the current data from the node */
		 var oTable = $('#dataset').dataTable()
		var aPos = oTable.fnGetPosition( this );

		/* Get the data array for this row */
		var aData = oTable.fnGetData( aPos[0] );

		/* Update the data array and return the value */
		aData[ aPos[2] ] = sValue;
		return sValue;
	}, { "onblur": 'submit' } ); /* Submit the form when bluring a field */

 $("#exp").on("click", function (){
    var data =  $('#dataset').DataTable().data()
    data = JSON.stringify(data)
    //if r.squared >= r2.threshold
    /*if (SQUARED >= THRESHOLD){
        $(function() {
            $( "#dialog-confirm" ).dialog({
              resizable: false,
              height:140,
              modal: true,
              buttons: {
                "Delete all items": function() {
                  $( this ).dialog( "close" );
                },
                Cancel: function() {
                  $( this ).dialog( "close" );
                }
              }
            });
          });
          }*/
     $.ajax({
                type: "get",
                url: "/exp_submit",
                dataType: "json",
                contentType: 'application/json;',
                data: { 'data': data, 'dataset_name': JSON.stringify(DATASET_NAME), },
                //data: {queryData : JSON.stringify({'data': data, 'dataset_name': DATASET_NAME})},
                success: function(data){
                    alert(data)
                    window.location = '/exp_iter?dataset=' + data;

                },
                error: function(){
                    console.log("error");
                }
            });

    });