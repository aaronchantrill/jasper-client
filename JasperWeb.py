#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from datetime import datetime
import json
import wsgiref.simple_server
from SocketServer import ThreadingMixIn
import re
import sqlite3
import urlparse
import os,sys
applicationdir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"jasper")
sys.path.insert(0,applicationdir)
import paths

def application(environ,start_response):
    print( "PATH_INFO=%s"%environ["PATH_INFO"] )
    if( environ["PATH_INFO"]=="/favicon.ico" ):
        start_response('404 Not Found',[('content-type','text/plain;charset=utf-8')])
        ret="404 Not Found"
        return ret
    else:
        audiolog_path=os.path.join(paths.CONFIG_PATH,"audiolog")
        audiolog_db=os.path.join(audiolog_path,"audiolog.db")
        wavfile=""
        action=""
        rowID=""
        transcription=""
        
        # gather parameters from GET
        if( environ["QUERY_STRING"] ):
            reQS=re.compile("([^=]+)=([^&]*)&?")
            for namevalue in reQS.findall(environ["QUERY_STRING"]):
                if( namevalue[0]=="wavfile" ):
                    wavfile=os.path.join(audiolog_path,namevalue[1])
        # gather parameters from POST
        content_length=0
        if( environ['CONTENT_LENGTH'] ):
            content_length = int(environ['CONTENT_LENGTH'])
        if( content_length ):
            request = json.loads(environ['wsgi.input'].read(content_length))
            for key in request:
                if( key.lower()=="action" ):
                    action=request[key]
                if( key.lower()=="rowid" ):
                    rowID=int(request[key])
                if( key.lower()=="transcription" ):
                    transcription=request[key]
        # Handle the request
        # serve a .wav file
        if( len(wavfile) and os.path.isfile(wavfile) ):
            start_response('200 OK',[('content-type','audio/wav')])
            with open(wavfile, "rb") as w:
                ret = w.read()
            w.close()
            return ret
        else:
            # delete a record from the database
            if( action.lower()=="delete" ):
                start_response('200 OK',[('content-type','application/json;charset=utf-8')])
                conn=sqlite3.connect(audiolog_db)
                c=conn.cursor()
                c.execute("delete from audiolog where RowID=%d"%rowID)
                conn.commit()
                conn.close()
                ret=json.dumps({"message":"SUCCESS;Deleted %s"%str(rowID)})
                return ret
            # update a transcription
            if( action.lower()=="update" ):
                start_response('200 OK',[('content-type','application/json;charset=utf-8')])
                conn=sqlite3.connect(audiolog_db)
                c=conn.cursor()
                c.execute( "update audiolog set verified_transcription='%s',reviewed=strftime('%%Y-%%m-%%d %%H:%%M:%%S','now') where RowID=%d"%(transcription,rowID) )
                conn.commit()
                conn.close()
                ret=json.dumps({"message":"SUCCESS;Updated %s"%str(rowID)})
                return ret
            else:
                # Return the main table
                ret=[]
                start_response('200 OK',[('content-type','text/html;charset=utf-8')])
                ret.append('<html><head><title>Test</title>')
                ret.append("""
<script language="javascript">
    // Submit an updated transcription to the server. Upon success, make the "revert" button inactive
    function UpdateTranscription(RowID){
        var Transcription=document.getElementById("transcription_"+RowID).value;
        var xhttp=new XMLHttpRequest();
        xhttp.onreadystatechange=function(){
            if( this.readyState==4 && this.status==200 ){
                // Check this.responseText
                var message=JSON.parse(this.responseText).message;
                if( message=="SUCCESS;Updated "+RowID ){
                    // disable reset button
                    document.getElementById("reset_"+RowID).disabled=true;
                    document.getElementById("r"+RowID).parentNode.removeChild(document.getElementById("r"+RowID));
                }else{
                    //alert( "message="+message );
                }
            }else{
                //alert( "responseText="+this.responseText );
            }
        }
        xhttp.open("POST",window.location.href.split(/[?#]/)[0],true);
        var request=JSON.stringify({"action":"update","RowID":RowID,"Transcription":Transcription});
        xhttp.send(request);
    }
    
    // Delete a line from the database and, if the response is success, delete the line from the page also.
    function DeleteAudio(RowID){
        var xhttp=new XMLHttpRequest();
        xhttp.onreadystatechange=function(){
            if( this.readyState==4 && this.status==200 ){
                // Check this.responseText to make sure it contains a success message
                var message=JSON.parse(this.responseText).message;
                if( message=="SUCCESS;Deleted "+RowID ){
                    document.getElementById("r"+RowID).parentNode.removeChild(document.getElementById("r"+RowID));
                }else{
                    //alert(message);
                }
            }
        };
        xhttp.open("POST",window.location.href.split(/[?#]/)[0],true);
        var request='{"action":"delete","RowID":"'+RowID+'"}';
        xhttp.send(request);
    }
</script>""")
                ret.append('</head>\n<body>\n')
                
                conn=sqlite3.connect(audiolog_db)
                c=conn.cursor()
                c.execute("select rowid,datetime,filename,type,transcription,verified_transcription,speaker,reviewed from audiolog where reviewed=''")
                rows=c.fetchall()
                ret.append("""<table id="audioclips" border=1 width="100%">\n""")
                for row in rows:
                    print( "%s"%str(row) )
                    RowID=int(row[0])
                    # Convert this to a datetime expression
                    #DateTime=datetime.strptime(row[1],'%Y-%m-%d %H:%M:%S')
                    Filename=str(row[2])
                    Type=str(row[3])
                    Transcription=str(row[4])
                    if( len(row[7]) ):
                        Transcription=str(row[5])
                    Speaker=str(row[6])
                    #Reviewed=datetime.strptime(row[7],'%Y-%m-%d %H:%M:%S')
                    ret.append( """<tr id="r%d">"""%RowID )
                    ret.append( """<td>%s</td>"""%Type )
                    ret.append( """<td style="width:320px"><audio controls src="?wavfile=%s" type="audio/wav"/></td>"""%Filename )
                    ret.append( """<form method="get"><td><input id="transcription_%d" type="text" name="transcription" value="%s" style="width:90%%;margin:20px" onchange="document.getElementById('reset_%d').disabled=false" /></td>"""%(RowID,Transcription,RowID) )
                    ret.append( """<td><input type="button" name="action" value="Verify" onclick="UpdateTranscription(%d)"/><input id="reset_%d" type="reset" disabled=true onclick="this.disabled=true"/></td></form>"""%(RowID,RowID) )
                    ret.append( """<form><td><input id="delete_%d" type="button" name="action" value="Delete" onclick="DeleteAudio(%d);"/></td></form>"""%(RowID,RowID) )
                    ret.append( """</tr>\n""" )
                ret.append("</table>\n")
                conn.close()
                ret.append( """</body></html>""" )
                return ret

class ThreadingWSGIServer(ThreadingMixIn,wsgiref.simple_server.WSGIServer):
    pass

port=8000
print("Listening on port %d"%port)
server=wsgiref.simple_server.make_server('',8000,application,ThreadingWSGIServer)
server.serve_forever()
