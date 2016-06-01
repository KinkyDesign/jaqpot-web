  $(document).ready( function () {
  $( "input[name='output']" ).on(
        {
          'change' : function( )
                     {
                       $.each( $( "input[name='output']" ),
                               function( )
                               {
                                 var ObjectId, ObjectValue;

                                 if( $(this).is(':checked') )
                                 {
                                   /*Checked radio button OBJECT */
                                   ObjectId    = $(this).attr( 'id' );     /* Id of above Jquery object */
                                   //get number of id
                                   num = ObjectId.split('output_')[1]
                                   if(  $("#id_input_"+num).is(':checked') ){
                                        $("#id_input_"+num).prop("checked", false);
                                   }
                                 }

                               }
                             );
                     }
        }
     );
});