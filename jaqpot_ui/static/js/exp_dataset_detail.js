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

//display tooltip left
$('[data-toggle="tool"]').tooltip({
    'placement': 'left'
});


/* setTimeout(function ()
  {
    oTable.fnAdjustColumnSizing();
  }, 10 );*/
 $('#dataset tbody td.edit').editable( function( sValue ) {
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
    //var data = $('#dataset').DataTable().column(2).data()
    data = JSON.stringify(data)
    //if r.squared >= r2.threshold
    if (SQUARED >= THRESHOLD){
        $("#myModal").modal()
        $('#btnYes').click(function() {
            // clean dataset send for training
            var id = $('#myModal').data('id');
            $('[data-id='+id+']').remove();
            $('#myModal').modal('hide');
             window.location = '/clean_dataset?dataset=' +DATASET_NAME
        });
         $('#btnNo').click(function() {
           //Continue with experimental design
            $.ajax({
                type: "post",
                url: "/exp_submit",
                dataType: "json",
                //contentType: 'application/json;',
                data: { 'data': data, 'dataset_name': JSON.stringify(DATASET_NAME) },
                //data: {queryData : JSON.stringify({'data': data, 'dataset_name': DATASET_NAME})},
                success: function(data){
                    window.location = '/exp_iter?dataset=' + data;

                },
                error: function(){
                    console.log("error");
                }
            });
            var id = $('#myModal').data('id');
            $('[data-id='+id+']').remove();
            $('#myModal').modal('hide');

        });
        /*$(function() {
            $( "#dialog-confirm" ).html("You have reached your desired R Squared threshold. Do you want to use this dataset for modelling?");
            $( "#dialog-confirm" ).dialog({
			  modal: true,
			  width: 608,
			  height: 320,
			  left: 300,
			  top: 200,
              buttons: {
                "Yes": function() {
                  $( this ).dialog( "close" );
                  //redirect to training and clean the dataset
                  //open.window.href = '/exp_iter?dataset=' + data;;
                },
                "No": function() {
                  $( this ).dialog( "close" );
                }
              }
            });
          });*/
          }
     else{
     $.ajax({
                type: "post",
                url: "/exp_submit",
                dataType: "json",
                //contentType: 'application/json;',
                data: { 'data': data, 'dataset_name': JSON.stringify(DATASET_NAME) },
                //data: {queryData : JSON.stringify({'data': data, 'dataset_name': DATASET_NAME})},
                success: function(data){
                    alert(data)
                    window.location = '/exp_iter?dataset=' + data;

                },
                error: function(){
                    console.log("error");
                }
            });
        }
    });