var console=new(Class.create({initialize:function(){this.win=window.open('','console','scrollbars=yes,resizable=yes,height=240,width=480');this.win.document.open('text/html','replace');this.win.document.writeln(['<html><head><title>Javascript debug console for IE</title>','<style type="text/css">','body { font-size: 8pt; font-family: "Tahoma"; background-color: black; color: silver; margin: 0; overflow: hidden; }','input { font-size: 8pt; font-family: "Tahoma"; }','div#container { width: 100%; overflow-y: auto; overflow-x: hidden; height: expression(document.body.clientHeight - 20); }','div#container ul#console { list-style: none;white-space: nowrap; padding: 0; margin: 0; }','div#container ul#console li { padding: 1px 5px 3px; margin-bottom: 1px; }','div#container ul#console li.warn { background: #740;  }','div#container ul#console li.error { background: #a22; }','div#container ul#console li.info { background: #148; }','div#container ul#console li.xhr { background: #333; }','div#container ul#console li.xhr strong.url { cursor: pointer; }','div#container ul#console li.xhr div.response {','width: expression(document.body.clientWidth - 35); height: 120px; overflow: auto;','background: #444; border: 1px solid #666; margin: 5px;','}','li .object { color: green; }','li .function { color: khaki; font-weight: bold; }','li .class { color: #fff; }','li .property { color: #8cf; }','li .array, li .value { color: #f9f; }','li .node { color: khaki; }','li .boolean { color: pink; }','li .number, li .null, li .error, li .method { color: red; }','li .string { }','div.input { padding: 0; margin: 0; height: 20px; background-color: #222; }','div.input input { width: 100%; border: none; background-color: transparent; color: white; padding: 2px; }','</style></head><body>','<div id="container"><ul id="console"></ul></div>','<div class="input"><input type="input" id="commend" value=""/></div>','</body></html>'].join('\n'));this.container=$(this.win.document.getElementById('container'));this.console=$(this.win.document.getElementById('console'));this.commend=$(this.win.document.getElementById('commend')).observe('keyup',this.keypress.bindAsEventListener(this));this.commend.focus();this.history=[];this.historyIndex=0;var self=this;this.commands={'close':function(){self.win.close();self.disabled=true;},'exit':function(){this.close();},'quit':function(){this.close();},'clear':function(){self.console.update('');}};this.XHR(this.xhr.bind(this));},evaluate:function(){var value=this.commend.value.strip();try{if(this.commands[value])return this.commands[value]();if(value.match(/(\s?)var\s.*\=/))
value=value.replace('var ','');if(value.match(/(\s?)function\s.*\(.*\)/))
value=value.split('function ')[1].split('(')[0]+'= function(){'+value.split('{')[1];var v=eval(value);if(v!==undefined&&(typeof v).match(/string|object|function|boolean|number/))this.log(v);else window.eval(value);}catch(e){return this.error('<strong>'+e.name+'</strong>, '+e.message,': error');}finally{this.history[this.historyIndex]=value;this.historyIndex++;this.commend.value='';this.commend.focus();}},keypress:function(event){var keyCode=event.which||event.keyCode;switch(keyCode){case Event.KEY_UP:if(this.historyIndex>0){this.historyIndex--;this.commend.value=this.history[this.historyIndex];}
event.stop();break;case Event.KEY_DOWN:if(this.historyIndex<=this.history.length-1){this.historyIndex++;this.commend.value=(!this.history[this.historyIndex])?'':this.history[this.historyIndex];}
event.stop();break;case Event.KEY_RETURN:this.evaluate();event.stop();break;}},_inject:function(args){var line=[];for(var i=0;i<args.length;i++)line.push(this.Dumper(args[i]));return line.join(' ');},error:function(){this.type='error';return this.log(this._inject(arguments));},info:function(){this.type='info';return this.log(this._inject(arguments));},warn:function(){this.type='warn';return this.log(this._inject(arguments));},xhr:function(){this.type='xhr';return this.log(this._inject(arguments));},log:function(){if(this.disabled)return;if(this.win==null||(this.win.closed))this.initialize();var line=(this.type)?arguments[0]:this._inject(arguments);line=this.append(line);this.container.scrollTop=this.container.scrollHeight;this.type='';return $(line);},append:function(node){var li=this.win.document.createElement('li');li.className=this.type;if(typeof node=='object')li.innerHTML=node.innerHTML;else li.innerHTML=node;this.console.appendChild(li);return li;},XHR:function(log){try{var oldActiveXObject=ActiveXObject;var oldXMLHttpRequest=XMLHttpRequest;}catch(e){}
var ReplacementCtor=function(objectName){var self=this,time=new Date().getTime(),actualXHR,line;if(objectName!=undefined&&!objectName.toLowerCase().match(/\.xmlhttp/))return new oldActiveXObject(objectName);if(oldXMLHttpRequest)actualXHR=new oldXMLHttpRequest();else actualXHR=new oldActiveXObject(objectName);this.requestHeaders="";this.requestBody="";this.open=function(a,b,c,d,e){self.openMethod=a.toUpperCase();self.openURL=b;if(self.onopen!=null&&typeof self.onopen=="function"){self.onopen(a,b,c,d,e);}
return actualXHR.open(a,b,c,d,e);}
this.send=function(a){if(self.onsend!=null&&typeof this.onsend=="function"){self.onsend(a);}
self.requestBody+=a;return actualXHR.send(a);}
this.setRequestHeader=function(a,b){if(self.onsetrequestheader!=null&&typeof(self.onsetrequestheader)=="function"){self.onsetrequestheader(a,b);}
self.requestHeaders+=a+":"+b+"\r\n";return actualXHR.setRequestHeader(a,b);}
this.getRequestHeader=function(){return actualXHR.getRequestHeader();}
this.getResponseHeader=function(a){return actualXHR.getResponseHeader(a);}
this.getAllResponseHeaders=function(){return actualXHR.getAllResponseHeaders();}
this.abort=function(){return actualXHR.abort();}
this.addEventListener=function(a,b,c){return actualXHR.addEventListener(a,b,c);}
this.dispatchEvent=function(e){return actualXHR.dispatchEvent(e);}
this.openRequest=function(a,b,c,d,e){return actualXHR.openRequest(a,b,c,d,e);}
this.overrideMimeType=function(e){return actualXHR.overrideMimeType(e);}
this.removeEventListener=function(a,b,c){return actualXHR.removeEventListener(a,b,c);}
function copyState(){try{self.readyState=actualXHR.readyState;}catch(e){}
try{self.status=actualXHR.status;}catch(e){}
try{self.responseText=actualXHR.responseText;}catch(e){}
try{self.statusText=actualXHR.statusText;}catch(e){}
try{self.responseXML=actualXHR.responseXML;}catch(e){}}
actualXHR.onreadystatechange=function(){copyState();try{if(self.onupdate!=null&&typeof self.onupdate=="function"){self.onupdate();}}catch(e){}
if(self.readyState==4&&line){var response=line.down('div.response');var url=line.down('strong.url');var container=line.up(1);url.onclick=function(){var test=container.scrollTop>=container.scrollHeight-container.offsetHeight;response[response.visible()?'hide':'show']();if(test)container.scrollTop=container.scrollHeight;};line.down('span.time').innerHTML=(new Date().getTime()-time)+'ms';if(!self.responseText)response.style.height='20px';else response.innerHTML=self.responseText.escapeHTML().replace(/\n/g,'<br/>').replace(/\s\s/g,'&nbsp;&nbsp;');if(self.status!=200){url.style.color='red';url.innerHTML+=' ['+self.status+'!] ';}}
if(self.onreadystatechange!=null&&typeof self.onreadystatechange=="function")return self.onreadystatechange();line=log(['<span class="method">',self.openMethod,'</span><strong class="url">',self.openURL,'</strong>'].join(' '),'<span class="time">Loading...</span><div class="response" style="display: none;"></div>');}};if(oldXMLHttpRequest)window.XMLHttpRequest=ReplacementCtor;else window.ActiveXObject=ReplacementCtor;},_escape:function(str){return str.escapeHTML().replace(/\n/g,'<br/>').replace(/\s\s/g,'&nbsp;&nbsp;');},Dumper:function(o,level){var dump=[],level=level||1;this.settings={DumperObject:null,DumperMaxDepth:2,DumperIgnoreStandardObjects:true,DumperProperties:null,DumperTagProperties:[]};if(this.settings.DumperMaxDepth!=-1&&level>this.settings.DumperMaxDepth)return"...";if(this.settings.DumperIgnoreStandardObjects)
if(o==window||o==window.document)
return'<span class="error"><strong>[Ignored Object]</strong></span>';if(o=='null'||o==null)return'<span class="null">null</span>';switch(typeof o){case'function':return'<span class="function">Function</span>';case'number':case'boolean':dump=['<span class="',typeof o,'">',o,'</span>'];break;case'string':dump=['<span class="string">',(this.type!='xhr')?this._escape(o):o,'</span>'];break;case'object':dump=this._analyzeObject(o,level);}
return(dump.join)?dump.join(''):dump;},_analyzeObject:function(o,level){var ret=[];if(o.nodeName){if(o.nodeType==3&&!/\S/.test(o.nodeValue)){ret.push('<span class="node">textnode</span>: ',o.nodeName);}else if(o.nodeType==1){var setAttribute=function(attribute,value){if(!attribute||!value)return'';else return[' <span class="property">',attribute,'="<span class="value">',value,'</span>"</span>'].join('');};var id=setAttribute('id',o.id);var cn=setAttribute('class',o.className);var ss=[];if(o.nodeName=="SCRIPT")ss.push(setAttribute('src',o.src));else if(o.nodeName=="LINK")ss.push(setAttribute('href',o.href));ret.push('<span class="node">&lt;',o.nodeName.toLowerCase(),id,cn,ss.join(''),'&gt;</span>');}}else if(typeof o.length=="number"){if(o.length>10)return'<span class="error">Error :</span> too many objects '+o.length;ret.push('<strong class="array">[</strong> ');for(var i=0;i<o.length;i++){if(i>0)ret.push(', ');ret.push(this.Dumper(o[i],level+1));}
ret.push('<strong class="array">]</strong>');}else{if(level>1)return'<span class="object">Object</span>';if(!(o instanceof Object)||!o)return o;ret.push('<strong class="object">{</strong> ');var count=0;for(i in o){if(count>this.settings.DumperMaxDepth){ret.push(' ...');break;}
if(o!=this.settings.DumperObject||this.settings.DumperProperties==null||this.settings.DumperProperties[i]==1){if(typeof o[i]!='unknown'){var processAttribute=true;if(typeof o.tagName!='undefined'){if(typeof this.settings.DumperTagProperties[o.tagName]!='undefined'){processAttribute=false;for(var p=0;p<this.settings.DumperTagProperties[o.tagName].length;p++){if(this.settings.DumperTagProperties[o.tagName][p]==i){processAttribute=true;break;}}}}
if(processAttribute){if(count++>0)ret.push(', ');ret.push(i+': '+this.Dumper(o[i],level+1));}}}}
ret.push(' <strong class="object">}</strong>');}
return ret;}}))();