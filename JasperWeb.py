#!/usr/bin/env python2

# This version of JasperWeb allows the user to step through one sample at a time, instead of returning a table full of samples.
# My assumption is that for the most part, you only need to validate the record once, after that it should automatically skip
# all the records that have already been verified.

# -*- coding: utf-8 -*-
from datetime import datetime
import json
import wsgiref.simple_server
from SocketServer import ThreadingMixIn
import re
import sqlite3
import urlparse
from urllib2 import unquote
import os,sys
from jasper import paths

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
        first_rowID=""
        prev_rowID=""
        next_rowID=""
        transcription=""
        result=""
        post_data=""
        reQS=re.compile("([^=]+)=([^&]*)&?")
        
        # gather parameters from GET
        if( environ["QUERY_STRING"] ):
            for namevalue in reQS.findall(environ["QUERY_STRING"]):
                if( namevalue[0].lower()=="wavfile" ):
                    wavfile=os.path.join(audiolog_path,namevalue[1])
                if( namevalue[0].lower()=="rowid" ):
                    rowID=namevalue[1]

        # gather parameters from POST
        content_length=0
        if( environ['CONTENT_LENGTH'] ):
            content_length = int(environ['CONTENT_LENGTH'])
            post_data=environ['wsgi.input'].read(content_length)
            # Parse it out
            for namevalue in reQS.findall(post_data):
                if( namevalue[0].lower()=="result" ):
                    result=namevalue[1].lower()
                if( namevalue[0].lower()=="transcription" ):
                    transcription=unquote(namevalue[1].replace('+',' '))
        """
        if( content_length ):
            request = json.loads(environ['wsgi.input'].read(content_length))
            for key in request:
                if( key.lower()=="action" ):
                    action=request[key]
                if( key.lower()=="rowid" ):
                    rowID=request[key]
                if( key.lower()=="transcription" ):
                    transcription=request[key]
                if( key.lower()=="result" ):
                    result=request[key]
        """
        # Handle the request
        # serve a .wav file
        if( len(wavfile) and os.path.isfile(wavfile) ):
            start_response('200 OK',[('content-type','audio/wav')])
            with open(wavfile, "rb") as w:
                ret = w.read()
            w.close()
            return ret
        else:
            conn=sqlite3.connect(audiolog_db)
            c=conn.cursor()
            # Return the main page
            c.execute("select RowID from audiolog where reviewed='' order by RowID asc limit 1")
            row=c.fetchone()
            if( row is not None ):
                first_rowID=str(row[0])
            if( rowID=="" ):
                rowID=first_rowID
            print( "rowID=%s"%rowID )
            # get the previous rowid and next rowid
            c.execute("select RowID from audiolog where RowID<:RowID order by RowID desc limit 1",{"RowID":rowID})
            row=c.fetchone()
            if( row is not None ):
                prev_rowID=str(row[0])
            c.execute("select RowID from audiolog where RowID>:RowID order by RowID asc limit 1",{"RowID":rowID})
            row=c.fetchone()
            if( row is not None ):
                next_rowID=str(row[0])
            if( result.lower()=="correct" ):
                c.execute("update audiolog set verified_transcription=transcription,reviewed=:reviewed where RowID=:RowID",{"reviewed":datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),"RowID":rowID} )
            if( result.lower()=="update" ):
                if( len(transcription) ):
                    c.execute("update audiolog set verified_transcription=:verified_transcription,reviewed=:reviewed where RowID=:RowID",{"verified_transcription":transcription,"reviewed":datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),"RowID":rowID} )
                else:
                    c.execute("update audiolog set type='noise',verified_transcription='',reviewed=:reviewed where RowID=:RowID",{"reviewed":datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),"RowID":rowID} )
            if( result.lower()=="nothing" ):
                c.execute("update audiolog set type='noise',verified_transcription='',reviewed=:reviewed where RowID=:RowID",{"reviewed":datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),"RowID":rowID} )
            conn.commit()
            conn.close()
            if( len(first_rowID) ):
                ret=[]
                # Get the first unvalidated row from the database
                start_response('200 OK',[('content-type','text/html;charset=utf-8')])
                ret.append('<html><head><title>Test</title>')
                ret.append("""
<script language="javascript">
    // Submit an updated transcription to the server. Upon success, make the "revert" button inactive
    function UpdateTranscription(RowID){
        var Transcription=document.getElementById("transcription_"+RowID).value;
        alert( "Transcription="+Transcription );
        var xhttp=new XMLHttpRequest();
        xhttp.onreadystatechange=function(){
            if( this.readyState==4 && this.status==200 ){
                // Check this.responseText
                var message=JSON.parse(this.responseText).message;
                if( message=="SUCCESS;Updated "+RowID ){
                    // disable reset button
                    document.getElementById("reset_"+RowID).disabled=true;
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
                c.execute("select datetime,filename,type,transcription,verified_transcription,speaker,reviewed from audiolog where rowid=:RowID",{"RowID":rowID})
                row=c.fetchone()
                conn.close()
                Filename=str(row[1])
                Type=str(row[2])
                Original_Transcription=str(row[3])
                Transcription=str(row[3])
                if( len(row[6]) ):
                    Transcription=str(row[4])
                Speaker=str(row[5])
                ret.append("""<ul>""")
                ret.append("""<li>post_data: %s</li>"""%post_data)
                ret.append("""<li>Result: %s</li>"""%result)
                if( result=="update" ):
                    ret.append("""<li>transcription: %s</li>"""%transcription)
                ret.append("""</ul>""")
                ret.append("""<h1>Jasper</h1>""")
                ret.append("""<audio controls type="audio/wav"><source src="?wavfile=%s" /></audio><br />"""%Filename )
                ret.append("""Jasper heard "<span style="font-weight:bold">%s</span>"<br />"""%Original_Transcription )
                ret.append("""What did you hear?<br />""")
                ret.append("""<form method="POST">""")
                ret.append("""<input type="radio" name="result" value="correct" onclick="document.getElementById('update_transcription').disabled=true"/> The transcription is correct. I heard the same thing<br />""")
                ret.append("""<input type="radio" name="result" value="update" onclick="document.getElementById('update_transcription').disabled=false"/> The transcription is not correct. This is what I heard: <input id="update_transcription" type="text" name="transcription" value="%s" disabled=true/><br />"""%Transcription)
                ret.append("""<input type="radio" name="result" value="nothing" onclick="document.getElementById('update_transcription').disabled=true"/> This was just noise with no voices.<br />""")
                ret.append("""<input type="submit" value="Submit"/><br />""")
                if( prev_rowID ):
                    ret.append("""<input type="button" value="Prev" onclick="goprev()">""")
                if( next_rowID ):
                    ret.append("""<input type="button" value="Next" onclick="gonext()">""")
                ret.append( """</body></html>""" )
                return ret
            else:
                return ["<html><head><title>Nothing to validate</title></head><body><h1>Nothing to validate</h1></body></html>"]

class ThreadingWSGIServer(ThreadingMixIn,wsgiref.simple_server.WSGIServer):
    pass

port=8080
print("Listening on port %d"%port)
server=wsgiref.simple_server.make_server('',port,application,ThreadingWSGIServer)
server.serve_forever()
